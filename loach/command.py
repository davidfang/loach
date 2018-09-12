# -*- coding: utf-8 -*-

# cmd = {
#     'app_name': 'douyin',
#     'task_type': Task.FINDING,
#     'force': False,
#     'timeout': 30 等待可用设备的时间
#     'data': {
#     }
# }
import uuid
from collections import Iterable
from loach.constant import Task
from loach.utils.exception import CommandInvalidException


class Command(object):
    def __init__(self, **kwargs):
        self.cmd = kwargs
        self.cmd['uuid'] = uuid.uuid4().hex
        if "app_name" not in self.cmd.keys():
            self.cmd['app_name'] = None
            # raise CommandInvalidException(msg="缺少属性 app_name")
        if "task_type" not in self.cmd.keys():
            self.cmd['task_type'] = None
            # raise CommandInvalidException(msg="缺少属性 task_type")
        if "timeout" not in self.cmd.keys():
            self.cmd['timeout'] = None
        if "data" not in self.cmd.keys():
            self.cmd['data'] = None
        if 'udid' not in self.cmd.keys():
            self.cmd['udid'] = None

    @property
    def app_name(self):
        return self.cmd["app_name"]

    def __getitem__(self, item):
        return self.cmd[item]

    def __setitem__(self, key, value):
        self.cmd[key] = value

    def __str__(self):
        return self.cmd.__str__()

    def __repr__(self):
        return self.__str__()

    def obj2dict(self):
        return self.cmd

    def dict2obj(self, d):
        self.cmd = d


class DouYinCommand(Command):
    """
    {
        'app_name': 'douyin',
        'task_type': Task 对象,
        'timeout': 默认没有超时时间,
        "udid": udid 指定获取某设备运行
        'data': {
                "attrs": 需要爬取的内容，list或tuple
            }
        或
        'data': [
            {
                'short_id'
                "attrs": 需要爬取的内容，list或tuple
            },
            {
                'short_id'
                "attrs": 需要爬取的内容，list或tuple
            },
        ]
    }
    Task:
        crawling任务:
            attrs = ("comment", 'author', "following", "follower", "work", "like", 'music', 'music_hot', 'music_latest')
        finding任务:
                {
                    attrs = ("comment", 'author', "following", "follower", "work", "like")
                    short_id
                }
        add_device:
            'ip': 设备的ip      使用wifi时，可以任意指定
            'port' 设备的port   使用wifi时，可以任意指定
            'sip' appium server ip
            'sport' appium server port
            'platform' 设备的android版本
            'device_name' 设备的型号（可查看设置-关于手机）
            'device_type' 为了区分不同设备，查看appbuttonmanager源码
            'udid' 设备ip 查看adb devices
        kol_letter:
            'data': [
                {
                    'short_id'
                    "words": 私信内容
                },
                {
                    'short_id'
                    "words": 私信内容
                },
            ]
        category:


    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not kwargs.get('app_name'):
            self.cmd['app_name'] = 'douyin'
        if self.cmd['task_type'] == Task.CRAWLING:
            if 'attrs' not in self.cmd['data'].keys():
                self.cmd['data']['attrs'] = None
            elif not isinstance(self.cmd['data']['attrs'], Iterable):
                raise CommandInvalidException('data.attrs必须是可迭代类型')
        if self.cmd['task_type'] == Task.FINDING:
            if 'short_id' not in self.cmd['data'].keys():
                raise CommandInvalidException('抖音搜索任务必须指定 short_id')
            if 'attrs' not in self.cmd['data'].keys():
                self.item['attrs'] = None
            elif not isinstance(self.cmd['data']['attrs'], Iterable):
                raise CommandInvalidException('data.attrs必须是可迭代类型')
        if self.cmd['task_type'] == Task.KOL_LETTER:
            for item in self.cmd['data']:
                if 'short_id' not in item.keys() or 'words' not in item.keys():
                    raise CommandInvalidException('私信任务必须指定short_id和words')
        if self.cmd['task_type'] == Task.ADD_DEVICE:
            if 'ip' not in self.cmd['data'].keys() or \
                    'port' not in self.cmd['data'].keys() or \
                    'sip' not in self.cmd['data'].keys() or \
                    'sport' not in self.cmd['data'].keys() or \
                    'platform' not in self.cmd['data'].keys() or \
                    'device_name' not in self.cmd['data'].keys() or \
                    'device_type' not in self.cmd['data'].keys() or \
                    'udid' not in self.cmd['data'].keys():
                raise CommandInvalidException('必须指定要添加的设备的信息')

    def is_force(self):
        return self.cmd['force']


class KuaiShouCommand(Command):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not kwargs.get('app_name'):
            self.cmd['app_name'] = 'kuaishou'
        if self.cmd['task_type'] == Task.CRAWLING:
            if 'attrs' not in self.cmd['data'].keys():
                self.cmd['data']['attrs'] = None
            elif not isinstance(self.cmd['data']['attrs'], Iterable):
                raise CommandInvalidException('data.attrs必须是可迭代类型')
        if self.cmd['task_type'] == Task.FINDING:
            if 'short_id' not in self.cmd['data'].keys():
                raise CommandInvalidException('抖音搜索任务必须指定 short_id')
            if 'attrs' not in self.cmd['data'].keys():
                self.cmd['data']['attrs'] = None
            elif not isinstance(self.cmd['data']['attrs'], Iterable):
                raise CommandInvalidException('data.attrs必须是可迭代类型')
        if self.cmd['task_type'] == Task.ADD_DEVICE:
            if 'ip' not in self.cmd['data'].keys() or 'port' not in self.cmd['data'].keys() or 'sip' not in self.cmd['data'].keys() or 'sport' not in self.cmd['data'].keys():
                raise CommandInvalidException('必须指定要添加的设备的信息')

    def is_force(self):
        return self.cmd['force']
