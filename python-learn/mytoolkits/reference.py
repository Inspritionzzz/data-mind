"""
    Bilibili动态转发抽奖脚本 Python 3 版本
    修改者信息：
    Bilibili 用户名：蝉森旅人
    Github：https://github.com/HaroldLee115
    原作者信息：
    Bilibili动态转发抽奖脚本 V1.1
    Auteur:Poc Sir   Bilibili:鸟云厂商
    Mon site Internet:https://www.hackinn.com
    Weibo:Poc-Sir Twitter:@rtcatc
    更新内容：1.增加了对画册类型动态的支持。
"""

import os
import urllib.request
import json
import sqlite3
import webbrowser
from urllib import parse as urlparse

import requests
import re
import time
import pymysql
import random
from tqdm import tqdm

class Bili():
    def __init__(self):
        self.sendurl = 'http://api.vc.bilibili.com/dynamic_repost/v1/dynamic_repost/repost'
        self.followurl = 'http://api.bilibili.com/x/relation/modify'

        # 填你的b站uid
        self.uid = ''
        # 先找cookie，抓下来以后找里面的bili_jct，以前叫crsf，懒得改了
        self.crsf = ''
        # 不会抓百度
        self.cookie = {'Cookie': ''}
        # 网上随便找个好了
        self.header = {'User-Agent': ''}

    def get(self):
        res = requests.get(geturl1, cookies=self.cookie, headers=self.header)
        cards = res.json().get('data').get('cards')
        for card in cards:
            card1 = card.get('card')
            pattern = re.compile('"orig_dy_id": (.*?), "pre_dy_id.*?uid": (.*?), "uname', re.S)
            items = re.findall(pattern, card1)
            for item in items:
                yield {
                    'dynamic_id': item[0],
                    'uid': item[1]
                }

    def follow(self):
        data = {
            'fid': item['uid'],
            'act': 1,
            're_src': 11,
            'jsonp': 'jsonp',
            'csrf': self.crsf
        }
        requests.post(self.followurl, data=data, cookies=self.cookie, headers=self.header)

    def send(self):
        data = {
            'uid': self.uid,
            'dynamic_id': item['dynamic_id'],
            'content' : str_list[random.randint(0, 4)],
            'ctrl': '[{"data":"5581898","location":2,"length":4,"type":1},{"data":"10462362","location":7,"length":5,"type":1},{"data":"1577804","location":13,"length":4,"type":1}]',
            'csrf_token': self.crsf
        }
        requests.post(self.sendurl, data=data, cookies=self.cookie, headers=self.header)

def GetMiddleStr(content,startStr,endStr):
    #result = re.findall(r'\d+', str(content))
    startIndex = content.index(startStr)
    if startIndex>=0:
        startIndex += len(startStr)
    endIndex = content.index(endStr)
    return content[startIndex:endIndex] #result[-1]

'''def GetMiddleStr(content,startStr,endStr):
    startIndex = content.index(startStr)
    if startIndex>=0:
        startIndex += len(startStr)
    endIndex = content.index(endStr)
    return content[startIndex:endIndex]'''

def GetUsers():
    global Bilibili_Key
    GetTotalRepost()
    Tmp_count = 0
    Bilibili_Key = 0
    DynamicAPI = "https://api.live.bilibili.com/dynamic_repost/v1/dynamic_repost/view_repost?dynamic_id="+ Dynamic_id + "&offset="
    conn = sqlite3.connect('Bilibili_TMP.db')
    c = conn.cursor()
    while Tmp_count < Total_count:
        Tmp_DynamicAPI = DynamicAPI + str(Tmp_count)
        try:
            BiliJson = json.loads(GetMiddleStr(urllib.request.urlopen(Tmp_DynamicAPI).read(), b"comments\":", b",\"total"))
            for BiliJson_dict in BiliJson:
                Bilibili_UID = str(BiliJson_dict['uid'])
                Bilibili_Uname = BiliJson_dict['uname']
                Bilibili_Comment = BiliJson_dict['comment']
                Bilibili_Sql = "INSERT or REPLACE into Bilibili (UID,Uname,Comment,ID) VALUES (" + Bilibili_UID + ", '" + Bilibili_Uname + "', '" + Bilibili_Comment + "', " + str(Bilibili_Key) + ")"
                c.execute(Bilibili_Sql)
                conn.commit()
                Bilibili_Key = Bilibili_Key + 1
        except:
            break
        Tmp_count = Tmp_count + 20
    else:
        Tmp_count = 0
    conn.close()

def GetTotalRepost():
    global Total_count
    global UP_UID
    DynamicAPI = "https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/get_dynamic_detail?dynamic_id=" + Dynamic_id
    BiliJson = json.loads(urllib.request.urlopen(DynamicAPI).read())
    Total_count = BiliJson['data']['card']['desc']['repost']
    UP_UID = BiliJson['data']['card']['desc']['user_profile']['info']['uid']

def GetLuckyDog():
    Bilibili_Doge = random.randint(0, Bilibili_Key)

    conn = sqlite3.connect('Bilibili_TMP.db')
    c = conn.cursor()
    cursor = c.execute("SELECT UID from Bilibili where ID=" + str(Bilibili_Doge))
    res = cursor.fetchall()
    suc = True
    if len(res) > 0 :
        suc = True
        cursor.close()
        conn.close()
        conn2 = sqlite3.connect('Bilibili_TMP.db')
        c2 = conn2.cursor()
        info_cursor = c2.execute("SELECT UID,Uname,Comment from Bilibili where ID=" + str(Bilibili_Doge))
        for row in info_cursor:
            print("用户ID:", row[0])
            print("用户名:", row[1])
            print("转发详情：", row[2], "\n")
            bilibili_open = input(TellTime() + "是否打开网页给获奖用户发送私信：（Y/N）");
            if bilibili_open == "Y":
                webbrowser.open("https://message.bilibili.com/#/whisper/mid" + str(row[0]))
            elif bilibili_open == "y":
                webbrowser.open("https://message.bilibili.com/#/whisper/mid" + str(row[0]))
            elif bilibili_open == "Yes":
                webbrowser.open("https://message.bilibili.com/#/whisper/mid" + str(row[0]))
            elif bilibili_open == "yes":
                webbrowser.open("https://message.bilibili.com/#/whisper/mid" + str(row[0]))
            elif bilibili_open == "是":
                webbrowser.open("https://message.bilibili.com/#/whisper/mid" + str(row[0]))
            elif bilibili_open == "是的":
                webbrowser.open("https://message.bilibili.com/#/whisper/mid" + str(row[0]))
        conn2.close()
    else:
        suc = False
        cursor.close()
        conn.close()
        GetLuckyDog()

def DeleteDatabase():
    DB_path = os.getcwd() + os.sep + "Bilibili_TMP.db"
    try:
        os.remove(DB_path)
        print (TellTime() + "正在清理缓存...")
    except:
        print (TellTime() + "正在清理缓存...")

def CreateDatabase():
    conn = sqlite3.connect('Bilibili_TMP.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE Bilibili
       (UID INT PRIMARY KEY     NOT NULL,
       Uname           TEXT    NOT NULL,
       Comment           TEXT    NOT NULL,
       ID            INT      NOT NULL);''')
    conn.commit()
    conn.close()

def GetDynamicid():
    s = input("请粘贴您获取到的网址：")
    nums = re.findall(r'\d+', s)

    #bilibili_domain = urllib.parse(s)[1]
    bilibili_domain = urlparse.urlparse(s)[1]
    #print(bilibili_domain)

    if bilibili_domain == "t.bilibili.com":
        print (TellTime() + "为纯文本类型动态")
        return str(nums[0])
    elif bilibili_domain == "h.bilibili.com":
        bilibili_docid = "https://api.vc.bilibili.com/link_draw/v2/doc/dynamic_id?doc_id=" + str(nums[0])
        Dynamic_id = GetMiddleStr(urllib.request.urlopen(bilibili_docid).read(),b"dynamic_id\":\"",b"\"}}")
        print (TellTime() + "为画册类型动态")
        return int(Dynamic_id)

def TellTime():
    localtime = "[" + str(time.strftime('%H:%M:%S',time.localtime(time.time()))) + "]"
    return localtime

if __name__ == '__main__':
    DeleteDatabase()
    print("+------------------------------------------------------------+")
    print("|在电脑端登录Bilibli,点击进入个人主页,再点击动态,进入动态页面|")
    print("|点击对应的动态内容，将获取到的网址复制，并粘贴在下方：      |")
    print("+------------------------------------------------------------+\n")
    Dynamic_id = str(GetDynamicid())
    TellTime()
    print (TellTime() + "获取动态成功，ID为：" + Dynamic_id)
    print (TellTime() + "正在获取转发数据中......")

    CreateDatabase()
    GetUsers()

    print(TellTime() + "获取数据成功！")
    #print(Bilibili_Key)
    print('总转发用户', Total_count)
    if Total_count == 0:
        print('没人转发 请黑箱我')
    else:
        print(TellTime() + "中奖用户信息：\n")
        GetLuckyDog()
        DeleteDatabase()



    # 这个是关键，你要去找一些b站上的抽奖号的uid，填进去就能转发他们的动态了
    host_uids = []
    geturl = 'http://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?host_uid=%s&offset_dynamic_id=0'
    sum = 0
    str_list = ['来当分母= =', '让我中一次吧QAQ', '继续分母', '转发动态', '单纯想中次奖']
    bili = Bili()
    for host_uid in host_uids:
        i = 0
        j = 0
        geturl1 = geturl % (host_uid)
        for item in tqdm(bili.get()):
            time.sleep(random.randint(1,5))
            # 数据库配置一下,具体配置写别的地方了
            db = pymysql.connect(host="", port=3306, user="", password="", db="", charset='utf8')
            cursor = db.cursor()
            insert_sql = "insert into bili (content_id) values ('%s')" % item['dynamic_id']
            select_sql = "select * from bili where content_id = " + item['dynamic_id']
            select_follow_sql = "select * from follow where follow_id = " + item['uid']
            insert_follow_sql = "insert into follow (follow_id) values (%s)" % item['uid']
            try:
                cursor.execute(select_sql)
                results = cursor.fetchall()
                if(len(results)==0):
                    try:
                        cursor.execute(insert_sql)
                        try:
                            cursor.execute(select_follow_sql)
                            results1 = cursor.fetchall()
                            if(len(results1)==0):
                                bili.follow()
                                cursor.execute(insert_follow_sql)
                        except:
                            print("获取关注失败" + item['uid'])
                        bili.send()
                        j = j+1
                        db.commit()
                    except:
                        db.rollback()
                        print('插入失败, 当前id为：' + item['dynamic_id'])
            except:
                print("搜索失败, 当前id为：" + item['dynamic_id'])
            db.close()
            i = i + 1
            if i % 10 == 0:
                time.sleep(random.randint(5,15))
        time.sleep(random.randint(25,35))
        print("第" + str(i) + "个" + ":" + str(j))
        sum = sum+j
    print("sum:" + str(sum))

