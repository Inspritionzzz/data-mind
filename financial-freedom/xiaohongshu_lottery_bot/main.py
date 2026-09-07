# -*- coding: utf-8 -*-
"""
小红书抽奖机器人入口
用法：
    python main.py --login    # 仅登录（首次扫码保存登录态）
    python main.py --once     # 立即执行一轮任务
    python main.py --status    # 查看当前登录账号
    python main.py --logout    # 退出登录（清理登录态）
    python main.py --switch    # 切换账号（退出当前 → 扫码登录新账号）
"""
import argparse
import sys
import time

from notifier import setup_logging
from browser import XhsBrowser
from scheduler import run_once


def run_status(browser):
    """查看当前登录账号"""
    browser.start()
    try:
        browser.page.goto('https://www.xiaohongshu.com/explore',
                         wait_until='domcontentloaded')
        time.sleep(3)  # 等签名函数就绪
        info = browser.get_user_info()
        if info:
            print(f'当前登录账号: {info["nickname"]} (user_id={info["user_id"]})')
        else:
            print('当前为游客态（未登录）')
        return 0
    finally:
        browser.close()


def run_logout(browser):
    """退出登录"""
    browser.start()
    try:
        ok = browser.logout()
        print('已退出登录' if ok else '退出失败，详见日志')
        return 0 if ok else 1
    finally:
        browser.close()


def run_switch(browser):
    """切换账号：退出当前 → 扫码登录新账号"""
    browser.start()
    try:
        ok = browser.switch_account()
        if ok:
            info = browser.get_user_info()
            who = info['nickname'] if info else '未知昵称'
            print(f'切换成功，当前账号: {who}')
        else:
            print('切换失败（登出或登录未完成），详见日志')
        return 0 if ok else 1
    finally:
        browser.close()


def main():
    parser = argparse.ArgumentParser(description='小红书抽奖机器人')
    parser.add_argument('--login', action='store_true', help='仅登录（扫码保存登录态）')
    parser.add_argument('--once', action='store_true', help='立即执行一轮任务')
    parser.add_argument('--status', action='store_true', help='查看当前登录账号')
    parser.add_argument('--logout', action='store_true', help='退出登录（清理登录态）')
    parser.add_argument('--switch', action='store_true', help='切换账号（登出后扫码登录新账号）')
    args = parser.parse_args()

    setup_logging()

    if args.login:
        browser = XhsBrowser()
        try:
            browser.start()
            ok = browser.login()
            print('登录成功' if ok else '登录失败')
            sys.exit(0 if ok else 1)
        finally:
            browser.close()
    if args.status:
        sys.exit(run_status(XhsBrowser()))
    if args.logout:
        sys.exit(run_logout(XhsBrowser()))
    if args.switch:
        sys.exit(run_switch(XhsBrowser()))

    # 默认 / --once：执行一轮
    run_once()


if __name__ == '__main__':
    main()
