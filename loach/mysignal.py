# -*- coding: utf-8 -*-

import signal
from loach.setting import config
from loach.schedule import scheduler

def quit():
    print('程序终止， 正在保存任务...')

    with open(config['PRO_DIR']+'data/data.json') as fr:
        pass



signal.signal(signal.SIGINT, quit)
signal.signal(signal.SIGTERM, quit)