import openpyxl
import numpy as np
from collections import Counter
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
print(matplotlib.matplotlib_fname())

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
wb = openpyxl.load_workbook('数据浏览器访问日志表_new.xlsx', read_only=True)
ws = wb.active
weeknum=50
list_currentweek=[]
list_lastweek=[]
for row in ws.iter_rows(min_row=2):
    employee_id=row[0].value
    employee = row[1].value
    department=row[6].value
    week = row[7].value
    if week==weeknum and department!="数据管理部" and employee_id not in {"CSC27209","CSC29808","CSC31363","CSE00551","CSE00849","CSE00517"}:
        list_currentweek.append(employee)

    if week==(weeknum-1) and department!="数据管理部"and employee_id not in {"CSC27209","CSC29808","CSC31363","CSE00551","CSE00849","CSE00517"}:
        list_lastweek.append(employee)

current_counts = Counter(list_currentweek)
last_counts  = Counter(list_lastweek)
print(current_counts)
print(last_counts)
all_depts = sorted(set(current_counts.keys())|set(last_counts.keys()),key=lambda d: (current_counts.get(d, 0), last_counts.get (d, 0)))
current_data = [current_counts.get(dept, 0) for dept in all_depts]
last_data = [last_counts.get(dept, 0) for dept in all_depts]

fig, ax = plt.subplots(figsize=(10, 6))

x = np.arange(len(all_depts))
width = 0.35
ax.bar(x - width / 2, current_data, width, label='本周', color='#78c6fd')
ax.bar(x + width / 2, last_data, width, label='上周', color='#4760fc')
ax.set_title('本周 vs 上周 人员访问次数对比', fontsize=14)
ax.set_xlabel('部门')
ax.set_ylabel('访问次数')
ax.set_xticks(x)
ax.set_xticklabels(all_depts, rotation=45, ha='right')
ax.legend()

for i, (cur, last) in enumerate(zip(current_data, last_data)):
    if cur > 0:
        ax.text(i - width / 2, cur + 0.1, str(cur), ha='center', va='bottom', fontsize=9)
    if last > 0:
        ax.text(i + width / 2, last + 0.1, str(last), ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.show()


