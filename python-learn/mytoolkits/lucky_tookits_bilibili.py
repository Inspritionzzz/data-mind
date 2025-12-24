"""
    bili自动参与抽奖工具
"""
import datetime
import logging
import os
from wxpy import *
import lib
from email.mime.text import MIMEText
import psycopg2


def postgre_conn():
    logging.basicConfig(level=logging.DEBUG,
                        filename='lucky_tookits_bilibili_output.log',
                        datefmt='%Y-%m-%d %H:%M:S',
                        format='%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(module)s - %(message)s')
    logger.info('开始连接数据库...')

    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="100037",
        database='postgres'
    )
    cur = conn.cursor()
    sql = "SELECT * FROM ums_admin WHERE id = '1'"
    cur.execute(sql)
    result = cur.fetchall()  # 打印结果

    conn.commit()  # 查询时无需,此方法提交当前事务.如果不调用这个方法,无论做了什么修改,自从上次调用#commit()是不可见的
    conn.close()  # 关闭链接
    return result;

def send_mail(content):
    #设置服务器，用户名、口令以及邮箱的后缀
    mail_from = "1011919111@qq.com"
    mail_pass = "buqgqocsbnpobbje"  # 邮件授权码，非登录密码
    mail_to = "591831416@qq.com"
    mail_server = "smtp.qq.com"  # smtp服务器

    # me = mail_user+"<"+mail_user+"@"+mail_postfix+">"
    msg = MIMEText('hello，send by python_test...' + content, 'plain', 'utf-8')  # 发送纯文本格式的文件

    msg['Subject'] = mail_from  # 发送邮件地址
    msg['From'] = ';'.join(mail_to)   # 接受邮件地址
    msg['To'] = 'just a python test'  # 主题
    try:
        s = smtplib.SMTP(mail_server, 25)
        # s.connect(mail_host)
        s.login(mail_from, mail_pass)  # 登录smtp服务器
        s.set_debuglevel(1)  # 打印和smtp服务器的所有信息
        s.sendmail(mail_from, mail_to, msg.as_string())  # param: 发送者,接收者,发送内容
        s.close()
        return True
    except Exception as err:
        print('邮件发送失败...')
        return False
    pass
"""
获取b站up主动态
"""
def collect_lucky_draw_info():

    pass

"""
微信消息推送
"""
def wechat_message():
    pass

if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG,
                        filename='lucky_tookits_bilibili_output.log',
                        datefmt='%Y-%m-%d %H:%M:S',
                        format='%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(module)s - %(message)s')
    logger = logging.getLogger(__name__)
    email_content = 'just a test'
    send_mail(email_content)
    # logger.info('This is a log info')
    # logger.debug('Debugging')
    # logger.warning('Warning exists')
    # logger.info('Finish')
    # logging.error('error')

    logger.info('抽奖程序启动成功...')

    # result = postgre_conn()
    # print(result)
    # logger.info('连接postgre数据库成功')
