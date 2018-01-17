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
from app.spider import JWC_LOGIN_URL, headers, COURSE_SYSTEM_URL, PROFESSIONAL_COURSE_MSG, PUBLIC_COURSE_MSG, PERSONAL_COURSE_MSG, BEAUTIFUL_SOUP_PARSE_METHOD, PROFESSIONAL_COURSE_TABLE_ID, PUBLIC_COURSE_TABLE_ID, PERSONAL_COURSE_TABLE_ID
from app import PROFESSIONAL_COURSES_JSON_FILE_NAME, PERSONAL_COURSES_JSON_FILE_NAME, ELECTIVE_COURSES_JSON_FILE_NAME
from app import LESSON_NAME, LESSON_URL, TEACHER, TIME, CLASSROOM, CAPACITY, SELECTED, THIS_SELECTED, LESSON_TYPE, CREDIT, REMARK, LANG_LEVEL


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

    # 单线程版本
    # return_value = parse_professional_courses(url_dict[PROFESSIONAL_COURSE_MSG], sess)
    # professional_courses = return_value
    # public_courses = parse_courses(url_dict[PUBLIC_COURSE_MSG], sess)
    # personal_courses = parse_courses(url_dict[PERSONAL_COURSE_MSG], sess)
    # write_json_to_file(professional_courses, os.path.join(user_folder, PROFESSIONAL_COURSES_JSON_FILE_NAME))
    # write_json_to_file(public_courses, os.path.join(user_folder, ELECTIVE_COURSES_JSON_FILE_NAME))
    # write_json_to_file(personal_courses, os.path.join(user_folder, PERSONAL_COURSES_JSON_FILE_NAME))

    # 多线程版本
    t1 = threading.Thread(target=thread_task, args=(parse_professional_courses, sess, os.path.join(user_folder, PROFESSIONAL_COURSES_JSON_FILE_NAME), url_dict[PROFESSIONAL_COURSE_MSG]))

    t2 = threading.Thread(target=thread_task, args=(parse_courses, sess, os.path.join(user_folder, ELECTIVE_COURSES_JSON_FILE_NAME), url_dict[PUBLIC_COURSE_MSG]))

    t3 = threading.Thread(target=thread_task, args=(parse_courses, sess, os.path.join(user_folder, PERSONAL_COURSES_JSON_FILE_NAME), url_dict[PERSONAL_COURSE_MSG]))

    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()


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
    public_courses_url = get_public_courses_info(soup)
    professional_courses_url = get_professional_courses_info(soup)
    personal_coures_url = get_personal_courses_info(soup)
    return_data = {
        PUBLIC_COURSE_MSG: public_courses_url,
        PROFESSIONAL_COURSE_MSG: professional_courses_url,
        PERSONAL_COURSE_MSG: personal_coures_url,
    }
    return return_data


def get_public_courses_info(soup):
    """
    获取公选课信息
    :param soup: 解析选课首页的 BeautifulSoup 对象
    :return:
    """
    href_url = soup.find(text=PUBLIC_COURSE_MSG).parent['href']
    return '{}/{}'.format(COURSE_SYSTEM_URL, href_url)


def get_professional_courses_info(soup):
    """
    获取专业课信息
    :param soup: 解析选课首页的 BeautifulSoup 对象
    :return:
    """
    href_url = soup.find(text=PROFESSIONAL_COURSE_MSG).parent['href']
    return '{}/{}'.format(COURSE_SYSTEM_URL, href_url)


def get_personal_courses_info(soup):
    """
    获取个性棵信息
    :param soup: 解析选课首页的 BeautifulSoup 对象
    :return:
    """
    href_url = soup.find(text=PERSONAL_COURSE_MSG).parent['href']
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
        lesson_info = parse_method(tmp_soup, table_id)
        courses_info.extend(lesson_info)
    return courses_info


def get_professional_courses_info_from_table(soup, table_id):
    """
    由于专业课选课界面与其他课程选课不一样，专业课选课会有起始周信息，而其他没有
    课程信息存储在表格中，该方法提供从表格中获取数据的接口，这是一个通用的方法
    :param soup: 抓取特定课程页面解析后的 BeautifulSoup 对象
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
            td_list = tr.find_all('td')
            # 依次提取：课程名称、上课老师、上课时间、上课地点、起止周、容量、选上、本轮已选、选课方式、学分、备注、双语等级
            tmp_dict = dict()
            # 选课链接
            tmp_dict[LESSON_URL] = '{}/{}'.format(COURSE_SYSTEM_URL, add_url.format(suid_obj=tr['rel']))
            # 课程名称
            tmp_dict[LESSON_NAME] = td_list[1].find('a').string
            # 老师
            tmp_dict[TEACHER] = td_list[2].find('a').string
            # 上课时间
            tmp_dict[TIME] = td_list[3].string
            # 上课地点
            tmp_dict[CLASSROOM] = td_list[4].string
            # 起始周
            # tmp_dict['period'] = td_list[5].string
            # 课程容量
            tmp_dict[CAPACITY] = td_list[6].string
            # 已选上
            tmp_dict[SELECTED] = td_list[7].string
            # 本轮已选
            tmp_dict[THIS_SELECTED] = td_list[8].string
            # 选课方式 推荐课程 or 跨专业选课
            tmp_dict[LESSON_TYPE] = td_list[9].string
            # 学分
            tmp_dict[CREDIT] = td_list[10].string
            # 备注
            tmp_dict[REMARK] = td_list[11].string
            # 双语等级
            a_tag = td_list[12].find('a')
            if a_tag:
                tmp_dict[LANG_LEVEL] = a_tag.string
            else:
                tmp_dict[LANG_LEVEL] = td_list[12].string.strip()
            course_info.append(tmp_dict)
    return course_info


def get_courses_info_from_table(soup, table_id):
    """
    由于专业课选课界面与其他课程选课不一样，专业课选课会有起始周信息，而其他没有
    :param table:
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
            td_list = tr.find_all('td')
            # 依次提取：课程名称、上课老师、上课时间、上课地点、起止周、容量、选上、本轮已选、选课方式、学分、备注、双语等级
            tmp_dict = dict()
            # 选课链接
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
            course_info.append(tmp_dict)
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
