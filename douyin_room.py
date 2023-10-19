import time

import wx

import uiautomator2 as u2
from logger import logger


class DouYinRoom:
    def __init__(self, device, app_id, app_server, enter_live_broadcast_event):
        self.device = device
        self.app_id = app_id
        self.app = app_server
        self.enter_live_broadcast_event = enter_live_broadcast_event

    async def enter_live_broadcast_room(self):
        """
        进入抖音直播间的主函数
        """
        d = u2.connect(f"{self.device.serial}")
        await self.enter_room(d)

    async def enter_room(self, d):
        """
        进入直播间的流程控制函数
        """
        if not self.is_in_live_room(d):
            await self.handle_popups(d)
            await self.enter_search_page(d)
            await self.enter_live_broadcast_page(d)
        else:
            logger.info("已进入直播间")
            self.enter_live_broadcast_event.set()

    @staticmethod
    def is_in_live_room(d):
        """
        检查是否已经在直播间
        """
        return d(resourceId="com.ss.android.ugc.aweme:id/c6+").exists

    @staticmethod
    async def handle_popups(d):
        """
        处理可能出现的弹窗
        """
        if d(resourceId="com.ss.android.ugc.aweme:id/jh").exists:
            d(resourceId="com.ss.android.ugc.aweme:id/close").click_exists()
        if d(resourceId="com.ss.android.ugc.aweme:id/rxd").exists:
            d(resourceId="com.ss.android.ugc.aweme:id/k_y").click_exists()
        if d(resourceId="com.ss.android.ugc.aweme:id/io4").exists:
            d(resourceId="com.ss.android.ugc.aweme:id/q0").click_exists()
        if d.xpath('//*[@resource-id="com.ss.android.ugc.aweme:id/content_layout"]').exists:
            d(resourceId="com.ss.android.ugc.aweme:id/d05").click_exists()
        if d(resourceId="com.android.permissioncontroller:id/content_container").exists:
            d(resourceId="com.android.permissioncontroller:id/permission_allow_button").click_exists()
        if d.xpath(
                '//*[@resource-id="com.android.permissioncontroller:id/content_container"]/android.widget'
                '.LinearLayout[1]').exists:
            d(resourceId="com.android.permissioncontroller:id/permission_deny_button").click_exists()

    async def login(self, d, phone:str, code:str):
        """
        登陆
        """
        # 手机号登陆
        if d.xpath('//*[@resource-id="com.ss.android.ugc.aweme:id/aw"]/android.view.ViewGroup[1]').exists:
            logger.info("进入登陆界面")
            d(resourceId="com.ss.android.ugc.aweme:id/qc6").click_exists()
            d(resourceId="com.ss.android.ugc.aweme:id/o_i").send_keys(phone)
            d(resourceId="com.ss.android.ugc.aweme:id/hxh").click_exists()
            if d.xpath('//android.widget.RelativeLayout/android.widget.FrameLayout[1]').exists:
                self.on_task_completed("请打开模拟器手动验证")
                if d.xpath('//android.widget.RelativeLayout/android.widget.FrameLayout[1]').wait_gone():
                    d(resourceId="com.ss.android.ugc.aweme:id/tq3").send_keys(code)
                    d(resourceId="com.ss.android.ugc.aweme:id/login").click_exists()
        # 账号密码登陆
        else:
            pass

    async def enter_search_page(self, d):
        """
        进入搜索页面
        """
        if d(resourceId="com.ss.android.ugc.aweme:id/j1+").wait() or \
                d(resourceId="com.ss.android.ugc.aweme:id/xkp").wait() or \
                d(resourceId="com.ss.android.ugc.aweme:id/o2z").wait():
            if d(resourceId="com.ss.android.ugc.aweme:id/j1+").click_exists():
                await self.enter_home_page(d)
            elif d(resourceId="com.ss.android.ugc.aweme:id/xkp").exists:
                await self.enter_search_result_page(d)
            elif d(resourceId="com.ss.android.ugc.aweme:id/o2z").exists:
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
        d(focused=True).set_text(f"{self.app_id}")  # 输入ID
        logger.info("已输入ID")
        # await self.enter_live_broadcast_page(d)

    async def enter_search_result_page(self, d):
        """
        进入搜索结果页面
        """
        logger.info("确定当前为搜索页面")
        d(focused=True).set_text(f"{self.app_id}")  # 输入ID
        logger.info("已输入ID")
        # await self.enter_live_broadcast_page(d)

    async def enter_account_info_page(self, d):
        """
        进入账号信息页面
        """
        logger.info("确定当前为账号信息页面")
        if d(resourceId="com.ss.android.ugc.aweme:id/k_8").exists():  # 直播标识
            d(resourceId="com.ss.android.ugc.aweme:id/vcj").click()  # '···'按钮
            id_flag = d(resourceId="com.ss.android.ugc.aweme:id/re+")
            if id_flag.exists:
                douyin_id = id_flag.get_text().split("抖音号: ")[1]  # 获取抖音账号
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
            d(resourceId="com.ss.android.ugc.aweme:id/vcj").click()  # '···'按钮
            id_flag = d(resourceId="com.ss.android.ugc.aweme:id/re+")
            if id_flag.exists:
                douyin_id = id_flag.get_text().split("抖音号: ")[1]  # 获取抖音账号
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
        if d(resourceId="com.ss.android.ugc.aweme:id/cw").click_exists() or \
                d(resourceId="com.ss.android.ugc.aweme:id/uej").click_exists():
            logger.info("已查询到账号直播信息")
            if d(resourceId="com.ss.android.ugc.aweme:id/k_8").exists:
                if d(resourceId="com.ss.android.ugc.aweme:id/o2z").click_exists():
                    enter_status = self.wait_full_enter_live_broadcast(d)
                    if enter_status:
                        logger.info("成功进入直播间")
                        self.enter_live_broadcast_event.set()
                else:
                    logger.warning("无法点击头像进入直播间")
            else:
                logger.info("未直播（未找到直播标志）")
                wx.CallAfter(self.on_task_completed, "未直播")
        elif d(resourceId="com.ss.android.ugc.aweme:id/xkp").click_exists():
            logger.info("已点击搜索按钮")
            # 从手动搜索的结果中点击头像进入直播间
            if d.xpath(
                    '//*[@resource-id="com.ss.android.ugc.aweme:id/lxd"]/android.widget.LinearLayout['
                    '1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout['
                    '1]/android.widget.FrameLayout[1]/android.widget.FrameLayout['
                    '1]/com.lynx.tasm.behavior.ui.view.UIView[3]').click_exists(timeout=1.5):
                enter_status = self.wait_full_enter_live_broadcast(d)
                if enter_status:
                    logger.info("成功进入直播间")
                    self.enter_live_broadcast_event.set()
            else:
                logger.info("未搜索到账号直播信息")
                wx.CallAfter(self.on_task_completed, "未搜索到账号直播信息")
        elif d(resourceId="com.ss.android.ugc.aweme:id/o2z").click_exists():
            enter_status = self.wait_full_enter_live_broadcast(d)
            if enter_status:
                logger.info("成功进入直播间")
                self.enter_live_broadcast_event.set()
        else:
            logger.info("未查询到账号直播信息")
            wx.CallAfter(self.on_task_completed, "未查询到账号直播信息")

    @staticmethod
    def wait_full_enter_live_broadcast(d, timeout=15):
        """
        等待完全进入直播间
        :param d: 连接设备服务
        :param timeout: 最大等待时间（秒）
        :return: 是/否
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            if d(resourceId="com.ss.android.ugc.aweme:id/c6+").exists:
                return True
            logger.info("等待进入直播间...")
            # 尝试重新进入
            if d.xpath(
                    '//*[@resource-id="com.ss.android.ugc.aweme:id/lxd"]/android.widget.LinearLayout['
                    '2]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout['
                    '1]/android.widget.FrameLayout[1]/android.widget.FrameLayout['
                    '1]/com.lynx.tasm.behavior.ui.LynxFlattenUI[3]').click_exists(timeout=0.5):
                logger.info("尝试点击搜索页面直播主窗口进入")
            if d.xpath(
                    '//*[@resource-id="com.ss.android.ugc.aweme:id/lxd"]/android.widget.LinearLayout['
                    '1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout['
                    '1]/android.widget.FrameLayout[1]/android.widget.FrameLayout['
                    '1]/com.lynx.tasm.behavior.ui.view.UIView[3]').click_exists(timeout=0.5):
                logger.info("尝试点击搜索页面账号头像进入")
            if d(resourceId="com.ss.android.ugc.aweme:id/o2z").click_exists(timeout=0.5):
                logger.info("尝试点击账号详情头像进入")
        return False

    @staticmethod
    def on_task_completed(result):
        """
        提示弹窗
        :param result: 提示信息
        """
        wx.MessageBox(result, "提示")
