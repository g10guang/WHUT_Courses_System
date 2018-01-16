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
    keep_request = True
    while keep_request:
        try:
            response = requests.post(url=JWC_LOGIN_URL, data=post_data, headers=headers)
        except requests.exceptions.ConnectionError as e:
            # 如果没有连接上教务处就继续请求，知道教务处能够被连接上
            # 尝试连接 baidu.com 如果不能够连接就判断无法连接网络，提醒用户连接网络
            try:
                baidu_response = requests.get(BAIDU_INDEX_URL)
            except requests.exceptions.ConnectionError as e:
                # 确实没有网络连接，假设 baidu.com 挂掉的可能性很低
                return 2
        else:
            # 如果没有发生异常就可以结束
            keep_request = False
        # 连接不上网站，不断尝试
    # 因为教务处登陆失败也是返回 200 状态码，但是能够通过cookie中是否有 CERLOGIN 来判断是否成功登陆
    if 'CERLOGIN' in response.cookies.keys():
        # 如果返回值中有该 cookie，则判断用户身份正确
        return 1
    else:
        return 0
