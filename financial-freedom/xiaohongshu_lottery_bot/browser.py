# -*- coding: utf-8 -*-
"""
登录层 / 浏览器会话管理
    小红书 Web API 有 X-s / X-t 签名防护，纯 HTTP 直连不可行。
    方案：Playwright 持久化浏览器承载登录态（扫码一次即可），
    并调用页面内官方签名函数 window._webmsxyw 生成签名后请求。
"""
import logging
import time
from urllib.parse import urlencode

try:
    from . import config
except ImportError:  # 支持在包内直接 python main.py 运行
    import config

logger = logging.getLogger(__name__)

USER_AGENT = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
              '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')


class XhsBrowser:
    """Playwright 持久化浏览器封装：登录态 + 签名 + API 请求"""

    def __init__(self):
        self.pw = None
        self.context = None
        self.page = None

    # ---------- 生命周期 ----------
    def start(self):
        from playwright.sync_api import sync_playwright
        config.ensure_data_dir()
        self.pw = sync_playwright().start()
        self.context = self.pw.chromium.launch_persistent_context(
            user_data_dir=config.BROWSER_PROFILE,
            headless=config.HEADLESS,
            viewport={'width': 1280, 'height': 800},
            user_agent=USER_AGENT,
        )
        self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
        logger.info('浏览器已启动（持久化登录态目录: %s）', config.BROWSER_PROFILE)

    def close(self):
        try:
            if self.context:
                self.context.close()
            if self.pw:
                self.pw.stop()
        except Exception as e:
            logger.warning('关闭浏览器异常: %s', e)

    # ---------- 登录 ----------
    def is_logged_in(self):
        """
        以 user/me 接口判断真实登录态
        注意：小红书对游客也会下发 web_session 且 user/me 返回 code=0，
        但游客响应带 guest=true，必须排除
        """
        try:
            data = self.api_get('/api/sns/web/v2/user/me')
            info = data.get('data') or {}
            return (data.get('code') == 0 and bool(info.get('user_id'))
                    and not info.get('guest'))
        except Exception:
            return False

    def _show_login_dialog(self):
        """未登录时尝试唤起登录弹窗（展示扫码框）"""
        try:
            for sel in ['text=登录', 'button:has-text("登录")', '.login-btn']:
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
        self.page.goto(config.EXPLORE_URL, wait_until='domcontentloaded')
        time.sleep(3)
        if self.is_logged_in():
            logger.info('登录态有效')
            return True
        self._show_login_dialog()
        logger.info('请在弹出的浏览器中扫码登录小红书（%d 秒内）...', config.LOGIN_TIMEOUT)
        deadline = time.time() + config.LOGIN_TIMEOUT
        while time.time() < deadline:
            time.sleep(3)
            if self.is_logged_in():
                logger.info('扫码登录成功')
                self.page.goto(config.EXPLORE_URL, wait_until='domcontentloaded')
                return True
        logger.error('登录超时')
        return False

    def get_self_user_id(self):
        """从页面侧边栏"我的"链接中提取自己的 user_id"""
        try:
            href = self.page.locator('a[href*="/user/profile/"]').first.get_attribute('href')
            if href:
                return href.rstrip('/').split('/user/profile/')[-1].split('?')[0]
        except Exception as e:
            logger.warning('提取自身 user_id 失败: %s', e)
        return ''

    # ---------- 签名与请求 ----------
    def _sign(self, uri, data=None):
        """调用页面内官方签名函数生成 X-s / X-t"""
        try:
            sign = self.page.evaluate(
                '([url, data]) => window._webmsxyw(url, data)', [uri, data])
            return {'X-s': sign.get('X-s', ''), 'X-t': str(sign.get('X-t', ''))}
        except Exception as e:
            logger.warning('签名失败，刷新页面重试: %s', e)
            self.page.goto(config.EXPLORE_URL, wait_until='domcontentloaded')
            time.sleep(3)
            sign = self.page.evaluate(
                '([url, data]) => window._webmsxyw(url, data)', [uri, data])
            return {'X-s': sign.get('X-s', ''), 'X-t': str(sign.get('X-t', ''))}

    def api_get(self, uri, params=None):
        """带签名的 GET 请求（使用浏览器上下文共享 Cookie）"""
        query = urlencode(params or {})
        full_uri = f'{uri}?{query}' if query else uri
        headers = self._sign(full_uri)
        resp = self.context.request.get(config.API_BASE + full_uri, headers=headers)
        return self._parse(resp, full_uri)

    def api_post(self, uri, payload=None):
        """带签名的 POST 请求"""
        payload = payload or {}
        headers = self._sign(uri, payload)
        headers['Content-Type'] = 'application/json;charset=UTF-8'
        resp = self.context.request.post(config.API_BASE + uri, headers=headers, data=payload)
        return self._parse(resp, uri)

    @staticmethod
    def _parse(resp, uri):
        try:
            data = resp.json()
        except Exception:
            logger.warning('接口 %s 返回非 JSON (status=%s)', uri, resp.status)
            return {'code': -1, 'message': f'http {resp.status}'}
        if data.get('code') == 300011:
            logger.warning('接口 %s 触发风控(300011): %s', uri, data.get('msg'))
        elif data.get('code') != 0:
            logger.warning('接口 %s 业务失败: code=%s msg=%s',
                           uri, data.get('code'), data.get('msg') or data.get('message'))
        return data
