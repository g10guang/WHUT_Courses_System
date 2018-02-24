#!/usr/bin/env python3
# coding=utf-8
# author: XiGuang Liu<g10guang@foxmail.com>
# 2017/11/28 15:12
# function: 

import requests

from app.spider import headers
from app.spider import JWC_LOGIN_URL, BAIDU_INDEX_URL


def validate_user(account, password):
    """
    验证用户身份，尝试登陆教务处，判断身份是否正确
    :param account:
    :param password:
    :return:
    0 ==> 用户名与密码不匹配
    1 ==> 用户与密码匹配
    2 ==> 无法连接网络
    """
    post_data = {
        "systemId": "",
        "xmlmsg": "",
        "userName": account,
        "password": password,
        "type": "xs",
    }
    while 1:
        try:
            response = requests.post(url=JWC_LOGIN_URL, data=post_data, headers=headers)
            # 教务处登陆失败也是返回 200 状态码，通过cookie中是否有 CERLOGIN 来判断是否成功登陆
            if 'CERLOGIN' in response.cookies.keys():
                return 1
            return 0
        except requests.exceptions.ConnectionError:
            try:
                # 尝试连接 baidu.com 如果不能够连接就判断无法连接网络
                _baidu_response = requests.get(BAIDU_INDEX_URL)
            except requests.exceptions.ConnectionError:
                return 2
