# simple download
import os
import re
import json
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

import config

header = {
    "User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "close"
}



def get_format_proxy():
    proxy = requests.get("http://127.0.0.1:5010/get/").json().get("proxy")
    if proxy is None:
        return None
    proxies = {"http": "http://{}".format(proxy), "https": "https://{}".format(proxy)}
    # print(proxies)
    return proxies


def del_proxy(proxies):
    if proxies is not None:
        print('删除无效代理', proxies)
        proxy = proxies["http"].split('//')[1]
        requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))

def down(url,encode='gbk'):
    """
    下载指定url内容
    :param url: 传递需要下载的url
    :return:
    """
    error_sum=0
    max_retry=3
    error_count = max_retry
    while True:
        proxies = get_format_proxy()
        print('proxies', proxies)
        while error_count>0:
            try:
                print('topicurl',url)
                topic_req = requests.get(url, headers=header, proxies=proxies, timeout=10)
                if encode=='gbk':
                    topic_req.encoding = 'gbk'
                print('topic_req', topic_req)
                if topic_req.status_code != 200:
                    error_count -= 1
                    continue
            except:
                error_count -= 1
                continue
            if topic_req.status_code==200:
                return topic_req
        if error_count<=0:
            # del_proxy(proxies)
            error_count=max_retry
            break
    return False



def dagaier(topicurl, title):
    '''下载帖子内容'''
    topic_req = None
    # print('topic_req.text',topic_req.text)
    topic_req = down(topicurl)
    m = re.findall("<title>.*</title>", str(topic_req.text))
    title = m[0][7:-35]
    print('title',title)
    pattern = re.compile(r'(https:[^\s]*?(jpg))')
    Imgurl_list = pattern.findall(str(topic_req.text))
    print('Imgurl_list',Imgurl_list)
    return Imgurl_list
    # for image_url in Imgurl_list:
    #     proxies = get_format_proxy()
    #     downimg(image_url[0],title,proxies)

    # topic_pq = pq(topic_req.text)
    # imglist = topic_pq("div[class='tpc_content do_not_catch']>input[type='image']").items()
    # print('imglist', imglist)
    # # print('imglistnext',imglist.__next__())
    # img_list = []
    # for item in imglist:
    #     img_list.append(item)
    # if len(img_list)==0:
    #     return
    # for item in imglist:
    #     img_list.append(item)
    #     print('item', item)
    #     if item.attr('src') is not None:
    #         print('downing', item.attr('src'))
    #         downimg(item.attr('src'), title, proxies)
    #     elif item.attr('data-src') is not None:
    #         print('downing', item.attr('data-src'))
    #         downimg(item.attr('data-src'), title, proxies)
    #     else:
    #         print('item no img')
    #         continue




def downimg(url, title, proxies):
    '''下载帖子图片'''
    rstr = r"[\/\\\:\*\?\"\<\>\|]"
    imgname = re.sub(rstr, "_", url.split('/')[-1])
    error_count = 2
    while error_count > 0:
        try:
            img_req = requests.get(url, headers=header, proxies=proxies, timeout=10)
            if img_req.status_code != 200:
                error_count -= 1
                continue
            elif img_req.status_code==200:
                dirname = re.sub(rstr, "_", title)
                if not os.path.exists("./images/" + dirname):
                    try:
                        os.makedirs("./images/" + dirname)
                    except:
                        return False
                write_image_path = "./images/" + dirname + '/' + imgname
                if os.path.exists(write_image_path):
                    print('已存在该图片跳过下载')
                    return
                with open(write_image_path, 'wb+') as fd:
                    print('write image')
                    fd.write(img_req.content)
                return
        except:
            error_count -= 1
    del_proxy(proxies)
    return
# 获取主题url
def parser_topic_page():
    BasicURL = 'https://cl.ze53.xyz/'
    offset = 0  # 页面偏移
    topic_lists = []
    with open('topic_temp.json','r') as f:
        topic_lists = json.load(f)
    page =100
    while offset < page:  # 主题列表分页数
        retry_count = 5
        proxies = get_format_proxy()
        print('proxies', proxies)
        print('############################################################################################offset', offset)
        while retry_count > 0:
            TopicList = []
            try:
                PageList = 'https://cl.ze53.xyz//thread0806.php?fid=16&search=&page=' + str(offset)
                Page_Obj = requests.get(PageList, headers=header, proxies=proxies, timeout=10)
                Page_Obj.encoding = 'gbk'
                if Page_Obj.status_code != 200:
                    retry_count -= 1
                    if offset >= page:
                        break
                    continue
            except:
                retry_count -= 1
                if offset >= page:
                    break
                continue
            print('Page_Obj.status_code', Page_Obj.status_code)
            print('Page_Obj', Page_Obj)
            PagePQ = pq(Page_Obj.text)
            TopicList = PagePQ("tbody>tr[class='tr3 t_one tac']>.tal>h3>a").items()
            print('TopicList', TopicList)
            page_topic = []
            for i in TopicList:
                print(i)
                if i.attr('href')[0:8] == 'htm_data':
                    print([BasicURL + i.attr('href'), i.text()])
                    page_topic.append([BasicURL + i.attr('href'), i.text()])
            if len(page_topic)==0:
                break
            for t in page_topic:
                if t not in topic_lists:
                    topic_lists.append(t)
                    # dagaier(BasicURL + i.attr('href'), i.text(), proxies)
            offset += 1

        del_proxy(proxies)
    print('topic_lists',len(topic_lists))

    with open('topic_save.json','w') as f:
        json.dump(topic_lists,f)


# 获取主题下图片地址
def parser_image_url():
    with open('topic.json') as f:
        topics = json.load(f)
    title_urls = []
    for topic in topics:
        url,title = topic[0],topic[1]
        urls = dagaier(url,title)

        if len(urls)==0:
            continue
        else:
            temp_list = []
            for url in urls:
                temp_list.append(url[0])
        item = [title,temp_list]
        print('item',item)
        title_urls.append(item)
        if len(title_urls)>50:
            with open('title_urls.json','w') as f:
                json.dump(title_urls,f)
    with open('title_urls.json', 'w') as f:
        json.dump(title_urls, f)


def download_image():
    """
    :return:
    """
    with open('title_urls.json','r') as f:
        title_urls = json.load(f)
    rstr = r"[\/\\\:\*\?\"\<\>\|]"

    for item in title_urls:
        title = item[0]
        urls = item[1]
        dirname = re.sub(rstr, "_", title)
        dir_path = os.path.join(config.save_root_dir , dirname)
        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path)
            except:
                return False
        for url in urls:
            img_req = down(url=url,encode=None)
            if img_req is False:
                continue
            imgname = re.sub(rstr, "_", url.split('/')[-1])
            write_image_path = os.path.join(dir_path,imgname)
            if os.path.exists(write_image_path):
                print('已存在该图片跳过下载')
                continue
            with open(write_image_path, 'wb+') as fd:
                print('write image')
                fd.write(img_req.content)

if __name__ == '__main__':
<<<<<<< HEAD
    #  下载主题
    # parser_topic_page()
    # 下载主题下图片
    # parser_image_url()
    # 下载图片
    download_image()
    # proxy = requests.get("http://127.0.0.1:5010/get/")
    # print(proxy.status_code)
    # print(type(proxy.json()),proxy.json())
=======
    parser_topic_page()
>>>>>>> 0b1dd00... 9
    # with open('topic.json','r') as f:
    #     topic = json.load(f)
    #     print(topic[:20])

