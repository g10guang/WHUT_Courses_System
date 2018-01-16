# -*- coding: utf-8 -*-
# @Author  : Chunguang Li
# @Mail : 1192126986@foxmail.com
# @Time : 2017/11/28 18:57
from scrapy.crawler import CrawlerProcess

# from WHUT.spiders.whut import WhutSpider
from WHUT.pipelines import JsonExporterPipleline
from WHUT.spiders.whut import WhutSpider


# from WHUT.pipelines import JsonExporterPipleline


def runserver(username, password, folder):
    process = CrawlerProcess({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
    })
    process.crawl(WhutSpider, username=username, password=password, folder=folder)
    process.start()
    JsonExporterPipleline.close_files(folder)


if __name__ == '__main__':
    # import sys
    runserver('0121509351504', 'G-=Whutxi1003', '123')
    # print(sys.argv)
    # print(sys.argv[1], sys.argv[2], sys.argv[3])
    # runserver(sys.argv[1], sys.argv[2], sys.argv[3])

