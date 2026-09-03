financial-freedom/weibo_lottery_bot/
├── config.py       # 全局配置：调度时间、关键词、邮件、限流参数
├── auth.py         # 登录层：Playwright 持久化浏览器 + Cookie 持久化/校验
├── collector.py    # 采集层：关注列表 → 探测新动态 → 拉取最新10条微博
├── classifier.py   # 识别层：官方抽奖平台 + 关键词识别，提取参与条件
├── executor.py     # 执行层：关注/转发/评论/点赞
├── notifier.py     # 记录层：SQLite 去重记录 + 日志 + 邮件汇总
├── scheduler.py    # 调度层：每日 09:00 触发，串联全流程
└── main.py         # 入口

cd financial-freedom\weibo_lottery_bot
python main.py --login   # 首次：弹出浏览器，登录微博（登录态持久保存）
python main.py --once    # 立即跑一轮
python main.py           # 常驻，每日 09:00 自动执行