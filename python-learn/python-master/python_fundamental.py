import json
import random
import sys
from collections import namedtuple, deque, OrderedDict, defaultdict, Counter
from datetime import datetime, timedelta
from functools import reduce
from math import sin as sin
from math import cos as cos
import random as rd
import numpy as np
import mytoolkits.parameters as PI
from itertools import islice


# from mytoolkits.parameters import PI

def builinFunction():
    # 查看python内置函数
    dir(__builtins__)
    help(type)


def operator():
    # 运算符
    print(1 + 1)  # 2
    print(2 - 1)  # 1
    print(3 * 4)  # 12
    print(3 / 4)  # 0.75
    print(3 // 4)  # 0
    print(20220202 // 10000 == 2022)
    print(3 % 4)  # 3
    print(2 ** 3)  # 8

    # 比较运算符
    print(2 > 1)  # True
    print(2 >= 4)  # False
    print(1 < 2)  # True
    print(5 <= 2)  # False
    print(3 == 4)  # False
    print(3 != 5)  # True

    # 逻辑运算符
    print((3 > 2) and (3 < 5))  # True
    print((1 > 3) or (9 < 2))  # False
    print(not (2 > 1))  # False

    # 位运算符
    print(bin(4))  # 0b100
    print(bin(5))  # 0b101
    print(bin(~4), ~4)  # -0b101 -5
    print(bin(4 & 5), 4 & 5)  # 0b100 4
    print(bin(4 | 5), 4 | 5)  # 0b101 5
    print(bin(4 ^ 5), 4 ^ 5)  # 0b1 1
    print(bin(4 << 2), 4 << 2)  # 0b10000 16
    print(bin(4 >> 2), 4 >> 2)  # 0b1 1

    # 三元运算符
    x, y = 4, 5
    small = x if x < y else y
    print(small)  # 4

    # 其他运算符
    letters = ['A', 'B', 'C']
    if 'A' in letters:
        print('A' + ' exists')
    if 'h' not in letters:
        print('h' + ' not exists')
    # A exists
    # h not exists

    a = "hello"
    b = "hello"
    print(a is b, a == b)  # True True
    print(a is not b, a != b)  # False False

    # 运算符优先级
    print(-3 ** 2)  # -9
    print(3 ** -2)  # 0.1111111111111111
    print(1 << 3 + 2 & 7)  # 0
    print(-3 * 2 + 5 / -2 - 4)  # -12.5
    print(3 < 4 and 4 < 5)  # True

    pass


def variables():
    teacher = "jason"
    print(teacher)  # jason

    first = 2
    second = 3
    third = first + second
    print(third)  # 5

    myTeacher = "jason"
    yourTeacher = "jason2"
    ourTeacher = myTeacher + ',' + yourTeacher
    print(ourTeacher)  # jason,jason2

    set_1 = {"welcome", "study", "Python"}
    print(set_1.pop())
    pass


def dataType():
    # Number: int float complex
    x = 1
    y = 1.0
    print(type(x))
    a1 = b1 = c1 = 2
    print(a1, b1, c1)
    a2, b2, c2 = 3, 3.1, 3 + 10j
    print(a2, b2, c2)
    print(type(a2), type(b2), type(c2))

    # Boolean
    print(True + 1)  # 可视为int
    print(False)
    print(not False)

    # String
    str1 = 'just\ta\ttest'
    print(str1, type(str1))
    print(str1 + '\ttest\t', 'test' * 3)
    print(len(str1))
    print(str1[0], str1[-1])
    print(dir(str))
    print(help(str.split))
    print(str1.split("\t"))
    print(str1.title())
    print("{} {}".format("hello", "python"))
    print("{0} {1} {0}".format("hello", "python"))
    print("{:.2f}".format(3.1415926))
    print("{:+.2f}".format(3.1415926))
    print("{:.0f}".format(3.1415926))

    # List
    list1 = []
    print(type(list1))
    list1 = ['abc', 'math', 10]
    print(list1, list1[-1], list1[-2])
    list1[0] = 'def'  # 修改列表数据
    print(list1[0])
    print(list1[0:5], list1[:2], list1[1:], list1[:])  # 左闭右开[0:5)

    list2 = [2, 'cn', [1, 2, 3]]  # 嵌套列表
    print(list2)

    list3 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    print(list3[0:9:2])
    print(list3[::-1])
    print(list3 + list1)
    print(list3 * 3)

    list4 = list('just a test')
    print(list4)

    list5 = ['aa', 'bb', 'cc', 'dd', 'ee']
    list5.append('ff')
    print(id(list5))  # 内存地址不会因为上述操作而改变
    list5.insert(2, 'gg')
    print(id(list5))
    list5.extend(list3)
    print(list5)
    print(id(list5))

    list5.pop()
    print(list5)
    list5.pop(2)
    print(list5)
    print(list5.remove('cc'))  # 删除列表中第一个值为cc的元素
    print(list5)
    del list5[1]
    print(list5)
    list5.clear()

    list6 = ['aaa', 'bbb', 'ccc', 'ddd', 'bbb']
    print(list6.count('bbb'))
    print(list6.index('bbb'))  # 首次出现的位置
    print('ccc' in list6)
    print('ddd' not in list6)

    list7 = ['AA', 'cc', 'BB', 'CC']
    print(list7)
    list7.sort()
    print(list7)
    list7.reverse()
    print(list7)
    list7.sort(key=None, reverse=False)
    print(list7)
    sorted(list7, reverse=True)  # 使用全局函数
    print(list7)  # 使用sort()会改变列表本身,内置函数在原始列表复制一个副本,在副本上进行排序操作

    print(dir(list))
    list8 = ['AA', 'BB', 'CC', 'DD']
    print(list(zip(list8, range(len(list8)))))
    print(enumerate(list8))  # 枚举对象不能直接输出
    print(list(enumerate(list8)))  # 添加序号并枚举列表
    print(list(enumerate(list8, start=1)))



    # Tuple
    tup1 = ()
    print(type(tup1))
    tup2 = (100,)
    tup3 = (100)
    print(type(tup2), type(tup3))
    tup4 = 'a', 'b', 2
    print(type(tup4))
    print(tup4[:1])
    print(tup2 + tup4)
    alist = [11, 22, 33]
    atuple = tuple(alist)
    print(atuple)
    newtuple = tuple('just a test')
    print(newtuple)
    print(id(newtuple))
    newtuple = newtuple[:1] + ('just',) + newtuple[1:]  # 元组不可更改,这里采用拼接的方式创建新的元组
    print(id(newtuple))

    # Dictionary
    dict1 = {'a': 1, '2022': [1, 2, 3], 100: ('just', 'a', 'test')}
    print(dict1)
    print(dict1.items())  # 获取字典中的所有键/值对元素,并封装在元组中
    print(dict1.keys())
    print(dict1.values())
    print(dict1[100])  # 看起来像数组的索引值,其实是字典里的一个键
    print(dict1.get('a'))
    print(dict1.get('a', '此元素不存在'))
    dict1['a'] = 2  # 修改元素
    dict1['2023'] = 3
    print(dict1)
    dict2 = {'zhao': 33, 'a': 4}
    dict1.update(dict2)  # 将一个字典整体更新另一个字典
    print(dict1)
    print(dict2.pop('a'))  # 指名道姓的删除
    print(dict2.popitem())

    # Set
    a = {3, 3, 4, 5}
    print(type(a), a)
    list1 = [1, 3, 3, 5, 7]
    print(set(list1))
    a_set = set([8, 9, 10, 11])
    b_set = {10, 11, 12, 13}
    print(a_set | b_set)
    print(a_set & b_set)
    print(a_set - b_set)
    print(a_set ^ b_set)
    print(a_set.symmetric_difference(b_set))
    pass


def Structured():
    flag = False
    if flag:
        print('test if')
    else:
        print('test if else')

    score = 90
    if 90 <= score <= 100:
        print('A')
    elif 80 <= score <= 89:
        print('B')
    else:
        print('C')

    a_dict = {}
    if not a_dict:
        print('空字典')  # 非空即为真,None为False

    x = 10
    y = 20
    small = x if x < y else y
    print(small)

    list1 = [1, 2, 3, 4, 5, 6, 7, 8]
    for mylist in list1:
        temp = mylist * 2
        print(temp)

    sum = 0
    for x in range(101):  # range(start, stop[, step])
        sum = sum + x
    print(sum)

    seq = ['a', 'b', 'c', 'd']
    for index, key in enumerate(seq):
        print('seq [{0}] = {1}'.format(index, key))

    # while
    numbers = [23, 43, 56, 64, 76]
    even = []
    odd = []
    # even, odd = [], []
    while len(numbers) > 0:
        num2 = numbers.pop()
        if num2 % 2 == 0:
            even.append(num2)
        else:
            odd.append(num2)
    print("Even", even)
    print("Odd", odd)

    n = 1
    nums = []
    while n < 100:
        n = n + 1
        if n > 50:
            break
        if n % 2 == 0:
            nums.append(n)
    print(nums)

    # 推导式
    # 列表推导式
    a_list = [1, '4', 9, 'a', 0, 'bc']
    squared_ints = [e ** 2 for e in a_list if type(e) == int]
    print(squared_ints)

    vec = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    flag_vec = [num for elem in vec for num in elem]
    print(flag_vec)

    new_list = [(x, y) for x in [1, 2, 3] for y in [3, 1, 4] if x != y]
    print(new_list)

    # 上面代码等价于
    new_list = []
    for x in [1, 2, 3]:
        for y in [3, 1, 4]:
            if x != y:
                new_list.append((x, y))
    print(new_list)
    # 字典推导式
    mcase = {'a': 10, 'b': 30, 'c': 50}
    kv_exchange = {v: k for k, v in mcase.items()}
    print(kv_exchange)
    # 集合推导式
    squared = {x ** 2 for x in [1, 1, 2, -2, 3]}
    print(squared)

    pass


def buildinFunction():
    # 1. 使用自定义模块
    sin(0.4)
    x = rd.random()
    print("x = ", x)
    a = np.array((1, 2, 3, 4, 5))
    print(a)
    PI.printPI()
    print("PI.PI ", PI.PI)

    # 2. 查看系统扫描模块路径
    print(sys.path)
    home_dir = 'D:\\DevelopmentEnvironment'
    sys.path.append(home_dir)
    print(sys.path)
    # %run parameters.py

    # 3. Collections
    # namedtuple: 创建特殊的类, 属于元组
    Point = namedtuple('Point', ['x', 'y'])
    p = Point(3, 4)
    print(p.x, p.y, isinstance(p, Point), isinstance(p, tuple), p[0], p[1])
    a, b = p
    print(a, b)
    # deque: 实现高效插入和删除操作的数据类型, 解决列表插入和删除慢的问题(线性存储)
    dq = deque(['a', 'b', 'c'])
    dq.append(1)
    print(dq)
    dq.appendleft(2)
    print(dq)
    dq.insert(2, 'x')
    print(dq)
    dq.pop()
    print(dq)
    dq.popleft()
    print(dq)
    dq.remove('x')
    print(dq)
    dq.reverse()
    print(dq)
    # OrderedDict: 有序字典
    od = OrderedDict()
    od["a"] = 1
    od["b"] = 2
    od["c"] = 3
    print(od)
    keys = ["aa", "bb", "cc"]
    value = [4, 5, 6]
    od.update(zip(keys, value))
    print(od)
    print(od.pop('a'))
    od.move_to_end('b')
    print(od)
    # defaultdict: 键值不存在时返回一个默认值
    dd = defaultdict(lambda: 'N/A')  # 要早于字典的创建
    dd['key1'] = 'abc'
    print(dd['key1'], dd['key2'])
    # Counter
    colors = ['aa', 'aa', 'dd', 'dd', 'ee', 'ff', 'aa']
    result = {}
    # 使用for统计颜色数量
    for color in colors:
        if result.get(color) == None:
            result[color] = 1
        else:
            result[color] += 1
    print(result)
    # 使用Counter统计
    result2 = Counter(colors)
    print(dict(result))
    print(result2.most_common(2))  # 频次前二, 返回列表对象
    print(result2.most_common(2)[1][1])  #

    # 4. datatime
    now = datetime.now()
    print(now, type(now))
    date = datetime(2020, 10, 31, 12, 59)
    print(date)
    print(date.year, date.month, date.day, date.hour, date.minute, date.second)
    print(date.timestamp())
    cday = datetime.strptime('2020-10-31 12:59:00', '%Y-%m-%d %H:%M:%S')
    print(cday)
    print(now.strftime("%Y"))
    print(now.strftime("%y"))
    print(now.strftime("%Y-%m-%d %H:%M"))
    # 计算日期差: timedelta
    print(now + timedelta(hours=2))
    print(now - timedelta(days=2, hours=12))
    list_1 = ["2020-10-17", "2021-10-17"]
    day1 = datetime.strptime(list_1[0], '%Y-%m-%d')
    day2 = datetime.strptime(list_1[1], '%Y-%m-%d')
    deltadays = day1 - day2
    print(deltadays.days)

    # 5. json
    data = {
        'name': 'jason',
        'shares': 100,
        'price': 123.12
    }
    # 5.1 dumps和loads
    json_str = json.dumps(data)  # 将字典data序列化为json对象
    print(json_str)
    data1 = json.loads(json_str)  # 将json对象反序列化
    print(data1)
    print(type(data1))
    # 5.2 dump和load
    data2 = [{
        'a': 1,
        'b': 2,
        'c': 3,
        'd': 4,
        'e': 5,
    }]
    with open('.\\resources\\data.json', 'w') as f:
        json.dump(data2, f)
    with open('.\\resources\\data.json', 'r') as f:
        data3 = json.load(f)
    print(data3)

    # 6. random模块
    print("random", random.random())  # 返回[0, 1)区间内的随机数
    print("random", random.uniform(10, 20))  # 返回[10, 20]区间的随机数
    # random.seed(123)
    print("random", random.uniform(10, 20))  # 设置随机种子为123
    print("random_int", random.randint(1, 100))
    print("random_randrange", random.randrange(1, 20, 3))  # 在range(1, 20, 3)产生的序列中随机挑选一个
    for x in range(1, 20, 3):
        print(x, end=' ')
    choice_list = ["just", "a", "test"]
    print(random.choice(choice_list))
    print(random.choices(choice_list, k=2))  # 放回采样
    print(random.sample(choice_list, 2))  # 从choice_list中碎金挑选3个元素
    random.shuffle(choice_list)  # 混洗列表元素
    print(choice_list)
    pass


# 实际返回的是一个元组
def return_mul_val():
    str1 = 'just a test'
    str2 = 'just a test'
    return str1, str2


# 使用关键字参数避免调用时位置错乱
def saySomething(name, words):
    print(name + ':' + words)


# 可变参数
def varParafun(name, *args):
    print("位置参数1： ", name)
    print("收集参数是： ", name)
    print("第一个收集参数是： ", args[0])


# 利用一个*构建参数元组
def mySum(*args):
    sum = 0
    for i in range(0, len(args)):
        sum = sum + args[i]
    return sum


# 利用两个**构建参数字典
def varFun(**agrs):
    if len(agrs) == 0:
        print("None")
    else:
        print(agrs)


# 使用字典给可变关键字参数赋值
def some_kwargs(name, age, sex):
    print("name:", name)
    print("age:", age)
    print("sex:", sex)


def defaultFun(x, y=3):
    print(x, y)
    pass


def add_end(L=None):
    if L is None:
        L = []
    L.append('END')
    return L


def paramPackage():
    """
    注意：
        1. 打包和解包元素数量必须一致
        2. 支持解包的操作不仅限于元组,也包括所有可迭代的对象,比如列表、字典等
    """
    val = 1, 2, 3, 4
    print("val_type:", type(val))  # 将四个整数打包成了匿名元组然后赋值成了val
    print("val:", val)
    a, b, c, d = val
    print(a, b, c, d)  # 元组作为整体给分散对象赋值
    print("a_type:", type(a))


def fun(a, b, c, d):
    print(a, b, c, d)
    pass


# 不可变参数传递
def numFuntion(x):
    """
    可变对象包括: 字典,列表,集合等
        如果参数传递的是可变对象,传递的就是地址,形参的地址就是实参的地址,修改了函数中的形参,就等于修改了实参
    不可变对象包括: 数值,字符串,不变集合等
        如果参数传递的是不可变对象,为了维护它的不可变性,函数内部会重构一个实参副本,此时实参的副本和主调函数提供的实参在不同的内存位置,
        因此对函数形参的修改不会对实参造成任何影响,结果上看起来和传值一样
    """
    print("在函数中,形参x的地址为:", id(x))
    print("在函数中,x形参x的值为:", x)
    x = x + 1
    print("在函数中,x的值更新为:", x)
    print("在函数中,x的地址更新为:", id(x))
    pass


# 不可变参数传递
def strFun(s):
    print("修改之前的字符串为s=", s)
    s = 'xxxx'
    print("修改之后的字符串s=", s)


# 不可变参数传递
def tupleFun(a):
    a = a + (333, 444)
    return a
    pass


# 可变参数传递
def listFun(a):
    a.append("可变对象")
    print("在函数中,参数列表是:", id(a))
    return a  # 修改形参的值等同于修改实参的值,因此这里的return其实是多余的
    pass


# 递推计算阶乘
def iterative_fact(n):
    fact = 1
    for i in range(1, n + 1):
        fact *= i
    return fact
    pass


# 递归计算阶乘
def recursive_fact(n):
    if n <= 1:
        return n
    return n * recursive_fact(n - 1)


# filter()函数
def funFileter(variable):
    letters = [3, 6, 9]
    if (variable in letters):
        return True
    else:
        return False


# map()函数: 一元操作函数
def funMap(n):
    return len(n)


# map()函数: 二元操作函数
def funMap2(a, b):
    return a + b


def Function():
    # 1. 函数文档
    # print(help(str))
    """
    函数名: Function
    功能: python函数demo
    """
    # 2. 参数
    # 2.1 关键字参数
    # 2.2 可变参数
    # 2.3 默认参数
    # 2.4 传值还是传引用

    print(Function.__doc__)
    str1, str2 = return_mul_val()
    print(str1, str2)
    saySomething(words="hi", name="jason")
    varParafun('name', 'just', 'a', 'test', '!')
    print(mySum(1, 2, 3))
    varFun(a=1, b=2)  # 错误写法: varFun(1, 2)
    kwargs_dic = {'name': 'jason', 'age': '10', 'sex': '0'}
    some_kwargs(**kwargs_dic)
    defaultFun(1, 5)  # 传入参数会改变默认参数值
    print(defaultFun.__defaults__)  # 查看默认参数值
    print(add_end(['just', 'a', 'test']))
    print(add_end())  # 定义默认参数时务必要让这个默认参数是不可变对象,比如数值型,元组,字符串,不可变集合,None等
    paramPackage()
    mylist = [1, 2, 3, 4]
    fun(*mylist)  # 自动解包传给fun()
    mydict = {'a': 2, 'b': 4, 'c': 10, 'd': 6}
    fun(*mydict)
    fun(**mydict)
    a = 3
    print("在函数外,实参a的地址为:", id(a))
    numFuntion(a)
    print("在函数调用后,实参a的值为:", a)  # a不变,传递方式是传引用;
    b = 'hhhh'
    strFun(b)
    print("函数调用后字符串的值为s=", b)
    tuple = (111, 222, 333)
    print("函数返回的元组tuple=", tupleFun(tuple))
    print("函数调用后tuple=", tuple)
    list1 = [111, 222, 333]
    print("函数执行前实参a的地址", id(list1))
    print("函数执行返回的", listFun(list1))
    print("函数执行后实参a的地址", id(list1))
    print(list1)

    # 3. 函数递归
    num = 5
    result = iterative_fact(num)
    print("递推方法: {}! = {}".format(num, result))
    result = recursive_fact(num)
    print("递归方法: {}! = {}".format(num, result))

    # 4. 函数式编程
    # 4.1 lambda表达式
    new_add = lambda x, y: x + y
    print(new_add(5, 19))
    # 4.2 filter()函数
    a_list = [1, 2, 3, 4, 5, 6, 8, 9, 10]
    filtered = filter(funFileter, a_list)
    print(list(filtered))  # filter函数返回一个迭代器,使用list()转换成列表进行输出
    data = filter(lambda x: x % 3 == 0, a_list)
    print(list(data))
    # 4.3 map()函数
    word_len = map(funMap, ('aa', 'aaa', 'aaaa', 'a', 'aaaaa'))
    print(list(word_len))
    my_map = map(lambda x: x * 2 + 1, a_list)
    print(list(my_map))
    str_cat = map(funMap2, ('aa', 'bb', 'cc'), ('AA', 'BB', 'CC'))
    print(list(str_cat))
    num_add = map(funMap2, [1, 2, 3], [4, 5, 6])
    print(list(num_add))
    # 4.4 reduce()函数
    print(reduce(lambda x, y: x + y, [1, 2, 3, 4, 5]))
    print(reduce(lambda x, y: x + y, range(1, 101)))
    print(reduce(lambda a, b: a if a > b else b, a_list))  # 求某个序列的最大值
    # 4.5 sorted()函数
    print(sorted([10, 20, -10, 40, 50]))  # 不会改变原有列表
    print(sorted([10, 20, -10, 40, 50], reverse=True))
    print(sorted([10, 20, -10, 40, 50], key=abs, reverse=True))
    L = [10, 20, -10, 40, 50]
    print(L)
    L.sort(key=abs, reverse=True)
    print(L)
    pass


class Person:
    """
    OOP相关概念:
        1. 方法指的是与特定实例绑定的函数,不与实例绑定的普通功能块称为函数(如print(),len()等);
        2. 当通过对象调用方法时,对象本身将作为第一个参数被传递过去,普通函数则不具备这个特性;
        3. _xxx: 保护成员,不能通过 from module import * 的方式导入,支队自己和其子类开放访问权限;
        4. __xxx__: python系统自定义的特殊成员,比如__init__()表示构造方法,__del__()表示析构方法;
        5. __xxx: 表示私有成员,只能供内部使用,不能被继承,但可以通过 对象名._类名__xxx 这样的特殊方式访问,因此严格意义上python不存在私有成员;
        6. python中没有使用new操作生产一个新对象,而是饮食调用__init__()方法初始化该对象;
        7. 可以用this来代替self,不过最好还是使用self;
        8. python可以为对象添加临时属性,不会影响其他的对象;
    """
    height = 120  # 定义类的数据成员

    # 定义构造方法
    def __init__(self, name, age, weight):
        self.name = name
        self.age = age
        # 定义私有属性,私有属性在类外部无法进行直接访问
        self.__weight = weight

    def say(self):
        print("%s, %d, %d, %d" % (self.name, self.age, self.__weight, self.height))

# 类的继承
class Student(Person):
    grad = ''
    def __init__(self, name, age, weight, grad):
        # 调用父类的构造方法,初始化父类的数据成员,交由父类执行
        Person.__init__(self, name, age, weight)
        # super.__init__(self, name, age, weight)
        # 需要自己进行初始化
        self.grad = grad
    def say(self):
        print("%s, %d, %s" % (self.name, self.age, self.grad))

# 斐波那契数列
def fibonacci(xterms):
    n, a, b = 0, 0, 1
    while n < xterms:
        print(b, end=' ')
        a, b = b, a + b
        # a = b
        # b = a + b
        n = n + 1
    return 'finish'

# 斐波那契数列生成器
def fibonacci2(xterms):
    n, a, b = 0, 0, 1
    while n < xterms:
        print(b, end=' ')
        yield b
        a, b = b, a + b
        # a = b
        # b = a + b
        n = n + 1
    return 'finish'

def my_gen():
    print("第一次返回")
    yield(1)
    print("第二次返回")
    yield (2)
    print("第三次返回")
    yield (3)

class Fibonacci:
    def __init__(self):
        self.previous, self.current = 0, 1
    def __iter__(self):
        return self
    def __next__(self):
        value = self.current
        self.previous, self.current = self.current, self.current + self.previous
        self.previous
        return value

def readFile():
    try:
        file = open('.\\resources\\data.json', mode='r')
        # python会根据上下文语境自动帮我们调用close()方法
        # with open('.\\resources\\data.json', 'r') as f:
        print(file)
        for line in file:   # 按行读取
            print(line)
        file2 = open('.\\resources\\data.json', mode='r')   # 一次性读出
        print(file2.read())
        file.seek(0)  # 将文件指针复位
        print(file.read())  # 其中read()未设定参数或者参数为负,则读取文件中所有数据
        print(file.tell())  # 返回指针位置
        file.seek(0)
        print(file.read(10))  # 从文件开始读取20字节的数据
        file.readline(10)  # 读取第一行的前10个字符,指针下移
        file.seek(0)
        lines = file.readlines()  # 读取文件所有行
        print(lines[:2])  # 返回文件的前两行
    finally:
        print("关闭资源")
        if file:
            file.close()
        if file2:
            file2.close()  # close()会先刷新缓冲区还没有写入磁盘的信息,然后关闭文件
    pass

def writeFile():
    a = 123
    with open(".\\resources\\data2.txt", 'w') as f:
        f.write("just a test\njust two test")
        f.write("\n" + str(a))
    pass

def this_fails():
    x = 1 / 0
    pass

def avg(score):
    assert len(score) != 0, "输入不能为空"  # 给出错误信息
    return sum(score) / len(score)
    pass

def Advanced():
    # 1. OOP
    p1 = Person('jason', 10, 20)
    p1.say()
    p1.age = 11
    p1.name = 'jason2'
    p1.say()
    p2 = Person('lua', 11, 20)
    p2.say()
    Person.height = 130
    p2.say()
    p1.say()  # 改变公有属性的值后,所有对象的值都变了;
    p1.nickname = 'zhangcy'
    print(p1.nickname)
    stu = Student('alice', 1, 2, 3)
    stu.say()

    # 2. 生成器与迭代器
    n = 10
    a = [x**2 for x in range(n) if x % 2 == 0]  # 列表推导式
    print(a, type(a))
    b = (x**2 for x in range(n) if x % 2 == 0)  # 生成器表达式
    print(b, type(b))
    print(next(b))
    print(b.__next__())  # 没有更多元素输出时,会抛出StopIteration异常
    for num in b:
        print(num)
    fibonacci(10)
    func = fibonacci2(10)
    print(func, next(func), next(func), next(func))  #  生成器函数每次调用next()执行,遇到yield就会中止,再次执行就会从上次返回的yield语句接着往下执行;
    for item in func:
        print(item, end=' ')
    gen = my_gen()
    print(next(gen))
    print(next(gen))
    print(next(gen))    # 生成器没法使用return的返回值,如果想获得该返回值,需要不过StopIteration异常,然后输出StopIteration.value

    x = [1, 2, 3]
    y = iter(x)
    z = iter(x)
    print(y, z)
    print(type(x), type(y), type(z))
    x_iter = iter(x)
    # 迭代器边界检查
    # 迭代器适合遍历大文件和无限集合,不用一次性的全部预存到内存之中,用到后临时拿来即可;
    while True:
        try:
            print(next(x_iter))
        except StopIteration:
            print("访问越界！")
            break
    print("正常输出")
    # 创建迭代器
    f = Fibonacci()
    a = list(islice(f, 0, 10))
    print(a)
    b = list(islice(f, 0, 10))
    print(b)

    # 3. 文件操作
    readFile()
    writeFile()

    # 4. 异常处理: try print() assert logging
    try:
        this_fails()
    except ZeroDivisionError as err:
        print('运行时异常:', err)
    finally:
        print('执行到了finally')
    print('代码执行完毕')

    # num = 10
    # if num > 5:
    #     raise Exception('处理自定义异常:{}'.format(num))
    score = [10, 20]
    print("平均分数为:", avg(score))
    print('代码执行完毕')

    pass



# 在本文件中__name__就是__main__
# 在外部执行本文件,__name__就是python文件名(不包含.py)
if __name__ == '__main__':
    # 运算符
    # operator()

    # 变量
    # variables()

    # 数据类型:Number Boolean String List Tuple Dictionary Set
    # dataType()

    # 程序结构
    # Structured()

    # python标准库和内置模块
    # buildinFunction()

    # python函数
    # Function()

    # python高级特性
    Advanced()
