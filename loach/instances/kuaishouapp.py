# -*- coding: utf-8 -*-

# from celery import Celery
# from loach.setting import config
# celery = Celery()
# celery.config_from_object(config['CELERY'])
#
# @celery.task(
#     name='weibo.articles.crawl.one',
#     autoretry_for=(requests.ConnectionError, requests.Timeout),
#     retry_kwargs={
#         'max_retries': 1,
#         'countdown': 0.5
#     },
#     ignore_result=True
# )
# def fuck_it(){
#
# }
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)) + "\\..\\..\\")
import pika
import json
import re
from loach.utils.redisobj import douyin_rds
from json.decoder import JSONDecodeError

con = pika.BlockingConnection(pika.ConnectionParameters(host='xxx', port=5672, virtual_host='/', credentials=pika.PlainCredentials('xxx', 'xxx')))
channel = con.channel()


binding_keys = [
    # routing_key       queue_name
    'kuaishou.author.kol', 'kuaishou.author.kol'
]
# "\"share_info\": ?\"userId= ?(?<kid>[A-Za-z0-9]+)&photoId= ?(?<vid>[A-Za-z0-9]+)\""
p1 = re.compile(r'"share_info\": ?\"userId= ?(?P<kid>[A-Za-z0-9]+)&photoId= ?(?P<vid>[A-Za-z0-9]+)\"')
p2 = re.compile(r'\"user_id\": ?(?P<uid>\d+)')


def kuaishou_author_kol(body):
    response = json.loads(body.decode('utf-8'))
    feeds = response['feeds']
    for feed in feeds:
        m1 = p1.search(json.dumps(feed))
        m2 = p2.search(json.dumps(feed))
        douyin_rds.sadd('kuaishou_kol', (m2['uid'], m1['kid']))
    return "OK"


routing_tasks = {
    'kuaishou.author.kol': kuaishou_author_kol
}

# channel.queue_bind(exchange="DouYin", queue="douyin.author", routing_key='douyin.author.#',)


def cb(ch, method, properties, body):
    print(" [x] %r:%r" % (method.routing_key, body))
    task = routing_tasks.get(method.routing_key, None)
    if task and callable(task):
        try:
            r = task(body)
        except (KeyError, IndexError, JSONDecodeError):
            # 这些报错说明都因返回的数据格式不对，可以直接抛弃
            r = "OK"
        if r == 'OK':
            ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=10)
channel.basic_consume(cb, queue="kuaishou.author.kol")
 
channel.start_consuming()
