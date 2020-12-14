"""
管理与调度程序入口
"""
import os
import sys
sys.path.append(os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)),'proxy_pool-master')))
print(sys.path)
import json
from Schedule.ProxyScheduler import runScheduler
import requests
import threading
from Api.ProxyApi import get_proxy


class Manager:
    def __init__(self):
        self.header ={"User-Agent" : "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1.6) ",
                      "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                      "Accept-Language" : "en-us",
                      # "Connection" : "keep-alive",
                      "Accept-Charset" : "GB2312,utf-8;q=0.7,*;q=0.7"}
        self.proxy = None

    def run_scheduler(self):
        # 启动抓取代理
        runScheduler()

    def get_proxy(self):
        """
        获取一个代理
        :return:
        """
        res = json.loads(get_proxy())
        # print(res)
        proxy = res["proxy"]
        if proxy is None:
            return None
        proxies = {"http": "http://{}".format(proxy), "https": "https://{}".format(proxy)}
        print('proxies',proxies)
        return proxies


    def visit_blog(self):
        """
        访问CSDN博客
        :return:
        """
        requests.adapters.DEFAULT_RETRIES = 5  # 增加重连次数
        s = requests.session()
        s.keep_alive = False  # 关闭多余连接
        with open('csdn/article_list.json','r') as f:
            article_list = json.load(f)
        while True:
            try:
                for k,v in article_list.items():
                    for article_url in v:
                        self.get_url(article_url)
            except Exception as e:
                print('error',e)


    def get_url(self,url):
        try:
            print('url',url)
            proxy=self.get_proxy()
            print('proxy',proxy)
            response = requests.get(url=url, proxies=proxy, headers=self.header)
            print('status_code',response.status_code)
        except Exception as e:
            print('error',e)
            self.proxy = self.get_proxy()


    def start(self):
        t1 = threading.Thread(target=self.run_scheduler)
        t2 = threading.Thread(target=self.visit_blog)

        t1.start()
        t2.start()

        t1.join()  # join函数让其他未join线程等待该进程结束
        t2.join()


if __name__ == '__main__':
    obj = Manager()
    # print(obj.get_proxy())
    # obj.start()
    # obj.run_scheduler()
    # 访问
    obj.visit_blog()
