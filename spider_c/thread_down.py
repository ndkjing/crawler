#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
import os
import re
import sys
import time
import inspect
import json
import logging

try:
    import httplib

    httplib.HTTPConnection._http_vsn_str = 'HTTP/1.0'
except:
    pass
import requests
import threading
from pyquery import PyQuery as pq

# try:
#     from Queue import Queue as queue
# except:
from queue import Queue as queue
from config import save_root_dir
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
save_dir = os.path.join(save_root_dir,'images')

def get_format_proxy():
    proxy = requests.get("http://127.0.0.1:5010/get/").json().get("proxy")
    proxies = {"http": "http://{}".format(proxy), "https": "https://{}".format(proxy)}
    # print(proxies)
    return proxies

def del_proxy(proxies):
    print('删除无效代理', proxies)
    proxy = proxies["http"].split('//')[1]
    requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))


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
                url, title = self.tasklist.get(timeout=6)
            except:
                continue
            else:
                try:
                    proxies = get_format_proxy()
                    dagaier(url, title,proxies)
                except:
                    self.tasklist.put((url,title))


def dagaier(topicurl, title, proxies):
    '''下载帖子内容'''
    topic_req = None
    error_count = 2
    while error_count>0:
        proxies = get_format_proxy()
        print('proxies',proxies)
        print('topicurl',topicurl)
        try:
            topic_req = requests.get(topicurl, headers=header, proxies=proxies, timeout=10)
        except:
            error_count -= 1
        topic_req.encoding = 'gbk'
        print('topic_req', topic_req)
        if topic_req.status_code != 200:
            error_count -= 1
            continue
        if topic_req.status_code==200:
            # print('topic_req.text',topic_req.text)
            m = re.findall("<title>.*</title>", str(topic_req.text))
            title = m[0][7:-35]
            print('title',title)
            pattern = re.compile(r'(https:[^\s]*?(jpg))')
            Imgurl_list = pattern.findall(str(topic_req.text))
            print('Imgurl_list',Imgurl_list)
            for image_url in Imgurl_list:
                proxies = get_format_proxy()
                downimg(image_url[0],title,proxies)
    raise Exception('extract images url error')

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
                if not os.path.exists(os.path.join(save_dir + dirname)):
                    try:
                        os.makedirs(os.path.join(save_dir, dirname))
                    except:
                        return False
                write_image_path = os.path.join(save_dir , dirname,imgname)
                if os.path.exists(write_image_path):
                    print('已存在该图片跳过下载')
                    return
                with open(write_image_path, 'wb+') as fd:
                    print('write image')
                    fd.write(img_req.content)
                return
        except:
            error_count -= 1
    # del_proxy(proxies)
    return


def main():
    while True:
        try:
            work_manager = ThreadManager(2)  # 线程数
            work_manager.__start__()
            with open('topic.json','r') as f:
                topics = json.load(f)
            for topic in topics:
                work_manager.add_task(topic[0], topic[1])
            while not work_manager.isEmpty():
                work_manager.loop()
                time.sleep(1)
            logging.info(u"设置程序关闭标志")
            work_manager.__close__()
            logging.info(u"等待所有线程退出")
            work_manager.waitcomplete()
            sys.exit(0)
        except:
            continue


if __name__ == '__main__':
    # print(get_format_proxy())
    main()
