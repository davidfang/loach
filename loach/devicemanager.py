# -*- coding: utf-8 -*-
"""
    用于管理多台设备的运行情况，包括
        preoared: 1
        running: 2
        fault: 4
        not_found: 8
"""
import traceback
import arrow
import logging
import time
from threading import Lock

import os

from loach.douyinapp import DouYinApp
from loach.kuaishouapp import KuaiShouApp
from loach.constant import Stat
from loach.utils.exception import *
from selenium.common.exceptions import WebDriverException
from loach.utils import retry
from loach.setting import config

device_stat_lock = Lock()
logger = logging.getLogger('loach')


class DeviceManager():
    def __init__(self, devices=None):
        self.devices = list()
        if devices:
            for ip, port, sip, sport in devices:
                device = Device(ip, port, sip, sport)
                self.devices.append(device)

    def add_device(self, device):
        for d in self.devices:
            if d.ip == device.ip and d.port == device.port:
                raise MultipleDeviceExceptiom(msg='设备已经存在 [%s:%d]' %(device.ip, device.port))
            if d.sip == device.sip and d.sport == device.sport:
                raise MultipleDeviceExceptiom(msg='添加设备失败 [%s:%d],appium节点已经被[%s:%d]使用 [%s:%d]' %(device.ip, device.port, device.sip, device.sport))
        self.devices.append(device)

    # def install_app_devices(self, app_name, device_udids=None, app=None):
    #     for device in self.devices:
    #         if not device_udids or device.udid in device_udids:
    #             device.install_app(app_name, app)
    #             device.modify_stat(Stat.RUNNING)
    #
    # def open_app_devices(self, app_name, device_udids=None):
    #     """
    #     打开所有设备上的app_name
    #     :param app_name:
    #     :param device_udids udid列表
    #     :return:
    #     """
    #     for device in self.devices:
    #         if not device_udids or device.udid in device_udids:
    #             device.open_app(app_name)
    #             device.modify_stat(Stat.RUNNING)

    def get_device_prepared(self, udid=None):
        device_stat_lock.acquire()
        for device in self.devices:
            if not udid:
                if device.stat == Stat.PREPARED:
                    device.modify_stat(Stat.RUNNING)
                    device_stat_lock.release()
                    return device
            else:
                if device.stat == Stat.PREPARED and device.udid == udid:
                    device.modify_stat(Stat.RUNNING)
                    device_stat_lock.release()
                    return device
        device_stat_lock.release()

    def get_devices_prepared(self):
        devices = list()
        device_stat_lock.acquire()
        for device in self.devices:
            if device.stat == Stat.PREPARED:
                device.modify_stat(Stat.RUNNING)
                devices.append(device)
        device_stat_lock.release()
        return devices

    # def get_device_running(self, task_type):
    #     device_stat_lock.acquire()
    #     for device in self.devices:
    #         if device.stat == Stat.RUNNING and device.task.task_type == task_type and not device.task_blocked:
    #             device_stat_lock.release()
    #             return device
    #     device_stat_lock.release()

    def check_device_stat(self, udid):
        for device in self.devices:
            if device.udid == udid:
                return device.stat

    def get_devices_stat(self):
        stats = []
        for device in self.devices:
            stats.append({
                'ip': device.ip,
                'port': device.port,
                'sip': device.sip,
                'sport': device.sport,
                'udid': device.udid,
                'platform': device.platform,
                'device_name': device.device_name,
                'device_type': device.device_type,
                'app': type(device.app).__name__,
                'stat': device.stat,
                'task': device.task.obj2dict() if device.task else dict()
            })
        return stats


class Device(object):
    def __init__(self, ip=None, port=None, sip=None, sport=None, udid=None, platform=None, device_name=None, device_type=None):
        self.ip = ip
        self.port = int(port)
        self.sip = sip
        self.sport = int(sport)
        self.udid = udid
        self.platform = platform
        self.device_name = device_name
        self.device_type = device_type
        self.app = None
        self.start_time = arrow.now('local').timestamp
        self.stat = Stat.PREPARED
        self.task = None

    def install_app(self, app_name, app):
        """
        打开app 如果没有安装，自动安装
        :param app: app的路径
        :return 返回一个App对象
        """
        if self.stat == Stat.PREPARED:
            self.app = DouYinApp(self.sip, self.sport, app)
        return self.app

    def open_app(self, app_name):
        """
        调用该方法之前应该确保设备已经安装了app，或者在此之前先调用install_app()方法
        :param app_name:
        :return:
        """
        if app_name == 'douyin':
            self.app = DouYinApp(self.sip, self.sport, platform=self.platform, device_name=self.device_name, device_type=self.device_type)
        elif app_name == 'kuaishou':
            self.app = KuaiShouApp(self.sip, self.sport, platform=self.platform, device_name=self.device_name, device_type=self.device_type)
        return self.app

    def modify_stat(self, stat):
        self.stat = stat

    @retry(times=3, forever=True)
    def do(self, command, thread_name, times=None):
        """
        这是一个线程，所有线程的异常在线程里处理
        理论上，既然能获取到可用的设备的就能成功执行，除非设备挂了
        :param command:
        :param thread_name: 使用设备的udid作为线程名，当设置设备争夺时，thread_name相同
            {
                'app_name': 'douyin',
                'task_type': Task,
                'force': False
                'data': {
                            'shortid': ''
                        },
            }
        :return:
        """
        fh = logging.FileHandler(os.path.join(config['PRO_DIR'], './logs/loach-{}'.format(self.udid)))
        fm = logging.Formatter(config['LOGGING_CONFIG']['formatters']['f']['format'])
        fh.setFormatter(fm)
        thread_logger = logging.getLogger('loach.{}'.format(self.udid))
        thread_logger.addHandler(fh)
        thread_logger.setLevel(logging.DEBUG)
        try:
            # print("[%s]: 正在执行 command: %s" % (thread_name, command))
            thread_logger.debug("[%s]: 正在执行 command: %s" % (thread_name, command))
            app = self.open_app(command['app_name'])
            self.task = command
            thread_logger.debug("[%s]: 成功打开app，马上执行命令" % thread_name)
            # print("[%s]: 成功打开app，马上执行命令" % thread_name)
            # app暂时没有跳出更新窗口，所以先注释调
            self.app.init_app()
            result = app.do(command, times)

        except (TimeoutException, NoSuchElementException, WebDriverException) as e:
            # print("[%s]: DeviceError" % thread_name)
            thread_logger.debug("[%s]: DeviceError" % thread_name)
            # print("[%s]: " % thread_name)
            raise DeviceError(msg=e.msg + "[cmd]: %s" % command)
        except (ConnectionRefusedError, ConnectionResetError, URLError) as e:
            # print("[%s]: AppiumServerTimeout" % thread_name)
            thread_logger.debug("[%s]: AppiumServerTimeout" % thread_name)
            # print("[%s]: " % thread_name)
            raise AppiumServerTimeout(
                msg="[===到appium server的连接超时，请检查网络或确保appium server已经启动===] " + "[cmd]: %s" % command)
        except DouYinFindTaskFailed as e:
            # TODO 回调通知失败,并 kill 线程
            # print("[%s]: DouYinFindTaskFailed" % thread_name)
            thread_logger.debug("[%s]: DouYinFindTaskFailed" % thread_name)
            raise e
        except DouYinLetterTaskFailed as e:
            thread_logger.debug("[%s]: DouYinLetterTaskFailed" % thread_name)
            # 不抛出任何异常即执行到底结束
        except InvalidSessionIdException as e:
            thread_logger.debug("[%s]: InvalidSessionIdException" % thread_name)
            # print("[%s]: InvalidSessionIdException" % thread_name)
            e.msg = e.msg + " [cmd]: %s" % command
            raise e
        except Exception as e:
            thread_logger.debug("[%s]: 未预见的异常，需要处理" % thread_name)
            # print("[%s]: 未预见的异常，需要处理" % thread_name)
            raise DouYinUnknowException(msg="[%s]: 未预见的异常，需要处理，%s" % (thread_name, e))
            # TODO 用来捕捉所有意料之外的异常，一旦发现在这里 catch
            # traceback.print_exc()
        else:
            thread_logger.debug("[%s]: 执行完成" % thread_name)
            # print("[%s]: 执行完成" % thread_name)
        finally:
            if self.app:
                self.app.quit()
        self.modify_stat(Stat.PREPARED)
        thread_logger.debug("[%s]: 线程结束" % thread_name)
        # print("[%s]: 线程结束" % thread_name)

    def __str__(self):
        return "设备: [%s:%s] \n 开始运行时间: [%s] \n 已经运行了[%d]分钟" \
               % (self.ip, self.port, arrow.get(self.start_time).to('+08:00').isoformat())

    def __repr__(self):
        return self.__str__()
