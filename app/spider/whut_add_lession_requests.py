# -*- coding: utf-8 -*-
# @Author  : Chunguang Li
# @Mail : 1192126986@foxmail.com
# @Time : 2017/11/24 14:00

import json
import threading

import requests

from app import LOGIN_TIMEOUT_MESSAGE, DUPLICATE_COURSE_MESSAGE, NOT_IN_SELECT_TIME_MESSAGE, CONFLICT_IN_TIME_MESSAGE, CAPPED_CREDIT_MESSAGE, NO_ENOUGH_POSITION
from app import SELECT_COURSE_MESSAGE

from app.spider import headers, JWC_LOGIN_URL, COURSE_SYSTEM_URL

local_thread = threading.local()


def request_index(account, password):
    """
    请求教务系统首页，保存首页的cookie
    模拟登陆
    :param account:
    :param password:
    :return:
    """
    post_data = {
        "systemId": "",
        "xmlmsg": "",
        "userName": account,
        "password": password,
        "type": "xs",
        # 教务处改变了登陆页面，原来 input button 有下面两项
        # "imageField.x": "20",
        # "imageField.y": "20"
    }
    response = requests.post(url=JWC_LOGIN_URL, data=post_data, headers=headers)
    if 'CERLOGIN' in response.cookies.keys():
        for name, value in response.cookies.items():
            local_thread.index_cookie[name] = value
        return 'success login'

    print('账号或者密码错误')
    return '账号或者密码错误'


def request_courses():
    """
    请求课程页，保存课程页cookie
    因为抢课在别的站点进行，这里教务处有一套多次重定向机制来同步教务处站点 sso.jwc.whut.edu.cn 与 202.114.90.180/Course/ 站点登陆状态
    :return:
    """
    # course_url = 'http://202.114.90.180/Course/'
    response = requests.get(url=COURSE_SYSTEM_URL, cookies=local_thread.index_cookie, headers=headers, allow_redirects=True)
    if 'CERLOGIN' in response.request._cookies.keys():
        local_thread.course_cookie['JSESSIONID'] = response.request._cookies.values()[2]
    else:
        print('登录超时')
        return '登录超时'


def request_add_lesson(add_lession_url):
    """
    请求添加课程
    :return:
    返回是否抢课成功
    -1 ==> 遇到未知情况，通常是教务处改版
    0 ==> 抢课成功
    1 ==> 登陆超时，重新登陆
    2 ==> 未到抢课时间
    3 ==> 重复选课
    4 ==> 连接不上
    5 ==> 选课时间冲突
    6 ==> 达到学分上限
    7 ==> 课程容量不足
    """
    # tag = False
    # if tag:
    #     # 模拟退出登录状态，也就是登录超时
    #     _r = requests.get(url='http://202.114.90.180/Course/logout.do', cookies=local_thread.course_cookie, headers=headers)
    try:
        response = requests.get(url=add_lession_url, cookies=local_thread.course_cookie, headers=headers)
    except requests.exceptions.ConnectionError:
        return 4
    try:
        response_data = json.loads(response.text)
        response_message = response_data.get(SELECT_COURSE_MESSAGE)
        if response_message == LOGIN_TIMEOUT_MESSAGE:
            # 登陆超时
            return 1
        elif response_message == NOT_IN_SELECT_TIME_MESSAGE:
            # 未到选课时间
            return 2
        elif response_message == DUPLICATE_COURSE_MESSAGE:
            # 重复选课
            return 3
        elif response_message == CONFLICT_IN_TIME_MESSAGE:
            # 选课时间冲突
            return 5
        elif response_message == CAPPED_CREDIT_MESSAGE:
            # 你所选的课程的课程性质已超出了限制的可选门数，不能选择此课程性质的课程！
            return 6
        elif response_message == NO_ENOUGH_POSITION:
            # 课程容量不足
            return 7
        return -1
    except json.decoder.JSONDecodeError:
        # 在成功选课的时候返回一个 JSONP，是 (js/css/html) 的集合体，不是 json 对象无法解析
        return 0


def start_request(username, password, lesson_url, tasks):
    # 教务处网站的 cookie
    local_thread.index_cookie = {}
    # 选课网站的 cookie
    local_thread.course_cookie = {}
    # 默认初始状态为 1, 为登陆超时，需要重新登陆操作
    status = 1
    while 1:
        if status in (0, 3, 5, 6):
            # 0:成功 3:重复选课 5:时间冲突 6:学分上限
            # 4:在连接不上、1:登陆超时、2:尚未开始抢课，需要继续不断重复循环
            break
        # 还没有获得登陆状态，在登陆超时、未连接上服务器情况下需要重新模拟登陆
        # 其他状态不需要重新模拟登陆
        elif status in (1, 4, -1):
            try:
                request_index(username, password)
                request_courses()
            except requests.exceptions.ConnectionError:
                pass
        status = request_add_lesson(lesson_url)
    # 更新状态是当前线程的最后一步
    call_back_update_manager(username, lesson_url, tasks, status)


def call_back_update_manager(username, lesson_url, tasks, status):
    """
    回调更新 manager 的 courses 信息，更新为已完成任务
    :return:
    """
    for index, item in enumerate(tasks):
        # 同一个用户的用一个课程 url
        if item['username'] == username and item['url'] == lesson_url:
            if status == 0:
                item['message'] = '已完成'
            elif status == 5:
                item['message'] = '失败，选课时间冲突'
            elif status == 6:
                item['message'] = '失败，课程性质已超出了限制的可选门数'
            elif status == 3:
                item['message'] = '重复选课'
            # elif status == 2:
            #     item['message'] = '未到选课时间'
            tasks[index] = item
    return True
