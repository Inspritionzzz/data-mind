# 简单的 HTTP 服务器
import socketserver
import http.serverPORT = 8000 handler = http.server.SimpleHTTPRequestHandler
with socketserver.TCPServer(("", PORT), handler) as http:
    print("Server Launch at Localhost: " + str(PORT))
    http.serve_forever()#在浏览器中输入http://127.0.0.1:8000/

mylist = [10, 11, 12, 13, 14]
print([i * 2 for i in mylist]) # [20, 22, 24, 26, 28]
print([i * 5 for i in mylist]) # [50, 55, 60, 65, 70]

# 更新字典
mydict = {1: "Python", 2: "JavaScript", 3: "Csharp"}
mydict.update({4: "Dart"})
print(mydict) # {1: 'Python', 2: 'JavaScript', 3: 'Csharp', 4: 'Dart'}

# 拆分多行字符串
string = "Data \n is encrpted \n by Python"
print(string)
# Output
# Data
# is encrpted
# by Python
splited = string.split("\n")
print(splited) # ['Data ', ' is encrpted ', ' by Python']

# Track Frequency
import collections
def Track_Frequency(List):
    return dict(collections.Counter(List))
print(Track_Frequency([10, 10, 12, 12, 10, 13, 13, 14]))
# Output
# {10: 3, 12: 2, 13: 2, 14: 1}

# 简单的类创建
import csv
with open("Test.csv", "r") as file:
    read = csv.reader(f)
    for r in read:
        print(row)
# 输出
# ['Sr', 'Name', 'Profession']
# ['1', '小猴子', '数据挖掘工程师']
# ['2', '云朵君', '算法工程师']

# 压缩字符串列表
mylist = ["I learn", "Python", "JavaScript", "Dart"]
string = " ".join(mylist)
print(string) # I learn Python JavaScript Dart

# 获取列表中元素的索引
mylist = [10, 11, 12, 13, 14]
print(mylist.index(10)) # 0
print(mylist.index(12)) # 2
print(mylist.index(14)) # 4

# *arg 的魔法
def func(*arg):
    num = 0
    for x in arg:
        num = num + x
print(num) # 600
func(100, 200, 300)

# 获取任意数据的类型
data1 = 123
data2 = "Py"
data3 = 123.443
data4 = True
data5 = [1, 2]

print(type(data1)) # <class 'int'>
print(type(data2)) # <class 'str'>
print(type(data3)) # <class 'float'>
print(type(data4)) # <class 'bool'>
print(type(data5)) # <class 'list'>

# 修改打印函数
print("顶级编程语言是 %r, %r 和 %r" % ('Py', 'Js', 'C#'))
# 输出
# 顶级编程语言是“Py”、“Js”和“C#”

# 字符串的去大写
data1 = "ABCD"
data2 = "Py"
data3 = "Learn Coding"
print(data1.lower()) # abcd
print(data2.lower()) # py
print(data3.lower()) # learn coding

# 快速交换变量的方法
d1 = 25
d2 = 50
d1, d2 = d2, d1
print(d1, d2) # 50 25

# 带分隔符打印
print("Py", "Js", "C#", sep="-") # Py-Js-C#
print("100", "200", "300", sep="x") # 100x200x300

# 使用 pip 安装请求的第一个安装请求导入请求
r = requests.get("https://www.baidu.com/s?wd=数据STUDIO ")
print(r) # 显示整页html数据

# 获取数据占用的内存导入系统
import sys
def memory(data):
    return sys.getsizeof(data)
print(memory(100)) # 28
print(memory("Pythonnnnnnn")) # 61


# 简单的类
class Employee:
    def __init__(self, empID):
        self.empID = empID
        self.name = "Haider"
        self.salary = 50000

    def getEmpData(self):
        return self.name, self.salary


emp = Employee(189345)
print(emp.getEmpData())  # ('Haider', 50000)

# 字符串乘数#
# 正常方式
for x in range(5):
    print("C#")

# 更好的方式
print("C# " * 5)  # C# C# C# C# C#

# 链式比较
a = 5
print(1 == a < 2) # False
print(2 < 3 < 6 > a) # True

# 数字化
integer = 234553
digitz = [int(i) for i in str(integer)]
print(digitz) # [2, 3, 4, 5, 5, 3]