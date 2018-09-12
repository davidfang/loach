# -*- coding: utf-8 -*-
from loach.api import kuaishou
from loach.command import KuaiShouCommand
from loach.constant import Task
from loach.schedule import scheduler
from flask import request
import json


@kuaishou.route('/hello/', methods=['GET'])
def hello():
    return 'hello'


@kuaishou.route('/task/crawling/', methods=['POST'])
def task_crawling():
    cmd = KuaiShouCommand(task_type=Task.CRAWLING, data=json.loads(request.data))
    # send_task(cmd)
    scheduler.push_command(cmd)
    return cmd.__str__()

