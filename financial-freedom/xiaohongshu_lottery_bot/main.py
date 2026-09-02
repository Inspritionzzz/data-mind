# -*- coding: utf-8 -*-
"""
小红书抽奖机器人入口
用法：
    python main.py --login   # 仅登录（首次扫码保存登录态）
    python main.py --once    # 立即执行一轮任务
"""
import argparse
import sys

from notifier import setup_logging
from browser import XhsBrowser
from scheduler import run_once


def main():
    parser = argparse.ArgumentParser(description='小红书抽奖机器人')
    parser.add_argument('--login', action='store_true', help='仅登录（扫码保存登录态）')
    parser.add_argument('--once', action='store_true', help='立即执行一轮任务')
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
        return

    # 默认 / --once：执行一轮
    run_once()


if __name__ == '__main__':
    main()
