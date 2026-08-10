


from EmQuantAPI import *

# loginresult = c.start()

from EmQuantAPI import *

loginresult = c.start()
# loginResult = c.start("UserName=jtbj11155,PassWord=dy734589")

# loginresult为c.EmQuantData类型数据
# print(loginresult)
# 2026-05-19 08:24:51
# cmd1 undefined 该表主要提供指定日期的指数成分股代码及次日权重等信息(联系您的客户经理获取) 参数: 指数代码 截止日期 字段: 指数代码 成分代码 交易日期 成分名称 收盘价 涨跌幅 指数次日权重(小数) 流通市值 总市值 流通股本 总股本
data=c.ctr("INDEXNEXTWEIGHT","INDEXCODE,SECUCODE,TRADEDATE,NAME,CLOSE,PCTCHANGE,WEIGHT,SHRMARKETVALUE,MV,TOTALTRADABLE,SHARETOTAL","IndexCode=399266.SZ,EndDate=2016-06-30")
print(data)
