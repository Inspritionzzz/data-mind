# -*- coding: utf-8 -*-
"""
登录层 / 浏览器会话管理（企查查）
    企查查需登录且反爬强（加密参数 + 滑块/点选验证码 + IP 频控），纯 HTTP 直连不可行。
    方案：Playwright 持久化浏览器承载登录态（扫码一次长期复用），
    命中验证码/风控页时暂停，由人工在可见浏览器内完成后再继续。
"""
import logging
import random
import time

try:
    from . import config
except ImportError:  # 支持在包内直接 python main.py 运行
    import config

logger = logging.getLogger(__name__)


class QccBrowser:
    """Playwright 持久化浏览器封装：登录态 + 页面导航 + 验证码处理"""

    # 命中验证/风控的判定线索
    BLOCK_URL_HINTS = ('check', 'verify', 'captcha', 'antibot', 'security')
    BLOCK_TEXT_HINTS = ('安全验证', '验证码', '拖动滑块', '拖动下方滑块', '点击图中',
                        '访问频繁', '访问验证', '人机验证', '请完成验证', '滑动验证',
                        '请先完成安全验证')

    def __init__(self, headless=None):
        self.pw = None
        self.context = None
        self.page = None
        self.headless = config.HEADLESS if headless is None else headless

    # ---------- 生命周期 ----------
    def start(self):
        from playwright.sync_api import sync_playwright
        config.ensure_data_dir()
        self.pw = sync_playwright().start()
        self.context = self.pw.chromium.launch_persistent_context(
            user_data_dir=config.BROWSER_PROFILE,
            headless=self.headless,
            viewport=config.VIEWPORT,
            user_agent=config.USER_AGENT,
        )
        self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
        logger.info('浏览器已启动（持久化登录态目录: %s）', config.BROWSER_PROFILE)

    def close(self):
        try:
            if self.context:
                self.context.close()
            if self.pw:
                self.pw.stop()
        except Exception as e:  # noqa: BLE001
            logger.warning('关闭浏览器异常: %s', e)

    def is_alive(self):
        """检测浏览器/页面是否仍存活（窗口被手动关闭后返回 False）"""
        try:
            return bool(self.page and self.page.evaluate('() => true'))
        except Exception:  # noqa: BLE001
            return False

    # ---------- 导航 ----------
    def goto(self, url, wait_until='domcontentloaded'):
        """统一跳转 + 随机短停，模拟人工浏览节奏"""
        self.page.goto(url, wait_until=wait_until)
        time.sleep(random.uniform(*config.PAGE_PAUSE))

    # ---------- 登录 ----------
    def is_logged_in(self):
        """
        DOM 判定登录态：
            已登录 -> 出现用户头像/“我的企查查/退出登录/会员中心”等；
            未登录 -> 顶栏出现“登录/注册”按钮。
        """
        try:
            return bool(self.page.evaluate('''() => {
                const hasAvatar = !!document.querySelector(
                    'img[class*="avatar"], .user-avatar, .header-userinfo, .userinfo, .user-info');
                const txt = document.body ? (document.body.innerText || '') : '';
                const memberHint = txt.includes('我的企查查') || txt.includes('退出登录')
                    || txt.includes('会员中心');
                if (hasAvatar || memberHint) return true;
                const nodes = Array.from(document.querySelectorAll('a, button, span, div'));
                const hasLoginBtn = nodes.some(el => el.childElementCount === 0
                    && ['登录', '注册', '登录/注册', '登录 | 注册'].includes((el.textContent || '').trim())
                    && el.offsetParent);
                return !hasLoginBtn && memberHint;
            }'''))
        except Exception:  # noqa: BLE001
            return False

    def show_login(self):
        """未登录时尝试唤起登录弹窗（展示扫码框）"""
        try:
            for sel in ['a:has-text("登录")', 'button:has-text("登录")',
                        'text=登录', '.login-btn', '.header-login']:
                try:
                    self.page.locator(sel).first.click(timeout=3000)
                    logger.info('已点击登录按钮，等待登录')
                    return
                except Exception:  # noqa: BLE001
                    continue
            logger.info('若未自动弹出登录框，请在浏览器中手动点击“登录”')
        except Exception as e:  # noqa: BLE001
            logger.warning('唤起登录失败: %s', e)

    def login(self):
        """登录主流程：已登录直接返回；否则唤起登录并轮询等待人工完成"""
        self.goto(config.HOME_URL)
        if self.is_logged_in():
            logger.info('登录态有效')
            return True
        logger.info('未检测到登录态，尝试唤起登录...')
        self.show_login()
        logger.info('请在弹出的浏览器中扫码/账号登录企查查（%d 秒内）...', config.LOGIN_TIMEOUT)
        deadline = time.time() + config.LOGIN_TIMEOUT
        while time.time() < deadline:
            time.sleep(3)
            if self.is_logged_in():
                logger.info('登录成功')
                self.goto(config.HOME_URL)
                return True
        logger.error('登录超时/未检测到登录态')
        return False

    # ---------- 验证码 / 风控 ----------
    def detect_block(self):
        """检测当前页是否命中验证/风控"""
        try:
            url = (self.page.url or '').lower()
            if any(h in url for h in self.BLOCK_URL_HINTS):
                return True
            text = self.page.evaluate(
                '() => (document.body && document.body.innerText || "").slice(0, 600)')
            return any(h in text for h in self.BLOCK_TEXT_HINTS)
        except Exception:  # noqa: BLE001
            return False

    def wait_human_solve(self, timeout=None):
        """命中验证时暂停，提示人工在可见浏览器完成，轮询直至验证消失或超时"""
        timeout = timeout or config.CAPTCHA_TIMEOUT
        if self.headless:
            logger.error('无头模式无法人工过验证码，请去掉 --headless 以有头模式运行')
            return False
        logger.warning('检测到验证码/风控页，请在浏览器窗口内手动完成验证（%d 秒内）...', timeout)
        deadline = time.time() + timeout
        while time.time() < deadline:
            time.sleep(3)
            if not self.detect_block():
                logger.info('验证已通过，继续')
                time.sleep(1.5)
                return True
        logger.error('等待人工验证超时')
        return False

    def ensure_no_block(self):
        """若命中验证则等待人工处理；返回是否可继续（True=无阻塞/已通过）"""
        if self.detect_block():
            return self.wait_human_solve()
        return True
