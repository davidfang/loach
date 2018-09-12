# -*- coding: utf-8 -*-
import sys
import os
import time
import subprocess
from flask import g
from loach.schedule import scheduler
from loach.devicemanager import Device
from loach.utils.exception import *

class SchedulerService(object):

    @classmethod
    def get_devices_stat(cls):
        stat = {}
        stat['stat'] = scheduler.device_manager.get_devices_stat()
        stat['waiting_tasks'] = scheduler._queue.qsize()
        if sys.platform == 'win32':
            r = os.system('tasklist | findstr node.exe > %s\\appium_process' % os.environ['TEMP'])
            if r == 0:
                with open(os.environ['TEMP']+'\\appium_process') as fr:
                    nodes = fr.readlines()
                stat['appium'] = nodes
        elif sys.platform.find('linux') >= 0:
            # r = os.system('ps -ef > %TEMP%\\appium_process')
            pass
        elif sys.platform == 'darwin':
            pass
        return stat

    @classmethod
    def restart_third_services(cls):
        cls.stop_third_services()
        cls.start_third_services()

    @classmethod
    def add_device(cls, cmd):
        try:
            scheduler.device_manager.add_device(Device(**(cmd['data'])))
        except MultipleDeviceExceptiom as e:
            return e.msg
        return 'success'

    @classmethod
    def start_third_services(cls, method=None):
        """
        默认使用usb方式连接，相对wifi快很多，此时不需要指定appium的-U参数
        :param method: usb/wifi
        :return:
        """
        devices = scheduler.device_manager.devices
        if sys.platform == 'win32':
            if not method or method == 'usb':
                for device in devices:
                    subprocess.Popen(['appium', '-p', str(device.sport), '-bp', str(device.sport+1000), '-U', device.udid, '--log', 'appium-%s.log' %device.udid, '--log-level', 'error'], shell=True)
                    time.sleep(2)
            elif method == 'wifi':
                for device in devices:
                    subprocess.Popen(['appium', '-p', str(device.sport), '-bp', str(device.sport+1000), '-U', "%s:%d" % (device.ip, device.port), '--log', 'appium-%s.log' %device.udid, '--log-level', 'error'], shell=True)
                    subprocess.Popen(['adb', 'connect', "%s:%d" % (device.ip, device.port)], shell=True)
                    time.sleep(2)
        elif sys.platform.find('linux') >= 0:
            # r = os.system('ps -ef > %TEMP%\\appium_process')
            pass
        elif sys.platform == 'darwin':
            pass

    @classmethod
    def stop_third_services(cls):
        devices = scheduler.device_manager.get_devices_stat()
        if sys.platform == 'win32':
            subprocess.Popen(['adb', 'kill-server'], stdout=subprocess.PIPE, shell=True)
            os.system('taskkill /im node.exe /f > %s\\restart_process' % os.environ['TEMP'])
        elif sys.platform.find('linux') >= 0:
            # r = os.system('ps -ef > %TEMP%\\appium_process')
            pass
        elif sys.platform == 'darwin':
            pass