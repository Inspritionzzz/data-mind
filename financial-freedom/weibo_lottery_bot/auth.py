# -*- coding: utf-8 -*-
"""
登录层：微博扫码/手动登录 + Cookie 持久化管理
流程：
    1. 优先加载本地 Cookie，校验有效性
    2. 失效则启动 Playwright 持久化浏览器，等待人工登录（扫码或账号密码）
    3. 登录成功后提取 Cookie 保存，供后续各层使用
"""
import json
import logging
import os
import re
import time

import httpx

try:
    from . import config
except ImportError:  # 支持在包内直接 python main.py 运行
    import config

logger = logging.getLogger(__name__)

# 首页 HTML 内嵌当前登录用户 uid（未登录则无）
HOME_URL = 'https://weibo.com/'
# 用户资料接口（带 uid 返回昵称）
PROFILE_URL = 'https://weibo.com/ajax/profile/info'


class WeiboAuth:
    """微博登录态管理"""

    def __init__(self):
        self.cookies = {}
        self.uid = ''
        self.uname = ''

    # ---------- Cookie 存取 ----------
    def save_cookie(self):
        """保存 Cookie 到本地 json"""
        config.ensure_data_dir()
        with open(config.COOKIE_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.cookies, f, ensure_ascii=False, indent=2)
        logger.info('Cookie 已保存至 %s', config.COOKIE_FILE)

    def load_cookie(self):
        """从本地加载 Cookie，不存在返回 False"""
        try:
            with open(config.COOKIE_FILE, 'r', encoding='utf-8') as f:
                self.cookies = json.load(f)
            logger.info('已加载本地 Cookie')
            return bool(self.cookies)
        except (FileNotFoundError, ValueError):
            logger.info('无本地 Cookie 或文件损坏')
            return False

    # ---------- 登录态校验 ----------
    def check_login(self):
        """
        校验 Cookie 是否有效，有效则记录 uid / uname
        方式：首页 HTML 内嵌当前登录用户 uid（未登录则解析不到），
        再用 profile/info 接口取昵称
        """
        if not self.cookies:
            return False
        try:
            resp = httpx.get(HOME_URL, headers=config.HEADERS, cookies=self.cookies,
                             timeout=15, trust_env=False)
            m = re.search(r'"uid"\s*:\s*"?(\d{5,})"?', resp.text)
            if m:
                self.uid = m.group(1)
                # 取昵称（失败不影响登录判定）
                try:
                    info = httpx.get(PROFILE_URL, params={'uid': self.uid},
                                     headers=config.HEADERS, cookies=self.cookies,
                                     timeout=15, trust_env=False).json()
                    self.uname = (info.get('data', {}).get('user', {})
                                  .get('screen_name', ''))
                except Exception:
                    self.uname = ''
                logger.info('登录态有效: %s (uid=%s)', self.uname, self.uid)
                return True
        except Exception as e:
            logger.warning('登录态校验异常: %s', e)
        logger.info('本地 Cookie 已失效')
        return False

    # ---------- Playwright 浏览器登录 ----------
    def browser_login(self, timeout=None):
        """
        启动 Playwright 持久化浏览器，等待人工登录
        登录成功后提取 Cookie 并保存
        """
        timeout = timeout or config.LOGIN_TIMEOUT
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            logger.error('未安装 playwright，请运行: pip install playwright && playwright install chromium')
            return False

        config.ensure_data_dir()
        os.makedirs(config.BROWSER_PROFILE, exist_ok=True)

        with sync_playwright() as pw:
            context = pw.chromium.launch_persistent_context(
                user_data_dir=config.BROWSER_PROFILE,
                headless=False,
                viewport={'width': 1280, 'height': 800},
            )
            page = context.pages[0] if context.pages else context.new_page()
            page.goto(config.LOGIN_URL, wait_until='domcontentloaded')
            logger.info('请在弹出的浏览器中登录微博（%d 秒内）...', timeout)

            deadline = time.time() + timeout
            logged_in = False
            while time.time() < deadline:
                time.sleep(3)
                # 提取浏览器 Cookie，用 httpx 校验登录态
                # （页内 fetch/DOM 选择器在新版前端不可靠，httpx 直连最稳）
                try:
                    cookies = {c['name']: c['value']
                               for c in context.cookies('https://weibo.com')}
                    if not cookies.get('SUB'):
                        continue
                    self.cookies = cookies
                    if self.check_login():
                        logged_in = True
                        break
                except Exception:
                    pass

            if not logged_in:
                logger.error('登录超时')
                context.close()
                return False

            # 提取 Cookie
            all_cookies = context.cookies('https://weibo.com')
            self.cookies = {c['name']: c['value'] for c in all_cookies}
            context.close()

        if not self.cookies:
            logger.error('未能提取到 Cookie')
            return False

        self.save_cookie()
        logger.info('浏览器登录成功，已提取 %d 个 Cookie', len(self.cookies))
        return self.check_login()

    # ---------- 对外入口 ----------
    def login(self):
        """登录主流程：本地 Cookie 优先，失效则浏览器登录"""
        if self.load_cookie() and self.check_login():
            return True
        return self.browser_login()

    @property
    def xsrf_token(self):
        """XSRF-TOKEN 即 csrf token，转发/评论/点赞接口需要"""
        return self.cookies.get('XSRF-TOKEN', '')
