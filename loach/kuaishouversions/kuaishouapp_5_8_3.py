# -*- coding: utf-8 -*-
import time
from loach.app import App
from loach.desired_capabilities import get_desired_capabilities
from loach.constant import Task, Stat
from loach.utils import retry
from appium.webdriver.common.mobileby import MobileBy as By
from selenium.common.exceptions import (TimeoutException,
                                        NoSuchElementException,
                                        WebDriverException)
from loach.utils.exception import (DouYinFindTaskFailed)
from selenium.webdriver.support.ui import WebDriverWait
from appium.webdriver.common.touch_action import TouchAction
from loach.appbuttonmanager import AppButtonManager


class Button(object):
    def __init__(self, left_top=None, right_bottom=None, id=None, name=None, text=None, locator=None):
        self.left_top = left_top
        self.right_bottom = right_bottom
        self.id = id
        self.name = name
        self.text = text
        self.locator = locator
        # self.uiselector = uiselector


class KuaiShouApp_5_8_3(App):
    def __init__(self, sip, sport, app=None,platform=None, device_name=None, device_type=None):
        desired_caps = get_desired_capabilities(app, platform=platform, device_name=device_name, appPackage='com.smile.gifmaker', appActivity='com.yxcorp.gifshow.HomeActivity')
        super(KuaiShouApp_5_8_3, self).__init__(desired_caps, sip, sport)
        # 首页滑动翻下一个视频时等待的时间
        self.swip_to_next_wait_time = 0.5
        # 点击时间等待的时间
        self.click_wait_time = 2
        # 滑动翻视频、粉丝、关注列表 等待的时间
        self.swip_to_bottom_wait_time = 0.5
        # 滑动翻视频、粉丝、关注时，每做一次至底判断滑动的次数
        self.swip_times_every_assert = 10
        # 点击搜索主播/音乐人时的等待时间
        self.find_wait_time = 3
        # 编辑editor等待时间
        self.editor_wait_time = 0.5
        # 定义需要点击的元素
        self.buttons = AppButtonManager.checkout_kuaishou(app_version='5.8.3', device_type=device_type)

    def init_app(self):
        self.sleep(10)
        # self.close_update_widget()
        # 登录帐号的情况下每次打开app都会跳出直播

        self.move_to_next()

    def capture_author_info_by_shortid(self, shortid, attrs=None):
        """
        抓取主播信息
        :param shortid: 抖音号
        :param attrs: 要抓取的信息
        """
        self.click_find_xy()
        self.input_find_keyword(shortid)
        self.click_do_find()
        self.click_first_find_result()
        if not attrs:
            attrs = ("following", "follower", "work", "like")
        if "following" in attrs:
            print('following')
            self.click_author_following()
            self.swip_to_bottom(30, 5, 1)
            self.click_back()
        if "follower" in attrs:
            print('follower')
            self.click_author_follower()
            self.swip_to_bottom(30, 5, 1)
            self.click_back()
        if "work" in attrs:
            print('work')
            self.click_author_works()
            self.swip_to_bottom(30, 5, 1)
        if "like" in attrs:
            print('like')
            self.click_author_like()
            self.swip_to_bottom(15, 5, 1)
        self.click_back()

    def capture_music_info_page(self):
        self.click_music_info_xy()
        self.click_music_hot()
        self.swip_to_bottom(2, 5, 1)
        self.click_music_latest()
        self.swip_to_bottom(2, 5, 1)
        self.click_back()

    def move_to_next(self):
        """
        首页翻下一个视频
        """
        self.swip(x1=int(0.5*self.window["width"]), y1=int(self.window['height']*0.9)
                  , x2=int(0.5*self.window["width"]), y2=int(self.window['height']*0.1))
        self.sleep(self.swip_to_next_wait_time)

    def swip_to_bottom(self, max_assert=None, times_once_assert=None, wait=None):
        """
            滑动至底, 滑动次数 = max_assert * times_once_assert
        :param max_assert: 最大断言（是否至底）次数
        :param times_once_assert: 每次断言（是否至底）的滑动次数
        :param wait: 每次滑动等待的时间
        """
        times_assert = 0
        while True:
            source_before = self.page_source
            for time in range(self.swip_times_every_assert if not times_once_assert else times_once_assert):
                self.swip(x1=int(0.5*self.window["width"]), y1=int(self.window['height']*0.8)
                          , x2=int(0.5*self.window["width"]), y2=int(self.window['height']*0.1))
                self.sleep(self.swip_to_bottom_wait_time if not wait else wait)
            source_after = self.page_source
            if source_before == source_after:
                break
            times_assert += 1
            if max_assert and max_assert < times_assert:
                break

    def set_up(self):
        super(KuaiShouApp_5_8_3, self).set_up()
        self.sleep(3)
        # self.capture_author_info_by_shortid("")
        # self.init_app()
        self.sleep(3)
        while True:
            self.move_to_next()
            self.capture_author_info_page()
            self.capture_music_info_page()

    def click_author_follower(self):
        e = self.wait_element_clickable(self.buttons['author_follower_button'].locator)
        e.click()
        self.sleep(self.click_wait_time)

    def click_author_following(self):
        e = self.wait_element_clickable(self.buttons['author_following_button'].locator)
        e.click()
        self.sleep(self.click_wait_time)

    def click_author_like_count(self):
        e = self.wait_element_clickable(self.buttons['author_like_count_button'].locator)
        e.click()
        self.sleep(self.click_wait_time)

    def click_author_info(self):
        e = self.wait_element_clickable(self.buttons['author_info_button'].locator)
        e.click()
        self.sleep(self.click_wait_time)

    def click_author_works(self):
        e = self.wait_element_clickable(self.buttons['author_work_button'].locator)
        e.click()
        self.sleep(self.click_wait_time)

    def click_author_like(self):
        e = self.wait_element_clickable(self.buttons['author_like_button'].locator)
        e.click()
        self.sleep(self.click_wait_time)

    def click_music_info(self):
        e = self.wait_element_clickable(self.buttons['music_info_button'].locator)
        e.click()
        self.sleep(self.click_wait_time)

    def click_music_hot(self):
        e = self.wait_element_clickable(self.buttons['music_hot_button'].locator)
        e.click()
        self.sleep(self.click_wait_time)

    def click_music_latest(self):
        e = self.wait_element_clickable(self.buttons['music_latest_button'].locator)
        e.click()
        self.sleep(self.click_wait_time)

    def click_comment(self):
        e = self.wait_element_clickable(self.buttons['comment_button'].locator)
        e.click()
        self.sleep(self.click_wait_time)

    def click_author_info_xy(self):
        self.click_by_xy(self.buttons['author_info_button'].left_top, self.buttons['author_info_button'].right_bottom)
        self.sleep(self.click_wait_time)

    def click_author_works_xy(self):
        self.click_by_xy(self.buttons['author_work_button'].left_top, self.buttons['author_work_button'].right_bottom)
        self.sleep(self.click_wait_time)

    def click_author_like_xy(self):
        self.click_by_xy(self.buttons['author_like_button'].left_top, self.buttons['author_like_button'].right_bottom)
        self.sleep(self.click_wait_time)

    def click_music_info_xy(self):
        self.click_by_xy(self.buttons['music_info_button'].left_top, self.buttons['music_info_button'].right_bottom)
        self.sleep(self.click_wait_time)

    def click_music_hot_xy(self):
        self.click_by_xy(self.buttons['music_hot_button'].left_top, self.buttons['music_hot_button'].right_bottom)
        self.sleep(self.click_wait_time)

    def click_music_latest_xy(self):
        self.click_by_xy(self.buttons['music_latest_button'].left_top, self.buttons['music_latest_button'].right_bottom)
        self.sleep(self.click_wait_time)

    def click_comment_xy(self):
        self.sleep(3)
        self.click_by_xy(self.buttons['comment_button'].left_top, self.buttons['comment_button'].right_bottom)
        self.sleep(self.click_wait_time)

    def click_first_find_result_xy(self):
        self.click_by_xy(self.buttons['first_find_result_button'].left_top, self.buttons['first_find_result_button'].right_bottom)
        self.sleep(self.click_wait_time)

    def click_find(self):
        self.wait_element_clickable(self.buttons['find_button'].locator).click()
        self.sleep(self.click_wait_time)

    def click_find_xy(self):
        self.click_by_xy(self.buttons['find_button'].left_top, self.buttons['find_button'].right_bottom)
        self.sleep(self.click_wait_time)

    def click_do_find(self):
        # 2018-6-27 app 界面更改，  废弃
        # self.wait_element_clickable(self.buttons['do_find_button'].locator).click()
        # 废弃，在nox抖音2.0上测试成功，在实体机抖音2.1测试失败
        # self.driver.press_keycode(66)
        self.click_by_xy(self.buttons['keyboard_search'].left_top, self.buttons['keyboard_search'].right_bottom)
        self.sleep(self.find_wait_time)

    def click_first_find_result(self):
        self.wait_element_clickable(self.buttons['first_find_result_button'].locator).click()
        self.sleep(self.click_wait_time)

    def input_find_keyword(self, k):
        e = self.wait_element_clickable(self.buttons['find_editor_button'].locator)
        e.click()
        e.send_keys(k)
        self.sleep(self.editor_wait_time)

    def click_back(self):
        # e = self.wait_element_clickable(self.back_button.locator)
        # e.click()
        self.driver.back()
        self.sleep(self.click_wait_time)

    def click(self):
        """
        有时app会跳出一些置顶的窗口，点击屏幕时关闭。同时点击事件被消费掉
        :return:
        """
        self.click_by_xy((0, 0), tuple(self.window.values()))

    def close_update_widget(self):
        self.sleep(12)
        self.click_by_xy(self.buttons['not_update_button'].left_top, self.buttons['not_update_button'].right_bottom)

    def sleep(self, senconds):
        time.sleep(senconds)

    def do_finding(self, command, times=None):
        """
        处理搜索任务，默认重试3次
        :param command:
        :param times 又retry装饰器传过来的，第几次执行
        :return:
        """
        try:
            self.capture_author_info_by_shortid(command['data']['short_id'], attrs=command['data']['attrs'])
        except (TimeoutException, NoSuchElementException, WebDriverException) as e:
            if times >= 5:
                raise DouYinFindTaskFailed(msg="抖音搜索任务失败 ")
            raise e

    def do_crawling(self, command):
        """
        处理爬虫任务，这是一个长期执行的任务,
        :param command:
        :param
        :return:
        """
        try:
            if 'mainpage' in command['data']['attrs']:
                while True:
                    self.swip_to_bottom(max_assert=20, times_once_assert=50)
        except (TimeoutException, NoSuchElementException, WebDriverException) as e:
            raise e

    def do(self, command, times):
        try:
            if command["task_type"] == Task.FINDING:
                self.do_finding(command, times)
            elif command["task_type"] == Task.CRAWLING:
                self.do_crawling(command)
        except DouYinFindTaskFailed as e:
            raise e
