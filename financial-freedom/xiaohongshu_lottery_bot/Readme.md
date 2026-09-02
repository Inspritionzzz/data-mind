xiaohongshu_lottery_bot/
├── config.py       # 配置：关键词、间隔、邮件等
├── browser.py      # 登录层：Playwright 持久化浏览器 + 官方签名
├── collector.py    # 采集层：关注列表 → 探测新动态 → 拉取最新10条笔记
├── classifier.py   # 识别层：抽奖/福利/礼遇关键词 + 参与条件提取
├── executor.py     # 执行层：关注 / 点赞 / 收藏 / 评论
├── notifier.py     # 记录层：SQLite 去重 + 日志 + 邮件汇总
├── scheduler.py    # 调度层：指令触发，串联全流程
└── main.py         # 入口

cd financial-freedom\xiaohongshu_lottery_bot
python main.py --login   # 首次：弹出浏览器，扫码登录（登录态持久保存）
python main.py --once    # 执行一轮任务