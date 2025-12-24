import requests
from lxml import etree
import re
import pickle
import os
import datetime
import copy
import time
from fake_useragent import UserAgent
from requests.packages import urllib3
urllib3.disable_warnings()

def get_text(url, data):
    while True:
        try:
            resp = requests.post(url, data=data)
            # print(resp.text)
            if resp.json()['resultCode'] == 200:
                try:
                    rows = resp.json()['records']
                    for row in rows:
                        print(row)
                    break
                except Exception as e:
                    print(resp.text)
            else:
                print("Msg:{}".format(resp.json()['resultMsg']))
        except Exception as e:
            data["access_token"] = get_user_token()

def get_user_token():
    # token
    params_token = {
        "loginName": "DZ_csc108",
        "loginPasswd": 'CSC#1212',
    }
    do = True
    while do or "access_token" not in response.json().keys():
        do = False
        res_get = False
        while not res_get:
            try:
                response = requests.post('https://fdp.cninfo.com.cn/logon/logonFdpApi.go', data=params_token, verify=False)
                res_get = True
            except:
                time.sleep(5)
    return response.json()["access_token"]

if __name__ == '__main__':
    # bondType_datas = {
    #     "GGU":"股基（AB港）",
    #     "HGU":"股基（A）",
    #     "MGU":"股票（A+港）",
    #     "AGU":"A股",
    #     "BGU":"B股",
    #     "IGU":"港股通",
    #     "CGU":"基金",
    #     "DGU":"债券现券",
    #     "EGU":"债券回购",
    #     "FGU":"可转债"
    # }
    data = {}
    data["queryCycle"] = 3
    data["orgName"] = "富国基金"
    data['bondType'] = "GGU"
    data['beginPeriod'] = "202405"
    data['endPeriod'] = "202405"
    data["access_token"] = get_user_token()
    print(str(data))
    url_transaction = 'https://fdp.cninfo.com.cn/api/load/tradeunitAPI/lease/org/transAmt.go'
    get_text(url_transaction, data)
