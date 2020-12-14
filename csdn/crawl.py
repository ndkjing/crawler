from urllib.request import urlopen
from urllib.request import urlretrieve
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import os
import json

class CSDNCrawl:
    """
    抓取CSDN博客
    """

    def __init__(self, name=None):
        """
        :param name: CSDN用户名
        """
        if name is None:
            self.name = 'jjjndk1314'
        else:
            self.name=name
        self.base_url = 'http://blog.csdn.net/%s' % self.name
        self.article_list = []

    # 获取一个页面上所有的文章链接地址
    def parse_page(self, bsObj):
        articles = bsObj.findAll('div', {'class': 'article-item-box csdn-tracking-statistics'})
        links = []
        for article in articles:
            links.append(article.h4.a.attrs['href'])
            print(links[-1])
            self.article_list.append(urljoin(self.url, links[-1]))
            # self.parse_article(urljoin(self.url, links[-1]))

    # Parse one article.
    def parse_article(self, url):
        print('article url ', url)

        global blogCount
        # 1. Open article site.
        html = urlopen(url)
        bsObj = BeautifulSoup(html, 'html.parser')

        # 2. Parse title and create directory with title.
        title = bsObj.h1.get_text()
        print('Article title is: %s' % title)
        convertTitle = replace_deny_char(title)
        blogCount += 1
        directory = 'CSDN Blog/%d.%s' % (blogCount, convertTitle)
        if os.path.exists(directory) is False:
            os.makedirs(directory)

        # 3. Parse and download images.
        images = bsObj.find('div', {'class': 'article_content'}
                            ).findAll('img')
        count = 0
        for img in images:
            count += 1
            imgUrl = urljoin(url, img.attrs['src'])
            print('Download image url: %s' % imgUrl)
            urlretrieve(imgUrl, '%s//%d.jpg' % (directory, count))

        # 4. Parse blog content and convert html to markdown.
        parse_article_content(bsObj, directory, convertTitle)

    # 获取页面上所有的文章url
    def get_article_list(self):
        self.url = self.base_url
        while True:
            # 1. Open new page.
            html = urlopen(self.url)
            bsObj = BeautifulSoup(html, 'html.parser')
            print('home page url: %s' % self.url)

            # 2. Crawl every article.
            self.parse_page(bsObj)

            # 3. Move to next page.
            next_url = bsObj.find('li',{'class':'js-page-next js-page-action ui-pager'})
            if next_url is not None:
                self.url = urljoin(self.url, next_url.attrs['href'])
            else:
                break
        print('博客数量',len(self.article_list))
        with open('article_list.json', 'w') as f:
            json.dump({'article_list':self.article_list},f)


# Parse article content and convert html to markdown.
def parse_article_content(bsObj, directory, title):
    # 1. Find html.
    html = bsObj.find('div', {'class': 'article_content'})
    # md = tomd.convert(html.prettify())
    #
    # # 2. Write to the file.
    # with open('%s/%s.md' % (directory, title), 'w', encoding='utf-8') as f:
    #     f.write(md)


# Replace deny char, used to name a directory.
def replace_deny_char(title):
    deny_char = ['\\', '/', ':', '*', '?', '\"', '<', '>', '|', '：']
    for char in deny_char:
        title = title.replace(char, ' ')
    print('Convert title is: %s' % title)
    return title


if __name__ == '__main__':
    obj = CSDNCrawl()
    obj.get_article_list()
