# -*- coding: utf-8 -*-


class Stat(object):
    # 就绪态 没有执行任何app
    PREPARED = 1
    # 运行态 正在运行app
    RUNNING = 2
    # 错误态
    FAULT = 4
    # 设备断开连接（模拟器进程死亡）
    NOT_FOUND = 8


class Task(object):
    FINDING = 1
    CRAWLING = 2
    ADD_DEVICE = 4
    KOL_LETTER = 8
    CATEGORY = 16


class Extra(object):
    FORCE = 1