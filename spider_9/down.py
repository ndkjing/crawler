import requests
from bs4 import BeautifulSoup
import uuid
import re
import time, os
import sys
import urllib.request
import xlwt
from lxml import etree
import base64
from multiprocessing import Pool
from urllib import request, parse
import threading

header = {
    "User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "close"
}


def getHTMLText(url, cookies):
    proxies = get_format_proxy()
    r = requests.get(url, cookies, headers=header, proxies=proxies)
    print('r', r)
    print('r.text', r.text)
    r.raise_for_status()
    r.encoding = r.apparent_encoding
    return r.text


class MyThread(threading.Thread):  # 定义类并继承threading.Thread类
    def __init__(self, url, proxies):
        threading.Thread.__init__(self)  # 调用父类构造函数

def get_format_proxy():
    proxy = requests.get("http://127.0.0.1:5010/get/").json().get("proxy")
    proxies = {"http": "http://{}".format(proxy), "https": "https://{}".format(proxy)}
    # print(proxies)
    return proxies


def del_proxy(proxies):
    if proxies is not None:
        print('删除无效代理', proxies)
        proxy = proxies["http"].split('//')[1]
        requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))
def getHTMLText(url, cookies):
    try:
        r = requests.get(url, cookies)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        print("Failed!")

class MyThread(threading.Thread):      # 定义类并继承threading.Thread类
    def __init__(self, url,proxies=None):
        threading.Thread.__init__(self)   # 调用父类构造函数
        self.url = url

    def run(self):  # 必须定义每个线程要运行的函数run
        print("running on number:%s" % self.num)
        time.sleep(3)



def get_format_proxy():
    proxy = requests.get("http://127.0.0.1:5010/get/").json().get("proxy")
    proxies = {"http": "http://{}".format(proxy), "https": "https://{}".format(proxy)}
    # print(proxies)
    return proxies


def del_proxy(proxies):
    print('删除无效代理', proxies)
    proxy = proxies["http"].split('//')[1]
    requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))

# if __name__ == '__main__':
#     t1 = MyThread(1)   # 生成线程对象t1
#     t2 = MyThread(2)   # 生成线程对象t2
#     t1.start()      # 运行
#     t2.start()

def write_video(url,video_path):
    r = requests.get(url.strip('\''), stream=True)
    print(r.status_code)
    with open(video_path, 'wb') as f:
        for data in r.iter_content():
            f.write(data)


def getVideoInfo(html,proxies):
    soup = BeautifulSoup(html, "html.parser")
    videoContentList = soup.find('div', attrs={'id': 'videobox'})
    # print(videoContentList)



# if __name__ == '__main__':
#     proxies = get_format_proxy()
#     t1 = MyThread(1,proxies)   # 生成线程对象t1
#     t2 = MyThread(2,proxies)   # 生成线程对象t2
#     t1.start()      # 运行
#     t2.start()

# def write_video(url, video_path=None):
#
#
#     video_path = os.path.join(r'C:\PythonProject\dataset\crawler\videos', str(uuid.uuid4()) + '.mp4')
#     # if os.path.exists(video_path):
#     #     pass
#
#     response = get_url(url,stream=True)
#     # r = requests.get(url.strip('\''), stream=True)
#
#     videoName = videoLi.find('img', attrs={'width': '120'}).get('title')
#     videoUrl = videoLi.find('a', attrs={'target': 'blank'}).get('href')
#     print('video name video url',videoName,videoUrl)
#     timetext = selector.xpath('//div[@class="listchannel"]/text()')[4 + i * 17].strip()
#     addtimetext = selector.xpath('//div[@class="listchannel"]/text()')[6 + i * 17].strip()
#     try:
#         videoAuthorContent = videoLi.find('a', attrs={'target': '_parent'}).getText()
#     except AttributeError:
#         videoAuthorContent = "None"
#
#
#     with open(video_path, 'wb') as f:
#         for data in response.iter_content():
#             f.write(data)


def getVideoInfo(html):
    soup = BeautifulSoup(html.content, "html.parser")
    # print(html.text)
    # print('soup',soup)
    # urls = soup.find_all(name='a',recursive=True, attrs={"href": re.compile(r'^http(.*)view_video(.*)')})
    # print('urls',urls)
    # print((html.content)
    print(str(html.content,'utf-8',errors='ignore'))
    viewkeys= re.findall(
        r'<a target=blank href="http://923.workgreat11.live/view_video.php?\?viewkey=(.*)&page=.*&viewtype=basic&category=.*?">',str(html.content,'utf-8',errors='ignore'))
    print('viewkey', viewkeys)
    if viewkeys is [] or len(viewkeys)==0:
        print('viewkey 为空为获取到视频')
        return
    else:
        viewkeys = list(set(viewkeys))
        for viewkey in viewkeys:
            video_page_url = 'http://923.workgreat11.live/view_video.php?viewkey='+viewkey+'&page=1&viewtype=basic&category=mr'
            video_url = get_video_url(video_page_url)
            write_video(video_url)

    # videoContentList = soup.find('div', attrs={'class': 'row'}, recursive=True)
    # # print('videoContentList',videoContentList)
    #
    # videoInfoList = videoContentList.find_all('dev')
    # print('videoInfoList', videoInfoList)
    # if videoInfoList is None:
    #     print('no video infeo lists')
    #     return
    # selector = etree.HTML(html.content)
    #
    # for videoLi in videoInfoList:
    #     videoName = videoLi.find('span', attrs={'class': 'title'}).text
    #     print('videoNmae', videoName)
    #     videoUrl = videoLi.find_all('a', recursive=True)
    #     print('videourl_node', videoUrl)
    #     print('videoUrl', videoUrl)
    #     timetext = selector.xpath('//div[@class="listchannel"]/text()')[4 + i * 17].strip()
    #     addtimetext = selector.xpath('//div[@class="listchannel"]/text()')[6 + i * 17].strip()
    #     try:
    #         videoAuthorContent = videoLi.find('a', attrs={'target': '_parent'}).getText()
    #     except AttributeError:
    #         videoAuthorContent = "None"
    #
    #     # print(videoUrl+str(i))
    #     try:
    #         videoAuthorUrl = videoLi.find('a', attrs={'target': '_parent'}).get('href')
    #     except AttributeError:
    #         videoAuthorUrl = "None"
    #     viewNumber = selector.xpath('//div[@class="listchannel"]/text()')[10 + i * 17].strip()
    #     likeNumber = selector.xpath('//div[@class="listchannel"]/text()')[11 + i * 17].strip()
    #     commentNumber = selector.xpath('//div[@class="listchannel"]/text()')[13 + i * 17].strip()
    #
    #     videoInfoList.append(videoUrl)  # 链接
    #     videoInfoList.append(videoName)  # 视频名
    #     videoInfoList.append(timetext)  # 视频时长
    #     videoInfoList.append(addtimetext)  # 上传时间
    #     videoInfoList.append(videoAuthorContent)  # 上传者id
    #     videoInfoList.append(videoAuthorUrl)  # 上传者主页
    #     videoInfoList.append(viewNumber)  # 观看数
    #     videoInfoList.append(likeNumber)  # 收藏数
    #     videoInfoList.append(commentNumber)  # 评论数
        # 解析正在的视频url
    #     try:
    #         true_videlo_url = get_video_url(videoUrl)
    #         videoInfoList.append(true_videlo_url)
    #         # 写入路径视频  如果路径已存在则跳过当前url
    #         video_path = os.path.join('videos', videoName + '.mp4')
    #         if os.path.exists(video_path):
    #             continue
    #         print(true_videlo_url)
    #         write_video(true_videlo_url, video_path)
    #     except:
    #         continue
    #
    # return videoInfoList

def get_url(url,stream=False):
    retry_count = 10
    proxies = get_format_proxy()
    print('proxies', proxies)
    while True:
        try:
            if stream:
                Page_Obj = requests.get(url, headers=header, proxies=proxies, timeout=10,stream = stream)
            else:
                Page_Obj = requests.get(url, headers=header, proxies=proxies, timeout=10,stream = stream)
                Page_Obj.raise_for_status()
                Page_Obj.encoding = Page_Obj.apparent_encoding
            if Page_Obj.status_code == 200:
                print('Page_Obj.status_code', Page_Obj.status_code)
                print('Page_Obj', Page_Obj)
                break
            else:
                print('error status code ...retry')
                retry_count -= 1
                if retry_count <= 0:
                    # del_proxy(proxies)
                    proxies = get_format_proxy()
                    retry_count = 10
        except:
            print('request error ...retry')
            retry_count -= 1
            if retry_count <= 0:
                # del_proxy(proxies)
                proxies = get_format_proxy()
                retry_count = 10
            continue
    return Page_Obj


def strdecode(input, key):
    input = base64.b64decode(input).decode("utf-8")
    str_len = len(key)
    code = ''
    for i in range(0, str_len):
        k = i % str_len
        input_i_unicode = ord(input[i])
        key_k_unicode = ord(key[k])
        code += chr(input_i_unicode ^ key_k_unicode)
    # print(input_i_unicode, key_k_unicode)
    missing_padding = 4 - len(code) % 4
    # print(code)
    if missing_padding:
        code = code + '=' * missing_padding
    code = base64.b64decode(code).decode("utf-8")
    # print(code)

    return code


def get_video_url(video_page_url):
    response =get_url(video_page_url)
    # video_url = re.findall(r'<source src="(.*?)" type=\'video/mp4\'>', str(response.content, 'utf-8', errors='ignore'))
    # print('video_url',video_url)
    # response.encoding = response.apparent_encoding
    res_text = response.text
    video_url_code = re.findall(r'document.write\(strencode\((.*?)\)\);', res_text, re.S)
    if video_url_code is [] or len(video_url_code) ==0:
        return
    temp = video_url_code[0]
    print(temp)
    # temp = temp.strip('\'')
    input, key, _ = temp.split(',')
    print(type(input),input,key)

    # video_url = strencode(input.strip('\"'), key.strip('\"'))
    # video_url = strencode(input.strip(''), key.strip(''))
    code = strdecode(input.strip('\"'), key.strip('\"'))
    print(type(code),code)
    video_url  = re.search('\'.*?\'',code).group().strip('\'')
    print('video download url',video_url)
    return video_url




def demo_fun():
    viewkeys =  ['8a6e066f50b8f712dbe2', '8a6e066f50b8f712dbe2', 'e063ebfee1cfceb63ae5', 'e063ebfee1cfceb63ae5', '0ed50f2de79449f54894', '0ed50f2de79449f54894', 'ab2a2991e0a6f7e5cafa', 'ab2a2991e0a6f7e5cafa', '7564a276a3046e6ff545', '7564a276a3046e6ff545', '753e4d54c961b9baf302', '753e4d54c961b9baf302', '597cde0fe396d5ab3e38', '597cde0fe396d5ab3e38', '3314471df81e822dcbe9', '3314471df81e822dcbe9', '31a28b1c473f310ab5ec', '31a28b1c473f310ab5ec', 'e3b6a1521b97b33d867a', 'e3b6a1521b97b33d867a', 'ac093461126cb70ffb2b', 'ac093461126cb70ffb2b', '7686a85c883452bf0bba', '7686a85c883452bf0bba', '1587623cf660703a128f']
    viewkeys = list(set(viewkeys))
    for viewkey in viewkeys:
        video_page_url = 'http://923.workgreat11.live/view_video.php?viewkey=' + viewkey + '&page=1&viewtype=basic&category=mr'
        video_url = get_video_url(video_page_url)
        write_video(video_url)

def saveToExcel(videoInfoList):
    workbook = xlwt.Workbook()
    sheet1 = workbook.add_sheet('sheet1', cell_overwrite_ok=True)

    k = 0
    for i in range(150):
        for j in range(10):
            print('正在写入的行和列是', i, j)
            sheet1.write(i, j, videoInfoList[k])
            k += 1
    workbook.save('9video_info.xls')



def get_topic(base_req):
    video_url = re.findall(r'<source src="(.*?)" type=\'video/mp4\'>',
                           str(base_req.content, 'utf-8', errors='ignore'))
    title = re.findall(r'<div id="viewvideo-title">(.*?)</div>', str(base_req.content, 'utf-8', errors='ignore'),
                       re.S)
    img_url = re.findall(r'poster="(.*?)"', str(base_req.content, 'utf-8', errors='ignore'))
    print(video_url)
    print(title)
    print(img_url)


def main():
    page = 0  # 页面偏移
    page_all =500
    while page< page_all:  # 主题列表分页数
        PageList_url = 'http://923.workgreat11.live/v.php?next=watch&page=' + str(page)
        Page_obj = get_url(PageList_url)
        getVideoInfo(Page_obj)
        page+=1

def main():

    BasicURL = 'http://923.workgreat11.live/'
    offset = 1  # 页面偏移
    page = 20
    while offset < page:  # 主题列表分页数
        retry_count = 5
        proxies = get_format_proxy()
        print('proxies', proxies)
        print('offset', offset)
        while retry_count > 0:
            TopicList = []
            PageList = 'http://923.workgreat11.live/v.php?next=watch&page=' + str(offset)
            try:
                Page_Obj = requests.get(PageList, headers=header,proxies=proxies, timeout=10)
            except:
                retry_count-=1
                continue
            print('Page_Obj.status_code',Page_Obj.status_code)
            if Page_Obj.status_code == 200:
                Page_Obj.encoding = 'gbk'
                # Page_Obj.raise_for_status()
                # Page_Obj.encoding = Page_Obj.apparent_encoding
                page_content =  Page_Obj.text
                getVideoInfo(page_content,proxies)
            if Page_Obj.status_code != 200:
                retry_count -= 1
                if offset >= page:
                    offset = 0
                continue

            print('Page_Obj.status_code', Page_Obj.status_code)
            print('Page_Obj', Page_Obj)
        # offset += 1
        # del_proxy(proxies)



if __name__ == '__main__':
    main()
    # demo_fun()