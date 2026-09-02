# -*- coding: utf-8 -*-
"""
登录层：B站扫码登录 + Cookie 持久化管理
流程：
    1. 优先加载本地 Cookie，校验有效性
    2. 失效则生成二维码，终端打印 + 图片预览，轮询扫码状态
    3. 登录成功后保存 Cookie 供后续各层使用
"""
import json
import logging
import os
import time

import httpx

try:
    from . import config
except ImportError:  # 支持在包内直接 python main.py 运行
    import config

logger = logging.getLogger(__name__)

QR_GENERATE_URL = 'https://passport.bilibili.com/x/passport-login/web/qrcode/generate'
QR_POLL_URL = 'https://passport.bilibili.com/x/passport-login/web/qrcode/poll'
NAV_URL = 'https://api.bilibili.com/x/web-interface/nav'
# 设备指纹接口：buvid3/buvid4 缺失易触发 -352/-412 风控
FINGER_SPI_URL = 'https://api.bilibili.com/x/frontend/finger/spi'


class BiliAuth:
    """B站登录态管理"""

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
        """校验 Cookie 是否有效，有效则记录 uid / uname"""
        if not self.cookies:
            return False
        try:
            resp = httpx.get(NAV_URL, headers=config.HEADERS, cookies=self.cookies,
                             timeout=15, trust_env=False)
            data = resp.json()
            if data.get('code') == 0 and data['data'].get('isLogin'):
                self.uid = str(data['data']['mid'])
                self.uname = data['data']['uname']
                logger.info('登录态有效: %s (uid=%s)', self.uname, self.uid)
                return True
        except Exception as e:
            logger.warning('登录态校验异常: %s', e)
        logger.info('本地 Cookie 已失效')
        return False

    # ---------- 扫码登录 ----------
    def qrcode_login(self, timeout=180):
        """扫码登录：生成二维码 → 终端打印 → 轮询扫码结果"""
        resp = httpx.get(QR_GENERATE_URL, headers=config.HEADERS, timeout=15, trust_env=False)
        qr_data = resp.json()['data']
        qr_url, qrcode_key = qr_data['url'], qr_data['qrcode_key']
        logger.info('二维码已生成，请用 B 站 App 扫码（%d 秒内有效）', timeout)
        self._print_qrcode(qr_url)

        deadline = time.time() + timeout
        with httpx.Client(headers=config.HEADERS, timeout=15, trust_env=False) as client:
            while time.time() < deadline:
                time.sleep(2)
                poll = client.get(QR_POLL_URL, params={
                    'qrcode_key': qrcode_key, 'source': 'main-fe-header'}).json()
                code = poll['data']['code']
                if code == 0:
                    # 登录成功，从响应头/跨域链接中提取 Cookie
                    self.cookies = dict(client.cookies)
                    self._merge_cross_domain_cookie(poll['data'].get('url', ''))
                    self.save_cookie()
                    logger.info('扫码登录成功')
                    self._ensure_buvid()
                    return self.check_login()
                if code == 86038:
                    logger.error('二维码已过期，请重新运行登录')
                    return False
                # 86101 未扫码 / 86090 已扫码待确认，继续轮询
        logger.error('扫码超时')
        return False

    def _merge_cross_domain_cookie(self, cross_url):
        """从跨域登录链接中解析 DedeUserID/SESSDATA/bili_jct 并入 Cookie"""
        from urllib.parse import urlparse, parse_qs
        try:
            query = parse_qs(urlparse(cross_url).query)
            for key in ('DedeUserID', 'DedeUserID__ckMd5', 'SESSDATA', 'bili_jct'):
                if key in query:
                    self.cookies[key] = query[key][0]
        except Exception as e:
            logger.warning('解析跨域 Cookie 失败: %s', e)

    @staticmethod
    def _print_qrcode(url):
        """终端打印二维码（黑白块字符），并保存图片/弹出预览"""
        try:
            import qrcode
            qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_L,
                               box_size=1, border=1)
            qr.add_data(url)
            qr.make(fit=True)
            # 终端字符画：适配深色终端（暗模块=空格露出深色底，亮模块=亮色块）
            for row in qr.modules:
                print(''.join('  ' if cell else '██' for cell in row))
            # 保存 PNG 并尝试用系统图片查看器打开，方便手机扫码
            try:
                config.ensure_data_dir()
                qr_path = os.path.join(config.DATA_DIR, 'qrcode.png')
                qr.make_image(fill_color='black').save(qr_path)
                print('二维码图片已保存:', qr_path)
                os.startfile(qr_path)
            except Exception:
                pass
        except ImportError:
            logger.warning('未安装 qrcode 库，请手动访问链接扫码: %s', url)
            print('扫码链接:', url)

    # ---------- 对外入口 ----------
    def login(self):
        """登录主流程：本地 Cookie 优先，失效则扫码；登录后补齐设备指纹"""
        if self.load_cookie() and self.check_login():
            self._ensure_buvid()
            return True
        return self.qrcode_login()

    def _ensure_buvid(self):
        """补齐 buvid3/buvid4 设备指纹，降低风控概率"""
        if self.cookies.get('buvid3') and self.cookies.get('buvid4'):
            return
        try:
            resp = httpx.get(FINGER_SPI_URL, headers=config.HEADERS,
                             timeout=15, trust_env=False).json()
            data = resp.get('data') or {}
            if data.get('b_3'):
                self.cookies['buvid3'] = data['b_3']
            if data.get('b_4'):
                self.cookies['buvid4'] = data['b_4']
            self.save_cookie()
            logger.info('已补齐 buvid 设备指纹')
        except Exception as e:
            logger.warning('获取 buvid 失败: %s', e)

    @property
    def csrf(self):
        """bili_jct 即 csrf token，转发/评论/点赞接口需要"""
        return self.cookies.get('bili_jct', '')
