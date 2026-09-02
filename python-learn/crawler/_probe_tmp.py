# -*- coding: utf-8 -*-
"""探索: 完整流程跑一家公司, 人工点一次极验, 保存结果页"""
import os
import sys
import time

_here = os.path.dirname(os.path.abspath(__file__))
sys.path = [p for p in sys.path if os.path.abspath(p or os.curdir) != _here]

from DrissionPage import ChromiumPage, ChromiumOptions

co = ChromiumOptions()
co.set_browser_path(r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe')
co.auto_port()
co.set_argument('--window-size', '1200,900')
co.set_argument('--window-position', '50,50')

page = ChromiumPage(co)
try:
    kw = '隰县供销合作社'
    page.get('https://www.cods.org.cn/cods/dmcx/index.html')
    inp = page.ele('#checkContent')
    inp.clear()
    inp.input(kw)
    page.ele('#checkBtn').click()

    # 等待最终跳转到 searchR（人工完成极验点选）
    print('*' * 60)
    print(f'如浏览器弹出验证码，请在 120 秒内完成文字点选验证...')
    print('*' * 60)
    ok = page.wait.url_change('searchR', timeout=120)
    print('到达结果页:', ok, '|', page.url)
    time.sleep(2)

    html = page.html
    with open(os.path.join(_here, '_cods_result.html'), 'w', encoding='utf-8') as f:
        f.write(html)
    print('已保存结果页 HTML, 长度:', len(html))
    print('标题:', page.title)

    # 查第二家, 看是否免验证
    page.get('https://www.cods.org.cn/cods/dmcx/index.html')
    inp = page.ele('#checkContent')
    inp.clear()
    inp.input('青海第五建筑工程公司')
    page.ele('#checkBtn').click()
    time.sleep(5)
    print('第二家 URL:', page.url)
    has_captcha = bool(page.ele('.geetest_window', timeout=3))
    print('第二家是否又弹验证码:', has_captcha)
    if not has_captcha:
        ok2 = page.wait.url_change('searchR', timeout=15)
        print('第二家直达结果页:', ok2, page.url)
        with open(os.path.join(_here, '_cods_result2.html'), 'w', encoding='utf-8') as f:
            f.write(page.html)
finally:
    page.quit()
