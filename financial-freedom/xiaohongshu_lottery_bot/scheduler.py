# -*- coding: utf-8 -*-
"""
定时调度层 (Scheduler)
    通过指令触发任务，串联 采集 → 识别 → 执行 → 记录通知 全流程
"""
import logging
import os
import random
import time

try:
    from . import config
    from .browser import XhsBrowser
    from .collector import Collector, RiskControlError
    from .classifier import Classifier
    from .executor import Executor
    from .notifier import Notifier
except ImportError:  # 支持在包内直接 python main.py 运行
    import config
    from browser import XhsBrowser
    from collector import Collector, RiskControlError
    from classifier import Classifier
    from executor import Executor
    from notifier import Notifier

logger = logging.getLogger(__name__)


def run_once():
    """执行一轮完整任务，返回参与抽奖数"""
    logger.info('=' * 50)
    logger.info('开始本轮抽奖任务 %s', time.strftime('%Y-%m-%d %H:%M:%S'))

    browser = XhsBrowser()
    summary = []
    try:
        browser.start()
        if not browser.login():
            logger.error('登录失败，本轮任务终止')
            return 0

        collector = Collector(browser)
        executor = Executor(browser)
        classifier = Classifier()
        notifier = Notifier()
        try:
            # 采集层：全量关注列表 → 探测新动态 → 仅采集有新动态用户的最新笔记
            self_uid = browser.get_self_user_id()
            if not self_uid:
                logger.error('无法获取自身 user_id，本轮任务终止')
                return 0
            followings = collector.get_followings(self_uid)
            cutoff = (time.time() - config.NEW_DYNAMIC_DAYS * 86400) * 1000

            # 轮换批次探测：单轮最多 MAX_PROBE_PER_RUN 人，从上次结束位置继续
            offset_file = config.PROBE_START_OFFSET_FILE
            offset = 0
            if os.path.exists(offset_file):
                try:
                    with open(offset_file, encoding='utf-8') as f:
                        offset = int(f.read().strip() or 0)
                except (ValueError, OSError):
                    offset = 0
            offset = offset % len(followings) if followings else 0
            batch = (followings[offset:] + followings[:offset])[:config.MAX_PROBE_PER_RUN]

            active_users = []
            for i, user in enumerate(batch):
                logger.info('探测 %d/%d: %s(uid=%s)',
                            i + 1, len(batch), user['nickname'], user['user_id'])
                try:
                    latest_ts, notes = collector.probe_latest(user['user_id'])
                except RiskControlError:
                    raise
                except Exception as e:
                    logger.warning('探测 %s 失败: %s', user['user_id'], e)
                    continue
                if latest_ts >= cutoff and notes:
                    user['notes'] = notes
                    active_users.append(user)
                time.sleep(random.uniform(*config.REQUEST_INTERVAL))
            # 记录下一轮起点
            next_offset = (offset + len(batch)) % max(len(followings), 1)
            with open(offset_file, 'w', encoding='utf-8') as f:
                f.write(str(next_offset))
            logger.info('关注 %d 人中本轮探测 %d 人、%d 人近 %d 天有新动态（下轮从第 %d 人继续）',
                        len(followings), len(batch), len(active_users),
                        config.NEW_DYNAMIC_DAYS, next_offset)
            records = collector.build_records(active_users)

            # 识别过滤层
            lotteries = classifier.filter(records)

            # 执行层 + 记录层
            participated = 0
            for lottery in lotteries:
                if participated >= config.MAX_ACTIONS_PER_RUN:
                    logger.info('已达单次运行参与上限 %d，停止', config.MAX_ACTIONS_PER_RUN)
                    break
                if notifier.is_participated(lottery['note_id']):
                    logger.info('笔记 %s 已参与过，跳过', lottery['note_id'])
                    continue
                actions = executor.execute(lottery)
                success = all(actions.values()) if actions else False
                exec_result = {'actions': actions, 'success': success}
                notifier.record(lottery, exec_result)
                summary.append((lottery, exec_result))
                participated += 1
                logger.info('参与笔记 %s 完成，结果=%s', lottery['note_id'], actions)

            # 通知层
            notifier.notify(summary)
            logger.info('本轮任务结束，参与 %d 个抽奖', participated)
            return participated
        finally:
            notifier.close()
    except RiskControlError as e:
        logger.error('触发风控，本轮终止: %s', e)
        return 0
    except Exception as e:
        logger.exception('本轮任务异常: %s', e)
        return 0
    finally:
        browser.close()
