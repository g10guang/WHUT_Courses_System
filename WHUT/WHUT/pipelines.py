# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json

from scrapy.exporters import JsonItemExporter

import os


class WhutPipeline(object):
    def process_item(self, item, spider):
        return item


class JsonExporterPipleline(object):
    def __init__(self, folder):
        if not os.path.exists(folder):
            os.mkdir(folder)
        # 公选课文件
        self.gx_file = open('{}/whut_gx_lession.json'.format(folder), 'wb')
        self.gx_exporter = JsonItemExporter(self.gx_file, encoding='utf-8', ensure_ascii=False)
        self.gx_exporter.start_exporting()

        # 个性课文件
        self.personal_file = open('{}/whut_personal_lession.json'.format(folder), 'wb')
        self.personal_exporter = JsonItemExporter(self.personal_file, encoding='utf-8', ensure_ascii=False)
        self.personal_exporter.start_exporting()

        # 专业课文件
        self.zy_file = open('{}/whut_zy_lession.json'.format(folder), 'wb')
        self.zy_exporter = JsonItemExporter(self.zy_file, encoding='utf-8', ensure_ascii=False)
        self.zy_exporter.start_exporting()

        # 其他课文件
        self.wk_file = open('{}/whut_wk_lession.json'.format(folder), 'wb')
        self.wk_exporter = JsonItemExporter(self.wk_file, encoding='utf-8', ensure_ascii=False)
        self.wk_exporter.start_exporting()

    def close_spider(self, spider):
        self.wk_exporter.finish_exporting()
        self.zy_exporter.finish_exporting()
        self.personal_exporter.finish_exporting()
        self.gx_exporter.finish_exporting()

        self.wk_file.close()
        self.zy_file.close()
        self.personal_file.close()
        self.gx_file.close()

    def process_item(self, item, spider):
        if item['lession_function'] == '通识选修':
            self.gx_exporter.export_item(item)
        elif item['lession_function'] == '个性课程':
            self.personal_exporter.export_item(item)
            # 这里留空格，是因为爬取下来的数据带有 ' ' 多余的空格
        elif item['lession_function'] == '推荐课程 ' or item['lession_function'] == ' 跨专业听课':
            self.zy_exporter.export_item(item)
        else:
            self.wk_exporter.export_item(item)

    @staticmethod
    def close_files(folder):
        """
        Modified by 刘曦光
        :param folder:
        :return:
        """
        JsonExporterPipleline.close('{}/whut_personal_lession.json'.format(folder))
        JsonExporterPipleline.close('{}/whut_gx_lession.json'.format(folder))
        JsonExporterPipleline.close('{}/whut_zy_lession.json'.format(folder))
        JsonExporterPipleline.close('{}/whut_wk_lession.json'.format(folder))

    @staticmethod
    def close(file):
        """
        做关闭文件的最后处理
        :param file:
        :return:
        """
        def is_file_empty(file):
            """
            判断文件是否为空
            :param file:
            :return:
            """
            if os.path.exists(file):
                with open(file, 'rb') as f:
                    # 直接跳转到文件末尾，统计字节数
                    end_pos = f.seek(0, os.SEEK_END)
                    if end_pos == 0:
                        return True
                    else:
                        return False
            return True
        # 空文件可能会出现 f.seek(-1, os.SEEK_END) 执行错误 OSError: [Errno 22] Invalid argument
        if is_file_empty(file):
            with open(file, 'wb') as f:
                f.write(b'[]')
        else:
            with open(file, 'r+b') as f:
                f.seek(-1, os.SEEK_END)
                f.write(b']')
