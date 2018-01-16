#!/usr/bin/env python3
# coding=utf-8
# author: XiGuang Liu<g10guang@foxmail.com>
# 2017/11/12 12:41
# function: 

User_Agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'


# 用于模拟 http 请求的头
headers = {
    'User-Agent': User_Agent
}


# 教务处提交登陆信息网址 post login
JWC_LOGIN_URL = 'http://sso.jwc.whut.edu.cn/Certification/login.do'

# 选课系统地址
COURSE_SYSTEM_URL = 'http://202.114.90.180/Course'

# 忘记密码
FORGET_PSW_MSG = '忘记密码'

# 以下选项用于 BeautifulSoup 做解析处理

# 专业选课
PROFESSIONAL_COURSE_MSG = '专业选课'

# 公选课
PUBLIC_COURSE_MSG = '公选课选课'

# 个性课程选课
PERSONAL_COURSE_MSG = '个性课程选课'

# BeautifulSoup 的解析方法
BEAUTIFUL_SOUP_PARSE_METHOD = 'lxml'

# 专业课 table_id
PROFESSIONAL_COURSE_TABLE_ID = 'zykxk_wxkc_tb'

# 公选课 table_id
PUBLIC_COURSE_TABLE_ID = 'gxkxk_wxkc_tb'

# 个性棵 table_id
PERSONAL_COURSE_TABLE_ID = 'gxkxk_wxkc_tb'

# 百度首页
BAIDU_INDEX_URL = 'https://baidu.com'

