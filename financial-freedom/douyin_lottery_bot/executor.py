# -*- coding: utf-8 -*-
"""
执行层 (Executor)
抖音 API 有签名防护，执行动作采用 DOM 点击方式：
    打开作品页 → 点赞 / 收藏 / 评论 / 关注
"""
import logging
import random
import time

try:
    from . import config
except ImportError:  # 支持在包内直接 python main.py 运行
    import config

logger = logging.getLogger(__name__)


class Executor:
    """执行参与动作并返回结果（DOM 点击）"""

    def __init__(self, browser):
        self.browser = browser

    def _sleep(self):
        time.sleep(random.uniform(*config.ACTION_INTERVAL))

    # ---------- 单个动作 ----------
    def like(self):
        """点赞当前作品（双击画面或点击点赞按钮）"""
        page = self.browser.page
        try:
            # 优先点击侧栏点赞按钮（未选中状态）
            btn = page.locator('[data-e2e="video-player-digg"]').first
            if btn.count():
                btn.click(timeout=5000)
            else:
                page.mouse.dblclick(640, 400)
            logger.info('点赞 -> 成功')
            return True
        except Exception as e:
            logger.warning('点赞失败: %s', e)
            return False

    def collect(self):
        """收藏当前作品"""
        page = self.browser.page
        try:
            btn = page.locator('[data-e2e="video-player-collect"]').first
            if btn.count():
                btn.click(timeout=5000)
                logger.info('收藏 -> 成功')
                return True
            logger.warning('未找到收藏按钮')
            return False
        except Exception as e:
            logger.warning('收藏失败: %s', e)
            return False

    def comment(self, content=None):
        """评论当前作品"""
        page = self.browser.page
        content = content or random.choice(config.COMMENT_TEXTS)
        try:
            # 点击评论图标展开评论区
            page.locator('[data-e2e="video-player-comment"]').first.click(timeout=5000)
            time.sleep(1.5)
            # 定位评论输入框并输入
            box = page.locator('[data-e2e="comment-input"] [contenteditable="true"], '
                               '.comment-input [contenteditable="true"]').first
            box.click(timeout=5000)
            page.keyboard.type(content, delay=50)
            time.sleep(0.5)
            # 发送（回车或点击发布）
            page.keyboard.press('Enter')
            logger.info('评论 -> 成功: %s', content)
            return True
        except Exception as e:
            logger.warning('评论失败: %s', e)
            return False

    def follow(self):
        """关注当前作品作者（主页/作品页的关注按钮）"""
        page = self.browser.page
        try:
            for sel in ['[data-e2e="follow-button"]',
                        'button:has-text("关注")', 'span:has-text("关注")']:
                btn = page.locator(sel).first
                if btn.count() and btn.is_visible():
                    btn.click(timeout=5000)
                    logger.info('关注 -> 成功')
                    return True
            logger.info('未找到关注按钮（可能已关注）')
            return True  # 已关注视为成功
        except Exception as e:
            logger.warning('关注失败: %s', e)
            return False

    # ---------- 按条件执行 ----------
    def participate(self, lottery):
        """
        打开作品页后按参与条件执行动作
        :return: {'like': bool, ...} 各动作结果
        """
        dynamic_id = lottery['dynamic_id']
        conditions = lottery.get('conditions', {'comment', 'like'})
        results = {}
        try:
            self.browser.page.goto(
                'https://www.douyin.com/video/' + dynamic_id,
                wait_until='domcontentloaded')
            time.sleep(3)
        except Exception as e:
            logger.error('打开作品页失败 id=%s: %s', dynamic_id, e)
            return {'actions': results, 'success': False}

        # 关注通常最先做
        if 'follow' in conditions:
            results['follow'] = self.follow()
            self._sleep()
        if 'like' in conditions:
            results['like'] = self.like()
            self._sleep()
        if 'collect' in conditions:
            results['collect'] = self.collect()
            self._sleep()
        if 'comment' in conditions:
            results['comment'] = self.comment()
            self._sleep()
        if 'forward' in conditions:
            # 抖音转发需分享面板，暂以评论代替并在日志说明
            logger.info('抖音转发暂不支持 DOM 自动化，跳过 forward 条件')

        success = all(results.values()) if results else False
        logger.info('参与 id=%s 完成，结果=%s', dynamic_id, results)
        return {'actions': results, 'success': success}
