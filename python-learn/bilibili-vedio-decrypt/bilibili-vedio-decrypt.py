import os
from time import sleep

# 文件操作

def remove_ff(full_path):
    flag = False
    with open(full_path, 'rb') as file:
        start1 = file.read(1)
        start2 = file.read(1)
        start3 = file.read(1)
        if start1 == b'\xff' and start2 == b'\xff' and start3 == b'\xff':
            dirname = os.path.dirname(full_path)
            temp_name = os.path.join(dirname, 'temp.mp4')
            print('生成文件：', full_path)
            f2 = open(temp_name, 'wb')
            nums = 0
            while f2.write(file.read(1024*1024)):
                nums += 1
            print("处理文件大小：", nums, 'M')
            f2.close()
            print('处理完成')
            flag = True
        else:
            print('此文件无需处理')
    if flag:
        if os.path.exists(full_path):
            os.remove(full_path)
        os.rename(temp_name, full_path)


if __name__ == '__main__':
    print('程序开始')
    counter = 0
    dirname = os.path.dirname(os.path.realpath(__file__))
    print(dirname)
    dirname = r"D:\\Users\\jason\\Desktop\\stu"
    for name in os.listdir(dirname):
        if name.endswith('.mp4'):
            counter += 1
            print('处理文件序号：', counter, '，处理文件名称：',name)
            remove_ff(os.path.join(dirname, name))
    print('所有任务处理完成，10s后关闭此窗口')
    sleep(10)

