# -*- coding: utf-8 -*-
"""
企查查企业证件信息抓取工具
    Playwright 持久化浏览器 + 人工扫码登录，逐个检索企业并抓取工商/营业执照证件信息。
    分层：config(配置) / browser(登录层) / collector(采集层) / writer(记录导出) / main(入口)
"""
