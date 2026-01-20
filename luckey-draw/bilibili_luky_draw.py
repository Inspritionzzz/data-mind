import json
import httpx
import qrcode
import os

def get_qrurl() -> list:
    """返回qrcode链接以及token"""
    with httpx.Client() as client:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'
        }
        url = 'https://passport.bilibili.com/x/passport-login/web/qrcode/generate?source=main-fe-header'
        data = client.get(url=url, headers=headers)
    total_data = data.json()
    qrcode_url = total_data['data']['url']
    qrcode_key = total_data['data']['qrcode_key']
    data = {}
    data['url'] = qrcode_url
    data['qrcode_key'] = qrcode_key
    return data


def make_qrcode(data):
    """制作二维码"""
    qr = qrcode.QRCode(
        version=5,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data['url'])
    qr.make(fit=True)
    # fill_color和back_color分别控制前景颜色和背景颜色，支持输入RGB色，注意颜色更改可能会导致二维码扫描识别失败
    img = qr.make_image(fill_color="black")
    img.show()


def sav_cookie(data, id):
    """用于储存cookie"""
    # 使用 pathlib 模块处理路径
    from pathlib import Path
    path = Path(r'D:\Users\chengyu\Desktop\github\jupyter\bilibili_login\cookie')

    # 确保路径存在
    path.mkdir(parents=True, exist_ok=True)

    # 拼接文件路径
    file_path = path / f'{id}.json'

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
        print(f"Cookie 已成功保存到 {file_path}")
    except Exception as e:
        print(f"保存 Cookie 时出现错误: {e}")



def main_run():
    """主函数"""
    data = get_qrurl()
    token = data['qrcode_key']
    print(token)
    make_qrcode(data)
    with httpx.Client() as client:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'
        }
        url = f"https://passport.bilibili.com/x/passport-login/web/qrcode/poll?qrcode_key={token}&source=main-fe-header"
        # https://passport.bilibili.com/x/passport-login/web/qrcode/poll?qrcode_key=6e5d11cbbddbeb506d38ccf217594a32&source=main-fe-header
        data_login = client.get(url=url, headers=headers)  # 请求二维码状态
        data_login = json.loads(data_login.text)
    code = int(data_login['data']['code'])
    # print(code)
    if code == 0:
        cookie = dict(client.cookies)
        print(cookie)
        sav_cookie(cookie, 'test')


# def load_cookie(id) -> dict:
#     """用于加载cookie"""
#     path = r'D:\Users\chengyu\Desktop\github\jupyter\bilibili_login\cookie'
#     try:
#         file = open(f'{path}\\{id}.json', 'r')
#         print(file)
#         cookie = dict(json.load(file))
#     except FileNotFoundError:
#         msg = '未查询到用户文件，请确认资源完整'
#         cookie = 'null'
#         print(msg)
#     return cookie

def load_cookie(id) -> dict:
    """用于加载cookie"""
    path = os.path.join(r'D:\Users\chengyu\Desktop\github\jupyter\bilibili_login', 'cookie')
    file_path = os.path.join(path, f'{id}.json')

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            cookie = json.load(file)
            print(f"从文件中读取的原始数据: {cookie}")  # 打印原始数据用于调试
            return dict(cookie)
    except FileNotFoundError:
        msg = '未查询到用户文件，请确认资源完整'
        print(msg)
        return {}
    except ValueError as e:
        print(f"加载 JSON 文件时出现错误: {e}")
        return {}


# def person():
#     """获取个人资料"""
#     url = 'https://api.bilibili.com/x/web-interface/nav'
#     cookie = load_cookie('test')
#     print(cookie)
#     with httpx.Client() as client:
#         headers = {
#             'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'
#         }
#         data = client.get(url=url, headers=headers, cookies=cookie)
#     print(data)
#     data = data.json()
#     person_data = data['data']  # 获取个人信息
#     # user_name = person_data['uname']  # 用户名
#     # coin_num = str(person_data['money'])  # 硬币数量
#     # level = str(person_data['level_info']['current_level'])  # 等级
#     # face = str(person_data['face'])  # 头像链接
#     print(person_data)

def load_cookie(id) -> dict:
    """用于加载cookie"""
    path = os.path.join(r'D:\Users\chengyu\Desktop\github\jupyter\bilibili_login', 'cookie')
    file_path = os.path.join(path, f'{id}.json')

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            cookie = json.load(file)
            print(dict(cookie))
            return dict(cookie)
    except FileNotFoundError:
        msg = '未查询到用户文件，请确认资源完整'
        print(msg)
        return {}
    except ValueError as e:
        print(f"加载 JSON 文件时出现错误: {e}")
        return {}

def person():
    """获取个人资料"""
    url = 'https://api.bilibili.com/x/web-interface/nav'
    cookie = load_cookie('test')
    print(cookie)
    # 将 cookie 字典中的所有值转换为字符串类型
    str_cookie = {key: str(value) for key, value in cookie.items()}
    with httpx.Client() as client:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'
        }
        data = client.get(url=url, headers=headers, cookies=str_cookie)
    print(data)
    data = data.json()
    person_data = data['data']  # 获取个人信息
    # user_name = person_data['uname']  # 用户名
    # coin_num = str(person_data['money'])  # 硬币数量
    # level = str(person_data['level_info']['current_level'])  # 等级
    # face = str(person_data['face'])  # 头像链接
    print(person_data)


if __name__ == "__main__":
    # test
    # sav_cookie('{"code":0,"message":"0","ttl":1,"data":{"url":"https://passport.biligame.com/x/passport-login/web/crossDomain?DedeUserID=188491761\u0026DedeUserID__ckMd5=aa66a1d81220458b\u0026Expires=1756988883\u0026SESSDATA=936d5fd2,1756988883,ea74e*32CjCDW5SfCLmi0RqiuMgHgHkkAoN69ZKjTUWsGLrj1qnICpmrPQcfVumct0EK6JQIcsYSVjAxM3ozRU9MTTVHaFE4bmlvY2JZZ3Bud0JCTWl0TkNHNDRncC1fUWZiRW5kN21PVmMzSzFQem9qbnhYVlRDXzFFbU9hdHZ0em9SVUhEWVRNVnBJTk9BIIEC\u0026bili_jct=490ad410cba0c28933763ec3fd744447\u0026gourl=https%3A%2F%2Fwww.bilibili.com\u0026first_domain=.bilibili.com","refresh_token":"a5a40003a868a21cfbee7d8e06322b32","timestamp":1741436883118,"code":0,"message":""}}','test')

    # main_run()
    person()


# https://passport.bilibili.com/login