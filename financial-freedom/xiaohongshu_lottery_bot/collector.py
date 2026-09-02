# -*- coding: utf-8 -*-
"""
数据采集层 (Collector)
    获取关注列表所有用户 → 探测新动态 → 拉取最新笔记
关注列表双通道：优先 API，失败回退个人主页"关注"tab DOM 解析
"""
import logging
import random
import re
import time

try:
    from . import config
except ImportError:  # 支持在包内直接 python main.py 运行
    import config

logger = logging.getLogger(__name__)

# 关注列表（IM 命名空间，page/size 分页，一次可取 200）
FOLLOWINGS_URL = '/api/im/web/users/following/all'
# 用户笔记列表
USER_NOTES_URL = '/api/sns/web/v1/user_posted'


class RiskControlError(Exception):
    """账号被风控（如 300011 安全限制），应立即停止本轮任务"""


def _sleep(interval=None):
    """请求间随机休眠，降低风控概率"""
    time.sleep(random.uniform(*(interval or config.REQUEST_INTERVAL)))


class Collector:
    """关注用户与笔记数据采集"""

    # 连续收到 N 次 300011 即判定为账号风控，熔断终止
    RISK_STREAK_LIMIT = 3

    def __init__(self, browser):
        self.browser = browser
        self._risk_streak = 0

    def _check_risk(self, data):
        """
        风控处理：单次 300011 冷却后重试一次；连续多次则熔断
        :return: True 表示本次为风控失败（调用方可考虑重试）
        """
        if data.get('code') == 300011:
            self._risk_streak += 1
            if self._risk_streak >= self.RISK_STREAK_LIMIT:
                raise RiskControlError(
                    f'连续 {self._risk_streak} 次触发风控(300011)，终止本轮任务，'
                    '请等待数小时或更换账号')
            # 单次风控：冷却后允许调用方重试
            cooldown = random.uniform(*config.RISK_COOLDOWN)
            logger.warning('触发风控(300011)，冷却 %.0f 秒后重试', cooldown)
            time.sleep(cooldown)
            return True
        if data.get('code') == 0:
            self._risk_streak = 0
        return False

    # ---------- 关注列表 ----------
    def get_followings(self, self_uid):
        """获取全部关注用户：API 优先，失败回退 DOM 解析"""
        users = self._get_followings_api(self_uid)
        if not users:
            logger.info('API 获取关注列表失败，回退 DOM 解析')
            users = self._get_followings_dom(self_uid)
        logger.info('关注列表共 %d 人', len(users))
        return users

    def _get_followings_api(self, self_uid):
        """分页拉取全部关注用户（API 通道）"""
        users, page = [], 1
        while True:
            data = self.browser.api_get(FOLLOWINGS_URL,
                                        {'page': page, 'size': 200})
            if data.get('code') != 0:
                return []
            batch = ((data.get('data') or {}).get('follow_user_d_t_o_list')
                     or [])
            for item in batch:
                users.append({'user_id': item.get('user_id'),
                              'nickname': item.get('nick_name', '')})
            if not batch:  # 空页说明取完
                break
            page += 1
            _sleep()
        return users

    def _get_followings_dom(self, self_uid):
        """
        个人主页"关注"tab DOM 解析通道：
        打开主页 → 点击关注 tab → 滚动加载 → 提取用户链接
        """
        page = self.browser.page
        page.goto(f'https://www.xiaohongshu.com/user/profile/{self_uid}',
                  wait_until='domcontentloaded')
        time.sleep(5)
        body = page.evaluate('() => document.body.innerText.slice(0, 300)')
        if '安全限制' in body or '账号异常' in body:
            raise RiskControlError('账号被风控(300011)，请等待数小时后重试')

        # 点击"关注"数字区（.user-interactions 内含"关注"文本的 div）
        clicked = self.browser.page.evaluate('''() => {
            const divs = document.querySelectorAll('.user-interactions div');
            for (const d of divs) {
                const shows = d.querySelector('span.shows');
                if (shows && shows.textContent.trim() === '关注') {
                    d.click();
                    return true;
                }
            }
            return false;
        }''')
        if not clicked:
            logger.warning('未找到关注 tab')
            return []
        time.sleep(3)

        # 滚动加载并提取用户链接
        users, seen = [], set()
        no_new_rounds = 0
        while no_new_rounds < 3:
            links = page.evaluate('''() =>
                Array.from(document.querySelectorAll('a[href*="/user/profile/"]'))
                .map(a => ({href: a.getAttribute('href'), name: (a.innerText || '').trim()}))
                .filter(x => x.name)''')
            new_count = 0
            for link in links:
                m = re.search(r'/user/profile/([0-9a-f]+)', link['href'])
                if not m or m.group(1) == self_uid or m.group(1) in seen:
                    continue
                seen.add(m.group(1))
                users.append({'user_id': m.group(1), 'nickname': link['name']})
                new_count += 1
            if new_count == 0:
                no_new_rounds += 1
            else:
                no_new_rounds = 0
            page.mouse.wheel(0, 1500)
            time.sleep(random.uniform(1.5, 3))
        return users

    # ---------- 用户笔记 ----------
    def get_user_notes(self, user_id):
        """拉取某用户最新笔记列表（最多 NOTES_PER_USER 条），风控时冷却重试一次"""
        for attempt in range(2):
            data = self.browser.api_get(USER_NOTES_URL, {
                'num': config.NOTES_PER_USER, 'cursor': '', 'user_id': user_id,
                'image_formats': 'jpg,webp,avif'})
            if not self._check_risk(data):
                break
            if attempt == 1:  # 重试仍风控
                return []
        notes = (data.get('data') or {}).get('notes') or []
        return notes[:config.NOTES_PER_USER]

    def probe_latest(self, user_id):
        """
        轻量探测：返回 (最新笔记时间戳毫秒, 笔记列表)
        探测请求本身已返回最新笔记，供后续直接复用，无需二次请求
        """
        notes = self.get_user_notes(user_id)
        if not notes:
            return 0, []
        try:
            latest_ts = int(notes[0].get('time', 0) or 0)
        except (TypeError, ValueError):
            latest_ts = 0
        return latest_ts, notes

    # ---------- 汇总采集 ----------
    def build_records(self, users_with_notes):
        """
        将探测阶段缓存的笔记转换为统一记录结构，不再发起新请求
        :param users_with_notes: [{'user_id','nickname','notes'}, ...]
        :return: 笔记记录列表
        """
        results = []
        for user in users_with_notes:
            for note in user['notes']:
                results.append({
                    'note_id': note.get('note_id'),
                    'user_id': user['user_id'],
                    'nickname': user['nickname'],
                    'title': note.get('display_title', ''),
                    'desc': note.get('desc', ''),
                    'time': note.get('time', 0),
                    'note': note,
                })
            logger.info('已采集 %s(uid=%s) 笔记 %d 条',
                        user['nickname'], user['user_id'], len(user['notes']))
        logger.info('本轮共采集笔记 %d 条', len(results))
        return results
