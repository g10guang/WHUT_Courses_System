# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class WhutItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class WhutLessionItem(scrapy.Item):
    # whut课程信息
    # zykxkList.do?jxjhh=20154129&kcdm=4120316140&&xnxq=2017-2018-1
    suid_obj = scrapy.Field()
    lession_name = scrapy.Field()
    lession_url = scrapy.Field()
    teacher = scrapy.Field()
    vector = scrapy.Field()  # 容量
    selected = scrapy.Field()  # 已选
    this_selected = scrapy.Field()  # 本轮已选
    lession_function = scrapy.Field()  # 选课方式
    score = scrapy.Field()  # 学分
    jxjhh = scrapy.Field()
    kcdm = scrapy.Field()
    xnxq = scrapy.Field()
    keyinfo = scrapy.Field()