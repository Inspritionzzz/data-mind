from EmQuantAPI import *

loginresult = c.start()
# loginresult为c.EmQuantData类型数据
# print(loginresult)

data = c.css("300059.SZ","TOTALSHARE","enddate=20190819")
if data.ErrorCode != 0:
    print("request css Error, ", data.ErrorMsg)
else:
    for code in data.Codes:
        for i in range(0,len(data.Indicators)):
            print("request css true,",data.Data[code][i])

data = c.tradedates("2016-07-01", "2016-07-12")
if(data.ErrorCode != 0):
    print("request tradedates Error, ", data.ErrorMsg)
else:
    print("tradedate输出结果======分隔线======")
    for item in data.Data:
        print(item)
