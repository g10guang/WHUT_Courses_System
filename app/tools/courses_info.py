#!/usr/bin/env python3
# coding=utf-8
# author: XiGuang Liu<g10guang@foxmail.com>
# 2017/11/12 12:09
# function: 加载从教务处爬去下来的课程信息

import json
import os
from app import DATA_DIR, LESSON_NAME
from app import PROFESSIONAL_COURSES_JSON_FILE_NAME, ELECTIVE_COURSES_JSON_FILE_NAME, PERSONAL_COURSES_JSON_FILE_NAME, PROFESSIONAL_COURSES_SHOW_NAME, PERSONAL_COURSES_SHOW_NAME, ELECTIVE_COURSES_SHOW_NAME, EN_PT_COURSES_JSON_FILE_NAME, EN_PE_COURSES_SHOW_NAME
from app.tools import grab_courses

def remove_space(string):
    """
    清洗 lession_name 的 '\r\n\t ' 四种没用字符
    :param string:
    :return:
    """
    new = []
    empty_ch = {' ', '\t', '\n', '\r'}
    for ch in string:
        if ch not in empty_ch:
            new.append(ch)
    return ''.join(new)


def clean_lesson_name(courses):
    """
    清洗 lession_name 的 '\r\n\t ' 四种没用字符
    :param courses: 课程 list
    :return:
    """
    for k, v in courses.items():
        for item in v:
            item[LESSON_NAME] = remove_space(item[LESSON_NAME])


def load_courses_info(username, password):
    """
    每个人的专业课，重修选课，公选课选课，补修课选课，提前选课，跨专业选课，英语体育课选课不一致
    加载课程信息
    :param username: 学号
    :param password: 用户密码
    :return:
    """
    if username and password:
        user_dir = os.path.join(DATA_DIR, username)
        if not os.path.exists(user_dir):
            grab_courses.grab_courses(username, password)
        with open(os.path.join(user_dir, ELECTIVE_COURSES_JSON_FILE_NAME), encoding='utf-8') as f:
            elective_courses = json.load(f)
        with open(os.path.join(user_dir, PERSONAL_COURSES_JSON_FILE_NAME), encoding='utf-8') as f:
            personal_courses = json.load(f)
        with open(os.path.join(user_dir, PROFESSIONAL_COURSES_JSON_FILE_NAME), encoding='utf-8') as f:
            professional_courses = json.load(f)
        with open(os.path.join(user_dir, EN_PT_COURSES_JSON_FILE_NAME), encoding='utf-8') as f:
            en_pe_courses = json.load(f)
        courses = {ELECTIVE_COURSES_SHOW_NAME: elective_courses, PERSONAL_COURSES_SHOW_NAME: personal_courses, PROFESSIONAL_COURSES_SHOW_NAME: professional_courses, EN_PE_COURSES_SHOW_NAME: en_pe_courses}
        clean_lesson_name(courses)
        return courses
