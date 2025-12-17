from datetime import datetime, timedelta

# 设置目标年份
year = 2025

# 获取当年第一天
start_date = datetime(year, 1, 1)

# 计算 1月1日 是星期几（0=Monday, 6=Sunday）
weekday = start_date.weekday()  # 0=Mon, 1=Tue, ..., 6=Sun

# 第一周的周一（可能是前一年的某天）
first_monday = start_date - timedelta(days=weekday)

# 初始化结果列表
weeks = []

# 当前周的开始日期
current_week_start = first_monday
week_num = 1

# 遍历所有周，直到超过2025年
while current_week_start.year <= year:
    # 当前周的起止时间
    week_start = current_week_start
    week_end = current_week_start + timedelta(days=6)

    # 如果这一周完全在2025年内，或者起始日在2025年，则保留
    if week_start.year == year or (week_start.year == year and week_end.year == year):
        # 格式化为 YYYYMMDD
        start_str = week_start.strftime("%Y%m%d")
        end_str = week_end.strftime("%Y%m%d")

        # 添加到结果
        weeks.append(f"第{week_num}周 ({start_str}-{end_str})")

    # 下一周
    current_week_start += timedelta(days=7)
    week_num += 1

# ✅ 输出所有周
for week in weeks:
    print(week)  # 确保这行没有被注释！

# 可选：打印总周数
print(f"\n共生成 {len(weeks)} 周数据。")