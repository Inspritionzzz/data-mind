# -*- coding: utf-8 -*-
"""
登录层：Playwright 持久化浏览器 + 登录态管理
抖音 Web API 有 a_bogus 签名防护，纯 httpx 不可行：
    - 数据采集：驱动页面、拦截页面自身发出的已签名 API 响应
    - 执行动作：DOM 点击（点赞/收藏/评论/关注）
"""
import logging
import os
import time

try:
    from . import config
except ImportError:  # 支持在包内直接 python main.py 运行
    import config

logger = logging.getLogger(__name__)


class DouyinBrowser:
    """持久化浏览器封装"""

    def __init__(self):
        self.pw = None
        self.context = None
        self.page = None

    def start(self):
        from playwright.sync_api import sync_playwright
        config.ensure_data_dir()
        os.makedirs(config.BROWSER_PROFILE, exist_ok=True)
        self.pw = sync_playwright().start()
        self.context = self.pw.chromium.launch_persistent_context(
            user_data_dir=config.BROWSER_PROFILE,
            headless=False,
            user_agent=config.USER_AGENT,
            viewport={'width': 1280, 'height': 800},
        )
        self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
        logger.info('浏览器已启动')

    def close(self):
        try:
            if self.context:
                self.context.close()
            if self.pw:
                self.pw.stop()
        except Exception as e:
            logger.warning('关闭浏览器异常: %s', e)

    def is_alive(self):
        """检测浏览器/页面是否仍存活（窗口被手动关闭后返回 False）"""
        try:
            return bool(self.page and self.page.evaluate('() => true'))
        except Exception:
            return False

    # ---------- 登录 ----------
    # 抖音登录后下发的 Cookie（任一存在即视为已登录，不同账号/版本可能不全）
    LOGIN_COOKIE_HINTS = ('LOGIN_STATUS', 'sessionid', 'sessionid_ss',
                          'sid_guard', 'sid_tt', 'uid_tt', 'uid_tt_ss')

    def is_logged_in(self):
        """多信号判断登录态：登录 Cookie 任一存在，或 DOM 无登录按钮且有头像"""
        try:
            cookies = {c['name']: c['value']
                       for c in self.context.cookies('https://www.douyin.com')}
            if any(cookies.get(name) for name in self.LOGIN_COOKIE_HINTS):
                return True
        except Exception:
            return False
        # DOM 兜底：未登录顶栏有"登录"按钮，已登录则显示头像
        try:
            return bool(self.page.evaluate('''() => {
                const hasLoginBtn = !!Array.from(
                    document.querySelectorAll('button, div, span'))
                    .find(el => el.childElementCount === 0 &&
                                el.textContent.trim() === '登录' && el.offsetParent);
                const avatar = document.querySelector(
                    '[data-e2e="user-info"] img, img[class*="avatar"]');
                return !hasLoginBtn && !!avatar;
            }'''))
        except Exception:
            return False

    def _show_login_dialog(self):
        """未登录时尝试唤起登录弹窗（展示扫码框）"""
        try:
            for sel in ['button:has-text("登录")', 'text=登录',
                        '[data-e2e="login-button"]']:
                try:
                    self.page.locator(sel).first.click(timeout=3000)
                    logger.info('已点击登录按钮，等待扫码')
                    return
                except Exception:
                    continue
            logger.info('若未自动弹出扫码框，请在浏览器中手动点击"登录"')
        except Exception as e:
            logger.warning('唤起登录弹窗失败: %s', e)

    def login(self):
        """登录主流程：已登录直接返回；否则等待人工扫码"""
        self.page.goto(config.HOME_URL, wait_until='domcontentloaded')
        time.sleep(3)
        if self.is_logged_in():
            logger.info('登录态有效')
            return True
        self._show_login_dialog()
        logger.info('请在弹出的浏览器中扫码登录抖音（%d 秒内）...', config.LOGIN_TIMEOUT)
        deadline = time.time() + config.LOGIN_TIMEOUT
        while time.time() < deadline:
            time.sleep(3)
            if self.is_logged_in():
                logger.info('扫码登录成功')
                self.page.goto(config.HOME_URL, wait_until='domcontentloaded')
                time.sleep(2)
                return True
        logger.error('登录超时')
        return False
