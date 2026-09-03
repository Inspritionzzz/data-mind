# -*- coding: utf-8 -*-
"""
识别过滤层 (Filter / Classifier)
    判断作品是否为抽奖动态 → 提取参与条件
抖音无官方抽奖组件接口暴露，按正文关键词识别
"""
import logging
import re

try:
    from . import config
except ImportError:  # 支持在包内直接 python main.py 运行
    import config

logger = logging.getLogger(__name__)


def _parse_conditions(text):
    """
    从正文中提取参与条件，返回动作集合
    如 "关注+评论+点赞" → {'follow', 'comment', 'like'}
    """
    conditions = set()
    for action, keywords in config.CONDITION_RULES.items():
        for kw in keywords:
            if kw in text:
                conditions.add(action)
                break
    # 抖音抽奖默认至少需要 评论+点赞（常见参与方式）
    if not conditions:
        conditions.add('comment')
        conditions.add('like')
    return conditions


def _parse_deadline(text):
    """尝试从正文提取开奖时间（如 2026-09-10 / 9月10日）"""
    m = re.search(r'(\d{4}[-/年]\d{1,2}[-/月]\d{1,2})', text)
    if m:
        return m.group(1)
    m = re.search(r'(\d{1,2})\s*月\s*(\d{1,2})\s*[日号]', text)
    if m:
        return f'{m.group(1)}月{m.group(2)}日'
    return ''


def classify(dynamic):
    """
    判断单条作品是否为抽奖动态
    :return: 是抽奖 → 补充 is_lottery/conditions/deadline 字段并返回；否则返回 None
    """
    text = dynamic.get('text', '') or ''
    if not any(re.search(kw, text) for kw in config.LOTTERY_KEYWORDS):
        return None

    dynamic['is_lottery'] = True
    dynamic['is_official_lott'] = False
    dynamic['conditions'] = _parse_conditions(text)
    dynamic['deadline'] = _parse_deadline(text)
    logger.info('识别到抽奖动态: uid=%s dynamic_id=%s 条件=%s',
                dynamic['uid'], dynamic['dynamic_id'], dynamic['conditions'])
    return dynamic


class Classifier:
    """批量过滤抽奖动态"""

    def filter(self, dynamics):
        """输入动态列表，输出抽奖动态列表"""
        lotteries = [d for d in dynamics if classify(d)]
        logger.info('本轮识别出抽奖动态 %d 条（共 %d 条）', len(lotteries), len(dynamics))
        return lotteries
