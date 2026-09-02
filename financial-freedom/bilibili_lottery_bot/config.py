# -*- coding: utf-8 -*-
"""
全局配置：路径、调度时间、行为参数、邮件通知
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

# ---------- 文件路径 ----------
COOKIE_FILE = os.path.join(DATA_DIR, 'cookie.json')      # 登录态持久化
DB_FILE = os.path.join(DATA_DIR, 'lottery.db')            # 参与记录数据库
LOG_FILE = os.path.join(DATA_DIR, 'bot.log')              # 运行日志

# ---------- 调度层 ----------
DAILY_RUN_TIME = '09:00'        # 每日定时触发时间 (HH:MM)
CHECK_INTERVAL_SECONDS = 30     # 调度轮询间隔

# ---------- 采集层 ----------
FRIEND_PAGE_SIZE = 50           # 好友列表每页数量
FEEDS_PER_FRIEND = 10           # 每个好友最多拉取的动态条数
REQUEST_INTERVAL = (1.5, 3.5)   # 请求随机间隔范围(秒)，避免风控
NEW_DYNAMIC_DAYS = 7            # 新动态判定窗口(天)：最新一条动态在此时间内视为有新动态
PROBE_INTERVAL = (1.5, 3.0)     # 探测用户最新动态时的请求间隔(秒)
RISK_COOLDOWN = (30, 60)        # 触发风控(-352)后的冷却休眠范围(秒)

# ---------- 识别过滤层 ----------
# 官方抽奖动态在 extension 字段中带 lott 信息；文本类则按关键词识别
LOTTERY_KEYWORDS = [
    # 抽奖类
    '抽奖', '转发抽奖', '互动抽奖', '抽送', '送出', '奖品', '抽取', '开奖', '中奖',
    # 福利/回馈类
    '福利', '粉丝回馈', '回馈粉丝', '回馈', '宠粉', '粉丝福利', '发福利', '送福利',
    # 赠送类
    '送周边', '免费送', '赠送', '送礼物', '送会员', '送红包',
    # 人数抽取类（正则）
    r'抽\d+[人位名]', r'抽[一二三四五六七八九十]+[人位名]',
]
# 参与条件关键词 → 动作映射
CONDITION_RULES = {
    'forward': ['转发', '转发本条', '转发这条'],
    'follow': ['关注', '关注我', '关注本'],
    'comment': ['评论', '留言'],
    'like': ['点赞', '赞我'],
}

# ---------- 执行层 ----------
REPOST_TEXTS = ['拉低中奖率', '分母+1', '求中奖！', '转发动态', '冲冲冲，让我中一次']
COMMENT_TEXTS = ['拉低中奖率', '分母来了', '求中奖！', '来了来了']
MAX_ACTIONS_PER_RUN = 30        # 单次运行最多参与的抽奖数，防止操作过频
ACTION_INTERVAL = (3, 8)        # 每个动作之间的随机间隔(秒)

# ---------- 通知层 ----------
# 邮件通知（留空则跳过邮件推送，仅写日志和数据库）
SMTP_HOST = 'smtp.qq.com'
SMTP_PORT = 465                          # SSL 端口
MAIL_FROM = ''                           # 发件人邮箱，如 '1011919111@qq.com'
MAIL_AUTH_CODE = ''                      # 邮箱授权码（非登录密码）
MAIL_TO = []                             # 收件人列表，如 ['591831416@qq.com']

HEADERS = {
    'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                   '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'),
    'Referer': 'https://www.bilibili.com/',
}


def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)
