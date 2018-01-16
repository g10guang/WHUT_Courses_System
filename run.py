#!/usr/bin/env python3
# coding=utf-8
# author: XiGuang Liu<g10guang@foxmail.com>
# 2017/11/13 9:52
# function:


if __name__ == '__main__':
    import multiprocessing
    # windows 开启多线程需要在最前面执行
    multiprocessing.freeze_support()

    manager = multiprocessing.Manager()

    # 创建用于进程间共享内存的 list
    courses = manager.list()

    from app import tasks

    # 复制 tasks.courses 引用，动态加入
    tasks.courses = courses

    #  创建进程，并启动进程
    p = multiprocessing.Process(target=tasks.start_process, args=(tasks.courses, ))
    p.start()

    from app.mainapp import MainApp

    app = MainApp()

    app.mainloop()
