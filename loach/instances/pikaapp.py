# -*- coding: utf-8 -*-

import pika
import json


def send_task(cmd):
    con = pika.BlockingConnection(pika.ConnectionParameters(host='xxx', port=5672, virtual_host='/',
                                                            credentials=pika.PlainCredentials('xxx',
                                                                                              'xxx')))
    channel = con.channel()
    channel.basic_publish(exchange='DouYin', routing_key='douyin.task.cmd', body=json.dumps(cmd.cmd))
    channel.close()
    con.close()
