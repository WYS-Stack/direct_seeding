import json
import os.path
import time

import wx

import uiautomator2 as u2
from logger import logger
from config.root_directory import ROOT_DIR
from room.element_init import (
    element_wait,
    element_exists,
    element_wait_gone,
    element_click_exists,
    element_send_keys,
    element_set_text,
    element_click,
    element_get_text, element_description
)

class DouYinRoom:
    def __init__(self, device, app_id, app_server, enter_live_broadcast_event):
        self.device = device
        self.app_id = app_id
        self.app = app_server
        self.enter_live_broadcast_event = enter_live_broadcast_event

    async def enter_live_broadcast_room(self):
        """
        进入直播间的主函数
        """
        d = u2.connect(f"{self.device.serial}")
        await self.enter_room(d)

    async def enter_room(self, d):
        """
        进入直播间的流程控制函数
        """
        self.config_data = await self.read_config()
        # 检查是否已经在直播间
        if not element_exists(d, self.config_data["live_broadcast_page"]["关闭按钮"]):
            await self.handle_popups(d)
            await self.enter_search_page(d)
            await self.enter_live_broadcast_page(d)
        else:
            logger.info("已进入直播间")
            self.enter_live_broadcast_event.set()

    @staticmethod
    async def read_config():
        # 读取JSON配置文件
        config_path = os.path.join(ROOT_DIR, "config", "room_config.json")
        with open(config_path, 'r') as json_file:
            config_data = json.load(json_file)["douyin"]
        return config_data

    @staticmethod
    async def process_popup(d, popup_key, close_key, use_xpath=False):
        if use_xpath:
            if element_exists(d, popup_key, use_xpath=True):
                element_click_exists(d, close_key)
        if element_exists(d, popup_key):
            element_click_exists(d, close_key)

    async def handle_popups(self, d):
        """
        处理打开应用时可能出现的弹窗
        """
        popup = self.config_data.get("popup", {})
        await DouYinRoom.process_popup(d, popup["弹窗1"], popup["关闭1"])
        await DouYinRoom.process_popup(d, popup["检测到更新（弹窗）"], popup["以后再说（按钮）"])
        await DouYinRoom.process_popup(d, popup["抖音想访问你的通讯录"], popup["拒绝访问通讯录"])
        await DouYinRoom.process_popup(d, popup["弹窗4"], popup["关闭4"], use_xpath=True)
        await DouYinRoom.process_popup(d, popup["弹窗5"], popup["关闭5"])
        await DouYinRoom.process_popup(d, popup["弹窗6"], popup["关闭6"], use_xpath=True)
        await DouYinRoom.process_popup(d, popup["抖音没有响应"], popup["等待响应"])
        if element_exists(d, popup["添加搜索到桌面"], use_xpath=True):
            element_description(d, popup["关闭添加搜索弹窗"])

    async def login(self, d, phone: str, code: str, config_data):
        """
        登陆
        """
        phone_login_page = config_data.get("phone_login_page", {})
        # 手机号登陆
        if element_exists(d, phone_login_page["登陆界面1"], use_xpath=True):
            element_click_exists(d, phone_login_page["操作1"])
            element_send_keys(d, phone_login_page["操作2"], phone)
            element_click_exists(d, phone_login_page["操作3"])
            if element_exists(d, phone_login_page["手动验证"], use_xpath=True):
                self.on_task_completed("请打开模拟器手动验证")
                if element_wait_gone(d, phone_login_page["手动验证"], use_xpath=True):
                    element_send_keys(d, phone_login_page["输入验证码"], code)
                    element_click_exists(d, phone_login_page["登录按钮"])
        # 账号密码登陆
        else:
            password_login_page = config_data.get("password_login_page", {})
            pass

    async def enter_search_page(self, d):
        """
        进入搜索页面
        """
        search_page = self.config_data.get("search_page", {})
        if element_wait(d, search_page["搜索页面1"]) or element_wait(d, search_page["搜索页面2"]) or element_wait(d, search_page["搜索页面3"]):
            if element_click_exists(d, search_page["搜索页面1"]):
                await self.enter_home_page(d)
            elif element_exists(d, search_page["搜索页面2"]):
                await self.enter_search_result_page(d)
            elif element_exists(d, search_page["搜索页面3"]):
                await self.enter_account_info_page(d)
        else:
            logger.info("未确定当前页面")
            if not hasattr(self, "force_flag"):
                logger.info("尝试重新进入中...")
                self.force_flag = True
                await self.app.force_restart_application_program()
                await self.enter_live_broadcast_room()

    async def enter_home_page(self, d):
        """
        进入抖音首页
        """
        logger.info("确定当前为首页")
        logger.info("已点击搜索🔍按钮")
        element_set_text(d, self.app_id)
        logger.info("已输入ID")
        # await self.enter_live_broadcast_page(d)

    async def enter_search_result_page(self, d):
        """
        进入搜索结果页面
        """
        logger.info("确定当前为搜索页面")
        element_set_text(d, self.app_id)  # 输入ID
        logger.info("已输入ID")
        # await self.enter_live_broadcast_page(d)

    async def enter_account_info_page(self, d):
        """
        进入账号信息页面
        """
        logger.info("确定当前为账号信息页面")
        account_info_page = self.config_data.get("account_info_page", {})
        if element_exists(d, account_info_page["直播标识"]):
            element_click(d, account_info_page["右上角按钮"])  # '···'按钮
            id_flag = account_info_page["id信息"]
            if element_exists(d, id_flag):
                douyin_id = element_get_text(d, id_flag).split("抖音号: ")[1]  # 获取抖音账号
                if douyin_id == self.app_id:
                    d.press("back")
                    # await self.enter_live_broadcast_page(d)
                else:
                    d.press("back")
                    d.press("back")
                    # 重新进入新的直播间
                    await self.enter_room(d)
            else:
                logger.info("未直播（未找到账号信息）")
                wx.CallAfter(self.on_task_completed, "未直播")
        else:
            element_click(d, account_info_page["右上角按钮"])  # '···'按钮
            id_flag = account_info_page["id信息"]
            if element_exists(d, id_flag):
                douyin_id = element_get_text(d, id_flag).split("抖音号: ")[1]  # 获取抖音账号
                if douyin_id == self.app_id:
                    logger.info("未直播（未找到直播标志）")
                    wx.CallAfter(self.on_task_completed, "未直播")
                else:
                    d.press("back")
                    d.press("back")
                    # 重新进入新的直播间
                    await self.enter_room(d)
            else:
                logger.info("未直播（未找到账号信息）")
                wx.CallAfter(self.on_task_completed, "未直播")

    async def enter_live_broadcast_page(self, d):
        """
        进入账号直播页面
        """
        search_page = self.config_data.get("search_page", {})
        account_info_page = self.config_data.get("account_info_page", {})
        live_broadcast_page = self.config_data.get("live_broadcast_page", {})

        if element_click_exists(d, live_broadcast_page["直播页面1"]) or \
                element_click_exists(d, live_broadcast_page["直播页面2"]):
            logger.info("已查询到账号直播信息")
            if element_exists(d, account_info_page["直播标识"]):
                if element_click_exists(d, search_page["搜索页面3"]):
                    enter_status = self.wait_full_enter_live_broadcast(d)
                    if enter_status:
                        logger.info("成功进入直播间")
                        self.enter_live_broadcast_event.set()
                else:
                    logger.warning("无法点击头像进入直播间")
            else:
                logger.info("未直播（未找到直播标志）")
                wx.CallAfter(self.on_task_completed, "未直播")
        elif element_click_exists(d, search_page["搜索页面2"]):
            logger.info("已点击搜索按钮")
            # 从手动搜索的结果中点击头像进入直播间
            if d.xpath(search_page["账号头像"]).click_exists(timeout=1.5):
                enter_status = self.wait_full_enter_live_broadcast(d)
                if enter_status:
                    logger.info("成功进入直播间")
                    self.enter_live_broadcast_event.set()
            else:
                logger.info("账号未直播")
                wx.CallAfter(self.on_task_completed, "账号未直播")
        elif element_click_exists(d, search_page["搜索页面3"]):
            enter_status = self.wait_full_enter_live_broadcast(d)
            if enter_status:
                logger.info("成功进入直播间")
                self.enter_live_broadcast_event.set()
        else:
            logger.info("未查询到账号直播信息")
            wx.CallAfter(self.on_task_completed, "未查询到账号直播信息")

    def wait_full_enter_live_broadcast(self, d, timeout=15):
        """
        等待完全进入直播间
        :param d: 连接设备服务
        :param timeout: 最大等待时间（秒）
        :return: 是/否
        """
        start_time = time.time()
        search_page = self.config_data.get("search_page", {})
        live_broadcast_page = self.config_data.get("live_broadcast_page", {})

        while True:
            time_diff = time.time() - start_time
            if time_diff >= timeout:
                break

            if element_exists(d, live_broadcast_page["关闭按钮"]):
                return True
            logger.info("等待进入直播间...")

            if time_diff > 0 and time_diff % 3 == 0:
                # 尝试重新进入
                if d.xpath(search_page["直播主窗口"]).click_exists(timeout=0.5):
                    logger.info("检测到'点击搜索页面直播主窗口'进入")
                elif d.xpath(search_page["账号头像"]).click_exists(timeout=0.5):
                    logger.info("检测到'点击搜索页面账号头像'进入")
                elif d(search_page["搜索页面3"]).click_exists(timeout=0.5):
                    logger.info("检测到'点击账号详情头像'进入")
                else:
                    logger.info("未检测到可重新进入方式...")
            time.sleep(1)
        return False

    @staticmethod
    def on_task_completed(result):
        """
        提示弹窗
        :param result: 提示信息
        """
        wx.MessageBox(result, "提示")
