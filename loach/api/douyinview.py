# -*- coding: utf-8 -*-
import json
from loach.api import douyin
from loach.command import DouYinCommand
from loach.constant import Task
from loach.schedule import scheduler
from loach.service.scheduler import SchedulerService
from flask import request, make_response
import json


@douyin.route('/hello/', methods=['GET'])
def hello():
    return 'hello'


@douyin.route('/task/category/', methods=['POST'])
def task_category():
    cmd = DouYinCommand(timeout=int(request.args.get('timeout', 0)), task_type=Task.CATEGORY)
    # send_task(cmd)
    cmd['udid'] = request.args.get('udid')
    task_num = int(request.args.get('task_num', 1))
    for i in range(task_num):
        scheduler.push_command(cmd)
    return cmd.__str__()


@douyin.route('/task/kol_letter/', methods=['POST'])
def task_kol_letter():
    cmd = DouYinCommand(timeout=int(request.args.get('timeout', 0)), task_type=Task.KOL_LETTER, data=json.loads(request.data))
    # send_task(cmd)
    cmd['udid'] = request.args.get('udid')
    print(cmd['udid'])
    scheduler.push_command(cmd)
    return cmd.__str__()


@douyin.route('/task/search/', methods=['POST'])
def task_search():
    cmd = DouYinCommand(timeout=int(request.args.get('timeout', 0)), task_type=Task.FINDING, data=json.loads(request.data))
    # send_task(cmd)
    scheduler.push_command(cmd)
    return cmd.__str__()


@douyin.route('/task/searches/', methods=['POST'])
def task_searches():
    tasks = json.loads(request.data)
    r = []
    for task in tasks:
        cmd = DouYinCommand(timeout=int(request.args.get('timeout', 0)), task_type=Task.FINDING, data=task)
        scheduler.push_command(cmd)
        r.append(str(cmd))
    return 'success'


@douyin.route('/task/crawling/', methods=['POST'])
def task_crawling():
    cmd = DouYinCommand(timeout=int(request.args.get('timeout', 0)), task_type=Task.CRAWLING, data=json.loads(request.data))
    # send_task(cmd)
    scheduler.push_command(cmd)
    return cmd.__str__()


@douyin.route('/task/device/', methods=['POST'])
def task_device_add():
    cmd = DouYinCommand(timeout=int(request.args.get('timeout', 0)), task_type=Task.ADD_DEVICE, data=json.loads(request.data))
    # send_task(cmd)
    return SchedulerService.add_device(cmd)


@douyin.route('/task/devices/', methods=['POST'])
def task_devices_add():
    cmds = json.loads(request.data)
    r = []
    for cmd in cmds.values():
        cmd = DouYinCommand(timeout=int(request.args.get('timeout', 0)), task_type=Task.ADD_DEVICE, data=cmd)
        # send_task(cmd)
        r.append(SchedulerService.add_device(cmd))
    return json.dumps(r)


@douyin.route('/task/stat/', methods=['GET'])
def task_devices_stat():
    return json.dumps(SchedulerService.get_devices_stat())


@douyin.route('/start/', methods=['GET'])
def start():
    SchedulerService.start_third_services(method=request.args['method'])
    return ''


@douyin.route('/stop/', methods=['GET'])
def stop():
    SchedulerService.stop_third_services()
    return ''


@douyin.route('/restart/', methods=['GET'])
def restart():
    SchedulerService.restart_third_services()
    return ''


