from tqdm import tqdm
import requests

import os
import logging

from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.header import Header
from email.utils import parseaddr, formataddr
import smtplib

'''
    1、获取更新动态
    2、提取中奖信息动态
    3、发送邮件
'''

logger = logging.getLogger(__name__)

def get_all_items():

    url = 'https://t.bilibili.com/?spm_id_from=444.41.0.0'

    pass

def send_simple_email():

    sender = 'jason-office-pc'
    receivers = ['591831416@qq.com']

    # 三个参数：第一个为文本内容，第二个 plain 设置文本格式，第三个 utf-8 设置编码
    message = MIMEText('Python 邮件发送测试...', 'plain', 'utf-8')
    message['From'] = Header("", 'utf-8')  # 发送者
    message['To'] = Header("测试", 'utf-8')  # 接收者

    subject = 'Python SMTP 邮件测试'
    message['Subject'] = Header(subject, 'utf-8')

    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect('smtp.qq.com,465')
        # smtpObj.login('1019919111@qq.com', 'zcy100037')

        smtpObj.login('1019919111@qq.com', 'oonlejzexpeibfef')  # 登录smtp服务器

        smtpObj.sendmail(sender, receivers, message.as_string())
        print("邮件发送成功")
    except smtplib.SMTPException:
        print("Error: 无法发送邮件")

    pass


def send_email():
    #设置服务器，用户名、口令以及邮箱的后缀
    mail_from = "1011919111@qq.com"
    mail_pass = "oonlejzexpeibfef"  # 邮件授权码，非登录密码
    mail_to = "591831416@qq.com"
    mail_server = "smtp.qq.com"  # smtp服务器

    # me = mail_user+"<"+mail_user+"@"+mail_postfix+">"
    msg = MIMEText('hello，send by python_test...' + 'content', 'plain', 'utf-8')  # 发送纯文本格式的文件

    msg = MIMEText('by python', 'plain', 'utf-8')  # 发送纯文本格式的文件
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
        print("邮件发送成功")
    except Exception as err:
        print('邮件发送失败...')
    pass



if __name__ == '__main__':

    send_email()
    # send_simple_email()
    pass