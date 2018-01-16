# -*- coding: utf-8 -*-
import scrapy

import re
from urllib import parse


from ..pipelines import JsonExporterPipleline
from ..items import WhutLessionItem


class WhutSpider(scrapy.Spider):
    name = 'whut'
    allowed_domains = ['sso.jwc.whut.edu.cn', '202.114.90.180']
    agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"

    def spider_closed(self, spider):
        # 当退出爬虫时关闭chrome
        print("spider closed")
        self.json_pipleline.close_spider('')

    def parse_index(self, response):
        header = {
            'User-Agent': self.agent
        }
        all_urls = response.css("a::attr(href)").extract()
        if all_urls:
            all_urls = [parse.urljoin(response.url, url) for url in all_urls]
            all_urls = filter(lambda x: True if x.startswith("http") else False, all_urls)
            for url in all_urls:
                match_obj = re.match("(.*zykxk.do\?xnxq=2017-2018-2)", url)
                match_obj2 = re.match("(.*gxkxk.do\?xnxq=2017-2018-2)", url)
                match_obj3 = re.match("(.*gxkxk.do\?xnxq=2017-2018-2&flag=1)", url)
                if match_obj:
                    request_url = match_obj.group(1)
                    yield scrapy.Request(request_url, headers=header, callback=self.parse_lession_list)
                if match_obj2:
                    request_url2 = match_obj2.group(1)
                    yield scrapy.Request(request_url2, headers=header, callback=self.parse_gx_list)
                if match_obj3:
                    request_url3 = match_obj3.group(1)
                    yield scrapy.Request(request_url3, headers=header, callback=self.parse_personality_list)
        else:
            self.start_requests()

    def parse_personality_list(self, response):
        """
        解析个性课选课列表，并请求每一门课
        """
        header = {
            'User-Agent': self.agent
        }
        nodes = response.css("a[href^='gxkxkList.do']")
        for node in nodes:
            request_url = node.css("::attr(href)").extract_first("")
            request_url = parse.urljoin(response.url, request_url)
            lession_name = node.css("::text").extract_first("")
            yield scrapy.Request(request_url, headers=header, meta={"lession_name": lession_name}, callback=self.parse_personality_lession)

    def parse_personality_lession(self, response):
        """
        解析每一门个性课
        """
        lession_item = WhutLessionItem()
        lession_item['lession_name'] = response.meta.get("lession_name")
        node = response.css("tr[target='suid_obj']")
        lession_item['suid_obj'] = node.css("::attr(rel)").extract_first("")
        lession_item['teacher'] = node.css("a[href*='jspj.do']::text").extract_first("")
        lession_item['vector'] = node.css("td:nth-child(6)::text").extract_first("")
        lession_item['selected'] = node.css("td:nth-child(7)::text").extract_first("")
        lession_item['this_selected'] = node.css("td:nth-child(8)::text").extract_first("")
        lession_item['lession_function'] = node.css("td:nth-child(9)::text").extract_first("")
        lession_item['score'] = node.css("td:nth-child(10)::text").extract_first("")

        request_url = response.css("a[href^='gxkxkAdd.do']::attr(href)").extract_first()
        match_obj = re.match(".*gxkxkAdd.do\?xnxq=(.*)&kcdm=(\d+)&jxjhh=(\d+)&addid=(.*)&gsdm=&keyinfo=(.*)", request_url)
        if match_obj:
            xnxq = match_obj.group(1)
            kcdm = match_obj.group(2)
            jxjhh = match_obj.group(3)
            keyinfo = match_obj.group(5)

            lession_item['xnxq'] = xnxq
            lession_item['kcdm'] = kcdm
            lession_item['jxjhh'] = jxjhh
            lession_item['keyinfo'] = keyinfo

            lession_item['lession_url'] = "http://202.114.90.180/Course/gxkxkAdd.do?xnxq={xnxq}&kcdm={kcdm}&jxjhh={jxjhh}&addid={addid}&gsdm=&keyinfo={keyinfo}".format(xnxq=xnxq, kcdm=kcdm, jxjhh=jxjhh, addid=lession_item['suid_obj'], keyinfo=keyinfo)
            if lession_item:
                yield self.json_pipleline.process_item(lession_item, '')

    def parse_gx_list(self, response):
        """
        解析公选课列表,并请求每一门课
        """
        header = {
            'User-Agent': self.agent
        }
        all_urls = response.css("a::attr(href)").extract()
        for url in all_urls:
            match_obj = re.match("(.*gxkxkList.do\?jxjhh=2015&.*&&xnxq=2017-2018-2&&flag=&&temp=1)", url)
            if match_obj:
                request_url = match_obj.group(1)
                lession_name = response.css("a[href='{}']::text".format(request_url)).extract_first("")
                request_url = parse.urljoin(response.url, request_url)
                yield scrapy.Request(request_url, headers=header, meta={"lession_name": lession_name}, callback=self.parse_gx_lession)

    def parse_gx_lession(self, response):
        """
        解析每一门公选课
        """
        lession_name = response.meta.get("lession_name")
        node = response.css("tr[target='suid_obj']")
        lession_item = WhutLessionItem()
        lession_item['suid_obj'] = node.css("::attr(rel)").extract_first()
        lession_item['lession_name'] = lession_name
        lession_item['teacher'] = node.css("a[href*='jspj.do']::text").extract_first("")
        lession_item['vector'] = node.css("td:nth-child(6)::text").extract_first("")
        lession_item['selected'] = node.css("td:nth-child(7)::text").extract_first("")
        lession_item['this_selected'] = node.css("td:nth-child(8)::text").extract_first("")
        lession_item['lession_function'] = node.css("td:nth-child(9)::text").extract_first("")
        lession_item['score'] = node.css("td:nth-child(10)::text").extract_first("")
        lession_url = response.css("a[href^='gxkxkAdd.do']::attr(href)").extract_first("")
        match_obj = re.match(".*xnxq=(.*)&kcdm=(\d+)&jxjhh=(\d+)&addid=(.*)&gsdm=&keyinfo=(.*)", lession_url)
        if match_obj:
            xnxq = match_obj.group(1)
            kcdm = match_obj.group(2)
            jxjhh = match_obj.group(3)
            keyinfo = match_obj.group(5)

            lession_item['xnxq'] = xnxq
            lession_item['kcdm'] = kcdm
            lession_item['jxjhh'] = jxjhh
            lession_item['keyinfo'] = keyinfo
            lession_item[
                'lession_url'] = "http://202.114.90.180/Course/gxkxkAdd.do?xnxq={xnxq}&kcdm={kcdm}&jxjhh={jxjhh}&addid={addid}&keyinfo={keyinfo}".format(xnxq=xnxq, kcdm=kcdm, jxjhh=jxjhh, addid=lession_item['suid_obj'], keyinfo=keyinfo)
            if lession_item:
                yield self.json_pipleline.process_item(lession_item, '')

    def parse_lession_list(self, response):
        """
        获取专业课程列表，并向每一门专业课发起请求
        """
        header = {
            'User-Agent': self.agent
        }
        all_urls = response.css("a::attr(href)").extract()
        # all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        # all_urls = filter(lambda x: True if x.startswith("http") else False, all_urls)
        for url in all_urls:
            match_obj = re.match("(.*zykxkList.do\?.*xnxq=2017-2018-2)", url)
            if match_obj:
                request_url = match_obj.group(1)
                lession_name = response.css("a[href='{}']::text".format(request_url)).extract_first("")
                request_url = parse.urljoin(response.url, request_url)
                yield scrapy.Request(request_url, headers=header, meta={"lession_name": lession_name}, callback=self.parse_lession)

    def parse_lession(self, response):
        """
        解析每一门专业课
        """
        lession_name = response.meta.get("lession_name", {})
        nodes = response.css("tr[target='suid_obj']")
        for node in nodes:  # 一门课可能有多个老师
            item = WhutLessionItem()
            item['lession_name'] = lession_name
            item['suid_obj'] = node.css("::attr(rel)").extract_first("")
            item['teacher'] = node.css("a[href*='jspj.do']::text").extract_first("")
            item['vector'] = node.css("td:nth-child(7)::text").extract_first("")
            item['selected'] = node.css("td:nth-child(8)::text").extract_first("")
            item['this_selected'] = node.css("td:nth-child(9)::text").extract_first("")
            item['lession_function'] = node.css("td:nth-child(10)::text").extract_first("")
            item['score'] = node.css("td:nth-child(11)::text").extract_first("")
            all_urls = response.css("a::attr(href)").extract()
            for url in all_urls:
                match_obj = re.match(
                    "zykxkAdd\.do\?xnxq=(.*)&kcdm=(\d+)&jxjhh=(\d+)&addid=(.*)&keyinfo=(.*)", url)
                if match_obj:
                    xnxq = match_obj.group(1)
                    kcdm = match_obj.group(2)
                    jxjhh = match_obj.group(3)
                    keyinfo = match_obj.group(5)

                    item['xnxq'] = xnxq
                    item['kcdm'] = kcdm
                    item['jxjhh'] = jxjhh
                    item['keyinfo'] = keyinfo
                    item['lession_url'] = "http://202.114.90.180/Course/zykxkAdd.do?xnxq={xnxq}&kcdm=&jxjhh=&addid={addid}&keyinfo={keyinfo}".format(xnxq=xnxq, addid=item['suid_obj'], keyinfo=keyinfo)
            if item:
                yield self.json_pipleline.process_item(item, '')

    def start_requests(self):
        header = {
            "HOST": "sso.jwc.whut.edu.cn",
            'User-Agent': self.agent
        }
        post_url = "http://sso.jwc.whut.edu.cn/Certification/login.do"
        post_data = {
            "systemId": "",
            "xmlmsg": "",
            "userName": self.username,
            "password": self.password,
            "type": "xs",
        }
        self.json_pipleline = JsonExporterPipleline(self.folder)
        return [scrapy.FormRequest(
            url=post_url,
            formdata=post_data,
            headers=header,
            callback=self.lession_index
        )]

    def lession_index(self, response):
        """
        请求课程页面
        """
        lession_url = "http://202.114.90.180/Course/"
        JSESSIONID = response.headers.getlist('Set-Cookie')[0]
        CERLOGIN = response.headers.getlist('Set-Cookie')[1]

        header = {
            'User-Agent': self.agent
        }
        yield scrapy.Request(lession_url, dont_filter=True, headers=header, callback=self.parse_index)

