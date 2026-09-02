# -*- coding: utf-8 -*-
"""
识别过滤层 (Filter / Classifier)
    判断笔记是否为抽奖动态 → 提取参与条件
识别依据：标题 + 正文命中抽奖/福利/礼遇类关键词
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
    从文本中提取参与条件，返回动作集合
    如 "关注+点赞+评论" → {'follow', 'like', 'comment'}
    """
    conditions = set()
    for action, keywords in config.CONDITION_RULES.items():
        for kw in keywords:
            if kw in text:
                conditions.add(action)
                break
    # 抽奖动态默认至少需要点赞
    if not conditions:
        conditions.add('like')
    return conditions


def _parse_deadline(text):
    """尝试从文本提取开奖时间（如 2026-09-10 / 9月10日）"""
    m = re.search(r'(\d{4}[-/年]\d{1,2}[-/月]\d{1,2})', text)
    if m:
        return m.group(1)
    m = re.search(r'(\d{1,2})\s*月\s*(\d{1,2})\s*[日号]', text)
    if m:
        return f'{m.group(1)}月{m.group(2)}日'
    return ''


def classify(record):
    """
    判断单条笔记是否为抽奖动态
    :param record: collector 产出的笔记记录
    :return: 是抽奖 → 补充 is_lottery/conditions/deadline 字段并返回；否则返回 None
    """
    text = f"{record.get('title', '')}\n{record.get('desc', '')}"

    hit_keyword = any(re.search(kw, text) for kw in config.LOTTERY_KEYWORDS)
    if not hit_keyword:
        return None

    record['is_lottery'] = True
    record['conditions'] = _parse_conditions(text)
    record['deadline'] = _parse_deadline(text)
    logger.info('识别到抽奖笔记: uid=%s note_id=%s 条件=%s',
                record['user_id'], record['note_id'], record['conditions'])
    return record


class Classifier:
    """批量过滤抽奖笔记"""

    def filter(self, records):
        """输入笔记列表，输出抽奖笔记列表"""
        lotteries = [r for r in records if classify(r)]
        logger.info('本轮识别出抽奖笔记 %d 条（共 %d 条）', len(lotteries), len(records))
        return lotteries
