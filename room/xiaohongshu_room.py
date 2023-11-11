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
    element_get_text,
    element_click_text
)

class XHSRoom:
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
            config_data = json.load(json_file)["xiaohongshu"]
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
        await XHSRoom.process_popup(d, popup["服务条款"], popup["同意条款"])
        await XHSRoom.process_popup(d, popup["系统通知"], popup["关闭系统通知"])
        await XHSRoom.process_popup(d, popup["未开启通知时推荐的弹窗"], popup["关闭推荐弹窗"], use_xpath=True)
        await XHSRoom.process_popup(d, popup["兴趣弹窗"], popup["跳过兴趣弹窗"], use_xpath=True)
        await XHSRoom.process_popup(d, popup["升级完整版"], popup["关闭升级窗口"])
        await XHSRoom.process_popup(d, popup["电话授权"], popup["拒绝电话授权"])
        if element_exists(d, popup["权限说明"], use_xpath=True):
            element_click_text(d, popup["取消权限"])

    async def login(self, d, phone: str, code: str, config_data):
        """
        处理登录界面
        :param d:
        """
        phone_login_page = config_data.get("phone_login_page", {})
        # 验证码登陆
        if element_exists(d, phone_login_page["登录界面"], use_xpath=True):
            element_click(d, phone_login_page["Log In 按钮"])
            element_send_keys(d, phone_login_page["输入框（手机号）"], phone)
            element_click(d, phone_login_page["政策条款（必须）"])
            element_click(d, phone_login_page["登录按钮"])
            # 验证码输入正确自动登录
            element_send_keys(d, phone_login_page["输入框（验证码）"], code)
        # 密码登录

    async def enter_search_page(self, d):
        """
        进入搜索页面
        """
        search_page = self.config_data.get("search_page", {})
        if element_wait(d, search_page["首页搜索按钮"]) or element_wait(d, search_page["搜索页面"]) or element_wait(d, search_page["账号信息页"]):
            if element_click_exists(d, search_page["首页搜索按钮"]):
                await self.enter_home_page(d)
            elif element_exists(d, search_page["搜索页面"]):
                await self.enter_search_result_page(d)
            elif element_exists(d, search_page["账号信息页"]):
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

    async def enter_search_result_page(self, d):
        """
        进入搜索结果页面
        """
        logger.info("确定当前为搜索页面")
        search_page = self.config_data.get("search_page", {})
        if element_exists(d, search_page["输入框（有值后的）"]):
            element_click(d, search_page["输入框（有值后的）"])
        element_set_text(d, self.app_id)  # 输入ID
        logger.info("已输入ID")

        element_click_exists(d, search_page["搜索按钮"])
        logger.info("已点击搜索按钮")

    async def enter_account_info_page(self, d):
        """
        进入账号信息页面
        """
        logger.info("确定当前为账号信息页面")
        d.press("back")
        d.press("back")
        # 重新进入新的直播间
        await self.enter_room(d)

    async def enter_live_broadcast_page(self, d):
        """
        进入账号直播页面
        """
        search_page = self.config_data.get("search_page", {})
        if element_exists(d, search_page["头像（用于进入直播间）"]):
            element_click(d, search_page["头像（用于进入直播间）"])
            enter_status = self.wait_full_enter_live_broadcast(d)
            if enter_status:
                logger.info("成功进入直播间")
                self.enter_live_broadcast_event.set()
        else:
            logger.info("账号未直播")
            wx.CallAfter(self.on_task_completed, "账号未直播")

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
                if element_click_exists(d, search_page["头像（用于进入直播间）"]):
                    logger.info("检测到'点击搜索页面 搜索结果的头像'进入")
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
