# -*- coding: utf-8 -*-
"""
数据采集层 (Collector)
    逐个企业：检索 -> 定位详情页 -> 解析工商信息（营业执照证件信息）-> 记录状态
    - 标签文本抽取（非固定选择器），对 QCC 改版更鲁棒
    - 非会员账号：被脱敏字段统一归一为“会员可见/受限”，绝不伪造
    - 每家完成即增量写 JSON，避免中途风控丢失进度
"""
import json
import logging
import random
import time
from urllib.parse import quote

try:
    from . import config
except ImportError:  # 支持在包内直接 python main.py 运行
    import config

logger = logging.getLogger(__name__)

# 检索命中验证码且未通过的哨兵值
BLOCKED = 'BLOCKED'


def _sleep(interval=None):
    """随机休眠，降低风控概率"""
    time.sleep(random.uniform(*(interval or config.REQUEST_INTERVAL)))


class Collector:
    """企业工商信息采集"""

    def __init__(self, browser):
        self.browser = browser
        self.page = browser.page
        self.results = []

    # ---------- 检索：定位企业详情页 ----------
    def _search_urls(self, name):
        kw = quote(name)
        return [config.SEARCH_URL.format(kw=kw), config.SEARCH_URL_FALLBACK.format(kw=kw)]

    def _parse_first_firm(self, name):
        """从结果页解析最匹配的企业详情链接（a[href*="/firm/"]）"""
        return self.page.evaluate('''(name) => {
            const links = Array.from(document.querySelectorAll('a[href*="/firm/"]'));
            if (!links.length) return null;
            for (const a of links) {
                if ((a.innerText || '').trim() === name) return a.href;
            }
            for (const a of links) {
                const t = (a.innerText || '').trim();
                if (t && (t.includes(name) || name.includes(t))) return a.href;
            }
            return links[0].href;
        }''', name)

    def _search_via_box(self, name):
        """回退通道：驱动首页搜索框输入回车（抗检索 URL 改版）"""
        try:
            self.browser.goto(config.HOME_URL)
            if not self.browser.ensure_no_block():
                return BLOCKED
            selectors = ['input#searchKey', 'input.search-input',
                         'input[placeholder*="搜索"]', 'input[placeholder*="企业"]',
                         'input[type="text"]']
            filled = False
            for sel in selectors:
                try:
                    loc = self.page.locator(sel).first
                    loc.click(timeout=2500)
                    loc.fill(name)
                    filled = True
                    break
                except Exception:  # noqa: BLE001
                    continue
            if not filled:
                return None
            self.page.keyboard.press('Enter')
            time.sleep(3)
            pages = self.browser.context.pages
            if len(pages) > 1:
                self.page = pages[-1]
                self.browser.page = pages[-1]
            if not self.browser.ensure_no_block():
                return BLOCKED
            return self._parse_first_firm(name)
        except Exception as e:  # noqa: BLE001
            logger.warning('搜索框回退失败: %s', e)
            return None

    def search_company(self, name):
        """返回企业详情页 URL；无结果返回 None；命中验证未通过返回 BLOCKED"""
        for url in self._search_urls(name):
            self.browser.goto(url)
            if not self.browser.ensure_no_block():
                return BLOCKED
            detail = self._parse_first_firm(name)
            if detail:
                return detail
        return self._search_via_box(name)

    # ---------- 详情：解析工商信息 ----------
    @staticmethod
    def _normalize(value):
        """清洗取值；命中脱敏线索归一为“会员可见/受限”"""
        v = (value or '').strip()
        if not v:
            return ''
        for hint in config.MASKED_HINTS:
            if hint in v:
                return config.MASKED_VALUE
        return v

    def _extract_fields(self):
        """按“标签文本 -> 值”抽取工商信息字段（对 DOM 结构变化更鲁棒）"""
        raw = self.page.evaluate('''(pairs) => {
            const out = {};
            function clean(s) { return (s || '').replace(/\\s+/g, ' ').trim(); }
            function findValue(label) {
                const nodes = Array.from(
                    document.querySelectorAll('td, th, dt, div, span, label, p'));
                for (const el of nodes) {
                    if (el.childElementCount > 2) continue;
                    const t = clean(el.textContent);
                    if (!t) continue;
                    const isLabelCell = (t === label || t === label + '：' || t === label + ':');
                    const isInline = t.length < 60
                        && (t.startsWith(label + '：') || t.startsWith(label + ':'));
                    if (!isLabelCell && !isInline) continue;
                    let v = '';
                    if (isInline) v = clean(t.slice(label.length).replace(/^[：:]/, ''));
                    if (!v && el.nextElementSibling) v = clean(el.nextElementSibling.textContent);
                    if (!v && el.parentElement && el.parentElement.childElementCount <= 6) {
                        const pt = clean(el.parentElement.textContent);
                        if (pt.startsWith(t)) v = clean(pt.slice(t.length).replace(/^[：:]/, ''));
                    }
                    if (v) return v;
                }
                return '';
            }
            for (const pair of pairs) {
                const label = pair[0], col = pair[1];
                const v = findValue(label);
                if (v) out[col] = out[col] ? (out[col] + ' / ' + v) : v;
            }
            return out;
        }''', config.LICENSE_FIELDS)

        fields = {}
        for col, val in (raw or {}).items():
            norm = self._normalize(val)
            if norm:
                fields[col] = norm
        return fields

    def extract_license(self, name, detail_url):
        """打开详情页并抽取工商信息，返回带状态的记录 dict"""
        self.browser.goto(detail_url)
        if not self.browser.ensure_no_block():
            return {'企业名称': name, '企查查URL': detail_url, '抓取状态': '需验证未完成'}

        # 工商信息通常为默认 tab；若存在“工商信息”标签则点击确保展开
        try:
            self.page.locator('text=工商信息').first.click(timeout=2500)
            time.sleep(1.2)
        except Exception:  # noqa: BLE001
            pass

        fields = self._extract_fields()

        record = {'企业名称': name, '企查查URL': detail_url, '主体类型': '企业(工商登记)'}
        record.update(fields)

        got = any(v for v in fields.values())
        masked = any(v == config.MASKED_VALUE for v in fields.values())
        if not got:
            record['抓取状态'] = '未找到工商记录'
            record['备注'] = '详情页未解析到工商信息，可能为机关/事业单位或页面结构变化'
        elif masked:
            record['抓取状态'] = '字段受限(部分)'
            record['备注'] = '非会员账号，部分证件字段被脱敏'
        else:
            record['抓取状态'] = '成功'
        return record

    # ---------- 单家采集（含重试） ----------
    def _collect_one(self, name):
        for attempt in range(config.MAX_RETRY + 1):
            try:
                detail = self.search_company(name)
                if detail == BLOCKED:
                    logger.warning('%s 检索命中验证且未通过', name)
                    return {'企业名称': name, '抓取状态': '需验证未完成',
                            '备注': '检索页验证码未通过'}
                if not detail:
                    logger.info('%s 未找到 /firm/ 企业结果', name)
                    return {'企业名称': name, '抓取状态': '未找到工商记录',
                            '备注': '可能为机关/事业单位，或名称不匹配（如存在错别字）'}
                record = self.extract_license(name, detail)
                if record.get('抓取状态') == '需验证未完成' and attempt < config.MAX_RETRY:
                    logger.warning('%s 详情页命中验证，重试(%d)', name, attempt + 1)
                    _sleep(config.RETRY_PAUSE)
                    continue
                logger.info('%s -> %s', name, record.get('抓取状态'))
                return record
            except Exception as e:  # noqa: BLE001
                logger.warning('%s 采集异常: %s', name, e)
                if attempt < config.MAX_RETRY:
                    _sleep(config.RETRY_PAUSE)
                    continue
                return {'企业名称': name, '抓取状态': '异常', '备注': str(e)[:200]}
        return {'企业名称': name, '抓取状态': '异常'}

    # ---------- 增量落盘 ----------
    def _dump_json(self):
        try:
            payload = {
                'updated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'count': len(self.results),
                'results': self.results,
            }
            with open(config.JSON_FILE, 'w', encoding='utf-8') as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
        except OSError as e:
            logger.warning('写 JSON 失败: %s', e)

    # ---------- 汇总采集 ----------
    def run(self, companies, limit=None):
        """逐家采集；每家之间随机休眠，完成即增量落盘"""
        targets = companies[:limit] if limit else list(companies)
        total = len(targets)
        logger.info('待采集企业 %d 家', total)
        for i, name in enumerate(targets, 1):
            logger.info('(%d/%d) 检索: %s', i, total, name)
            record = self._collect_one(name)
            self.results.append(record)
            self._dump_json()          # 增量保存，防止中途风控丢数据
            if i < total:
                _sleep()               # 频控间隔
        return self.results
