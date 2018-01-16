# -*- coding: utf-8 -*-
# @Author  : Chunguang Li
# @Mail : 1192126986@foxmail.com
# @Time : 2017/11/28 11:04

from scrapy.cmdline import execute

import sys
import os


def runserver(username, password):
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    execute(["scrapy", "crawl", "whut", "-a", "username={}".format(username), "-a", "password={}".format(password)])


if __name__ == '__main__':
    runserver('', '')
