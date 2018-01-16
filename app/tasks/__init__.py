#!/usr/bin/env python3
# coding=utf-8
# author: XiGuang Liu<g10guang@foxmail.com>
# 2017/11/28 9:07
# function: 启动新进程/线程进行抢课处理
# 爬取课程信息使用多进程
# 抢课逻辑使用多线程

import threading

from app.spider.whut_add_lession_requests import start_request


# 用于压制
# python 'daemonic processes are not allowed to have children' AssertionError: daemonic processes are not allowed to have children
# 异常信息
# os.environ['PYTHONOPTIMIZE'] = '1'


def start_process(tasks):
    """
    开启子线程进行抢课逻辑， courses 为通信介质
    不停检测 courses 中是否有新任务加入
    :param get_course_func: 抢课的方法
    :param tasks: 格式
     [
        {'username': '', 'password': '', 'url': '', 'message': '未完成', 'is_new': True, 'describe': 'some thing to show'},
        {'username': '', 'password': '', 'url': '', 'message': '已完成', 'is_new': False, 'describe': 'some thing to show'},
     ]
    :return:
    """
    import time
    # 用于记录所有的在正在进行的线程
    jobs = []
    # 循环每隔一秒进行任务扫描
    while 1:
        for index, task in enumerate(tasks):
            # is_new 用于标志一个任务是否已经有一个线程正在执行
            if task['is_new']:
                print('进程发现新任务')
                t = threading.Thread(target=start_request, args=(task['username'], task['password'], task['url'], tasks))
                jobs.append(t)
                # 由于 manager.ADT 中只能够修改顶级的内容，不能够修改下级内容，所以这里需要整体替换对象，python系统设计原因
                task['is_new'] = False
                tasks[index] = task
                t.start()
        time.sleep(1)

# 已经把多进程迁移到 run.py 进行，因为 multiprocessing.freeze_support() 需要在最前面被执行

# 用于共享数据
# A manager object returned by Manager() controls a server process which holds Python objects and allows
# other processes to manipulate them using proxy.
# manager = multiprocessing.Manager()

# 创建用于进程间共享内存的 list
# courses = manager.list()


# #  创建进程，并启动进程
# p = multiprocessing.Process(target=start_process, args=(courses, ))
# p.start()


# 创建线程池
# pool = multiprocessing.Pool(1)
# pool.apply_async(func=start_process, args=(courses,))


def append_task_to_manager(username: str, password: str, url: str, describe: str):
    """
    添加抢课任务
    :return:
    """
    # 全局变量 courses，courses 在 run.py 中动态绑定，并没有在 task.__init__.py 代码中编码体现
    global courses
    new_task = {'username': username, 'password': password, 'url': url, 'message': '未完成', 'is_new': True, 'describe': describe}
    courses.append(new_task)
    return True
