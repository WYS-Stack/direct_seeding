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

    async def enter_douyin_live_broadcast_room(self):
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

    def is_in_live_room(self, d):
        """
        检查是否已经在直播间
        """
        return d(resourceId="com.ss.android.ugc.aweme:id/c6+").exists

    async def handle_popups(self, d):
        """
        处理可能出现的弹窗
        """
        if d(resourceId="com.ss.android.ugc.aweme:id/jh").exists:
            d(resourceId="com.ss.android.ugc.aweme:id/close").click_exists()
        if d(resourceId="com.ss.android.ugc.aweme:id/rxd").exists:
            d(resourceId="com.ss.android.ugc.aweme:id/k_y").click_exists()

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
                await self.enter_douyin_live_broadcast_room()

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
        if d(resourceId="com.ss.android.ugc.aweme:id/k_8").exists:
            logger.info("确定当前为账号信息页面")
            d.press("back")
            await self.enter_douyin_live_broadcast_room()
        else:
            logger.info("未直播（未找到直播标志）")
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
            if d.xpath(  # 点击头像进入直播间
                    '//*[@resource-id="com.ss.android.ugc.aweme:id/lxd"]/android.widget.LinearLayout['
                    '1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout['
                    '1]/android.widget.FrameLayout[1]/android.widget.FrameLayout['
                    '1]/com.lynx.tasm.behavior.ui.view.UIView[3]').click_exists():
                enter_status = self.wait_full_enter_live_broadcast(d)
                if enter_status:
                    logger.info("成功进入直播间")
                    self.enter_live_broadcast_event.set()
            else:
                logger.info("未搜索到账号直播信息")
                wx.CallAfter(self.on_task_completed, "未搜索到账号直播信息")
        else:
            logger.info("未查询到账号直播信息")
            wx.CallAfter(self.on_task_completed, "未查询到账号直播信息")

    @staticmethod
    def wait_full_enter_live_broadcast(d, timeout=30):
        """
        等待完全进入直播间
        :param d: 连接设备服务
        :param timeout: 最大等待时间（秒）
        :return:
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            if d(resourceId="com.ss.android.ugc.aweme:id/c6+").exists:
                return True
            logger.info("等待进入直播间...")
            time.sleep(1)
        return False

    def on_task_completed(self, result):
        """
        提示弹窗
        :param result: 提示信息
        """
        wx.MessageBox(result, "提示")
