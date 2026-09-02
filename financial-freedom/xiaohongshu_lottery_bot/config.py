# -*- coding: utf-8 -*-
"""
小红书抽奖机器人 - 全局配置
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
# Playwright 持久化浏览器目录（保存登录态，扫码一次即可）
BROWSER_PROFILE = os.path.join(DATA_DIR, 'browser_profile')
COOKIE_FILE = os.path.join(DATA_DIR, 'cookie.json')
DB_FILE = os.path.join(DATA_DIR, 'xhs_lottery.db')
LOG_FILE = os.path.join(DATA_DIR, 'bot.log')

EXPLORE_URL = 'https://www.xiaohongshu.com/explore'
API_BASE = 'https://edith.xiaohongshu.com'

# ---------- 浏览器 ----------
HEADLESS = False                # 首次登录需扫码，建议 False；稳定后可改 True
LOGIN_TIMEOUT = 300             # 等待扫码登录的超时(秒)

# ---------- 采集层 ----------
FOLLOW_PAGE_SIZE = 20           # 关注列表每页数量
NOTES_PER_USER = 10             # 每个用户最多拉取的笔记条数
# 探测间隔(秒)：小红书风控严格，逐用户探测必须保持足够间隔
REQUEST_INTERVAL = (10, 20)
NEW_DYNAMIC_DAYS = 7            # 新动态判定窗口(天)
RISK_COOLDOWN = (60, 120)       # 触发风控后的冷却休眠范围(秒)
MAX_PROBE_PER_RUN = 50         # 单轮最多探测的用户数(分多轮覆盖全部关注)
PROBE_START_OFFSET_FILE = 'data/probe_offset.txt'  # 轮换起点记录

# ---------- 识别过滤层 ----------
# 抽奖/福利类关键词（支持正则）
LOTTERY_KEYWORDS = [
    # 抽奖类
    '抽奖', '转发抽奖', '互动抽奖', '抽送', '送出', '奖品', '抽取', '开奖', '中奖',
    # 福利/回馈/礼遇类
    '福利', '粉丝回馈', '回馈粉丝', '回馈', '宠粉', '粉丝福利', '发福利', '送福利',
    '礼遇', '粉丝礼遇', '惊喜',
    # 抽奖账号/话题
    '我们爱抽奖', '@我们爱抽奖',
    # 赠送类
    '送周边', '免费送', '赠送', '送礼物', '送会员', '送红包', '白嫖', '0元',
    # 人数抽取类（正则）
    r'抽\d+[人位名]', r'抽[一二三四五六七八九十]+[人位名]',
]
# 参与条件关键词 → 动作映射（小红书动作：点赞/收藏/评论/关注）
CONDITION_RULES = {
    'like': ['点赞', '点个赞', '双击'],
    'collect': ['收藏', '收藏职位'],
    'comment': ['评论', '留言', '扣1', '评论区'],
    'follow': ['关注', '关注我', '关注本'],
}

# ---------- 执行层 ----------
MAX_ACTIONS_PER_RUN = 30        # 单次运行最多参与的抽奖数
ACTION_INTERVAL = (3, 8)        # 动作间隔(秒)
COMMENT_TEXT = '来啦，期待中奖！'  # 默认评论内容

# ---------- 通知层 ----------
MAIL_FROM = ''                  # 发件邮箱
MAIL_AUTH_CODE = ''             # 邮箱授权码
MAIL_TO = []                    # 收件人列表
SMTP_HOST = 'smtp.qq.com'
SMTP_PORT = 465


def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)
