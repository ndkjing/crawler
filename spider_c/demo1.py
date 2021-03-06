#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
import os
import re
import sys
import time
import inspect
import logging

try:
    import httplib

    httplib.HTTPConnection._http_vsn_str = 'HTTP/1.0'
except:
    pass
import requests
import threading
from pyquery import PyQuery as pq
from queue import Queue as queue
import json

from Api.ProxyApi import get_proxy

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)-6s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logging.addLevelName(50, 'CRIT')
logging.addLevelName(30, 'WARN')

header = {
    "User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "close"
}


## 从FlaskAPI/redis数据库获取代理
def get_format_proxy(web=False):
    if web:
        res = requests.get("http://127.0.0.1:5010/get/")
        if res.status_code == 200:
            proxy = res.json().get("proxy")
            if proxy is None:
                return None
            proxies = {"http": "http://{}".format(proxy), "https": "https://{}".format(proxy)}
            # print(proxies)
            return proxies
        else:
            return None
    else:
        res = json.loads(get_proxy())
        # print(res)
        proxy = res["proxy"]
        if proxy is None:
            return None
        proxies = {"http": "http://{}".format(proxy), "https": "https://{}".format(proxy)}
        # print(proxies)
        return proxies


def del_proxy(proxies):
    print('删除无效代理', proxies)
    proxy = proxies["http"].split('//')[1]
    requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))


'''国内抓取需配置代理'''
# proxy = {"http": "http://192.168.168.1:1089", "https": "https://192.168.168.1:1089"}
proxy = None


class ThreadManager(object):
    '''线程池管理'''

    def __init__(self, num):
        self.thread_num = num  # 线程数量
        self.queue = queue()  # 任务队列
        self.threadlist = list()  # 线程池列表
        self.shutdown = threading.Event()  # 线程退出标志

    def add_task(self, topic_url, topic_title):
        '''添加任务'''
        self.queue.put((topic_url, topic_title))

    def __start__(self):
        '''线程初始化'''
        for i in range(self.thread_num):
            i = ThreadWork(self.queue, self.shutdown, i)
            i.start()
            self.threadlist.append(i)

    def loop(self):
        for i in self.threadlist:
            if not i.isAlive():
                i = ThreadWork(self.queue, self.shutdown, i)
                i.start()

    def waitcomplete(self):
        '''等待线程退出'''
        for i in self.threadlist:
            if i.isAlive():
                i.join()

    def isEmpty(self):
        '''判断任务队列为空'''
        return self.queue.empty()

    def __close__(self):
        '''设置线程退出标志'''
        self.shutdown.set()


class ThreadWork(threading.Thread):
    '''工作线程入口'''

    def __init__(self, work_queue, shutdown, num):
        threading.Thread.__init__(self)
        self.setName(str(num))
        self.tasklist = work_queue
        self.shutdown = shutdown
        self.setDaemon(True)

    def run(self):
        while True:
            if self.shutdown.isSet():
                logging.info(u"线程ID：%s，检测到线程退出标志！" % (self.getName()))
                break
            try:
                url, title = self.tasklist.get(timeout=3)
            except:
                continue
            else:
                proxies = get_format_proxy()
                dagaier(url, title,proxies)


def dagaier(topicurl, title,proxies):
    '''下载帖子内容'''
    topic_req = None
    error_count = 0
    while True:
        if error_count > 2:  # 异常或错误超过三次
            logging.warning(u"线程ID：%s，下载帖子内容失败, URL:%s" % (threading.currentThread().getName(), topicurl))
            # del_proxy(proxies)
            return
        try:
            topic_req = requests.get(topicurl, headers=header, proxies=proxy, timeout=10)
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
    for item in imglist:
        if item.attr('src') is not None:
            downimg(item.attr('src'), title)
        elif item.attr('data-src') is not None:
            downimg(item.attr('data-src'), title)
        else:
            logging.warning(u"线程ID：%s，读取帖子图片URL失败, URL:%s" % (threading.currentThread().getName(), topicurl))
            return False


def downimg(url, title,proxies):
    '''下载帖子图片'''
    rstr = r"[\/\\\:\*\?\"\<\>\|]"
    imgname = re.sub(rstr, "_", url.split('/')[-1])
    error_count = 0
    while True:
        if error_count > 2:
            logging.warning(u"线程ID：%s，下载帖子图片失败, URL:%s" % (threading.currentThread().getName(), url))
            # del_proxy(proxies)
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
            logging.error(u"创建目录失败:\"%s\"" % ("./images/" + dirname))
            return False
    with open("./images/" + dirname + '/' + imgname, 'wb+') as fd:
        fd.write(img_req.content)
    return True



if __name__ == '__main__':
    # os.chdir(os.path.dirname(os.path.realpath(inspect.getfile(inspect.currentframe()))))

    if not os.path.exists("./images"):
        try:
            os.makedirs("./images")
        except:
            logging.critical(u"创建images目录失败,请检查当前用户是否有权限新建目录!")
            sys.exit(-1)
    work_manager = ThreadManager(20)  # 线程数
    work_manager.__start__()
    BasicURL = 'https://cl.fs75.xyz'
    offset = 0
    error_count = 0
    while offset < 100:  # 主题列表分页数
        proxy = get_format_proxy()
        print(proxy)
        offset += 1
        if error_count >= 3:
            logging.error(u"遍历主题列表页失败！页码:%i" % (offset))
            error_count = 0
            continue

        PageList = BasicURL + '/thread0806.php?fid=16&search=&page=' + str(offset)
        try:
            Page_Obj = requests.get(PageList, headers=header, proxies=proxy, timeout=10)
        except:
            offset+=1
            continue
        Page_Obj.encoding = 'gbk'
        if Page_Obj.status_code != 200:
            error_count += 1
            logging.warn(u"下载主题列表分页失败：%i，重试:%i" % (offset, error_count))
            offset -= 1
        retry_count = 3
        while retry_count>0:
            try:
                PageList = 'https://cl.ze53.xyz/thread0806.php?fid=16&search=&page=' + str(offset)
                Page_Obj = requests.get(PageList, headers=header, proxies=proxy, timeout=10)
                Page_Obj.encoding = 'gbk'
                if Page_Obj.status_code != 200:
                    error_count += 1
                    logging.warn(u"下载主题列表分页失败：%i，重试:%i" % (offset, error_count))
                    offset -= 1
                    continue
                elif Page_Obj.status_code==200:
                    break
            except:
                retry_count-=1
        if retry_count<=0:
            continue
        error_count = 0
        PagePQ = pq(Page_Obj.text)
        TopicList = PagePQ("tbody>tr[class='tr3 t_one tac']>.tal>h3>a").items()
        for i in TopicList:
            if i.attr('href')[0:8] == 'htm_data':
                work_manager.add_task(BasicURL + i.attr('href'), i.text())
    while not work_manager.isEmpty():
        work_manager.loop()
        time.sleep(1)
    logging.info(u"设置程序关闭标志")
    work_manager.__close__()
    logging.info(u"等待所有线程退出")
    work_manager.waitcomplete()
    sys.exit(0)

