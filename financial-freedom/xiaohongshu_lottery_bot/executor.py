# -*- coding: utf-8 -*-
"""
执行层 (Executor)
    按参与条件执行动作：关注 / 点赞 / 收藏 / 评论
"""
import logging
import random
import time

try:
    from . import config
except ImportError:  # 支持在包内直接 python main.py 运行
    import config

logger = logging.getLogger(__name__)

LIKE_URL = '/api/sns/web/v1/note/like'
COLLECT_URL = '/api/sns/web/v1/note/collect'
COMMENT_URL = '/api/sns/web/v2/comment/post'
FOLLOW_URL = '/api/sns/web/v1/user/follow'


class Executor:
    """执行抽奖参与动作"""

    def __init__(self, browser):
        self.browser = browser

    def _sleep(self):
        time.sleep(random.uniform(*config.ACTION_INTERVAL))

    # ---------- 原子动作 ----------
    def like(self, note_id, xsec_token=''):
        """点赞笔记"""
        resp = self.browser.api_post(LIKE_URL, {
            'note_id': note_id, 'xsec_token': xsec_token})
        ok = resp.get('code') == 0
        logger.info('点赞 %s -> %s', note_id, '成功' if ok else resp.get('msg'))
        return ok

    def collect(self, note_id, xsec_token=''):
        """收藏笔记"""
        resp = self.browser.api_post(COLLECT_URL, {
            'note_id': note_id, 'xsec_token': xsec_token})
        ok = resp.get('code') == 0
        logger.info('收藏 %s -> %s', note_id, '成功' if ok else resp.get('msg'))
        return ok

    def comment(self, note_id, xsec_token='', content=None):
        """评论笔记"""
        resp = self.browser.api_post(COMMENT_URL, {
            'note_id': note_id,
            'content': content or config.COMMENT_TEXT,
            'xsec_token': xsec_token})
        ok = resp.get('code') == 0
        logger.info('评论 %s -> %s', note_id, '成功' if ok else resp.get('msg'))
        return ok

    def follow(self, target_user_id):
        """关注用户"""
        resp = self.browser.api_post(FOLLOW_URL, {'target_user_id': target_user_id})
        ok = resp.get('code') == 0
        logger.info('关注 %s -> %s', target_user_id, '成功' if ok else resp.get('msg'))
        return ok

    # ---------- 组合执行 ----------
    def execute(self, lottery):
        """
        按参与条件执行动作
        :return: {'like': bool, 'comment': bool, ...} 各动作结果
        """
        note_id = lottery['note_id']
        xsec_token = (lottery.get('note') or {}).get('xsec_token', '')
        conditions = lottery.get('conditions', {'like'})
        results = {}

        # 关注通常要最先做（部分抽奖要求先关注）
        if 'follow' in conditions:
            results['follow'] = self.follow(lottery['user_id'])
            self._sleep()
        if 'like' in conditions:
            results['like'] = self.like(note_id, xsec_token)
            self._sleep()
        if 'collect' in conditions:
            results['collect'] = self.collect(note_id, xsec_token)
            self._sleep()
        if 'comment' in conditions:
            results['comment'] = self.comment(note_id, xsec_token)
            self._sleep()
        return results
