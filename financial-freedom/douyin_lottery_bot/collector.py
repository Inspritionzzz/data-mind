# -*- coding: utf-8 -*-
"""
数据采集层 (Collector)
抖音 Web API 有 a_bogus 签名防护，无法直接 httpx 调用，
改为：驱动页面 → 拦截页面自身发出的已签名 API 响应
    关注列表：/aweme/v1/web/user/following/list/
    用户作品：/aweme/v1/web/aweme/post/
"""
import logging
import random
import time

try:
    from . import config
except ImportError:  # 支持在包内直接 python main.py 运行
    import config

logger = logging.getLogger(__name__)


def _sleep():
    """页面跳转间随机休眠，降低风控概率"""
    time.sleep(random.uniform(*config.REQUEST_INTERVAL))


class Collector:
    """关注用户与作品数据采集（API 响应拦截方式）"""

    def __init__(self, browser):
        self.browser = browser
        self._captured = []
        self._patterns = []

    def _on_response(self, resp):
        if not self._patterns:
            return
        url = resp.url
        if any(p in url for p in self._patterns):
            try:
                self._captured.append(resp.json())
            except Exception:
                pass

    def _capture(self, patterns, navigate_fn, timeout=15, scroll_times=0):
        """
        注册响应拦截 → 执行页面操作 → 等待并返回捕获的 JSON 列表
        注意：同步 Playwright 中必须用 page.wait_for_timeout 等待，
        time.sleep 会阻塞事件分发导致 response 回调不触发
        :param patterns: 需要拦截的 URL 子串列表
        :param navigate_fn: 页面操作（goto/点击等）
        :param timeout: 等待首批响应的超时(秒)
        :param scroll_times: 捕获后额外滚动次数（触发分页请求）
        """
        self._patterns = patterns
        self._captured = []
        page = self.browser.page
        page.on('response', self._on_response)
        try:
            navigate_fn()
            deadline = time.time() + timeout
            while time.time() < deadline and not self._captured:
                page.wait_for_timeout(500)
            for _ in range(scroll_times):
                page.mouse.wheel(0, 1200)
                page.wait_for_timeout(int(config.SCROLL_PAUSE * 1000))
            # 等待分页响应落地
            page.wait_for_timeout(1500)
            return list(self._captured)
        finally:
            page.remove_listener('response', self._on_response)
            self._patterns = []

    # ---------- 关注列表 ----------
    def get_followings(self):
        """
        打开个人主页"关注"tab，拦截 following/list 响应并滚动加载，
        返回 [{'uid','sec_uid','nickname'}, ...]
        """
        def navigate():
            page = self.browser.page
            page.goto('https://www.douyin.com/user/self?showTab=follow',
                      wait_until='domcontentloaded')
            page.wait_for_timeout(3000)
            # 兜底：URL 参数未自动加载关注列表时，点击"关注"tab
            if not self._captured:
                try:
                    page.locator('span:text-is("关注")').first.click(timeout=3000)
                    page.wait_for_timeout(2000)
                except Exception:
                    pass

        payloads = self._capture(['/aweme/v1/web/user/following/list'],
                                 navigate, timeout=15, scroll_times=4)
        users, seen = [], set()
        for data in payloads:
            for item in (data.get('followings') or []):
                uid = str(item.get('uid', ''))
                if uid and uid not in seen:
                    seen.add(uid)
                    users.append({'uid': uid,
                                  'sec_uid': item.get('sec_uid', ''),
                                  'nickname': item.get('nickname', '')})
        logger.info('关注列表共 %d 人', len(users))
        return users

    # ---------- 用户作品 ----------
    def get_user_videos(self, sec_uid):
        """打开用户主页，拦截 aweme/post 响应，返回最新作品列表"""
        def navigate():
            self.browser.page.goto(
                'https://www.douyin.com/user/' + sec_uid,
                wait_until='domcontentloaded')
            self.browser.page.wait_for_timeout(3000)

        payloads = self._capture(['/aweme/v1/web/aweme/post'], navigate,
                                 timeout=15)
        videos = []
        for data in payloads:
            videos.extend(data.get('aweme_list') or [])
        # 按发布时间倒序，截取最新 N 条
        videos.sort(key=lambda v: v.get('create_time', 0), reverse=True)
        return videos[:config.VIDEOS_PER_USER]

    def probe_latest(self, sec_uid):
        """
        探测用户最新作品：返回 (最新发布时间戳, 作品列表)
        探测请求本身已返回最新作品，供后续直接复用
        """
        videos = self.get_user_videos(sec_uid)
        if not videos:
            return 0, []
        return int(videos[0].get('create_time', 0)), videos

    @staticmethod
    def _extract_text(video):
        """提取作品文案（含 @提及 文本）"""
        parts = [video.get('desc', '') or '']
        for extra in (video.get('text_extra') or []):
            name = extra.get('hashtag_name') or extra.get('mentioned_user', {}) \
                .get('nickname', '')
            if name:
                parts.append('@' + name)
        return '\n'.join(p for p in parts if p)

    # ---------- 汇总采集 ----------
    def build_records(self, users_with_videos):
        """
        将探测阶段缓存的作品转换为统一记录结构
        :param users_with_videos: [{'uid','sec_uid','nickname','videos'}, ...]
        """
        results = []
        for user in users_with_videos:
            for video in user['videos']:
                author = video.get('author') or {}
                results.append({
                    'dynamic_id': str(video.get('aweme_id', '')),
                    'uid': user['uid'],
                    'sec_uid': user['sec_uid'],
                    'uname': user['nickname'] or author.get('nickname', ''),
                    'pub_ts': int(video.get('create_time', 0)),
                    'text': self._extract_text(video),
                    'video': video,
                })
            logger.info('已采集 %s(uid=%s) 作品 %d 条',
                        user['nickname'], user['uid'], len(user['videos']))
        logger.info('本轮共采集作品 %d 条', len(results))
        return results
