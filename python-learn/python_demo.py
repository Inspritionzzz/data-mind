import time


def f1():
    # 字典推导式
    letter_dict = {"A": 1, "B": 2, "C": 3}
    letter_dict2 = {v: k for k, v in letter_dict.items()}
    print(letter_dict2)

    # 集合推导式
    num_list = {i for i in range(1, 10) if i % 2 == 1}
    print(num_list)

def f2():
    # I/O
    with open("记录-远程.md", "w", encoding='utf-8') as f:
        f.write("line1\n")
        f.write("line2\n")

    with open("记录-远程.md", "r", encoding='utf-8') as f:
        # line1 = f.readline()
        # line2 = f.readline()
        # print(line1)
        # print(line2)

        lines = f.readlines()
        print(lines)


def f3():
    import datetime
    # exception
    try:
        a = 10 / 0;
    except Exception as e:
        with open("记录-远程.md", "a+", encoding="utf-8") as f:
            datetime_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:S")
            f.write(datetime_str + "\t" + str(e) + "\n")
        print(e)
    print("end")

class People:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def introduce(self):
        print(self.name + " " + str(self.age))

from utils.people_model import People2
def f4():
    p = People("jason", 23)
    p.introduce()

    p = People2("Alice", 18)
    p.introduce()

# python内置函数：随机数,数学运算,时间和日期,序列化,文件操作,加密库,日志
import random
import math
import datetime
import os
import shutil
import hashlib
import logging

def f5():
    rand_list = [random.randrange(1000) for i in range(10)]
    print(rand_list)

    num_list = list(range(1, 101))
    for i in range(3):
        print(random.choice(num_list))

    print(math.pi)
    ret = math.log(10, 2)
    print(ret)

    print(datetime.datetime.now())
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:S"))
    print(time.time())
    print(datetime.datetime.fromtimestamp(time.time()))

    print(os.getcwd())  # 获取当前运行的工作区
    print(os.listdir("./"))     # 获取某个文件夹下所有的子文件夹
    print(os.path.exists("./python_demo.py"))
    is_exist = os.path.exists("./test")     # 创建文件夹
    if not is_exist:
        os.makedirs("./test")
    else:
        print("文件已经存在,请勿重复创建！")
    file_list = os.listdir("./")
    for file in file_list:
        abs_file_path = os.path.join(os.getcwd(), file)
        print(abs_file_path)

    # shutil.copy("./python_demo.py", "./python_demo_copy.py")    # 复制文件

    s = "100037"
    md5 = hashlib.md5()
    md5.update(s.encode('utf-8'))
    print(md5.hexdigest())

    logging.basicConfig(level=logging.DEBUG,
                        filename='output.log',
                        datefmt='%Y-%m-%d %H:%M:S',
                        format='%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(module)s - %(message)s')
    logger = logging.getLogger(__name__)
    logger.info('This is a log info')
    logger.debug('Debugging')
    logger.warning('Warning exists')
    logger.info('Finish')

if __name__ == '__main__':
    print('PyCharm')
    # f1()
    # f2()
    # f3()
    # f4()
    f5()
