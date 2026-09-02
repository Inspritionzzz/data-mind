financial-freedom/bilibili_lottery_bot/
├── config.py       # 全局配置：调度时间、关键词、邮件、限流参数
├── auth.py         # 登录层：扫码登录 + Cookie 持久化/校验
├── collector.py    # 采集层：好友列表 → 好友动态 → 动态详情
├── classifier.py   # 识别层：官方 lott 组件 + 关键词识别，提取参与条件
├── executor.py     # 执行层：关注/转发/评论/点赞
├── notifier.py     # 记录层：SQLite 去重记录 + 日志 + 邮件汇总
├── scheduler.py    # 调度层：每日 09:00 触发，串联全流程
└── main.py         # 入口

cd financial-freedom\bilibili_lottery_bot
python main.py --login   # 首次：扫码登录保存 Cookie
python main.py --once    # 立即跑一轮
python main.py           # 常驻，每日 09:00 自动执行