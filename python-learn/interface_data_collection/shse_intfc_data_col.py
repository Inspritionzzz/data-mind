import time

import requests
import json
import urllib3


urllib3.disable_warnings()
def get_data_from_url(url, params_json):
    headers = {'Content-Type': 'application/json'}
    params_json['access_token'] = get_access_token()
    # params_json = json.dumps(params_json)
    response = requests.post(url, params=params_json, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"请求失败，状态码: {response.status_code}")
        return None

# 示例用法
url = "https://fdp.cninfo.com.cn/api/load/tradeunitAPI/lease/org/transAmt.go"
# url = "https://fdp.cninfo.com.cn/api/load/tradeunitAPI/lease/org/transAmt.go?access_token=8ee40baa63e6430aa90ac6dbb66347a5&queryCycle=6&beginPeriod=2021&endPeriod=2021"
params_json = {
    "queryCycle": 3,
    "orgName": "富国基金",
    "bondType": "GGU",
    "beginPeriod": "202405",
    "endPeriod": "202405",
    "searchMode": "MARKET"
}

def get_access_token():
    params_login = {
        "loginName": "",
        "loginPasswd": ""
    }

    # params_login = {
    #     "loginName": "DZ_csc108",
    #     "loginPasswd": 'CSC#1212',
    # }

    do = True
    while do or "access_token" not in response.json().keys():
        do = False
        res_get = False
        while not res_get:
            try:
                # requests.packages.urllib3.disable_warnings()
                response = requests.post('https://fdp.cninfo.com.cn/logon/logonFdpApi.go', data=params_login, verify=False)
                res_get = True
            except:
                time.sleep(5000)
    return response.json()["access_token"]
    # return response.json()

data = get_data_from_url(url, params_json)
if data:
    # print(get_access_token())
    print(data)