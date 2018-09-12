# -*- coding: utf-8 -*-

# 抖音app 1.7.6 版本的 app
VERSION = '2.1.1'

if VERSION == '1.7.6':
    from loach.douyinversions.douyinapp_1_7_6 import DouYinApp_1_7_6 as DouYinApp
elif VERSION == '1.9.0':
    from loach.douyinversions.douyinapp_1_9_0 import DouYinApp_1_9_0 as DouYinApp
elif VERSION == '2.0.0':
    from loach.douyinversions.douyinapp_2_0_0 import DouYinApp_2_0_0 as DouYinApp
elif VERSION == '2.1.1':
    from loach.douyinversions.douyinapp_2_1_0 import DouYinApp_2_1_1 as DouYinApp