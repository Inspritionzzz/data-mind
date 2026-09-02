# -*- coding: utf-8 -*-
"""
执行层 (Executor)
    按抽奖动态的参与条件执行：关注 / 转发 / 评论 / 点赞
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

REPOST_URL = 'https://api.vc.bilibili.com/dynamic_repost/v1/dynamic_repost/repost'
COMMENT_URL = 'https://api.bilibili.com/x/v2/reply/add'
LIKE_URL = 'https://api.vc.bilibili.com/dynamic_like/v1/dynamic_like/thumb'
FOLLOW_URL = 'https://api.bilibili.com/x/relation/modify'


class Executor:
    """执行参与动作并返回结果"""

    def __init__(self, auth):
        self.auth = auth
        # trust_env=False: B站为国内站点，不走系统代理，避免代理工具未开时连接被拒
        self.client = httpx.Client(headers=config.HEADERS, cookies=auth.cookies,
                                   timeout=20, trust_env=False)

    def close(self):
        self.client.close()

    def _sleep(self):
        time.sleep(random.uniform(*config.ACTION_INTERVAL))

    # ---------- 单个动作 ----------
    def follow(self, fid):
        """关注 UP 主（已关注视为成功）"""
        resp = self.client.post(FOLLOW_URL, data={
            'fid': fid, 'act': 1, 're_src': 11, 'jsonp': 'jsonp',
            'csrf': self.auth.csrf}).json()
        ok = resp.get('code') == 0 or '已关注' in (resp.get('message') or '')
        logger.info('关注 uid=%s -> %s', fid, '成功' if ok else resp.get('message'))
        return ok

    def forward(self, dynamic_id, content=None):
        """转发动态"""
        content = content or random.choice(config.REPOST_TEXTS)
        resp = self.client.post(REPOST_URL, data={
            'uid': self.auth.uid, 'dynamic_id': dynamic_id, 'content': content,
            'csrf': self.auth.csrf, 'csrf_token': self.auth.csrf}).json()
        ok = resp.get('code') == 0
        logger.info('转发 dynamic_id=%s -> %s', dynamic_id, '成功' if ok else resp.get('message'))
        return ok

    def comment(self, dynamic_id, content=None):
        """评论动态（动态的评论区 type=11，oid=动态id）"""
        content = content or random.choice(config.COMMENT_TEXTS)
        resp = self.client.post(COMMENT_URL, data={
            'oid': dynamic_id, 'type': 11, 'message': content,
            'csrf': self.auth.csrf}).json()
        ok = resp.get('code') == 0
        logger.info('评论 dynamic_id=%s -> %s', dynamic_id, '成功' if ok else resp.get('message'))
        return ok

    def like(self, dynamic_id):
        """点赞动态"""
        resp = self.client.post(LIKE_URL, data={
            'uid': self.auth.uid, 'dynamic_id': dynamic_id, 'up': 1,
            'csrf': self.auth.csrf}).json()
        ok = resp.get('code') == 0
        logger.info('点赞 dynamic_id=%s -> %s', dynamic_id, '成功' if ok else resp.get('message'))
        return ok

    # ---------- 按条件执行 ----------
    def participate(self, lottery):
        """
        按参与条件执行动作
        :return: {'forward': bool, 'comment': bool, ...} 各动作结果
        """
        dynamic_id = lottery['dynamic_id']
        conditions = lottery.get('conditions', {'forward'})
        results = {}

        # 关注通常要最先做（部分抽奖要求先关注）
        # 关注目标优先抽奖发起人（转发动态的原作者），其次动态发布者
        if 'follow' in conditions:
            target = lottery.get('orig_author') or {
                'mid': lottery['uid'], 'name': lottery['uname']}
            results['follow'] = self.follow(target['mid'])
            self._sleep()
        if 'forward' in conditions:
            results['forward'] = self.forward(dynamic_id)
            self._sleep()
        if 'comment' in conditions:
            results['comment'] = self.comment(dynamic_id)
            self._sleep()
        if 'like' in conditions:
            results['like'] = self.like(dynamic_id)
            self._sleep()

        success = all(results.values()) if results else False
        logger.info('参与 dynamic_id=%s 完成，结果=%s', dynamic_id, results)
        return {'actions': results, 'success': success}
