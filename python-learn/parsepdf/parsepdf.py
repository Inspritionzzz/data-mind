import json
import logging
import pdfplumber
import re
# import pymupdf
from itertools import chain


def get_bug_file_name():

    pdf = pdfplumber.open("合规系统-综合审计报告20220907.pdf")
    all_pages = pdf.pages
    result = []
    for page in all_pages:  # 遍历所有页的数据

        text = page.extract_text()  # 用extract_text函数获取当前页的文本内容

        try:
            print(text.index("源源码码定定位位"))
            # print(text)
            print(re.findall(r"源源码码定定位位：：  (.+?)：", text))
            for bad_code in result.append(re.findall(r"：：  (.+?)：", text)):
                result.append(bad_code)
        except Exception as err:
            print('未找到文件...')
        print(page.page_number)
        print('=========================分页=================================')
    print(list(chain(*result)))
    result = list(chain(*result))
    result_duplicate = []
    [result_duplicate.append(i) for i in result if i not in result_duplicate]
    result_duplicate.remove("pom.xml")
    with open("conmand", 'w') as f:
        f.truncate()
        for i in range(len(result_duplicate)):
            print(result_duplicate[i])
            f.write(result_duplicate[i])
            f.write("\n")
    # 测试
    # with pdfplumber.open("合规系统-综合审计报告20220907.pdf") as pdf:
    #     second_page = pdf.pages[1]
    #     print(second_page.extract_text())

    return result

def writeFile(list):
    with open("conmand", 'w') as f:
        for line in list:
            f.write(line + "\n")
    pass


if __name__ == '__main__':
    result = get_bug_file_name()
    logger = logging.getLogger(__name__)
    logger.info('提取成功...')
    # writeFile(result)
    logger.info('git指令生成成功...')

