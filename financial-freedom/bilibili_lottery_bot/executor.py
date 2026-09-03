# -*- coding: utf-8 -*-
"""
执行层 (Executor)
    按参与条件执行：关注 / 转发 / 评论 / 点赞
    代理抽奖（工具人专栏）：解析专栏 → 拉取其中列出的抽奖 UP 动态 → 参与目标抽奖
"""
import logging
import random
import re
import time

import httpx

try:
    from . import config
    from .classifier import classify
except ImportError:  # 支持在包内直接 python main.py 运行
    import config
    from classifier import classify

logger = logging.getLogger(__name__)

REPOST_URL = 'https://api.vc.bilibili.com/dynamic_repost/v1/dynamic_repost/repost'
COMMENT_URL = 'https://api.bilibili.com/x/v2/reply/add'
LIKE_URL = 'https://api.vc.bilibili.com/dynamic_like/v1/dynamic_like/thumb'
FOLLOW_URL = 'https://api.bilibili.com/x/relation/modify'
ARTICLE_URL = 'https://api.bilibili.com/x/article/view'

# 专栏中"【UP名】、【uid】"格式的抽奖条目
ARTICLE_UID_RE = re.compile(r'【([^【】]{1,40})】、【(\d{5,20})】')


class Executor:
    """执行参与动作并返回结果"""

    def __init__(self, auth, collector=None, notifier=None):
        self.auth = auth
        # 拉取目标 UP 动态（代理抽奖需要）
        self.collector = collector
        # 子抽奖查重（代理抽奖需要）
        self.notifier = notifier
        # 跨专栏的 UP 去重（工具人一天发多篇专栏，列出的 UP 高度重复）
        self._proxy_seen_ups = set()
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

    # ---------- 代理抽奖（工具人专栏） ----------
    def _fetch_article_content(self, article_id):
        """获取专栏正文内容"""
        resp = self.client.get(ARTICLE_URL, params={'id': article_id}).json()
        if resp.get('code') != 0:
            logger.warning('获取专栏 cv%s 失败: %s', article_id, resp.get('message'))
            return ''
        return (resp.get('data') or {}).get('content') or ''

    def _extract_target_ups(self, content):
        """
        从专栏正文提取抽奖 UP 列表（"【UP名】、【uid】"格式），
        按出现顺序去重（置顶抽奖在前）
        """
        ups, seen = [], set()
        for name, uid in ARTICLE_UID_RE.findall(content):
            if uid not in seen:
                seen.add(uid)
                ups.append({'name': name, 'uid': uid})
        return ups

    def _participate_proxy(self, lottery):
        """
        代理抽奖：解析专栏 → 提取抽奖 UP → 拉其动态 → 参与目标抽奖动态
        对目标动态执行 转发 + 点赞，并关注目标 UP
        :return: {'actions': {...}, 'success': bool, 'sub_lotteries': [(lot, res), ...]}
        """
        article = lottery['article']
        content = self._fetch_article_content(article['id'])
        if not content:
            return {'actions': {}, 'success': False, 'sub_lotteries': []}
        ups = self._extract_target_ups(content)[:config.PROXY_MAX_TARGETS]
        logger.info('专栏 cv%s 提取到抽奖 UP %d 个（截取前 %d 个处理）',
                    article['id'], len(self._extract_target_ups(content)),
                    len(ups))

        sub_lotteries = []
        all_ok = True
        for up in ups:
            # 跨专栏 UP 去重：本轮已处理过的 UP 不再拉取
            if up['uid'] in self._proxy_seen_ups:
                continue
            self._proxy_seen_ups.add(up['uid'])
            if not self.collector:
                logger.warning('未注入 collector，无法拉取目标 UP 动态，终止代理参与')
                break
            # 拉取目标 UP 的动态，识别其中的抽奖动态（官方优先）
            items = self.collector.get_friend_dynamics(up['uid'])
            target = None
            for item in items:
                rec = {
                    'dynamic_id': item.get('id_str'),
                    'uid': up['uid'],
                    'uname': up['name'],
                    'text': self.collector._extract_text(item),
                    'additional': (((item.get('modules') or {})
                                    .get('module_dynamic')) or {}).get('additional'),
                    'item': item,
                }
                c = classify(rec)
                if c and not c.get('is_proxy'):
                    target = c
                    break
            if not target:
                logger.info('UP %s(uid=%s) 近期无抽奖动态，跳过',
                            up['name'], up['uid'])
                continue
            # 子抽奖查重：已成功参与过则跳过
            if self.notifier and self.notifier.is_participated(target['dynamic_id']):
                logger.info('目标动态 %s 已参与过，跳过', target['dynamic_id'])
                continue

            # 对目标动态执行 转发 + 点赞 + 关注 UP
            actions = {}
            actions['forward'] = self.forward(target['dynamic_id'])
            self._sleep()
            actions['like'] = self.like(target['dynamic_id'])
            self._sleep()
            actions['follow'] = self.follow(up['uid'])
            self._sleep()
            success = all(actions.values())
            if not success:
                all_ok = False
            result = {'actions': actions, 'success': success}
            sub_lotteries.append((target, result))
            logger.info('代理子抽奖完成: UP=%s 目标动态=%s 结果=%s',
                        up['name'], target['dynamic_id'], actions)
            # 拉取下一个 UP 前的防风控间隔
            time.sleep(random.uniform(*config.REQUEST_INTERVAL))

        return {'actions': {}, 'success': all_ok and bool(sub_lotteries),
                'sub_lotteries': sub_lotteries}

    # ---------- 按条件执行 ----------
    def participate(self, lottery):
        """
        按参与条件执行动作
        :return: {'forward': bool, 'comment': bool, ...} 各动作结果
        """
        # 代理抽奖：动态本身不是抽奖，走专栏解析逻辑
        if lottery.get('is_proxy'):
            return self._participate_proxy(lottery)

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
