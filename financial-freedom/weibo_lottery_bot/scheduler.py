# -*- coding: utf-8 -*-
"""
定时调度层 (Scheduler)
    每日定时触发（如 09:00），串联 采集 → 识别 → 执行 → 记录通知 全流程
"""
import logging
import random
import time
from datetime import datetime

try:
    from . import config
    from .auth import WeiboAuth
    from .classifier import Classifier
    from .collector import Collector
    from .executor import Executor
    from .notifier import Notifier
except ImportError:  # 支持在包内直接 python main.py 运行
    import config
    from auth import WeiboAuth
    from classifier import Classifier
    from collector import Collector
    from executor import Executor
    from notifier import Notifier

logger = logging.getLogger(__name__)


def run_once():
    """
    执行一轮完整流程：采集 → 过滤 → 执行 → 记录通知
    :return: 本轮参与成功的抽奖数
    """
    logger.info('=' * 50)
    logger.info('开始本轮抽奖任务 %s', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    # 登录层
    auth = WeiboAuth()
    if not auth.login():
        logger.error('登录失败，本轮任务终止')
        return 0

    collector = Collector(auth)
    executor = Executor(auth)
    classifier = Classifier()
    notifier = Notifier()
    summary = []
    try:
        # 采集层：全量关注列表 → 探测新动态 → 仅采集有新动态用户的最新10条
        friends = collector.get_friends()
        cutoff = time.time() - config.NEW_DYNAMIC_DAYS * 86400
        active_friends = []
        for friend in friends:
            latest_ts, statuses = collector.probe_latest(friend['uid'])
            if latest_ts >= cutoff and statuses:
                friend['statuses'] = statuses
                active_friends.append(friend)
            time.sleep(random.uniform(*config.PROBE_INTERVAL))
        logger.info('关注 %d 人中 %d 人近 %d 天有新动态',
                    len(friends), len(active_friends), config.NEW_DYNAMIC_DAYS)
        dynamics = collector.build_records(active_friends)
        # 识别过滤层
        lotteries = classifier.filter(dynamics)

        # 执行层 + 记录层
        joined = 0
        for lottery in lotteries:
            if joined >= config.MAX_ACTIONS_PER_RUN:
                logger.warning('已达单次运行上限 %d，剩余跳过', config.MAX_ACTIONS_PER_RUN)
                break
            if notifier.is_participated(lottery['dynamic_id']):
                logger.info('微博 %s 已参与过，跳过', lottery['dynamic_id'])
                continue
            result = executor.participate(lottery)
            notifier.record(lottery, result)
            summary.append((lottery, result))
            joined += 1

        # 通知层
        notifier.notify(summary)
        logger.info('本轮任务结束，参与 %d 个抽奖', len(summary))
        return len(summary)
    except Exception as e:
        logger.exception('本轮任务异常: %s', e)
        return 0
    finally:
        collector.close()
        executor.close()
        notifier.close()


def _seconds_until(target_hhmm):
    """计算距离目标时刻(如 09:00)的秒数，已过则顺延到明天"""
    from datetime import timedelta
    now = datetime.now()
    hour, minute = map(int, target_hhmm.split(':'))
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)
    return (target - now).total_seconds()


def schedule_loop():
    """常驻调度：每天在 DAILY_RUN_TIME 触发一轮任务"""
    logger.info('调度器启动，每日 %s 执行', config.DAILY_RUN_TIME)
    while True:
        wait = _seconds_until(config.DAILY_RUN_TIME)
        logger.info('下次运行在 %.0f 秒后（%s）', wait, config.DAILY_RUN_TIME)
        time.sleep(wait)
        run_once()
        # 防止同一分钟内重复触发
        time.sleep(config.CHECK_INTERVAL_SECONDS * 2)
