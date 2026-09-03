financial-freedom/douyin_lottery_bot/
├── config.py       # 配置：关键词、间隔、邮件等
├── browser.py      # 登录层：Playwright 持久化浏览器 + 登录态检测
├── collector.py    # 采集层：拦截页面已签名 API 响应（关注列表+作品）
├── classifier.py   # 识别层：抽奖/福利/礼遇关键词 + 参与条件提取
├── executor.py     # 执行层：DOM 点击 关注/点赞/收藏/评论
├── notifier.py     # 记录层：SQLite 去重 + 日志 + 邮件汇总
├── scheduler.py    # 调度层：指令/每日 09:00 触发，串联全流程
└── main.py         # 入口


cd financial-freedom\douyin_lottery_bot
python main.py --login   # 首次：弹出浏览器，扫码登录（登录态持久保存）
python main.py --once    # 执行一轮任务
python main.py           # 常驻，每日 09:00 自动执行