# -*- coding: utf-8 -*-
"""
数据采集层 (Collector)
    获取好友(互相关注)列表 → 遍历好友动态
使用新版动态接口: /x/polymer/web-dynamic/v1/feed/space
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

# 互相关注(好友)列表
FRIENDS_URL = 'https://api.bilibili.com/x/relation/followings'
# 用户动态（新版接口）
SPACE_FEED_URL = 'https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/space'


def _sleep():
    """请求间随机休眠，降低风控概率"""
    time.sleep(random.uniform(*config.REQUEST_INTERVAL))


class Collector:
    """好友与动态数据采集"""

    def __init__(self, auth):
        self.auth = auth
        # trust_env=False: B站为国内站点，不走系统代理，避免代理工具未开时连接被拒
        self.client = httpx.Client(headers=config.HEADERS, cookies=auth.cookies,
                                   timeout=20, trust_env=False)

    def close(self):
        self.client.close()

    # ---------- 好友列表 ----------
    def get_friends(self):
        """
        获取全部关注列表（分页拉取直到取完），
        返回 [{'mid':..., 'uname':..., 'following': bool}, ...]
        """
        friends, page = [], 1
        while True:
            resp = self.client.get(FRIENDS_URL, params={
                'vmid': self.auth.uid, 'pn': page, 'ps': config.FRIEND_PAGE_SIZE,
                'order_type': 'attention'}).json()
            if resp.get('code') != 0:
                logger.warning('获取好友列表失败: %s', resp.get('message'))
                break
            data = resp['data']
            batch = data.get('list') or []
            for item in batch:
                friends.append({'mid': item['mid'], 'uname': item['uname'],
                                'following': True})
            # 接口无 total_page 字段，按 total 与每页数量判断是否取完
            if len(friends) >= data.get('total', 0) or not batch:
                break
            page += 1
            _sleep()
        logger.info('关注列表共 %d 人', len(friends))
        return friends

    # ---------- 好友动态 ----------
    def get_friend_dynamics(self, mid):
        """拉取某好友最近的动态列表（新版结构 items），风控(-352)时冷却重试一次"""
        resp = self.client.get(SPACE_FEED_URL, params={'host_mid': mid}).json()
        if resp.get('code') == -352:
            logger.warning('触发风控(-352)，冷却 %d 秒后重试 uid=%s',
                           int(config.RISK_COOLDOWN[0]), mid)
            time.sleep(random.uniform(*config.RISK_COOLDOWN))
            resp = self.client.get(SPACE_FEED_URL, params={'host_mid': mid}).json()
        if resp.get('code') != 0:
            logger.warning('获取 uid=%s 动态失败: %s', mid, resp.get('code'))
            return []
        items = (resp.get('data') or {}).get('items') or []
        return items[:config.FEEDS_PER_FRIEND]

    def probe_latest(self, mid):
        """
        轻量探测：返回 (最新动态时间戳, 动态items列表)
        探测请求本身已返回最新 10 条动态，供后续直接复用，无需二次请求
        """
        items = self.get_friend_dynamics(mid)
        if not items:
            return 0, []
        ma = (items[0].get('modules') or {}).get('module_author') or {}
        try:
            latest_ts = int(ma.get('pub_ts') or 0)
        except (TypeError, ValueError):
            latest_ts = 0
        return latest_ts, items

    @staticmethod
    def _extract_text(item):
        """从新版动态结构中提取正文文本（文字/图文/视频/专栏）"""
        md = (item.get('modules') or {}).get('module_dynamic') or {}
        parts = []
        desc = md.get('desc') or {}
        if desc.get('text'):
            parts.append(desc['text'])
        major = md.get('major') or {}
        opus = major.get('opus') or {}
        if (opus.get('summary') or {}).get('text'):
            parts.append(opus['summary']['text'])
        if (major.get('archive') or {}).get('desc'):
            parts.append(major['archive']['desc'])
        if (major.get('article') or {}).get('title'):
            parts.append(major['article']['title'])
        return '\n'.join(parts)

    # ---------- 汇总采集 ----------
    def build_records(self, friends_with_items):
        """
        将探测阶段缓存的动态 items 转换为统一记录结构，不再发起新请求
        :param friends_with_items: [{'mid','uname','following','items'}, ...]
        :return: 动态记录列表，每条包含 dynamic_id / uid / uname / following /
                 pub_ts / text / additional(官方抽奖组件) / item(原始结构)
        """
        results = []
        for friend in friends_with_items:
            for item in friend['items']:
                md = (item.get('modules') or {}).get('module_dynamic') or {}
                ma = (item.get('modules') or {}).get('module_author') or {}
                # 转发动态的原作者（抽奖发起人往往是原作者）
                orig_ma = ((item.get('orig') or {}).get('modules') or {}).get('module_author') or {}
                orig_author = ({'mid': orig_ma.get('mid'), 'name': orig_ma.get('name')}
                               if orig_ma.get('mid') else None)
                try:
                    pub_ts = int(ma.get('pub_ts') or 0)
                except (TypeError, ValueError):
                    pub_ts = 0
                results.append({
                    'dynamic_id': item.get('id_str'),
                    'uid': friend['mid'],
                    'uname': friend['uname'],
                    'following': friend.get('following', True),
                    'pub_ts': pub_ts,
                    'orig_author': orig_author,
                    'text': self._extract_text(item),
                    'additional': md.get('additional'),
                    'item': item,
                })
            logger.info('已采集 %s(uid=%s) 动态 %d 条',
                        friend['uname'], friend['mid'], len(friend['items']))
        logger.info('本轮共采集动态 %d 条', len(results))
        return results
