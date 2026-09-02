# -*- coding: utf-8 -*-
"""
B站抽奖动态自动参与机器人 - 入口
用法（在 bilibili_lottery_bot 目录下）:
    python main.py --once    # 立即执行一轮
    python main.py           # 常驻，每日定时执行
    python main.py --login   # 仅登录保存 Cookie
"""
import argparse

try:
    from .notifier import setup_logging
    from .scheduler import run_once, schedule_loop
except ImportError:  # 支持在包内直接 python main.py 运行
    from notifier import setup_logging
    from scheduler import run_once, schedule_loop


def main():
    parser = argparse.ArgumentParser(description='B站抽奖动态自动参与机器人')
    parser.add_argument('--once', action='store_true', help='立即执行一轮后退出')
    parser.add_argument('--login', action='store_true', help='仅扫码登录并保存 Cookie')
    args = parser.parse_args()

    setup_logging()

    if args.login:
        try:
            from .auth import BiliAuth
        except ImportError:
            from auth import BiliAuth
        BiliAuth().login()
        return
    if args.once:
        run_once()
        return
    schedule_loop()


if __name__ == '__main__':
    main()
