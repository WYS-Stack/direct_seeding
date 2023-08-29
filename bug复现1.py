# TODO 复现bug：Loop <_UnixSelectorEventLoop running=False closed=True debug=False> that handles pid 8378 is closed

import asyncio
import subprocess
import threading

import wx
from ppadb.client import Client as AdbClient

class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        super(MyFrame, self).__init__(parent, title=title, size=(500, 500), pos=(600, 200))
        self.panel = wx.Panel(self)
        self.selected_Android_option_name = "Pixel_6_API_33"
        # 检测设备连接
        self.check_device_connection()
        self.check_selected_device_status()

        if hasattr(self, "Reconnect_button"):
            self.Reconnect_button.SetLabel("关闭")
        else:
            self.Reconnect_button = wx.Button(parent=self.panel, label="关闭", pos=(300, 10), size=(100, -1))
        self.Reconnect_button.Bind(wx.EVT_BUTTON, self.stop_device)
        if hasattr(self, "Reconnect_button1"):
            self.Reconnect_button1.SetLabel("启动")
        else:
            self.Reconnect_button1 = wx.Button(parent=self.panel, label="启动", pos=(150, 10), size=(100, -1))
        self.Reconnect_button1.Bind(wx.EVT_BUTTON, self.start_device)

    def check_selected_device_status(self):
        """
        检查选中的设备启动状态，来显示开启关闭，并切换服务到指定设备
        :return: 是/否
        """
        try:
            # 获取所有已启动设备的名称
            running_Android_name_dict = {}
            for index, device in enumerate(self.devices):
                cmd = f'adb -s {device.serial} shell getprop ro.boot.qemu.avd_name'
                running_name = subprocess.getoutput(cmd)
                running_Android_name_dict[running_name] = index
        except subprocess.CalledProcessError:
            running_Android_name_dict = {}
        # 下拉框选择的设备已开启
        if self.selected_Android_option_name in running_Android_name_dict:
            self.device = self.devices[running_Android_name_dict[self.selected_Android_option_name]]
            return True
        else:
            return False

    def check_device_connection(self,max_retries=3):
        """
        检测服务是否连接
        """
        for attempt in range(max_retries):
            try:
                # 连接到 ADB 服务器，默认端口为5037
                self.client = AdbClient(host="127.0.0.1", port=5037)
                # 查看连接上的安卓设备
                self.devices = self.client.devices()
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    # 尝试启动 adb 服务器
                    result = subprocess.run(['adb', 'start-server'], capture_output=True, check=True)
                    if result.returncode != 0:
                        wx.MessageBox('请检查ADB服务是否正常', '提示', wx.OK | wx.ICON_INFORMATION)
                        self.Close()
                else:
                    wx.MessageBox('请检查ADB服务是否正常', '提示', wx.OK | wx.ICON_INFORMATION)
                    self.Close()

    def check_device_in_adb_devices(self):
        """
        检查设备是否在 "adb devices" 已连接设备
        :return: 是/否
        """
        # 通过判断adb服务是否有这个安卓模拟器来决定是否已完全关闭
        cmd = f'adb -s {self.device.serial} devices'
        output = subprocess.getoutput(cmd)
        if self.device.serial in output:
            return True
        else:
            return False
    async def listen_stop_device(self):
        """
        异步监听安卓模拟器是否已完全关闭
        :return:
        """
        while True:
            # 检查关闭模拟器指令是否成功执行
            if hasattr(self, "simulator_exit_code"):
                # 如果关闭失败
                if self.simulator_exit_code is None or self.simulator_exit_code != 0:
                    wx.MessageBox('安卓模拟器关闭失败', '警告', wx.YES_NO | wx.ICON_ERROR)
                    break
                else:
                    del self.device
                    break
            else:
                status = self.check_device_in_adb_devices()
                if status:
                    await asyncio.sleep(0.5)
                else:
                    del self.device
                    break

    async def process_concurrent(self,func):
        """
        使用asyncio.gather实现协程并发
        """
        await asyncio.gather(func())

    def listener_stop_thread(self):
        """
        启用关闭监听线程
        """
        stop_loop = asyncio.new_event_loop()  # 创建独立的事件循环
        asyncio.set_event_loop(stop_loop)  # 设置事件循环为当前线程的循环
        stop_loop.run_until_complete(self.process_concurrent(self.listen_stop_device))
        stop_loop.close()  # 关闭事件循环
        print("关闭了")
    def stop_device(self, event):
        """
        关闭按钮
        """
        # 关闭前检查是否在开启状态
        status = self.check_device_in_adb_devices()
        if status:
            # 异步调用关闭模拟器
            asyncio.run(self.close_simulator())
            # 异步监听关闭状态
            threading.Thread(target=self.listener_stop_thread).start()
        else:
            del self.device

    async def close_simulator(self):
        """
        关闭安卓模拟器
        """
        process = await asyncio.create_subprocess_shell(
            f'adb -s {self.device.serial} emu kill',
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        self.simulator_exit_code = await process.wait()

    async def listen_start_device(self):
        """
        异步监听模拟器是否已完全 "开启"（启动过程中需要）
        """
        sleep_time = 0
        while True:
            status = self.check_selected_device_status()
            if status:
                break
            else:
                if sleep_time <= 30:
                    sleep_time += 1
                    self.devices = self.client.devices()
                    await asyncio.sleep(0.5)
                else:
                    wx.MessageBox('安卓模拟器启动失败', '警告', wx.YES_NO | wx.ICON_ERROR)
                    break
    def listener_start_thread(self):
        start_loop = asyncio.new_event_loop()  # 创建独立的事件循环
        asyncio.set_event_loop(start_loop)  # 设置事件循环为当前线程的循环
        start_loop.run_until_complete(self.process_concurrent(self.listen_start_device))
        start_loop.close()  # 关闭事件循环
        print("开始了")

    def start_device(self, event):
        """
        未检测到启动设备时，启动对应的安卓模拟器
        :return:
        """
        status = self.check_selected_device_status()
        if not status:
            # 异步调用开启模拟器
            asyncio.run(self.start_simulator())
            # 异步监听开启状态
            threading.Thread(target=self.listener_start_thread).start()

    async def start_simulator(self):
        """
        开启安卓模拟器
        :return:
        """
        await asyncio.create_subprocess_shell(
            f'/Users/wanghan/Library/Android/sdk/emulator/emulator -avd {self.selected_Android_option_name}',
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
if __name__ == '__main__':
    app = wx.App()
    frm = MyFrame(parent=None, title="飞播")
    frm.Show()
    app.MainLoop()
