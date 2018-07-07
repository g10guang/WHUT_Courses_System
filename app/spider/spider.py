#!/usr/bin/env python3
# coding=utf-8
# author: XiGuang Liu<g10guang@foxmail.com>
# 2018/1/16 2:16
# function: 使用 requests 和 BeautifulSoup 组合获取教务处网站的课程信息
# 以下操作默认在用户名和密码正确前提下进行

import requests
from bs4 import BeautifulSoup
import json
import os
import threading
import re
from urllib import parse
from app.spider import JWC_LOGIN_URL, headers, COURSE_SYSTEM_URL, PROFESSIONAL_COURSE_MSG, PUBLIC_COURSE_MSG, PERSONAL_COURSE_MSG, BEAUTIFUL_SOUP_PARSE_METHOD, PROFESSIONAL_COURSE_TABLE_ID, PUBLIC_COURSE_TABLE_ID, PERSONAL_COURSE_TABLE_ID, EN_PE_COURSE_MSG, GET_MORE_ITEM_URL
from app import PROFESSIONAL_COURSES_JSON_FILE_NAME, PERSONAL_COURSES_JSON_FILE_NAME, ELECTIVE_COURSES_JSON_FILE_NAME, EN_PT_COURSES_JSON_FILE_NAME
from app import LESSON_NAME, LESSON_URL, TEACHER, TIME, CLASSROOM, CAPACITY, SELECTED, THIS_SELECTED, LESSON_TYPE, CREDIT, REMARK, LANG_LEVEL


PAGE_MSG_RE_PATTERN = re.compile(r'条，共(\d+)条')


def get_courses_info(username, password, user_folder):
    """
    获取课程信息
    :param username: 用户名
    :param password: 密码
    :param user_folder: 用于保存用户数据的目录
    :return:
    """
    sess = requests.Session()
    # 登陆教务处，将会拿到 cookie
    login_jwc(username, password, sess)
    # 继续登陆选课系统
    index_html = login_course_system(sess)
    url_dict = get_course_url(index_html)

    # 多线程版本
    t1 = threading.Thread(target=thread_task, args=(parse_professional_courses, sess, os.path.join(user_folder, PROFESSIONAL_COURSES_JSON_FILE_NAME), url_dict[PROFESSIONAL_COURSE_MSG]))

    t2 = threading.Thread(target=thread_task, args=(parse_courses, sess, os.path.join(user_folder, ELECTIVE_COURSES_JSON_FILE_NAME), url_dict[PUBLIC_COURSE_MSG]))

    t3 = threading.Thread(target=thread_task, args=(parse_courses, sess, os.path.join(user_folder, PERSONAL_COURSES_JSON_FILE_NAME), url_dict[PERSONAL_COURSE_MSG]))

    t4 = threading.Thread(target=thread_task, args=(parse_courses, sess, os.path.join(user_folder, EN_PT_COURSES_JSON_FILE_NAME), url_dict[EN_PE_COURSE_MSG]))

    t1.start()
    t2.start()
    t3.start()
    t4.start()

    t1.join()
    t2.join()
    t3.join()
    t4.join()


def thread_task(parse_func, sess, file_path, urls):
    """
    线程下载任务
    :param parse_func:
    :param sess:
    :param file_path:
    :param urls:
    :return:
    """
    course_info = parse_func(urls, sess)
    write_json_to_file(course_info, file_path)


def login_jwc(username, password, sess):
    """
    登陆教务处
    :param username: 用户名
    :param password: 密码
    :param sess: Session 会话
    :return:
    """
    login_form = {
        "systemId": "",
        "xmlmsg": "",
        "userName": username,
        "password": password,
        "type": "xs",
    }
    # 登陆教务处，将会拿到 cookie
    rspo = sess.post(JWC_LOGIN_URL, data=login_form, headers=headers)


def login_course_system(sess):
    """
    登陆选课系统，登陆选课系统是通过同步教务处登陆状态达到的
    :param sess: Session 会话
    :return: 返回选课系统的首页 html 用于后续 BeautifulSoup 做分析
    """
    # 将会被多次重定向，从而达到登陆状态
    rspo = sess.get(COURSE_SYSTEM_URL, headers=headers, allow_redirects=True)
    return rspo.text


def get_course_url(html):
    """
    通过 html 来获取各个获取课程信息的连接
    :param html: 选课系统首页的 html
    :return:
    """
    soup = BeautifulSoup(html, BEAUTIFUL_SOUP_PARSE_METHOD)
    categories = (PUBLIC_COURSE_MSG, PROFESSIONAL_COURSE_MSG, PERSONAL_COURSE_MSG, EN_PE_COURSE_MSG)
    return_data = {}
    for c in categories:
        return_data[c] = get_category_url(c, soup)
    return return_data


def get_category_url(category: str, soup):
    """
    获取课程种别对应的 url，比如"专业选课", "公选课选课", "个性课程选课", "英语体育课选课"
    :param category: 类别名称
    :param soup: 解析选课首页的 BeautifulSoup 对象
    :return:
    """
    href_url = soup.find(text=category).parent['href']
    return '{}/{}'.format(COURSE_SYSTEM_URL, href_url)


def parse_professional_courses(url, sess):
    """
    爬取专业课信息，因为专业课与【公选课、个性棵、英语、体育】等有差别，专业课没有文件夹展开分类
    :param sess: 以及获得教务处系统和选课系统登陆状态的 Session 会话
    :param url: 获取专业课信息的 url
    :return:
    """
    rspo = sess.get(url, headers=headers)
    soup = BeautifulSoup(rspo.text, BEAUTIFUL_SOUP_PARSE_METHOD)
    # 各个课程信息的父节点
    tree_folder = soup.find('ul', class_='tree treeFolder')
    # courses_info = []
    courses_url = []
    for li_tag in tree_folder.children:
        a_tag = li_tag.find('a')
        # 因为html没有经过压缩，有大量 '\n' 换行符存在，-1 就是防止 '\n'
        if a_tag != -1:
            # 暂存课程链接
            courses_url.append('{}/{}'.format(COURSE_SYSTEM_URL, a_tag['href']))
    courses_info = access_url_and_extract_courses_info(courses_url, sess, PROFESSIONAL_COURSE_TABLE_ID, get_professional_courses_info_from_table)
    return courses_info


def parse_courses(url, sess):
    """
    解析除了专业课意外的其他课程，比如 公选课、个性课
    这类课程的信息多了一层文件夹展开树
    :param url:
    :param sess:
    :return:
    """
    repo = sess.get(url, headers=headers)
    soup = BeautifulSoup(repo.text, BEAUTIFUL_SOUP_PARSE_METHOD)
    # 找到展示树
    tree_folder = soup.find('ul', class_='tree treeFolder')
    courses_url = []
    # 作为树形展开那一层
    # 获取该类课程的所有链接
    folder_li_list = tree_folder.find_all('li', recursive=False)
    for folder_li in folder_li_list:
        ul = folder_li.find('ul')
        course_li_list = ul.find_all('li', False)
        for course_li in course_li_list:
            courses_url.append('{}/{}'.format(COURSE_SYSTEM_URL, course_li.find('a')['href']))
    courses_info = access_url_and_extract_courses_info(courses_url, sess, PUBLIC_COURSE_TABLE_ID, get_courses_info_from_table)
    return courses_info


def access_url_and_extract_courses_info(courses_url, sess, table_id, parse_method):
    """
    通过 courses_url 链表来获取 url，通过 sess 访问得到 html，然后提取各个课程信息
    :param parse_method: 解析课程表格的方法，因为专业课选课与其他选课的表格不一致
    :param courses_url:
    :param sess:
    :param table_id: 这个 table_id 用来通过 css 选择器来筛选课程，但是 table_id 在专业课和公选课、个性棵下不一样
    :return:
    """
    courses_info = []
    for url in courses_url:
        tmp_resp = sess.get(url, headers=headers)
        tmp_soup = BeautifulSoup(tmp_resp.text, BEAUTIFUL_SOUP_PARSE_METHOD)
        lesson_info = parse_method(tmp_soup, table_id, sess)
        courses_info.extend(lesson_info)
    return courses_info


def get_professional_courses_info_from_table(soup, table_id, sess):
    """
    由于专业课选课界面与其他课程选课不一样，专业课选课会有起始周信息，而其他没有
    课程信息存储在表格中，该方法提供从表格中获取数据的接口，这是一个通用的方法
    :param soup: 抓取特定课程页面解析后的 BeautifulSoup 对象
    :param sess: request.Session 会话对象
    :return:
    """
    # 解析 "添加" 按钮中的 url
    add_btn = soup.find('a', class_='add', target='ajax')
    add_url = add_btn['href']
    table = soup.find('table', id=table_id)
    tbody = table.find('tbody')
    tr_list = tbody.find_all('tr')
    course_info = []
    # 判断是否有课程信息
    if tr_list:
        for tr in tr_list:
            course_info.append(add_tmp_dict(tr, True))
    return course_info


def add_tmp_dict(tr, professional=False):
    """professional是否是专业课"""
    td_list = tr.find_all('td')
    if professional:
        # 干掉专业课的起始周
        # tmp_dict['period'] = td_list[5].string
        td_list.pop(5)

    tmp_dict = {}
    tmp_dict[LESSON_URL] = '{}/{}'.format(COURSE_SYSTEM_URL, add_url.format(suid_obj=tr['rel']))
    # 课程名称
    tmp_dict[LESSON_NAME] = td_list[1].find('a').string
    # 老师
    tmp_dict[TEACHER] = td_list[2].find('a').string
    # 上课时间
    tmp_dict[TIME] = td_list[3].string
    # 上课地点
    tmp_dict[CLASSROOM] = td_list[4].string
    # 课程容量
    tmp_dict[CAPACITY] = td_list[5].string
    # 已选上
    tmp_dict[SELECTED] = td_list[6].string
    # 本轮已选
    tmp_dict[THIS_SELECTED] = td_list[7].string
    # 选课方式 推荐课程 or 跨专业选课
    tmp_dict[LESSON_TYPE] = td_list[8].string
    # 学分
    tmp_dict[CREDIT] = td_list[9].string
    # 备注
    tmp_dict[REMARK] = td_list[10].string
    # 双语等级
    a_tag = td_list[11].find('a')
    if a_tag:
        tmp_dict[LANG_LEVEL] = a_tag.string
    else:
        tmp_dict[LANG_LEVEL] = td_list[11].string.strip()
    return tmp_dict


def get_courses_info_from_table(soup, table_id, sess):
    """
    由于专业课选课界面与其他课程选课不一样，专业课选课会有起始周信息，而其他没有
    :param soup:
    :param table_id: 用于在 html 定位 table
    :param sess: requests.Session 会话
    :return:
    """
    course_info = []
    # 解析 "添加" 按钮中的 url
    add_btn = soup.find('a', class_='add', target='ajax')
    # 如：gxkxkAdd.do?xnxq=2017-2018-2&kcdm=4210085150&jxjhh=2015&addid={suid_obj}&gsdm=&keyinfo=15EFCA92D914E5ECB4094F7F30E96155
    add_url = add_btn['href']
    # 首先分析该页是否已经包含了第一页到最后一页的数据，这里是为了避免分页造成的需要多次爬取同一个课程的多门课信息
    page_msg = soup.find(text=PAGE_MSG_RE_PATTERN)
    # 获取到底有多少门课程信息
    item_num = int(PAGE_MSG_RE_PATTERN.search(page_msg)[1])
    if item_num >= 10:
        parse_result = parse.urlparse(add_url)
        # 解析 add_url 中的参数
        url_params = parse.parse_qs(parse_result.query)
        data = {}
        data['gsdm'] = url_params.get('gsdm', [''])[0]
        data['jxjhh'] = url_params.get('jxjhh')[0]
        data['kcdm'] = url_params.get('kcdm')[0]
        data['xnxq'] = url_params.get('xnxq')[0]
        data['numPerPage'] = item_num
        data['orderDirection'] = 'asc'
        data['orderField'] = 'jsxm,sksj'
        data['pageNum'] = '1'
        data['temp'] = 'true'
        # 在"个性课程选课" flag=1
        # 在"英语体育课选课" flag=2
        # 这里暂且不考虑 个性课
        data['flag'] = '2'
        rspo = sess.post(GET_MORE_ITEM_URL, headers=headers, data=data)
        soup = BeautifulSoup(rspo.text, BEAUTIFUL_SOUP_PARSE_METHOD)
    elif item_num == 0:
        # 没有任何条目可以爬取，可以直接返回
        return course_info
    table = soup.find('table', id=table_id)
    tbody = table.find('tbody')
    tr_list = tbody.find_all('tr')
    # 判断是否有课程信息
    if tr_list:
        for tr in tr_list:
            course_info.append(add_tmp_dict(tr))
    return course_info


def write_json_to_file(courses_info, file_path):
    """
    将课程信息写到文件中
    :param courses_info: 课程信息
    :param file_path: 写入的文件
    :return:
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(courses_info, f)
