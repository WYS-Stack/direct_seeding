import asyncio
import configparser
import os
import subprocess
import threading

import wx
import wx.adv
from datetime import datetime
from ppadb.client import Client as AdbClient


# 自定义窗口类MyFrame
class MyFrame(wx.Frame):
    id_open = wx.NewIdRef()
    id_save = wx.NewIdRef()
    id_quit = wx.NewIdRef()

    id_help = wx.NewIdRef()
    id_about = wx.NewIdRef()
    def __init__(self, parent, title):
        super(MyFrame, self).__init__(parent, title=title, size=(500, 500), pos=(600, 200))
        self.Bind(wx.EVT_CLOSE, self.on_close)
        # 创建一个面板，self设置当前所在的父容器为当前窗口对象
        self.panel = wx.Panel(self)

        """创建状态栏"""
        self.sb = self.CreateStatusBar()
        self.sb.SetFieldsCount(3)
        self.sb.SetStatusWidths([-2, -1, -1])
        self.sb.SetStatusStyles([wx.SB_RAISED, wx.SB_RAISED, wx.SB_RAISED])

        # 当前需要点赞的数量
        self.current_click_num = 0
        # 默认点击的坐标轴
        self.click_X = 302
        self.click_Y = 534
        # 默认点击间隔
        self.click_T = 0.1
        # 累积点赞数量
        self.total_click_num = 0

        # # 创建全局的事件循环
        self.loop = asyncio.get_event_loop()

        # 线程
        self.thread = None
        # 取消标签
        self.stop_flag = threading.Event()
        # 暂停标签
        self.pause_flag = threading.Event()
        # 等待线程
        self.wait_event = threading.Event()

        # 检测设备连接
        self.check_device_connection()

        # 主控制面板
        self.control_panel_main()

        # self._create_menubar()  # 菜单栏
        # self._create_toolbar()  # 工具栏
        # self._create_statusbar()  # 状态栏

    def _create_menubar(self):
        """创建菜单栏"""

        self.mb = wx.MenuBar()

        # 文件菜单
        m = wx.Menu()
        m.Append(self.id_open, '打开文件')
        m.Append(self.id_save, '保存文件')
        m.AppendSeparator()
        m.Append(self.id_quit, '退出系统')
        self.mb.Append(m, '文件')

        self.Bind(wx.EVT_MENU, self.on_open, id=self.id_open)
        self.Bind(wx.EVT_MENU, self.on_save, id=self.id_save)
        self.Bind(wx.EVT_MENU, self.on_quit, id=self.id_quit)

        # 帮助菜单
        m = wx.Menu()
        m.Append(self.id_help, '帮助主题')
        m.Append(self.id_about, '关于...')
        self.mb.Append(m, '帮助')

        self.Bind(wx.EVT_MENU, self.on_help, id=self.id_help)
        self.Bind(wx.EVT_MENU, self.on_about, id=self.id_about)

        self.SetMenuBar(self.mb)

    def _create_toolbar(self):
        """创建工具栏"""

        self.toolbar = self.CreateToolBar(style=wx.TB_HORZ_TEXT)  # 创建工具栏
        self.toolbar.SetToolBitmapSize((16, 16))  # 设置工具按钮的位图大小

        self.toolbar.AddTool(wx.ID_NEW, "New", wx.ArtProvider.GetBitmap(wx.ART_NEW))  # 添加工具按钮
        self.toolbar.AddTool(wx.ID_OPEN, "Open", wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN))
        self.toolbar.AddTool(wx.ID_SAVE, "Save", wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE))

        self.toolbar.Realize()  # 实现工具栏

        self.Bind(wx.EVT_TOOL, self.on_tool_click)  # 绑定工具按钮点击事件

    def on_tool_click(self, event):
        tool_id = event.GetId()

        if tool_id == wx.ID_NEW:
            print("New tool clicked")
        elif tool_id == wx.ID_OPEN:
            print("Open tool clicked")
        elif tool_id == wx.ID_SAVE:
            print("Save tool clicked")

    # def _create_statusbar(self):
    #     """创建状态栏"""
    #     self.sb.SetStatusText('状态信息:未启动', 2)

    def on_open(self, evt):
        """打开文件"""
        self.sb.SetStatusText(u'打开文件1', 1)

    def on_save(self, evt):
        """保存文件"""
        self.sb.SetStatusText(u'保存文件', 1)

    def on_quit(self, evt):
        """退出系统"""
        self.sb.SetStatusText(u'退出系统', 1)
        self.Destroy()

    def on_help(self, evt):
        """帮助"""
        self.sb.SetStatusText(u'帮助', 1)

    def on_about(self, evt):
        """关于"""
        self.sb.SetStatusText(u'关于', 1)

    def control_panel_main(self):
        """
        主控制面板
        """
        self.device_connection_success_statictext = wx.StaticText(parent=self.panel,
                                                                  label="请选择安卓模拟器:",
                                                                  pos=(10, 10))
        if hasattr(self,"device"):
            # 获取 已完全启动的 安卓模拟器名称
            choices = [device.get_properties().get("ro.boot.qemu.avd_name") for device in self.devices if
                       device.get_properties().get("sys.boot_completed") == "1"]
            if not hasattr(self, "Android_choice"):
                self.Android_choice = wx.Choice(self.panel, choices=choices, pos=(140, 10))
            else:
                self.Android_choice.Set(choices)
            self.Android_choice.Bind(wx.EVT_CHOICE, self.on_choice_selected)
            self.sb.SetStatusText('状态信息:已启动', 2)
        else:
            # 模拟器列表
            result = subprocess.run("/Users/wanghan/Library/Android/sdk/emulator/emulator -list-avds", shell=True,
                                    capture_output=True)
            Android_list = result.stdout.decode().strip().split("\n")
            if not hasattr(self, "Android_choice"):
                self.Android_choice = wx.Choice(self.panel, choices=Android_list, pos=(140, 10))
            else:
                self.Android_choice.Set(Android_list)
            if Android_list:
                # 状态栏信息
                self.sb.SetStatusText(f'模拟器信息:{Android_list[0]}', 0)
                self.sb.SetStatusText('', 1)
                self.sb.SetStatusText('状态信息:未启动', 2)
            # 初始化下拉列表
            self.on_choice_Android_selected(None)
            self.Android_choice.Bind(wx.EVT_CHOICE, self.on_choice_Android_selected)

        # 加载控件
        self.animation = wx.adv.AnimationCtrl(self.panel)
        self.animation.LoadFile("Spinner-1s-30px.gif")  # Replace with your GIF file path
        self.animation.SetPosition((400, 6))
        self.animation.Play()
        self.animation.Hide()

        # 创建静态文本(StaticText)对象，将静态文本对象放到panel面板中，所以parent参数传递的是panel，参数label是在静态文本对象上显示的文字，参数pos用于设置静态文本对象的位置
        self.input_click_statictext = wx.StaticText(parent=self.panel, label="请输入本次点赞数量：",
                                                    pos=(10, 40))
        self.input_click_text_ctrl = wx.TextCtrl(self.panel, pos=(140, 38), size=(200, -1))

        # 复选框
        self.confirm_click_statictext = wx.StaticText(parent=self.panel, label="是否启用点赞任务：",
                                                      pos=(10, 70))
        self.confirm_checkbox = wx.CheckBox(self.panel, label="启用", pos=(140, 70))

        # 配置文件
        self.button = wx.Button(self.panel, label='打开配置', pos=(255, 68))
        self.button.Bind(wx.EVT_BUTTON, self.open_config_button)

        self.start_button = wx.Button(parent=self.panel, label="开始", pos=(30, 250), size=(100, -1))
        self.start_button.Bind(wx.EVT_BUTTON, self.click_start_control)

        self.stop_button = wx.Button(parent=self.panel, label="取消", pos=(200, 250), size=(100, -1))
        self.stop_button.Bind(wx.EVT_BUTTON, self.click_cancel_control)

        self.pause_resume_button = wx.Button(parent=self.panel, label="暂停", pos=(370, 250), size=(100, -1))
        self.pause_resume_button.Bind(wx.EVT_BUTTON, self.on_pause_resume)
        self.pause_resume_button.Disable()

    def start_thread(self, target):
        """
        开始线程
        :param target:
        :return:
        """
        if self.thread is None or not self.thread.is_alive():
            self.stop_flag.clear()
            self.pause_flag.clear()
            self.thread = threading.Thread(target=target)
            self.thread.start()

    def stop_thread(self):
        """
        停止线程——点赞
            当线程存在并且处于活动状态时，
                设置等待时间为True时，任务等待会被取消
                设置停止标签为True时，会停止点赞
                恢复暂停标签为False，为True时会暂停到当前位置
        :return:
        """
        if self.thread is not None and self.thread.is_alive():
            self.wait_event.set()
            self.stop_flag.set()
            self.pause_flag.clear()

    def on_close(self, evt):
        """
        关闭主控制面板窗口"x"控件
        :param evt: 当前窗口
        :return:
        """
        self.stop_thread()
        # 主窗口关闭时，子窗口也要关闭
        if hasattr(self, "self.new_frame"):
            self.new_frame.Close()
        if hasattr(self, "device"):
            # 通过判断adb服务是否有这个安卓模拟器来决定是否已完全关闭
            cmd = f'adb -s {self.device.serial} devices'
            output = subprocess.getoutput(cmd)
            if self.device.serial in output:
                choice = wx.MessageBox('是否关闭', '安卓模拟器已启动', wx.YES_NO | wx.ICON_QUESTION)
                if choice == wx.YES:
                    # asyncio.run(self.close_simulator())
                    # 创建一个任务并添加到事件循环中
                    task = self.loop.create_task(self.close_simulator())
                    # 主进程结束前等待任务完成
                    try:
                        self.loop.run_until_complete(task)
                    finally:
                        self.loop.close()
        else:
            self.loop.close()
        evt.Skip()

    def on_choice_selected(self, event):
        """
        选择设备下拉框
        :param event:
        :return:
        """
        # 获取选中设备的索引
        selected_index = self.Android_choice.GetSelection()
        # 切换设备服务
        self.device = self.devices[selected_index]

    def on_choice_Android_selected(self, event):
        """
        选择要启动的Android设备
        :return:
        """
        selected_index = self.Android_choice.GetSelection()
        # 获取选中设备的名称
        self.selected_Android_option_name = self.Android_choice.GetString(selected_index)
        self.sb.SetStatusText(f'模拟器信息:{self.selected_Android_option_name}', 0)

    def check_device_connection(self):
        """
        检测服务是否连接
        :return:
        """
        # try:
        if not hasattr(self,"client"):
            # 连接到 ADB 服务器，默认端口伟5037
            self.client = AdbClient(host="127.0.0.1", port=5037)
        # 查看连接上的安卓设备
        self.devices = self.client.devices()

        # 没有已启动的设备，显示启动按钮
        if len(self.devices) == 0:
            #
            if hasattr(self, "Reconnect_button"):
                self.Reconnect_button.SetLabel("启动")
            else:
                self.Reconnect_button = wx.Button(parent=self.panel, label="启动", pos=(300, 10), size=(100, -1))
            self.Reconnect_button.Bind(wx.EVT_BUTTON, self.start_device)

        # 存在已启动的设备，显示关闭按钮
        else:
            if hasattr(self, "Reconnect_button"):
                self.Reconnect_button.SetLabel("关闭")
            else:
                self.Reconnect_button = wx.Button(parent=self.panel, label="关闭", pos=(300, 10), size=(100, -1))
            self.Reconnect_button.Bind(wx.EVT_BUTTON, self.stop_device)

            # 设备服务（默认值：第一个设备）
            if not hasattr(self,"device"):
                self.device = self.devices[0]

    async def listen_start_device(self):
        """
        异步监听模拟器是否已完全 "开启"
        """
        start_sleep = 0
        while True:
            if len(self.devices) > 0:
                self.device = self.devices[self.Android_choice.GetSelection()]
            # 判断设备是否已完全开启
            try:
                Android_name_list = [device.get_properties().get("ro.boot.qemu.avd_name") for device in self.devices if device.get_properties().get("sys.boot_completed") == "1"]
            except RuntimeError:
                # 如果连接超时，判定adb服务没有启动
                result = subprocess.run(['adb', 'start-server'], capture_output=True, check=True)
                if result.returncode == 0:
                    Android_name_list = []
                    self.devices = self.client.devices()
                else:
                    Android_name_list = []
                    wx.MessageBox('请检查ADB服务是否正常', '提示', wx.OK | wx.ICON_INFORMATION)
                    self.Close()
            if self.selected_Android_option_name in Android_name_list:
                self.sb.SetStatusText('状态信息:已启动', 2)
                self.animation.Hide()
                self.check_device_connection()
                break
            else:
                if start_sleep <= 30:
                    start_sleep += 1
                    self.devices = self.client.devices()
                    await asyncio.sleep(0.5)
                else:
                    # 启动失败时保持原状态信息
                    self.sb.SetStatusText('状态信息:未启动', 2)
                    wx.MessageBox('安卓模拟器启动失败', '警告', wx.YES_NO | wx.ICON_ERROR)
                    break

    def listener_start_thread(self):
        """
        启用开启监听线程
        run_until_complete：等待运行完毕
        """
        self.loop.run_until_complete(self.listen_start_device())

    def start_device(self, event):
        """
        未检测到启动设备时，启动对应的安卓模拟器
        :return:
        """
        self.sb.SetStatusText('状态信息:启动中', 2)
        self.animation.Show()
        # 异步调用开启模拟器
        asyncio.run(self.start_simulator())
        # 异步监听开启状态
        threading.Thread(target=self.listener_start_thread).start()

    async def start_simulator(self):
        """
        开启安卓模拟器
        :return:
        """
        if not hasattr(self,"selected_Android_option_name"):
            self.on_choice_Android_selected(None)
        await asyncio.create_subprocess_shell(
            f'/Users/wanghan/Library/Android/sdk/emulator/emulator -avd {self.selected_Android_option_name}',
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    async def listen_stop_device(self):
        """
        异步监听安卓模拟器是否已完全关闭
        :return:
        """
        while True:
            # 每次监听都检查关闭模拟器指令是否成功执行
            if hasattr(self, "simulator_exit_code"):
                # 如果关闭失败
                if self.simulator_exit_code is None or self.simulator_exit_code != 0:
                    self.animation.Hide()
                    wx.MessageBox('安卓模拟器关闭失败', '警告', wx.YES_NO | wx.ICON_ERROR)
                    self.sb.SetStatusText('状态信息:已启动', 2)
                    break

            # 通过判断adb服务是否有这个安卓模拟器来决定是否已完全关闭
            cmd = f'adb -s {self.device.serial} devices'
            output = subprocess.getoutput(cmd)
            if self.device.serial in output:
                await asyncio.sleep(0.5)
            else:
                del self.device
                self.animation.Hide()
                self.sb.SetStatusText('状态信息:未启动', 2)
                self.check_device_connection()
                break

    def listener_stop_thread(self):
        """
        启用关闭监听线程
        :return:
        """
        self.loop.run_until_complete(self.listen_stop_device())

    def stop_device(self,event):
        """
        关闭按钮
        :param event:
        :return:
        """
        self.animation.Show()
        self.sb.SetStatusText('状态信息:关闭中', 2)
        # 异步调用关闭模拟器
        asyncio.run(self.close_simulator())
        # 通过判断adb服务是否有这个安卓模拟器来决定是否已完全关闭
        cmd = f'adb -s {self.device.serial} devices'
        output = subprocess.getoutput(cmd)
        if self.device.serial in output:
            # 异步监听关闭状态
            threading.Thread(target=self.listener_stop_thread).start()
        else:
            self.animation.Hide()
            self.sb.SetStatusText('状态信息:已关闭', 2)

    async def close_simulator(self):
        """
        关闭安卓模拟器
        :return:
        """
        # 确保模拟器没关闭
        cmd = f'adb -s {self.device.serial} devices'
        output = subprocess.getoutput(cmd)
        if self.device.serial in output:
            process = await asyncio.create_subprocess_shell(
                f'adb -s {self.device.serial} emu kill',
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            self.simulator_exit_code = await process.wait()

    def open_config_button(self, event):
        """
        打开配置面板
        :param event:
        :return:
        """
        self.new_frame = NewFrame(None)
        self.new_frame.Bind(wx.EVT_CLOSE, self.on_close_newframe)
        self.new_frame.Show()

    def on_close_newframe(self, evt):
        """
        关闭窗口
        :param evt: 当前窗口
        :return:
        """
        # 获取配置的值
        self.new_frame.on_get_values(None)
        # 存储配置的值
        self.config_values = self.new_frame.config_values_output
        # 将事件继续传递给下一个事件处理函数
        evt.Skip()

    def click_start_control(self, evt):
        """
        点赞开始控件
        :return:
        """
        # 防止未启动设备直接开始
        if not hasattr(self, "device"):
            choice = wx.MessageBox('是否启动', '安卓模拟器未启动', wx.YES_NO | wx.ICON_QUESTION)
            if choice == wx.YES:
                self.start_device(None)
            else:
                return
        # 获取手动点赞框输入的点赞数量（第一次点击不计入）
        self.current_click_num = "" if not self.input_click_text_ctrl.GetValue() else int(
            self.input_click_text_ctrl.GetValue())
        # 获取复选框直播任务状态
        self.checked = self.confirm_checkbox.GetValue()

        # 当只输入了点赞数量，没选择执行任务时
        if self.current_click_num:
            self.total_click_num -= 1
            self.start_thread(self.click_simulator_control)
            self.start_button.Disable()
            self.pause_resume_button.SetLabel("暂停")
            self.pause_resume_button.Enable()
            self.stop_button.Enable()
        if self.checked:
            self.click_date_start = datetime.now()
            self.start_thread(self.click_task)
            self.start_button.Disable()
            self.pause_resume_button.SetLabel("暂停")
            self.pause_resume_button.Enable()
            self.stop_button.Enable()
        if not self.current_click_num and not self.checked and not self.device:
            wx.MessageBox('1.请输入点赞次数\n2.选中直播任务', '提示', wx.OK | wx.ICON_INFORMATION)

    def click_simulator_control(self):
        """
        点赞开始后的准备事项
            更新累积点赞次数
            设置模拟器内部的鼠标点击间隔
            反馈成功/失败结果
            调整按钮控件
        :return:
        """
        loop_count = 0
        batch_value = 1
        for i in range(self.current_click_num + 1):
            if hasattr(self, "globle_click_num"):
                self.globle_click_num += 1
            loop_count += 1
            # 异步调用开始点赞，并传递参数loop_count
            wx.CallAfter(self.click_simulator, loop_count)
            if self.stop_flag.is_set():
                break
            while self.pause_flag.is_set():
                wx.MilliSleep(100)
                if self.stop_flag.is_set():
                    break
            wx.MilliSleep(400)

        # 判断此次点赞任务是否完成
        if loop_count - 1 == self.current_click_num:
            if hasattr(self, "click_status_statictext"):
                self.click_status_statictext.SetLabel(f"第{batch_value}批点赞任务，已完成。成功：{loop_count - 1}个")
            else:
                self.click_status_statictext = wx.StaticText(parent=self.panel,
                                                             label=f"第{batch_value}批点赞任务，已完成。成功：{loop_count - 1}个",
                                                             pos=(10, 160))
        else:
            if hasattr(self, "click_status_statictext"):
                self.click_status_statictext.SetLabel(
                    f"本次点赞任务，未完成。失败：{self.current_click_num - loop_count}个")
            else:
                self.click_status_statictext = wx.StaticText(parent=self.panel,
                                                             label=f"第{batch_value}批点赞任务，未完成。失败：{self.current_click_num - loop_count}个",
                                                             pos=(10, 160))
        # 如果是点赞任务，当任务完全结束时开启按钮
        if self.checked:
            if self.config_value == self.config_values[-1]:
                self.pause_resume_button.Disable()
                self.start_button.Enable()
        # 当是单次点击任务时
        else:
            self.pause_resume_button.Disable()
            self.start_button.Enable()

    def click_task(self):
        """
        直播点赞任务控件
        :return:
        """
        if not hasattr(self, "self.config_values"):
            self.config_values = self.read_config()
        for config_value in self.config_values:
            click_num_total = int(config_value[0])  # 点赞总量
            self.click_T = float(config_value[1])  # 点赞间隔
            click_time_total = int(config_value[2]) * 60  # 换算分钟为秒数
            click_batch_total = int(config_value[3])  # 点赞批数
            self.config_value = config_value  # 用于记录点赞任务最后是执行完最后一次，来开启"开始"禁用"暂停/继续"按钮
            self.globle_click_num = 0
            for index, value in enumerate(range(click_batch_total)):
                # 计算本次需要点赞的数量
                if index < click_batch_total - 1:
                    self.current_click_num = round(click_num_total / click_batch_total)
                    self.total_click_num -= 1
                else:
                    self.current_click_num = click_num_total - self.globle_click_num
                    self.total_click_num -= 1
                # 开始点赞
                self.click_simulator_control()
                # 点赞结束后，需要冷却时间
                click_date_end = datetime.now()
                # time_cooling = (round(click_time_total / click_batch_total)) - (
                #             click_date_end - self.click_date_start).seconds
                time_cooling = 3
                if time_cooling > 0:
                    # 等待time_cooling秒
                    self.wait_event.wait(timeout=time_cooling)
                    # 当取消按钮被点击，self.wait_event标记会为True，并取消上一步的等待，继续执行
                    if self.wait_event.is_set():
                        self.wait_event.clear()  # 重置事件状态
                        break
                    else:
                        self.wait_event.clear()  # 重置事件状态
                self.click_date_start = click_date_end

    def click_simulator(self, loop_count):
        """
        开始点赞
            模拟器内部的鼠标点击
        :param loop_count:
        :return:
        """
        # 模拟点击屏幕上的点(302, 534)
        result = self.device.shell(f'input tap {self.click_X} {self.click_Y}')
        # 成功
        if result == "":
            self.total_click_num += 1
            if hasattr(self, "countdown_static_text1_auxiliary"):
                self.countdown_static_text1_auxiliary.SetLabel(
                    f"请稍后，点赞中······（当前点赞任务：{self.current_click_num}，点赞间隔：{self.click_T}，累计点赞：{self.total_click_num}）")
            else:
                self.countdown_static_text1_auxiliary = wx.StaticText(parent=self.panel,
                                                                      label=f"请稍后，点赞中······（当前点赞任务：{self.current_click_num}，点赞间隔：{self.click_T}，累计点赞：{self.total_click_num}）",
                                                                      pos=(10, 130))
        else:
            pass
            # TODO 需要写入日志文件
            # print(f"第{loop_count}次点击失败")

    def click_cancel_control(self, evt):
        """
        取消按钮
            1.停止线程——点赞
            2.显示开始按钮
            3.禁用取消/暂停按钮
        :param evt:
        :return:
        """
        self.stop_thread()
        self.start_button.Enable()

        self.stop_button.Disable()
        self.pause_resume_button.Disable()

    def on_pause_resume(self, evt):
        """
        暂停/继续按钮
        :param evt:
        :return:
        """
        if self.pause_flag.is_set():
            self.pause_flag.clear()
            self.pause_resume_button.SetLabel("暂停")
        else:
            self.pause_flag.set()
            self.pause_resume_button.SetLabel("继续")

    def read_config(self):
        """
        读取点赞任务的配置文件
        :return:
        """
        config_read = configparser.ConfigParser()
        config_read.read('config.ini')
        # 配置文件默认值
        default_values = []
        for section in config_read.sections():
            num = config_read[section]['num']
            interval = config_read[section]['interval']
            time = config_read[section]['time']
            batch = config_read[section]['batch']
            default_values.append((num, interval, time, batch))
        return default_values


# 配置页面
class NewFrame(wx.Frame):
    def __init__(self, parent):
        super().__init__(parent, title='配置', size=(500, 250), pos=(900, 200))

        self.panel = wx.Panel(self)

        # 静态文本和对应的输入框
        labels = [
            ('点赞总量', '每次点赞间隔', '点赞总时间', '点赞总批数'),
            ('', '', '', ''),
            ('', '', '', ''),
            ('', '', '', '')
        ]
        # 读取配置文件获取结果
        config_read = configparser.ConfigParser()
        current_parent_path = os.path.dirname(os.path.abspath(__file__))
        config_read.read(current_parent_path+'/config.ini')
        # 配置文件默认值
        default_values = []
        for section in config_read.sections():
            num = config_read[section]['num']
            interval = config_read[section]['interval']
            time = config_read[section]['time']
            batch = config_read[section]['batch']
            default_values.append((num, interval, time, batch))

        # 创建静态文本和输入框
        self.static_text_controls = []
        self.input_controls = []

        for row in range(len(labels)):
            for col, label in enumerate(labels[row]):
                if row == 0:
                    static_text = wx.StaticText(self.panel, label=label, pos=(20 + col * 120, 10 + row * 30))
                    self.static_text_controls.append(static_text)
                else:
                    input_box = wx.TextCtrl(self.panel, pos=(20 + col * 120, 10 + row * 30), size=(100, -1))
                    input_box.SetValue(default_values[row - 1][col])  # 设置输入框的默认值
                    self.input_controls.append(input_box)

        # 创建获取输入框值的按钮
        button = wx.Button(self.panel, label='保存', pos=(395, 130))
        button.Bind(wx.EVT_BUTTON, self.on_get_values)

    def on_get_values(self, event):

        self.config_values = [control.GetValue() for control in self.input_controls]

        # 将值转换成所需的形式
        self.config_values_output = [
            (self.config_values[i], self.config_values[i + 1], self.config_values[i + 2], self.config_values[i + 3]) for
            i in range(0, len(self.config_values), 4)]
        # 将转换后的值写入配置文件
        config = configparser.ConfigParser()
        for i, value in enumerate(self.config_values_output):
            section_name = f'Section{i + 1}'
            config[section_name] = {}
            config[section_name]['num'] = value[0]
            config[section_name]['interval'] = value[1]
            config[section_name]['time'] = value[2]
            config[section_name]['batch'] = value[3]

        with open('config.ini', 'w') as configfile:
            config.write(configfile)


if __name__ == '__main__':
    # 创建应用程序对象
    app = wx.App()
    # 创建窗口对象
    frm = MyFrame(parent=None, title="飞播")
    # 显示窗口
    frm.Show()
    # 进入竹事件循环
    app.MainLoop()
