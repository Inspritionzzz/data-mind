# -*- coding: utf-8 -*-
"""
记录与通知层 (Logger & Notifier)
    写入日志 / SQLite 数据库 → 推送汇总通知（邮件）
"""
import logging
import smtplib
import sqlite3
from datetime import datetime
from email.header import Header
from email.mime.text import MIMEText

try:
    from . import config
except ImportError:  # 支持在包内直接 python main.py 运行
    import config

logger = logging.getLogger(__name__)

CREATE_TABLE_SQL = """
create table if not exists lottery_record (
    id integer primary key autoincrement,
    dynamic_id text not null unique,
    uid text,
    uname text,
    is_official_lott integer,
    conditions text,
    deadline text,
    actions text,
    success integer,
    created_at text
)
"""


class Notifier:
    """记录参与结果并推送通知"""

    def __init__(self):
        config.ensure_data_dir()
        self.conn = sqlite3.connect(config.DB_FILE)
        self.conn.execute(CREATE_TABLE_SQL)
        self.conn.commit()

    def close(self):
        self.conn.close()

    # ---------- 数据库记录 ----------
    def is_participated(self, dynamic_id):
        """判断该动态是否已成功参与过（去重）；失败的记录允许下轮重试"""
        cur = self.conn.execute(
            'select 1 from lottery_record where dynamic_id = ? and success = 1',
            (str(dynamic_id),))
        return cur.fetchone() is not None

    def record(self, lottery, exec_result):
        """写入一条参与记录"""
        try:
            self.conn.execute(
                'insert or replace into lottery_record '
                '(dynamic_id, uid, uname, is_official_lott, conditions, deadline, '
                ' actions, success, created_at) values (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (str(lottery['dynamic_id']), str(lottery['uid']), lottery['uname'],
                 int(lottery.get('is_official_lott', False)),
                 ','.join(sorted(lottery.get('conditions', []))),
                 lottery.get('deadline', ''),
                 str(exec_result['actions']),
                 int(exec_result['success']),
                 datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            self.conn.commit()
        except sqlite3.Error as e:
            logger.error('写入数据库失败: %s', e)

    # ---------- 汇总通知 ----------
    def notify(self, summary_records):
        """
        推送本轮汇总通知
        :param summary_records: [(lottery, exec_result), ...]
        """
        if not summary_records:
            logger.info('本轮无新参与的抽奖，跳过通知')
            return
        lines = [f'本轮共参与 {len(summary_records)} 个抽奖：', '']
        for lottery, result in summary_records:
            status = '成功' if result['success'] else '部分失败'
            lines.append(
                f"- [{status}] {lottery['uname']}(uid={lottery['uid']}) "
                f"作品 {lottery['dynamic_id']} 条件:{','.join(sorted(lottery.get('conditions', [])))} "
                f"开奖:{lottery.get('deadline') or '未知'}")
        content = '\n'.join(lines)
        logger.info('汇总通知:\n%s', content)
        self._send_mail('抖音抽奖机器人运行报告', content)

    def _send_mail(self, subject, content):
        """邮件推送（未配置则跳过）"""
        if not (config.MAIL_FROM and config.MAIL_AUTH_CODE and config.MAIL_TO):
            logger.info('未配置邮件通知，跳过邮件推送')
            return
        msg = MIMEText(content, 'plain', 'utf-8')
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = config.MAIL_FROM
        msg['To'] = ','.join(config.MAIL_TO)
        try:
            server = smtplib.SMTP_SSL(config.SMTP_HOST, config.SMTP_PORT)
            server.login(config.MAIL_FROM, config.MAIL_AUTH_CODE)
            server.sendmail(config.MAIL_FROM, config.MAIL_TO, msg.as_string())
            server.quit()
            logger.info('汇总邮件发送成功')
        except Exception as e:
            logger.error('邮件发送失败: %s', e)


def setup_logging():
    """配置日志：同时输出到控制台和文件"""
    config.ensure_data_dir()
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.LOG_FILE, encoding='utf-8'),
            logging.StreamHandler(),
        ])
