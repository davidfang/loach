# -*- coding: utf-8 -*-
import logging
import os
from kombu import Queue, Exchange, binding
from celery.schedules import crontab

def create_task_queues(binding_list):
    binding_map = {}
    exchange = Exchange('DouYin', type='topic')

    _queues = [
        Queue(
            'ocean:debug',
            [binding(exchange, routing_key='douyin.debug.#')],
            queue_arguments={'x-queue-mode': 'lazy'}
        )
    ]

    for routing_key, queue_name in binding_list:
        binding_map.setdefault(queue_name, [])
        binding_map[queue_name].append(routing_key)

    for queue_name, routing_keys in binding_map.items():
        _queues.append(
            Queue(
                queue_name,
                [binding(exchange, routing_key=routing_key)
                 for routing_key in routing_keys],
                queue_arguments={'x-queue-mode': 'lazy'}
            )
        )
    return _queues


bindings = [
    ('douyin.author.#', 'douyin.author'),
    ('douyin.schedule.#', 'douyin.schedule')
]
queues = create_task_queues(bindings)


def route_task(name, args, kwargs, options, tuask=None, **kw):
    return {
        'exchange': 'DouYin',
        'exchange_type': 'topic',
        'routing_key': name
    }


class ProductConfig(object):
    PRO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../')
    CACHE_REDIS_URL = 'redis://192.168.1.8:6379/1'

    # SQLALCHEMY_DATABASE_URI = 'postgresql://oceanuser:851JqIaLlicRwkGs@10.30.183.102:5432/douyin'
    SQLALCHEMY_DATABASE_URI = 'postgresql://xxx:xxx@192.168.1.8:5432/douyin'
    SQLALCHEMY_DATABASE_URI_4 = 'postgresql://xxx:xxx@192.168.1.4:5432/douyin'
    # 公网地址: 'amqp://admin:avGX9IHGeUVVcs5B@118.190.112.223:5672/'
    RABBITMQ_URL = 'amqp://xxx:xxx@xxx/'

    DOUYIN_REDIS = 'redis://192.168.1.8:6379/15'
    DOUYIN_REDIS_FOLLOW_RELATION = 'douyin:follow_relation'
    DOUYIN_REDIS_LIKE_RELATION = 'douyin:like_relation'

    CELERY = {
        'broker_url': RABBITMQ_URL,

        # 'broker_transport_options': {},
        'result_backend': CACHE_REDIS_URL,
        'task_ignore_result': True,
        'broker_pool_limit': None,
        # 默认任务配置
        'task_default_queue': 'douyin:default',
        'task_default_exchange': 'DouYin',
        'task_default_exchange_type': 'topic',
        'task_default_routing_key': 'default',
        'task_default_delivery_mode': 'persistent',
        'task_track_started': True,
        'enable_utc': True,
        'timezone': "Asia/Shanghai",

        # 发送端路由
        'task_queues': queues,
        'task_routes': (route_task, ),
        'beat_schedule': {
            'database_clean_every_day': {
                'task': 'douyin.schedule.database.clean',
                'schedule': crontab(minute=10, hour=4), # 使用
                'options': {'exchange': 'DouYin', 'routing_key': 'douyin.schedule.database.clean'}
            },
            'database_clean_every_month': {
                'task': 'douyin.schedule.database.relation.distinct',
                'schedule': crontab(minute=10, hour=4, day_of_week=5),  # 使用
                'options': {'exchange': 'DouYin', 'routing_key': 'douyin.schedule.database.relation.distinct'}
            },
        },
        # 日志
        'worker_task_log_format': "[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
        'worker_log_format': "[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
    }

    LOGGING_CONFIG = {
        "version": 1,
        "formatters": {
            'f': {
                'format':
                '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'}
        },
        "handlers": {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'f',
            },
            'file': {
                'level': 'DEBUG',
                'class': 'logging.FileHandler',
                'filename': os.path.join(PRO_DIR, 'logs/loach.log'),
                'encoding': 'utf-8',
                'formatter': 'f',
            },
        },
        "root": {
            'handlers': ['console'],
            'level': logging.DEBUG,
        },
        "loggers": {
            'loach': {
                'propagate': False,
                'level': 'DEBUG',
                'handlers': ['console', 'file']
            },
        }
    }

def obj2dict(obj):
    return {key: getattr(obj, key) for key in dir(obj) if key.isupper()}


config = obj2dict(ProductConfig)
