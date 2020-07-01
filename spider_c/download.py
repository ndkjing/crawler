#simple download
import os
import re
import sys
import time
import inspect


try:
    import httplib

    httplib.HTTPConnection._http_vsn_str = 'HTTP/1.0'
except:
    pass
import requests

from pyquery import PyQuery as pq



header = {
    "User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "close"
}


# proxy={"http":"http://114.83.130.84	:9797","https":"https://114.83.130.84:9797"}
# proxy={"http":"socks5://127.0.0.1:1088","https":"socks5://127.0.0.1:1088"}


def get_format_proxy():
    proxy = requests.get("http://127.0.0.1:5010/get/").json().get("proxy")
    proxies = {"http": "http://{}".format(proxy), "https": "https://{}".format(proxy)}
    # print(proxies)
    return proxies


def dagaier(topicurl, title,proxies):
    '''下载帖子内容'''
    topic_req = None
    error_count = 0
    while True:
        if error_count > 5:  # 异常或错误超过三次
            return
        try:
            topic_req = requests.get(topicurl, headers=header, proxies=proxies, timeout=20)
            topic_req.encoding = 'gbk'
            if topic_req.status_code != 200:
                error_count += 1
                continue
        except:
            error_count += 1
            continue
        else:
            break
    topic_pq = pq(topic_req.text)
    imglist = topic_pq("div[class='tpc_content do_not_catch']>input[type='image']").items()
    print(imglist)
    for item in imglist:
        if item.attr('src') is not None:
            downimg(item.attr('src'), title,proxies)
        elif item.attr('data-src') is not None:
            downimg(item.attr('data-src'), title,proxies)
        else:
            return False


def downimg(url, title,proxies):
    '''下载帖子图片'''
    rstr = r"[\/\\\:\*\?\"\<\>\|]"
    imgname = re.sub(rstr, "_", url.split('/')[-1])
    error_count = 0
    while True:
        if error_count > 5:
            return
        try:
            img_req = requests.get(url, headers=header, proxies=proxies, timeout=10)
            if img_req.status_code != 200:
                error_count += 1
                continue
        except:
            error_count += 1
            continue
        else:
            break
    dirname = re.sub(rstr, "_", title)
    if not os.path.exists("./images/" + dirname):
        try:
            os.makedirs("./images/" + dirname)
        except:
            return False
    with open("./images/" + dirname + '/' + imgname, 'wb+') as fd:
        fd.write(img_req.content)
    return True


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.realpath(inspect.getfile(inspect.currentframe()))))
    if not os.path.exists("./images"):
        try:
            os.makedirs("./images")
        except:
            print('已存在images文件夹')
            pass

<<<<<<< HEAD
    BasicURL = 'https://cl.ab78.xyz/'
    offset = 0  # 页面偏移
    error_count = 0
    page = 217
    while offset <page:  # 主题列表分页数
        try:
            offset += 1
            print(offset)
            # proxies = get_format_proxy()
            proxies = proxy = {"http": "http://192.168.168.1:1089", "https": "https://192.168.168.1:1089"}
            PageList = 'https://cl.ab78.xyz//thread0806.php?fid=16&search=&page=' + str(offset)
            # Page_Obj = requests.get(PageList, headers=header, proxies=proxies, timeout=10)
            Page_Obj = requests.get(PageList, headers=header, timeout=10)
            Page_Obj.encoding = 'gbk'
            print('Page_Obj.status_code',Page_Obj.status_code)
            if Page_Obj.status_code != 200:
                if offset >= page:
                    offset = 0
                continue

            PagePQ = pq(Page_Obj.text)
            TopicList = PagePQ("tbody>tr[class='tr3 t_one tac']>.tal>h3>a").items()
            for i in TopicList:
                if i.attr('href')[0:8] == 'htm_data':
                    dagaier(BasicURL + i.attr('href'), i.text(),proxies)
        except KeyboardInterrupt:
            break
        except:
            if offset >= 210:
=======
    BasicURL = 'https://cl.ze53.xyz/'

    offset = 1  # 页面偏移
    error_count = 1
    page = 217
    while offset <page:  # 主题列表分页数
        print(offset)
        proxies = get_format_proxy()
        print(proxies)
        PageList = 'https://cl.ze53.xyz//thread0806.php?fid=16&search=&page=' + str(offset)
        Page_Obj = requests.get(PageList, headers=header, proxies=proxies, timeout=10)
        Page_Obj.encoding = 'gbk'
        print('Page_Obj.status_code',Page_Obj.status_code)
        print(Page_Obj)
        if Page_Obj.status_code != 200:
            if offset >= page:
>>>>>>> temp
                offset = 0
            continue

        PagePQ = pq(Page_Obj.text)
        TopicList = PagePQ("tbody>tr[class='tr3 t_one tac']>.tal>h3>a").items()
        print(TopicList)
        for i in TopicList:
            if i.attr('href')[0:8] == 'htm_data':
                dagaier(BasicURL + i.attr('href'), i.text(),proxies)

