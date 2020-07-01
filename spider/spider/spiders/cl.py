import scrapy
from spider import items


#https://cl.ce59.xyz//thread0806.php?fid=16&search=&page=1
BasicURL = 'https://cl.ce59.xyz'
page_url = BasicURL + '//thread0806.php?fid=16&search=&page='
max_page = 101

class CaoliuSpider(scrapy.Spider):
    name = 'cl'
    start_urls = [page_url+str(i) for i in range(1,101)]

    def parse(self, response):
        titles = response.xpath('//*[@class="tr3 t_one tac"]//a[@href and @id]/text()')
        urls = response.xpath('//*[@class="tr3 t_one tac"]//a[@href and @id]/@href')


if __name__ == '__main__':
    from scrapy import cmdline
    cmdline.execute("scrapy crawl cl".split())
