# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)) + "\\..\\..\\")
from loach.setting import config
from redis import StrictRedis

douyin_rds = StrictRedis.from_url(
    config['DOUYIN_REDIS'],
    max_connections=50,
    socket_connect_timeout=4
)