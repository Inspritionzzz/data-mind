# -*- coding: utf-8 -*-
"""
企查查企业证件信息抓取工具 - 入口
用法（在 qcc_license_spider 目录下）:
    python main.py --login                        # 首次：扫码登录并保存登录态
    python main.py                                # 抓取全部企业并导出 Excel/JSON
    python main.py --limit 2                      # 只抓前 2 家（小规模试跑，降低风控）
    python main.py --company "南博置业有限公司"    # 只抓指定单家
说明：企查查反爬严格，默认有头模式运行；命中验证码时请在浏览器窗口内手动完成。
"""
import argparse
import logging

try:
    from . import config
    from .browser import QccBrowser
    from .collector import Collector
    from .writer import setup_logging, save
except ImportError:  # 支持在包内直接 python main.py 运行
    import config
    from browser import QccBrowser
    from collector import Collector
    from writer import setup_logging, save

logger = logging.getLogger(__name__)


def do_login(headless=False):
    """交互式登录：打开浏览器 -> 唤起登录 -> 人工完成 -> 保存登录态"""
    browser = QccBrowser(headless=headless)
    browser.start()
    try:
        browser.goto(config.HOME_URL)
        if browser.is_logged_in():
            logger.info('已检测到登录态，无需重复登录')
        else:
            browser.show_login()
            input('请在浏览器中完成扫码/账号登录，登录成功后回到此窗口按回车...')
        # 二次校验（登录态已持久化到 profile，即使自动判定失败也可直接尝试抓取）
        browser.goto(config.HOME_URL)
        if browser.is_logged_in():
            logger.info('登录态校验通过，已保存到: %s', config.BROWSER_PROFILE)
        else:
            logger.warning('未自动校验到登录态，但登录信息可能已保存在 profile，'
                           '可直接运行抓取验证')
    finally:
        browser.close()


def do_run(limit=None, company=None, headless=False):
    """登录校验 -> 逐家采集 -> 导出"""
    browser = QccBrowser(headless=headless)
    browser.start()
    try:
        if not browser.login():
            logger.error('未登录，无法继续。请先运行: python main.py --login')
            return
        targets = [company] if company else config.COMPANIES
        collector = Collector(browser)
        results = collector.run(targets, limit=limit)
        out = save(results)

        logger.info('==== 抓取完成，共 %d 家 ====', len(results))
        for r in results:
            logger.info('%-32s %s', r.get('企业名称', ''), r.get('抓取状态', ''))
        logger.info('结果已导出: %s', out)
        logger.info('JSON 明细: %s', config.JSON_FILE)
    finally:
        browser.close()


def main():
    parser = argparse.ArgumentParser(description='企查查企业证件信息抓取工具')
    parser.add_argument('--login', action='store_true', help='仅扫码登录并保存登录态')
    parser.add_argument('--limit', type=int, default=None, help='只抓前 N 家')
    parser.add_argument('--company', type=str, default=None, help='只抓指定企业')
    parser.add_argument('--headless', action='store_true',
                        help='无头模式（不推荐：登录/验证码需可见）')
    args = parser.parse_args()

    setup_logging()

    if args.login:
        do_login(headless=args.headless)
        return
    do_run(limit=args.limit, company=args.company, headless=args.headless)


if __name__ == '__main__':
    main()
