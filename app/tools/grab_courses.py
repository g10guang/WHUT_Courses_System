#!/usr/bin/env python3
# coding=utf-8
# author: XiGuang Liu<g10guang@foxmail.com>
# 2017/11/28 16:08
# function:


import os

from app import DATA_DIR

from app.spider import spider
import shutil


def grab_courses(username: str, password: str):
    """
    爬取课程信息
    :param username: 学号
    :param password: 密码
    :return:
    """
    USER_DIR = os.path.join(DATA_DIR, username)
    # 如果用户目录存在，移除原有数据
    if os.path.exists(USER_DIR):
        shutil.rmtree(USER_DIR)
    os.mkdir(USER_DIR)
    # 执行爬虫的时候，当前程序会挂起
    spider.get_courses_info(username, password, USER_DIR)


# def grab_courses(username: str, password: str):
#     """
#     爬取课程信息
#     :param username: 学号
#     :param password: 密码
#     :return:
#     """
#     from WHUT.crawl import runserver
#     import shutil
#     USER_DIR = os.path.join(DATA_DIR, username)
#     # 如果用户目录存在，移除原有数据
#     if os.path.exists(USER_DIR):
#         shutil.rmtree(USER_DIR)
#     os.mkdir(USER_DIR)
#     # 执行爬虫的时候，当前程序会挂起
#     runserver(username, password, USER_DIR)
#     # if not grab_courses_successfully(USER_DIR):
#     #     runserver(username, password, USER_DIR)

