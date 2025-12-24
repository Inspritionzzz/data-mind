import urllib3

def download(url):
    http = urllib3.PoolManager()
    res = http.request('GET', url)
    return res.data



url = "http://www.baidu.com"
print(download(url))