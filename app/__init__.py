#!/usr/bin/env python3
# coding=utf-8
# author: XiGuang Liu<g10guang@foxmail.com>
# 2017/11/12 11:31
# function: 

import os
import sys

# 如果在 pyinstaller 打包下运行， sys['frozen'] 会被置
# FRONZEN 用于判断是否在打包环境下运行
FROZEN = getattr(sys, 'frozen', False)

if FROZEN:
    # running on bundled app.
    BASE_DIR = os.path.abspath(os.getcwd())
else:
    # running in normal py env
    # 当前项目所在磁盘的绝对路径，如: F:\code\python\projects\data-manager-back-end
    BASE_DIR = os.path.abspath(os.path.join(__file__, os.pardir, os.pardir))

# assert 文件夹
ASSERT_DIR = os.path.abspath(os.path.join(BASE_DIR, 'assert'))

# data 文件夹，存放爬虫爬取的课程信息文件，文件结构如下：
# + data
#       + 学号
#           - whut_zy_lession.json
#           - whut_personal_lession.json
#           - whut_gx_lession.json
DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, 'data'))

# 如果 data 目录不存在，则创建该目录
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# json 数据文件命名

# 专业课
PROFESSIONAL_COURSES_JSON_FILE_NAME = 'whut_zy_lesson.json'

# 个性棵
PERSONAL_COURSES_JSON_FILE_NAME = 'whut_personal_lesson.json'

# 公选课
ELECTIVE_COURSES_JSON_FILE_NAME = 'whut_gx_lesson.json'

# "专业课" 名字
PROFESSIONAL_COURSES_SHOW_NAME = '专业课'

# "个性课" 名字
PERSONAL_COURSES_SHOW_NAME = '个性课'

# "公选课" 名字
ELECTIVE_COURSES_SHOW_NAME = '公选课'

# 登陆超时 message
LOGIN_TIMEOUT_MESSAGE = '登陆超时，请重新登陆！'

# 重复选课
DUPLICATE_COURSE_MESSAGE = '课程重复，不能选已选课程'

# 未到抢课时间
NOT_IN_SELECT_TIME_MESSAGE = '目前不在选课期间，不能选课'

# 抢课时间冲突
CONFLICT_IN_TIME_MESSAGE = '该课程与已选课程上课时间冲突'

# 学分达到上限
CAPPED_CREDIT_MESSAGE = '你所选的课程的课程性质已超出了限制的可选门数，不能选择此课程性质的课程！'

# 成功选课
GET_COURSE_SUCCESSFULLY_MESSAGE = '成功选课'

# 抢课反馈信息
SELECT_COURSE_MESSAGE = 'message'

# 抢课反馈码
SELECT_COURSE_STATUS_CODE = 'statusCode'

# 课程容量不足
NO_ENOUGH_POSITION = '该门课程容量不足，选课失败'

# 以下配置有关课程 json 文件中变量名的信息

# 课程名称
LESSON_NAME = 'lesson_name'

# 选课连接
LESSON_URL = 'lesson_url'

# 任课老师
TEACHER = 'teacher'

# 上课时间
TIME = 'time'

# 上课地点
CLASSROOM = 'classroom'

# 课程容量
CAPACITY = 'capacity'

# 已选人数
SELECTED = 'selected'

# 本轮已选
THIS_SELECTED = 'this_selected'

# 课程类型 推荐课程 or 跨专业选课
LESSON_TYPE = 'lesson_type'

# 学分
CREDIT = 'credit'

# 备注
REMARK = 'remark'

# 双语等级
LANG_LEVEL = 'lang_level'