import os

path = r'D:\Users\chengyu\Desktop\github\jupyter\bilibili_login\cookie'

# 检查路径是否存在
if not os.path.exists(path):
    # 如果路径不存在，尝试创建路径
    try:
        os.makedirs(path)
        print(f"路径 {path} 已创建。")
    except FileExistsError:
        # 当路径已存在时，会抛出此异常
        print(f"路径 {path} 已经存在。")
    except PermissionError:
        # 当没有权限创建路径时，会抛出此异常
        print(f"没有权限创建路径 {path}。")
else:
    print(f"路径 {path} 已经存在。")