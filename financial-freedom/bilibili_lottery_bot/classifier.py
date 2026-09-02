# -*- coding: utf-8 -*-
"""
识别过滤层 (Filter / Classifier)
    判断动态是否为抽奖动态 → 提取参与条件
识别依据（优先级从高到低）：
    1. 官方抽奖：新版结构 modules.module_dynamic.additional.type == ADDITIONAL_TYPE_LOTTERY
    2. 文本关键词：正文命中抽奖关键词
"""
import logging
import re

try:
    from . import config
except ImportError:  # 支持在包内直接 python main.py 运行
    import config

logger = logging.getLogger(__name__)


def _has_official_lott(additional):
    """判断是否为 B 站官方抽奖动态（additional 为抽奖组件）"""
    if not isinstance(additional, dict):
        return False
    return additional.get('type') == 'ADDITIONAL_TYPE_LOTTERY' or 'lottery' in additional


def _parse_conditions(text, is_official=False):
    """
    从正文中提取参与条件，返回动作集合
    如 "关注+转发+评论" → {'follow', 'forward', 'comment'}
    """
    conditions = set()
    for action, keywords in config.CONDITION_RULES.items():
        for kw in keywords:
            if kw in text:
                conditions.add(action)
                break
    # 抽奖动态默认至少需要转发；官方抽奖默认要求 关注+转发
    if not conditions:
        conditions.add('forward')
        if is_official:
            conditions.add('follow')
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
    判断单条动态是否为抽奖动态
    :param dynamic: collector 产出的动态记录
    :return: 是抽奖 → 补充 is_lottery/conditions/deadline 字段并返回；否则返回 None
    """
    text = dynamic.get('text', '') or ''

    is_official = _has_official_lott(dynamic.get('additional'))
    hit_keyword = any(re.search(kw, text) for kw in config.LOTTERY_KEYWORDS)

    if not (is_official or hit_keyword):
        return None

    dynamic['is_lottery'] = True
    dynamic['is_official_lott'] = is_official
    dynamic['conditions'] = _parse_conditions(text, is_official)
    dynamic['deadline'] = _parse_deadline(text)
    logger.info('识别到抽奖动态: uid=%s dynamic_id=%s 官方=%s 条件=%s',
                dynamic['uid'], dynamic['dynamic_id'], is_official, dynamic['conditions'])
    return dynamic


class Classifier:
    """批量过滤抽奖动态"""

    def filter(self, dynamics):
        """输入动态列表，输出抽奖动态列表"""
        lotteries = [d for d in dynamics if classify(d)]
        logger.info('本轮识别出抽奖动态 %d 条（共 %d 条）', len(lotteries), len(dynamics))
        return lotteries
