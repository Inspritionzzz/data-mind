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

# 微博 Web Ajax 接口
REPOST_URL = 'https://weibo.com/ajax/statuses/repost'
COMMENT_URL = 'https://weibo.com/ajax/statuses/comment'
LIKE_URL = 'https://weibo.com/ajax/statuses/like'
FOLLOW_URL = 'https://weibo.com/ajax/friendships/create'


class Executor:
    """执行参与动作并返回结果"""

    def __init__(self, auth):
        self.auth = auth
        # trust_env=False: 微博为国内站点，不走系统代理
        # X-XSRF-TOKEN 为微博 ajax POST 接口的 csrf 校验头（值等于 Cookie 的 XSRF-TOKEN）
        self.client = httpx.Client(
            headers={**config.HEADERS, 'X-XSRF-TOKEN': auth.xsrf_token},
            cookies=auth.cookies, timeout=20, trust_env=False)

    def close(self):
        self.client.close()

    def _sleep(self):
        time.sleep(random.uniform(*config.ACTION_INTERVAL))

    def _post(self, url, payload):
        """统一 POST 请求，返回 (ok, message)"""
        try:
            resp = self.client.post(url, json=payload).json()
        except Exception as e:
            return False, str(e)
        # 微博接口成功通常返回 ok=1 或无 error
        if resp.get('ok') == 1 or resp.get('data'):
            return True, '成功'
        err = resp.get('error') or resp.get('msg') or str(resp)
        return False, err

    # ---------- 单个动作 ----------
    def follow(self, uid):
        """关注用户（已关注视为成功）"""
        ok, msg = self._post(FOLLOW_URL, {'uid': uid})
        if not ok and '已关注' in msg:
            ok = True
        logger.info('关注 uid=%s -> %s', uid, '成功' if ok else msg)
        return ok

    def forward(self, dynamic_id, content=None):
        """转发微博"""
        content = content or random.choice(config.REPOST_TEXTS)
        ok, msg = self._post(REPOST_URL, {
            'id': dynamic_id, 'content': content, 'visible': 0})
        logger.info('转发 id=%s -> %s', dynamic_id, '成功' if ok else msg)
        return ok

    def comment(self, dynamic_id, content=None):
        """评论微博"""
        content = content or random.choice(config.COMMENT_TEXTS)
        ok, msg = self._post(COMMENT_URL, {
            'id': dynamic_id, 'content': content})
        logger.info('评论 id=%s -> %s', dynamic_id, '成功' if ok else msg)
        return ok

    def like(self, dynamic_id):
        """点赞微博"""
        ok, msg = self._post(LIKE_URL, {'id': dynamic_id})
        logger.info('点赞 id=%s -> %s', dynamic_id, '成功' if ok else msg)
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
        # 关注目标优先抽奖发起人（转发微博的原作者），其次动态发布者
        if 'follow' in conditions:
            target = lottery.get('orig_author') or {
                'uid': lottery['uid'], 'name': lottery['uname']}
            results['follow'] = self.follow(target['uid'])
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
        logger.info('参与 id=%s 完成，结果=%s', dynamic_id, results)
        return {'actions': results, 'success': success}
