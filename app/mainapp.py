#!/usr/bin/env python3
# coding=utf-8
# author: XiGuang Liu<g10guang@foxmail.com>
# 2017/11/12 11:32
# function: 使用 tkinter 渲染界面，这是渲染界面的全部代码

import os
import tkinter as tk
import tkinter.messagebox

from app import ASSERT_DIR, DATA_DIR, LESSON_TYPE
from app.tools.courses_info import load_courses_info
from app.spider import validate
from PIL import ImageTk, Image
from app import tasks
from app.tasks import append_task_to_manager
from app import LESSON_URL, LESSON_NAME, TEACHER, CLASSROOM, SELECTED, CAPACITY, CREDIT, LANG_LEVEL
import webbrowser

# 声明两个字体的使用
ARIAL_16_FONT = ('Arial', 16)
ARIAL_14_FONT = ('Arial', 14)


class MainApp(tk.Tk):
    """
    抢课软件主要界面
    """

    def __init__(self, screenName=None, baseName=None, className='Tk', useTk=1, sync=0, use=None, *args, **kwargs):
        super().__init__(screenName, baseName, className, useTk, sync, use)
        self.title('武汉理工抢课软件')

        # 用于装 Frames 的容器，container 并不是 self 属性
        container = tk.Frame(self)
        container.pack(side='top', fill='both', expand=True)
        # container 设置为一行一列，只有一个空格填充界面 tk.Frame
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # 记录用户 username password 信息用于抢课模拟登陆
        self.user_info = {}

        # 记录正在抢的课程
        self.courses_grabbing = {}

        # 该用户的课程信息
        self.courses_info = {}

        # 用于记录可以显示的有哪些 Frames
        self.frames = {}

        # 创建三个界面，并添加进 frames 中保存，分别是 登陆界面、选课页面、查看正在抢课的页面
        for F in (LoginPage, ChooseCoursePage, CheckTasksPage):
            page_name = F.__name__
            # 新建 Frame
            frame = F(container, self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky='nsew')
        # 软件启动显示登陆界面
        self.show_page(LoginPage.__name__)

    def show_page(self, page_name):
        """
        设置需要显示的页面
        :param page_name:
        :return:
        """
        # self.geometry() 为了适应子页面大小，重新重新缩放窗口
        if page_name == LoginPage.__name__:
            self.geometry('450x320')
        elif page_name == ChooseCoursePage.__name__:
            self.geometry('1000x700')
            # 刷新课程信息展示
            self.frames[page_name].refresh_listbox_info()
            # 清空用户选择项
            self.frames[page_name].empty_user_choice()
        elif page_name == CheckTasksPage.__name__:
            self.geometry('1100x700')
            self.frames[page_name].reload_manager_list()
        else:
            # 出现尚未定义处理的页面
            return
        # 将需要展示的页面置顶
        frame = self.frames[page_name]
        frame.tkraise()

    def reload_courses_info(self):
        """
        重新根据 username 加载课程信息
        :return:
        """
        self.courses_info = load_courses_info(self.user_info['username'], self.user_info['password'])
        if not self.courses_info:
            # TODO 用户还没输入用户名或者密码，需要提醒用户输入用户名或者密码
            pass


class LoginPage(tk.Frame):
    """
    登陆界面
    """

    def __init__(self, master, controller, **kw):
        super().__init__(master, **kw)
        self.controller = controller

        # 设置 UI 布局
        # 欢迎登录的画布
        canvas = tk.Canvas(self, height=200, width=500)
        # 需要给 image_file 加上引用 reference，否则 image_file 会被 GC 回收
        self.welcome_img = tk.PhotoImage(file=os.path.join(ASSERT_DIR, 'welcome.gif'))
        self.image = canvas.create_image(0, 0, anchor='nw', image=self.welcome_img)
        canvas.pack(side='top')

        # 记录用户名和密码
        self.username = tk.StringVar()
        self.password = tk.StringVar()

        tk.Label(self, text='username:', font=ARIAL_16_FONT).place(x=20, y=150)
        tk.Label(self, text='password:', font=ARIAL_16_FONT).place(x=20, y=190)

        tk.Entry(self, textvariable=self.username, font=ARIAL_16_FONT).place(x=135, y=155)
        self.psw_entry = tk.Entry(self, textvariable=self.password, show='*', font=ARIAL_16_FONT)
        self.psw_entry.place(x=135, y=190)

        # 是否显示密码
        self.is_showing_password = False

        # 重新显示密码
        # self.psw_entry.config(show='')

        # 用于判断是否需要重新获取课程信息
        self.is_regrab = tk.IntVar()
        tk.Checkbutton(self, text='获取课程信息', variable=self.is_regrab, font=ARIAL_16_FONT).place(x=130, y=220)
        # 用于判断是否验证用户账号和密码，因为如果网络环境不好，验证登陆可能失败
        self.is_validate = tk.IntVar()
        tk.Checkbutton(self, text='验证', variable=self.is_validate, font=ARIAL_16_FONT).place(x=320, y=220)

        def start_up():
            """
            用户点击开始
            需要让用户选择是否重新爬去课程信息
            :return:
            """
            # nonlocal 是因为函数闭包
            nonlocal self
            # 将目前用户的用户名和密码保存在顶级 TK 中
            self.controller.user_info['password'] = self.password.get()
            self.controller.user_info['username'] = self.username.get()
            if self.is_validate.get() or self.is_regrab.get():
                # 尝试登陆教务处，判断是否能够登陆成功
                # 验证学号和密码是否匹配，validate_user == 1 证明密码正确
                validate_user = validate.validate_user(self.controller.user_info['username'],
                                                  self.controller.user_info['password'])
                if validate_user == 0:
                    # 弹出提示框，用户名和密码不正确
                    tk.messagebox.showwarning(title='输入错误', message='用户名与密码不匹配')
                    return
                elif validate_user == 2:
                    # 弹出提示框，网络无法连接
                    tk.messagebox.showwarning(title='网络无法连接', message='尝试了连接\nbaidu.com\n也无法连接上，估计网络断了，请检查')
                    return
            # is_regrab.get() == 1 重新爬去课程信息，is_regrab.get() == 0 不重新爬去信息
            if self.is_regrab.get():
                tk.messagebox.showinfo(title='武汉理工抢课软件', message='爬取教务处课程信息可能需要几分钟\n'
                                                                 '在此期间可能软件会无响应，请不要关闭\n'
                                                                 '点击确认开始')
                from app.tools import grab_courses
                grab_courses.grab_courses(self.controller.user_info['username'], self.controller.user_info['password'])
            # 跳转好选课界面
            self.controller.reload_courses_info()
            # 用于记录当前用户抢课的信息
            if self.controller.user_info['username'] not in self.controller.courses_grabbing:
                self.controller.courses_grabbing[self.controller.user_info['username']] = {}
            self.controller.show_page(ChooseCoursePage.__name__)

        def more():
            """
            通过 webbrowser 调用浏览器打开连接，链接到 github.com 仓库 README.md
            :return:
            """
            webbrowser.open('https://github.com/g10guang/WHUT_Courses_System')

        def show_psw_btn_command():
            """
            让用户选择是否显示密码
            :return:
            """
            nonlocal self
            self.is_showing_password = not self.is_showing_password
            if self.is_showing_password:
                self.psw_entry.config(show='')
            else:
                self.psw_entry.config(show='*')

        tk.Button(self, text='More info', command=more, font=ARIAL_16_FONT).place(x=100, y=260)
        tk.Button(self, text='Start up', command=start_up, font=ARIAL_16_FONT).place(x=250, y=260)
        self.show_psw_img = ImageTk.PhotoImage(Image.open(os.path.join(ASSERT_DIR, 'show.png')))
        self.show_psw_btn = tk.Button(self, image=self.show_psw_img, command=show_psw_btn_command)
        self.show_psw_btn.place(x=390, y=195)


class ChooseCoursePage(tk.Frame):
    """
    查看课程以及选择抢哪些课程界面
    """

    def __init__(self, master, controller, **kw):
        super().__init__(master, **kw)
        self.controller = controller

        # 设置 UI 布局
        # 选择课程并进行抢课的页面
        self.l1_selection = tk.StringVar()
        # 设置下拉单
        self.l1_selection.set([k for k in self.controller.courses_info.keys()])

        self.lb1 = tk.Listbox(self, listvariable=self.l1_selection, height=25, width=30, font=ARIAL_14_FONT)
        self.lb1.place(x=10, y=40)

        self.l2_selection = tk.StringVar()

        self.lb2 = tk.Listbox(self, listvariable=self.l2_selection, height=25, width=100, font=ARIAL_14_FONT)
        self.lb2.place(x=150, y=40)

        self.l3_selection = tk.StringVar()

        self.lb3 = tk.Listbox(self, listvariable=self.l3_selection, height=25, width=100, font=ARIAL_14_FONT)
        self.lb3.place(x=450, y=40)

        # 用户第一级选择
        self.current_1_choice = None
        # 用户第二季选择
        self.current_2_choice = None

        def join_course_info(item: dict):
            """
            将课程的信息拼在一起
            :return:
            """
            # 需要展示的信息
            info = [item[TEACHER], item[LESSON_TYPE], '学分：{}'.format(item[CREDIT]),
                    '容量：{}'.format(item[CAPACITY]), '已选：{}'.format(item[SELECTED])]
            return '  '.join(info)

        def grab_course():
            """
            抢课响应事件
            :return:
            """
            nonlocal self
            index = self.lb3.curselection()
            if not index:
                # 用户没有做选择，提醒用户选择
                tk.messagebox.showinfo(title='武汉理工抢课软件', message='请选择需要的课程')
                return
            user_choice = self.lb3.get(index)
            # 取消用户重复选同一门课的选择
            # # 判断该课程是否已经被当前账号抢
            # if user_choice in self.controller.courses_grabbing[self.controller.user_info['username']]:
            #     # 该课程已经在抢，避免用户重复
            #     tk.messagebox.showinfo(title='冲突', message='该课程已经加入了抢课队列，请不要重复抢同一门课')
            #     return
            # 判断用户选择的是哪一门课程
            for item in self.controller.courses_info[self.current_1_choice]:
                if item[LESSON_NAME] == self.current_2_choice:
                    if join_course_info(item) == user_choice:
                        # 提示用户发起了抢课
                        self.controller.courses_grabbing[user_choice] = item[LESSON_URL]
                        tk.messagebox.showinfo(title='发起抢课通知', message='正在抢：{}'.format(user_choice))
                        append_task_to_manager(self.controller.user_info['username'], self.controller.user_info['password'], item[LESSON_URL], self.current_2_choice + ' ' + user_choice)

        def back2login():
            """
            返回登陆界面
            :return:
            """
            nonlocal self
            self.empty_user_choice()
            self.controller.show_page(LoginPage.__name__)

        btn_back2login = tk.Button(self, text='返回', command=back2login)
        btn_back2login.place(x=10, y=5)

        btn_grab = tk.Button(self, text='发起抢课', command=grab_course)
        btn_grab.place(x=450, y=5)

        def check_tasks_list():
            """
            检查任务列表
            :return:
            """
            self.controller.show_page(CheckTasksPage.__name__)

        def select1(evt):
            """
            用户点击第一级 Listbox 的 item 的响应事件
            :param evt:
            :return:
            """
            # 声明使用全局变量 current_1_choice
            # 取出用户选择的选项名，比如 "专业选课"
            nonlocal self
            w = evt.widget
            index = w.curselection()
            if not index:
                return
            user_choice = w.get(index)
            self.current_1_choice = user_choice
            # 这里使用 set() 是为了避免重复，因为数据中存在课程名称冲突的地方，比如同一门课程不同老师或者时间开了好几门
            courses_list = {item[LESSON_NAME] for item in self.controller.courses_info[user_choice]}
            courses_list = list(courses_list)
            # 设置相应的数据到第二列
            self.l2_selection.set(courses_list)
            # 置空第三列
            self.l3_selection.set(())

        def select2(evt):
            """
            用户点击第二级 Listbox 的 item 的响应事件
            :param evt:
            :return:
            """
            nonlocal self
            # 去除 Listbox 引用
            w = evt.widget
            # 获取当前选中的位置
            index = w.curselection()
            if not index:
                return
            user_choice = w.get(index)
            # 根据当前选中的位置来获取当前 item 的 value 名称，如专业选课
            # 声明使用 current_1_choice current_2_choice 全局变量
            if not self.current_1_choice:
                return
            courses_list = self.controller.courses_info[self.current_1_choice]
            self.current_2_choice = user_choice
            courses_to_show = [join_course_info(item) for item in courses_list if item['lesson_name'] == user_choice]
            self.l3_selection.set(courses_to_show)

        # 注册事件监听器
        self.lb1.bind('<<ListboxSelect>>', select1)
        self.lb2.bind('<<ListboxSelect>>', select2)
        btn_check_tasks_list = tk.Button(self, text='查看任务列表', command=check_tasks_list)
        btn_check_tasks_list.place(x=900, y=650)

    def refresh_listbox_info(self):
        """
        清空 listbox2/3 数据，重新展示 listbox1 数据
        :return:
        """
        self.l1_selection.set([k for k in self.controller.courses_info.keys()])
        self.l2_selection.set(())
        self.l3_selection.set(())

    def empty_user_choice(self):
        """
        清空用户选择
        :return:
        """
        self.current_1_choice, self.current_2_choice = None, None


class CheckTasksPage(tk.Frame):
    """
    用于查看任务列表的窗口
    """

    def __init__(self, master, controller, **kw):
        super().__init__(master, **kw)
        self.controller = controller

        self.tasks_list = tk.StringVar()

        self.content_box = tk.Listbox(self, listvariable=self.tasks_list, height=25, width=100, font=ARIAL_14_FONT)
        self.content_box.place(x=10, y=40)

        def back_to_choose_page():
            """
            返回到选课页面
            :return:
            """
            self.controller.show_page(ChooseCoursePage.__name__)

        self.btn_back_to_choose_page = tk.Button(self, text='返回', command=back_to_choose_page)
        self.btn_back_to_choose_page.place(x=10, y=5)

    def reload_manager_list(self):
        """
        重新加载任务列表
        :return:
        """
        self.tasks_list.set(['{} 状态：{}'.format(t['describe'], t['message']) for t in tasks.courses])

