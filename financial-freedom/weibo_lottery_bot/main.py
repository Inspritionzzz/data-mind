# -*- coding: utf-8 -*-
"""
微博抽奖动态自动参与机器人 - 入口
用法（在 weibo_lottery_bot 目录下）:
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
    parser = argparse.ArgumentParser(description='微博抽奖动态自动参与机器人')
    parser.add_argument('--once', action='store_true', help='立即执行一轮后退出')
    parser.add_argument('--login', action='store_true', help='仅登录并保存 Cookie')
    args = parser.parse_args()

    setup_logging()

    if args.login:
        try:
            from .auth import WeiboAuth
        except ImportError:
            from auth import WeiboAuth
        WeiboAuth().login()
        return
    if args.once:
        run_once()
        return
    schedule_loop()


if __name__ == '__main__':
    main()
