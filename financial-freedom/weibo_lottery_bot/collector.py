# -*- coding: utf-8 -*-
"""
数据采集层 (Collector)
    获取关注列表 → 遍历好友动态 → 拉取动态详情
使用微博 Web Ajax 接口
"""
import logging
import random
import time

import httpx

try:
    from . import config
except ImportError:  # 支持在包内直接 python main.py 运行
    import config

logger = logging.getLogger(__name__)

# 关注列表
FRIENDS_URL = 'https://weibo.com/ajax/friendships/friends'
# 用户微博列表
USER_STATUSES_URL = 'https://weibo.com/ajax/statuses/mymblog'


def _sleep():
    """请求间随机休眠，降低风控概率"""
    time.sleep(random.uniform(*config.REQUEST_INTERVAL))


class Collector:
    """关注与动态数据采集"""

    def __init__(self, auth):
        self.auth = auth
        # trust_env=False: 微博为国内站点，不走系统代理
        self.client = httpx.Client(
            headers={**config.HEADERS, 'XSRF-TOKEN': auth.xsrf_token},
            cookies=auth.cookies, timeout=20, trust_env=False)

    def close(self):
        self.client.close()

    # ---------- 关注列表 ----------
    def get_friends(self):
        """
        获取全部关注列表（分页拉取直到取完），
        返回 [{'uid':..., 'screen_name':...}, ...]
        """
        friends, page = [], 1
        while True:
            try:
                resp = self.client.get(FRIENDS_URL, params={
                    'page': page, 'count': config.FRIEND_PAGE_SIZE}).json()
            except Exception as e:
                logger.warning('获取关注列表异常: %s', e)
                break
            users = resp.get('users') or []
            if not users:
                break
            for item in users:
                friends.append({
                    'uid': str(item.get('id', '')),
                    'screen_name': item.get('screen_name', ''),
                })
            total = resp.get('total_number', 0)
            if len(friends) >= total or not users:
                break
            page += 1
            _sleep()
        logger.info('关注列表共 %d 人', len(friends))
        return friends

    # ---------- 好友动态 ----------
    def get_friend_statuses(self, uid):
        """拉取某好友最近的微博列表，风控时冷却重试一次"""
        try:
            resp = self.client.get(USER_STATUSES_URL, params={
                'uid': uid, 'page': 1, 'feature': 0}).json()
        except Exception as e:
            logger.warning('获取 uid=%s 动态异常: %s', uid, e)
            return []
        # 微博风控返回 ok 字段或 error
        if resp.get('ok') != 1 and resp.get('error'):
            logger.warning('获取 uid=%s 动态失败: %s', uid, resp.get('error'))
            return []
        data = resp.get('data') or {}
        statuses = data.get('list') or []
        return statuses[:config.FEEDS_PER_FRIEND]

    def probe_latest(self, uid):
        """
        轻量探测：返回 (最新动态时间戳, 动态列表)
        探测请求本身已返回最新动态，供后续直接复用
        """
        statuses = self.get_friend_statuses(uid)
        if not statuses:
            return 0, []
        # 微博时间格式: "created_at": "Thu Sep 03 14:30:00 +0800 2026"
        try:
            from datetime import datetime
            created = statuses[0].get('created_at', '')
            # 解析微博时间
            dt = datetime.strptime(created, '%a %b %d %H:%M:%S %z %Y')
            latest_ts = int(dt.timestamp())
        except (ValueError, TypeError, IndexError):
            latest_ts = 0
        return latest_ts, statuses

    @staticmethod
    def _extract_text(status):
        """从微博结构中提取正文文本"""
        parts = []
        # 主文本
        text = status.get('text_raw') or status.get('text') or ''
        if text:
            parts.append(text)
        # 长文本
        long_text = status.get('long_text') or {}
        if long_text.get('long_text_content'):
            parts.append(long_text['long_text_content'])
        # 转发的原微博文本
        retweeted = status.get('retweeted_status') or {}
        if retweeted:
            rt_text = retweeted.get('text_raw') or retweeted.get('text') or ''
            if rt_text:
                parts.append('[转发] ' + rt_text)
        return '\n'.join(parts)

    # ---------- 汇总采集 ----------
    def build_records(self, friends_with_items):
        """
        将探测阶段缓存的动态转换为统一记录结构
        :param friends_with_items: [{'uid','screen_name','statuses'}, ...]
        :return: 动态记录列表
        """
        results = []
        for friend in friends_with_items:
            for status in friend['statuses']:
                # 转发微博的原作者
                retweeted = status.get('retweeted_status') or {}
                orig_author = None
                if retweeted:
                    orig_user = retweeted.get('user') or {}
                    orig_author = {
                        'uid': str(orig_user.get('id', '')),
                        'name': orig_user.get('screen_name', ''),
                    } if orig_user.get('id') else None

                # 解析时间
                try:
                    from datetime import datetime
                    created = status.get('created_at', '')
                    dt = datetime.strptime(created, '%a %b %d %H:%M:%S %z %Y')
                    pub_ts = int(dt.timestamp())
                except (ValueError, TypeError):
                    pub_ts = 0

                results.append({
                    'dynamic_id': str(status.get('id', '')),
                    'mid': status.get('mid', ''),
                    'uid': friend['uid'],
                    'uname': friend['screen_name'],
                    'pub_ts': pub_ts,
                    'orig_author': orig_author,
                    'text': self._extract_text(status),
                    'status': status,
                })
            logger.info('已采集 %s(uid=%s) 动态 %d 条',
                        friend['screen_name'], friend['uid'], len(friend['statuses']))
        logger.info('本轮共采集动态 %d 条', len(results))
        return results
