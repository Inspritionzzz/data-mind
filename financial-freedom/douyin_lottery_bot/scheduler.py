# -*- coding: utf-8 -*-
"""
定时调度层 (Scheduler)
    每日定时触发（如 09:00），串联 采集 → 识别 → 执行 → 记录通知 全流程
"""
import logging
import random
import time
from datetime import datetime, timedelta

try:
    from . import config
    from .browser import DouyinBrowser
    from .classifier import Classifier
    from .collector import Collector
    from .executor import Executor
    from .notifier import Notifier
except ImportError:  # 支持在包内直接 python main.py 运行
    import config
    from browser import DouyinBrowser
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

    browser = DouyinBrowser()
    browser.start()
    try:
        # 登录层
        if not browser.login():
            logger.error('登录失败，本轮任务终止')
            return 0

        collector = Collector(browser)
        executor = Executor(browser)
        classifier = Classifier()
        notifier = Notifier()
        summary = []
        try:
            # 采集层：全量关注列表 → 探测新动态 → 仅采集有新动态用户的最新10条
            followings = collector.get_followings()
            if not followings:
                logger.error('关注列表为空，本轮任务终止')
                return 0
            cutoff = time.time() - config.NEW_DYNAMIC_DAYS * 86400
            active_users = []
            for i, user in enumerate(followings):
                # 浏览器存活检测：窗口被关闭则立即终止，避免空转
                if not browser.is_alive():
                    logger.error('浏览器已关闭（窗口可能被手动关闭），本轮任务终止')
                    return 0
                logger.info('探测 %d/%d: %s(uid=%s)',
                            i + 1, len(followings), user['nickname'], user['uid'])
                try:
                    latest_ts, videos = collector.probe_latest(user['sec_uid'])
                except Exception as e:
                    if not browser.is_alive():
                        logger.error('浏览器已关闭，本轮任务终止')
                        return 0
                    logger.warning('探测 %s 失败: %s', user['uid'], e)
                    continue
                if latest_ts >= cutoff and videos:
                    user['videos'] = videos
                    active_users.append(user)
                time.sleep(random.uniform(*config.REQUEST_INTERVAL))
            logger.info('关注 %d 人中 %d 人近 %d 天有新动态',
                        len(followings), len(active_users), config.NEW_DYNAMIC_DAYS)
            dynamics = collector.build_records(active_users)

            # 识别过滤层
            lotteries = classifier.filter(dynamics)

            # 执行层 + 记录层
            joined = 0
            for lottery in lotteries:
                if joined >= config.MAX_ACTIONS_PER_RUN:
                    logger.warning('已达单次运行上限 %d，剩余跳过', config.MAX_ACTIONS_PER_RUN)
                    break
                if notifier.is_participated(lottery['dynamic_id']):
                    logger.info('作品 %s 已参与过，跳过', lottery['dynamic_id'])
                    continue
                result = executor.participate(lottery)
                notifier.record(lottery, result)
                summary.append((lottery, result))
                joined += 1

            # 通知层
            notifier.notify(summary)
            logger.info('本轮任务结束，参与 %d 个抽奖', len(summary))
            return len(summary)
        finally:
            notifier.close()
    finally:
        browser.close()


def _seconds_until(target_hhmm):
    """计算距离目标时刻(如 09:00)的秒数，已过则顺延到明天"""
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
