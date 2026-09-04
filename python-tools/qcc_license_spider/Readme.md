# 企查查企业证件信息抓取工具（qcc_license_spider）

基于 Playwright 持久化浏览器 + 人工扫码登录，逐个检索企业并抓取其**工商 / 营业执照证件信息**，导出 Excel + JSON。

沿用仓库 `financial-freedom/*_bot` 的分层与反爬处理模式（持久化登录态、慢速随机间隔、验证码人工处理、增量落盘）。

## 目录结构

```
qcc_license_spider/
├── config.py       # 配置：路径 / URL / 浏览器 / 频控 / 字段映射 / 企业清单
├── browser.py      # 登录层：Playwright 持久化浏览器 + 扫码登录 + 验证码检测与人工暂停
├── collector.py    # 采集层：检索企业 -> 定位详情页 -> 解析工商信息 -> 增量落盘
├── writer.py       # 记录层：日志 + 导出 Excel(.xlsx) / JSON
├── main.py         # 入口（argparse）
├── Readme.md
└── data/           # 运行产物（已被 .gitignore 忽略，含浏览器登录态，勿提交）
    ├── browser_profile/   # 持久化登录态（Cookie）
    ├── qcc_license.xlsx   # Excel 结果
    ├── qcc_license.json   # JSON 结果（每家采集完即增量写入）
    └── run.log            # 运行日志
```

## 前置条件

- Python 3.10+（本机为 3.13.2）
- 依赖：`playwright`、`pandas`、`openpyxl`（本机均已安装，无需额外安装）
- Playwright Chromium 内核已下载（本机已就绪）。若换机部署：
  ```powershell
  pip install playwright pandas openpyxl
  python -m playwright install chromium
  ```
- **需本人企查查账号**。查看企业营业执照详情需登录；统一社会信用代码 / 工商注册号 / 组织机构代码等完整字段通常**仅会员(VIP)可见**。

## 使用方法

在 `python-tools/qcc_license_spider` 目录下执行：

```powershell
cd python-tools\qcc_license_spider

# 1) 首次：弹出浏览器，扫码/账号登录（登录态持久保存，之后免登录）
python main.py --login

# 2) 小规模试跑：只抓前 1~2 家，确认能定位详情页、解析字段、生成文件
python main.py --limit 1
python main.py --limit 2

# 3) 抓取全部企业清单并导出
python main.py

# 只查某一家
python main.py --company "南博置业有限公司"
```

产物：`data/qcc_license.xlsx`（中文表头，列顺序固定）与 `data/qcc_license.json`（原始明细）。

## 待抓取企业清单

清单内嵌于 `config.py` 的 `COMPANIES`（原文照录，含机关/事业单位/研究所等非公司主体）。可直接在该列表增删。

> 注意：清单中的“北京市计划经济委员会”（政府机关）、“北京控制工程研究所 / 南京船舶雷达研究所”（事业单位/研究所）等**可能没有企业营业执照**，脚本会记为 `未找到工商记录`；“南京民族装钸艺术研究所”等若存在错别字，可能检索不到，请在结果备注中留意。

## 抓取字段（工商 / 营业执照证件信息）

登记状态、统一社会信用代码、工商注册号、组织机构代码、纳税人识别号、纳税人资质、法定代表人、注册资本、实缴资本、成立日期、核准日期、登记机关、企业类型、营业期限、所属行业、人员规模、参保人数、注册地址、经营范围、英文名/曾用名、主体类型、企查查URL、抓取状态、备注。

抽取方式为**按中文标签文本匹配取值**（非固定 CSS 选择器），以降低 QCC 前端改版导致失效的概率。

## 关键说明（务必阅读）

- **非会员账号**：被脱敏/隐藏的字段统一记为 `会员可见/受限`，脚本**不猜测、不伪造**任何证件号。
- **验证码 / 风控**：企查查会不定期弹滑块/点选验证或提示“访问频繁”。脚本检测到后会**暂停并提示你在浏览器窗口内手动完成验证**，完成后自动继续；默认有头模式（`HEADLESS=False`），无头模式无法人工过验证。
- **频率控制**：每家企业之间随机休眠 8~20 秒（`config.REQUEST_INTERVAL`），请**不要**调得过小，否则易触发频控/封禁。建议先用 `--limit` 小步试跑。
- **抗改版**：QCC 的检索 URL、页面结构、验证策略会变动。脚本已内置检索 URL 回退与首页搜索框回退；首次实跑若个别标签解析不到，可按真实 DOM 在 `config.LICENSE_FIELDS` 中补充/调整标签名。
- **登录态安全**：`data/browser_profile/` 含登录 Cookie，属敏感数据，已在 `.gitignore` 忽略，请勿分享或提交。

## 合规声明

本工具仅用于**个人学习与研究**，请遵守企查查服务条款与 `robots` 约定，控制访问频率，不得用于商业批量倒卖、绕过付费墙或伪造被脱敏数据。

cd python-tools\qcc_license_spider
python main.py --login      # 1) 弹出浏览器，扫码登录（登录态持久保存）
python main.py --limit 1    # 2) 先小步试跑 1 家，确认能定位详情页/解析字段/出文件
python main.py              # 3) 跑全部 18 家，导出 data\qcc_license.xlsx 与 .json
