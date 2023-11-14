import os
import time
import json
import random
import asyncio
import functools
import threading
import subprocess
import configparser

import wx
import wx.adv
import pandas as pd
import uiautomator2 as u2
from datetime import datetime

from PyQt5.QtWidgets import QApplication
from ppadb.client import Client as AdbClient

from logger import logger
from room.douyin_room import DouYinRoom
from app.application_program import App_Program
from config.root_directory import ROOT_DIR
from configframe.click_config_frame import ClickWindow
from configframe.comment_config_frame import CommentWindow
from room.xiaohongshu_room import XHSRoom


class FeiboFrame(wx.Frame):
    id_open = wx.NewIdRef()
    id_save = wx.NewIdRef()
    id_quit = wx.NewIdRef()

    id_help = wx.NewIdRef()
    id_about = wx.NewIdRef()

    def __init__(self, parent, title, size):
        super(FeiboFrame, self).__init__(parent, title=title, size=size, pos=(600, 200))
        self.Bind(wx.EVT_CLOSE, self.on_close_x)
        # 设置窗口的最小和最大尺寸为固定值
        self.SetMinSize(size)
        self.SetMaxSize(size)
        # 创建一个面板，self设置当前所在的父容器为当前窗口对象
        self.panel = wx.Panel(self)

        self._create_menubar()  # 菜单栏
        # self._create_toolbar()  # 工具栏
        self._create_statusbar()  # 状态栏

        # 当前需要点赞的数量
        self.current_click_num = 0
        # 累积点赞数量
        self.total_click_num = 0
        # 默认点击的坐标轴
        self.click_X = 450
        self.click_Y = 750
        # 默认点击间隔
        self.click_T = 0.1
        # 等待设备时间
        self.device_timeout = 45
        # 历史记录面板
        self.history_popup = None
        # 历史记录文件
        self.history_filename = os.path.join(ROOT_DIR, 'config', 'history.json')
        # 历史记录
        self.history_json = self.read_history(self.history_filename)

        # 检测设备连接
        self.check_device_connection()
        # 记录所有设备实时信息
        self.devices_info = {}
        # 存储当前选中的设备名称
        self.current_option = None
        # 主控制面板
        self.control_panel_main()

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

    @staticmethod
    def on_tool_click(event):
        tool_id = event.GetId()

        if tool_id == wx.ID_NEW:
            print("New tool clicked")
        elif tool_id == wx.ID_OPEN:
            print("Open tool clicked")
        elif tool_id == wx.ID_SAVE:
            print("Save tool clicked")

    def _create_statusbar(self):
        """创建状态栏"""
        self.sb = self.CreateStatusBar()
        self.sb.SetFieldsCount(3)
        self.sb.SetStatusWidths([-2, -1, -1])
        self.sb.SetStatusStyles([wx.SB_RAISED, wx.SB_RAISED, wx.SB_RAISED])

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

    @staticmethod
    def get_emulator_path():
        # 获取当前用户的主目录
        user_home = os.path.expanduser("~")
        return os.path.join(user_home, "Library/Android/sdk/emulator/emulator")

    def emulators_list(self):
        """
        模拟器列表
        :return: 所有的模拟器
        """
        # 获取当前用户的主目录
        emulator_path = self.get_emulator_path()
        result = subprocess.run(f"{emulator_path} -list-avds", shell=True, capture_output=True)
        android_list = result.stdout.decode().strip().split("\n")
        return android_list

    def control_dynamic_loading(self):
        """初始化动态加载控件（扩展）"""
        self.animation = wx.adv.AnimationCtrl(self.panel)
        loading_path = os.path.join(ROOT_DIR, 'img', 'Spinner-1s-30px.gif')
        self.animation.LoadFile(loading_path)
        self.animation.SetPosition((400, 6))
        self.animation.Play()
        self.animation.Hide()

    def control_panel_main(self):
        """
        主控制面板
        """
        # 扩展：动态加载控件
        self.control_dynamic_loading()

        # 主界面
        wx.StaticText(parent=self.panel, label="请选择模拟器:", pos=(10, 10))
        wx.StaticText(parent=self.panel, label="请选择应用程序:", pos=(10, 40))
        application_program_list = ['抖音', '小红书']
        if not hasattr(self, "Android_choice"):
            self.application_program_choice = wx.Choice(self.panel, choices=application_program_list, pos=(140, 40))
        else:
            self.application_program_choice.Set(application_program_list)
        self.choice_application_program(None)
        self.application_program_choice.Bind(wx.EVT_CHOICE, self.choice_application_program)
        # 设置初始化焦点 在当前按钮上（可任意部件）
        self.application_program_choice.SetFocus()

        # 模拟器列表
        android_list = self.emulators_list()
        if not hasattr(self, "Android_choice"):
            self.Android_choice = wx.Choice(self.panel, choices=android_list, pos=(140, 10))
        else:
            self.Android_choice.Set(android_list)
        # 初始化下拉列表，并添加开启关闭控件
        self.Android_choice.Bind(wx.EVT_CHOICE, self.choice_android_device)

        # 初始化状态栏信息
        if android_list:
            wx.CallAfter(self.sb.SetStatusText, f'模拟器信息:{android_list[0]}', 0)
            wx.CallAfter(self.sb.SetStatusText, '', 1)
            wx.CallAfter(self.sb.SetStatusText, '状态信息:未启动', 2)

        self.input_id_text = wx.StaticText(parent=self.panel, label="请输入ID：", pos=(10, 70))
        self.input_id = wx.TextCtrl(self.panel, pos=(140, 68), size=(200, -1), style=wx.TE_PROCESS_ENTER)
        self.input_id.Bind(wx.EVT_TEXT, self.on_text_change)
        self.input_id.Bind(wx.EVT_TEXT_ENTER, self.on_text_enter)
        self.input_id.Bind(wx.EVT_SET_FOCUS, self.on_text_focus)
        self.input_id.Bind(wx.EVT_KILL_FOCUS, self.on_text_lost_focus)
        self.input_id.Bind(wx.EVT_KEY_DOWN, self.on_key_down)

        self.input_click_text = wx.StaticText(parent=self.panel, label="请输入本次点赞数量：", pos=(10, 100))
        self.input_click_num = wx.SpinCtrl(self.panel, pos=(140, 98), size=(80, -1), min=0, max=999999)
        self.input_click_num.SetIncrement(10)  # 设置步进值为10

        # 复选框
        self.confirm_click_text = wx.StaticText(parent=self.panel, label="是否启用自动点赞：",
                                                      pos=(10, 130))
        self.confirm_click_checkbox = wx.CheckBox(self.panel, label="启用", pos=(140, 130))

        # 点赞配置文件
        self.click_button = wx.Button(self.panel, label='点赞配置', pos=(255, 128))
        self.click_button.Bind(wx.EVT_BUTTON, self.open_click_config)

        # 评论
        self.confirm_comment_text = wx.StaticText(parent=self.panel, label="是否启用自动评论：",
                                                        pos=(10, 160))
        self.confirm_comment_checkbox = wx.CheckBox(self.panel, label="启用", pos=(140, 160))
        # 评论配置
        self.comment_button = wx.Button(parent=self.panel, label="评论配置", pos=(255, 158))
        self.comment_button.Bind(wx.EVT_BUTTON, self.open_comment_config)

        self.start_button = wx.Button(parent=self.panel, label="开始", pos=(30, 250), size=(100, -1))
        self.start_button.Bind(wx.EVT_BUTTON, self.start_control)

        self.cancel_button = wx.Button(parent=self.panel, label="取消", pos=(200, 250), size=(100, -1))
        self.cancel_button.Bind(wx.EVT_BUTTON, self.cancel_control)

        self.pause_resume_button = wx.Button(parent=self.panel, label="暂停", pos=(370, 250), size=(100, -1))
        self.pause_resume_button.Bind(wx.EVT_BUTTON, self.pause_resume_control)

        self.choice_android_device(None)

    def unstarted_buttons(self):
        """
        未启动时的按钮状态
        :return:
        """
        self.start_button.Enable()
        self.pause_resume_button.Disable()
        self.cancel_button.Disable()

    def started_buttons(self, selected_android_option_name):
        """
        启动后的按钮状态
        """
        if self.current_option == selected_android_option_name:
            self.start_button.Disable()
            self.pause_resume_button.Enable()
            self.cancel_button.Enable()

    @staticmethod
    def read_history(filename):
        """
        读取历史记录
        :param filename: 历史记录文件名
        """
        history = {}
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                history = json.load(file)
        except FileNotFoundError:
            pass
        return history

    def write_history(self):
        """
        写入历史记录
        """
        with open(self.history_filename, 'w', encoding="utf-8") as file:
            json.dump(self.history_json, file, ensure_ascii=False, indent=4)

    def on_text_change(self, event):
        """
        文本框内容发生改变时，展示不同的历史记录
        """
        entered_text = self.input_id.GetValue()
        if entered_text:
            matching_items = [item for item in self.history_list if entered_text.lower() in item.lower()]
            if matching_items:
                if self.history_popup:
                    self.history_popup.Destroy()
                self.show_history_popup(matching_items)
            else:
                if self.history_popup:
                    self.history_popup.Destroy()
        else:
            if self.history_popup:
                self.history_popup.Destroy()
            self.on_text_focus(None)

    def on_text_enter(self, event):
        """
        文本框内回车时，将其添加到历史记录
        """
        entered_text = self.input_id.GetValue()
        if entered_text:
            matching_items = [item for item in self.history_list if entered_text.lower() in item.lower()]
            if not matching_items:
                # 将新记录插入到列表的开头
                self.history_list.insert(0, entered_text)
                # 如果历史记录超过30个，删除最早的记录
                if len(self.history_list) > 30:
                    self.history_list.pop()
                # 写入历史记录到文件
                self.write_history()

    def on_listbox_select(self, event):
        """
        将选中的历史记录填充到文本框，并关闭历史记录
        """
        if self.history_popup and self.history_popup.GetSelection() != wx.NOT_FOUND:
            selected_item = self.history_popup.GetString(self.history_popup.GetSelection())
            self.history_popup.Destroy()
            self.input_id.SetValue(selected_item)
            # 设置光标在文本的末尾
            self.input_id.SetInsertionPointEnd()

        if self.history_popup:
            self.history_popup.Destroy()

    def on_text_focus(self, event):
        """
        获得焦点时（默认展示4个历史记录）
        """
        entered_text = self.input_id.GetValue()
        if not self.history_popup and not entered_text:
            self.show_history_popup(self.history_list)
        else:
            self.on_text_change(None)

    def on_text_lost_focus(self, event):
        """
        离开焦点时
        """
        if self.history_popup:
            self.history_popup.Hide()
        self.on_text_enter(None)

    def on_key_down(self, event):
        """
        获取键盘的键位
        """
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_DOWN:
            self.handle_down_key()
        elif keycode == wx.WXK_UP:
            self.handle_up_key()
        elif keycode == wx.WXK_RETURN:
            self.handle_return_key()
        else:
            event.Skip()  # 其他键的事件继续传递

    def handle_up_key(self):
        """
        ⬆️上键
        """
        if self.history_popup:
            if self.selected_index > -1:
                self.selected_index -= 1
                self.history_popup.SetSelection(self.selected_index)

    def handle_down_key(self):
        """
        ⬇️下键
        """
        entered_text = self.input_id.GetValue()
        if entered_text:
            self.on_text_change(None)

        if self.history_popup:
            if self.selected_index == -1:
                self.selected_index = 0
            elif self.selected_index < len(self.history_choices) - 1:
                self.selected_index += 1
            self.history_popup.SetSelection(self.selected_index)
        else:
            self.show_history_popup(self.history_list)
            self.selected_index = 0
            self.history_popup.SetSelection(self.selected_index)

    def handle_return_key(self):
        """
        回车键
        """
        if self.history_popup and self.selected_index != -1:
            selected_item = self.history_choices[self.selected_index]
            self.input_id.SetValue(selected_item)
            # 设置光标在文本的末尾
            self.input_id.SetInsertionPointEnd()
            self.history_popup.Destroy()

    def show_history_popup(self, data):
        """
        展示历史记录
        :param data: 展示数据
        """
        if not data:  # 如果没有数据，则不创建或显示历史记录弹出窗
            return

        # 存储历史记录选项的成员变量
        self.history_choices = data[:4]
        self.history_popup = wx.ListBox(self.panel, choices=self.history_choices, style=wx.LB_SINGLE)
        self.history_popup.Bind(wx.EVT_LISTBOX, self.on_listbox_select)
        # 历史记录框大小
        if len(data[:4]) > 0:
            self.history_popup.SetSize((self.input_id.GetSize().GetWidth(), 16 + 18 * len(data[:4])))
        else:
            self.history_popup.Hide()
        # 历史记录框位置
        self.history_popup.SetPosition(
            (self.input_id.GetPosition().x,
             self.input_id.GetPosition().y + self.input_id.GetSize().GetHeight()))
        self.selected_index = -1

    def start_task(self, target, device, selected_android_option_name):
        """
        开始任务
        :param target: 点赞/评论任务
        :param device: 需要操作的模拟器
        :param selected_android_option_name: 当前模拟器
        """
        # 当前任务线程
        thread = threading.Thread(target=target, args=(device, selected_android_option_name))
        self.devices_info[selected_android_option_name]["current_task"] = thread
        # 当前线程运行状态
        is_running = threading.Event()
        is_running.set()
        self.devices_info[selected_android_option_name]['is_running'] = is_running
        # 暂停/继续按钮状态
        pause_resume = threading.Event()
        self.devices_info[selected_android_option_name]["pause_resume"] = pause_resume
        self.started_buttons(selected_android_option_name)
        self.devices_info[selected_android_option_name].update(
            {"start_button": False, "pause_resume_button": True, "cancel_button": True})
        thread.start()

    def stop_task(self):
        """
        停止任务
            当线程存在并且处于活动状态时：
            设置等待时间为True时，任务等待会被取消
            设置停止标签为True时，会停止点赞/评论
            恢复暂停标签为False，为True时会暂停到当前位置
        """
        selected_android_option_name = self.get_choice_android_device_name()
        if self.devices_info[selected_android_option_name].get("current_task"):
            thread = self.devices_info[selected_android_option_name]["current_task"]
            wait_event = self.devices_info[selected_android_option_name]["wait_event"]
            stop_flag = self.devices_info[selected_android_option_name]["stop_flag"]
            pause_flag = self.devices_info[selected_android_option_name]["pause_flag"]
            if thread is not None and thread.is_alive():
                wait_event.set()
                stop_flag.set()
                pause_flag.clear()

    def on_close_x(self, evt):
        """
        关闭主控制面板窗口"x"控件
        :param evt: 当前窗口
        """
        # self.stop_task()
        # 主窗口关闭时，子窗口也要关闭
        if hasattr(self, "self.config_click_frame"):
            self.config_click_frame.Close()
        # 当有模拟器启动时
        if len(self.devices) > 0:
            # 为当前线程创建独享的事件循环，避免多线程间的事件循环干扰
            closeX_loop = asyncio.new_event_loop()  # 创建独立的事件循环
            asyncio.set_event_loop(closeX_loop)  # 设置事件循环为当前线程的循环
            closeX_loop.run_until_complete(self.create_close_simulator_task())  # 创建关闭模拟器的任务
            closeX_loop.close()  # 关闭事件循环
        evt.Skip()

    async def create_close_simulator_task(self):
        """
        创建关闭模拟器的任务
        """
        tasks = [self.count_and_handle_simulators(device) for device in self.devices]
        # asyncio.gather() 是一个用于收集多个协程的函数，以便同时运行它们并等待它们完成
        await asyncio.gather(*tasks)

    async def count_and_handle_simulators(self, device):
        """
        计算需要关闭的模拟器，并根据指令来处理是否关闭这些模拟器
        :param device: 模拟器服务对象
        """
        try:
            running_name = subprocess.check_output(
                ["adb", "-s", f"{device.serial}", "shell", "getprop", "ro.boot.qemu.avd_name"],
                stderr=subprocess.DEVNULL).decode("utf-8").strip()
        except subprocess.CalledProcessError:
            return
        choice = wx.MessageBox('是否关闭', f'模拟器 {running_name} 已启动', wx.YES_NO | wx.ICON_QUESTION)
        if choice == wx.YES:
            await self.close_simulator(device=device)

    def get_choice_android_device_name(self):
        """
        获取选择设备的名称
        """
        # 获取选中设备的索引
        selected_index = self.Android_choice.GetSelection()
        # 获取选中设备的名称
        selected_android_option_name = self.Android_choice.GetString(selected_index)
        return selected_android_option_name

    def choice_android_device(self, event):
        """
        选择设备
        """
        selected_android_option_name = self.get_choice_android_device_name()
        # 开启关闭控件
        status = self.check_selected_device_status(selected_android_option_name)
        self.check_animation_status(selected_android_option_name)
        # 已开启、关闭中（显关闭按钮）
        if status in ['started', 'unstarting']:
            self.switch_off_button()
        # 开启中、未启动（显开启按钮）
        else:
            self.switch_on_button()

        self.current_option = selected_android_option_name
        if status == "started" and self.devices_info[selected_android_option_name].get("is_running"):
            if self.devices_info[selected_android_option_name]["is_running"].is_set():
                self.started_buttons(selected_android_option_name)
                if self.devices_info[selected_android_option_name]["pause_resume"].is_set():
                    self.pause_resume_button.SetLabel("继续")
                    self.devices_info[selected_android_option_name].update({"pause_resume_button": False})
                else:
                    self.pause_resume_button.SetLabel("暂停")
                    self.devices_info[selected_android_option_name].update({"pause_resume_button": True})
        else:
            self.unstarted_buttons()
            self.pause_resume_button.SetLabel("暂停")
            keys = ["start_button", "pause_resume_button", "cancel_button"]
            if all(i in self.devices_info[selected_android_option_name] for i in keys):
                state = self.devices_info[selected_android_option_name]
                self.start_button.Enable(state["start_button"])
                self.cancel_button.Enable(state["cancel_button"])
                self.pause_resume_button.Enable(state["pause_resume_button"])

    def choice_application_program(self, event):
        """选择应用程序"""
        # 获取选中应用程序的索引
        selected_index = self.application_program_choice.GetSelection()
        # 获取选中设备的名称
        self.Application_program_name = self.application_program_choice.GetString(selected_index)
        if self.Application_program_name == "抖音":
            self.history_list = self.history_json["douyin"]
        else:
            self.history_list = self.history_json["xiaohongshu"]
        if self.history_popup and self.history_popup.IsShown():
            self.history_popup.Destroy()
            self.show_history_popup(self.history_list)

    def check_device_connection(self, max_retries=3):
        """
        检测服务是否连接
        :param max_retries: 最大重试次数
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

    def switch_on_button(self):
        """
        展示启动按钮
        """
        wx.CallAfter(self.sb.SetStatusText, '状态信息:未启动', 2)
        if hasattr(self, "Reconnect_button"):
            self.Reconnect_button.SetLabel("启动")
        else:
            self.Reconnect_button = wx.Button(parent=self.panel, label="启动", pos=(300, 10), size=(100, -1))
        self.Reconnect_button.Bind(wx.EVT_BUTTON, self.start_device)

    def switch_off_button(self):
        """
        展示关闭按钮
        """
        wx.CallAfter(self.sb.SetStatusText, '状态信息:已启动', 2)
        if hasattr(self, "Reconnect_button"):
            self.Reconnect_button.SetLabel("关闭")
        else:
            self.Reconnect_button = wx.Button(parent=self.panel, label="关闭", pos=(300, 10), size=(100, -1))
        self.Reconnect_button.Bind(wx.EVT_BUTTON, self.stop_device)

    def check_animation_status(self, selected_android_option_name):
        """动态加载状态"""
        if selected_android_option_name in self.devices_info and self.devices_info[selected_android_option_name]:
            # 启动中、关闭中
            if self.devices_info[selected_android_option_name]["status"] in ["starting", "unstarting"]:
                self.animation.Show()
            # 已启动
            else:
                self.animation.Hide()
        # 未启动
        else:
            self.animation.Hide()

    def check_selected_device_status(self, selected_android_option_name):
        """
        检查选中的设备启动状态
        (用于显示开启关闭，并切换服务到指定设备)
        :return: 是/否
        """
        # 查看设备信息下是否记录有当前设备
        if selected_android_option_name in self.devices_info and self.devices_info[selected_android_option_name].get(
                "status"):
            status = self.devices_info[selected_android_option_name]["status"]
            # 已启动
            if status == "started":
                # 已启动
                return "started"
            # 启动中
            elif status == "starting":
                # 获取所有已启动设备的名称
                running_android_name = {}
                for index, device in enumerate(self.devices):
                    cmd = f'adb -s {device.serial} shell getprop ro.boot.qemu.avd_name'
                    running_name = subprocess.getoutput(cmd)
                    running_android_name[running_name] = index
                # 已启动
                if selected_android_option_name in running_android_name:
                    self.devices_info[selected_android_option_name]["server"] = self.devices[
                        running_android_name[selected_android_option_name]]
                    self.devices_info[selected_android_option_name]["status"] = "started"
                    return "started"
                # 启动中
                else:
                    return "starting"
            # 未启动、关闭中
            else:
                return status
        else:
            try:
                # 获取所有已启动设备的名称
                running_android_name = {}
                for index, device in enumerate(self.devices):
                    cmd = f'adb -s {device.serial} shell getprop ro.boot.qemu.avd_name'
                    running_name = subprocess.getoutput(cmd)
                    running_android_name[running_name] = index

                # 下拉框选择的设备已开启
                self.devices_info[selected_android_option_name] = {}
                if selected_android_option_name in running_android_name:
                    # 经检测已启动
                    self.devices_info[selected_android_option_name]["server"] = self.devices[
                        running_android_name[selected_android_option_name]]
                    self.devices_info[selected_android_option_name]["status"] = "started"
                    return "started"
                else:
                    # 未启动
                    self.devices_info[selected_android_option_name]["status"] = "unstarted"
                    return "unstarted"
            except (subprocess.CalledProcessError, KeyError) as e:
                import traceback
                logger.info(traceback.format_exc())
                return "unstarted"

    async def listen_start_device(self, selected_android_option_name):
        """
        异步监听模拟器是否已完全 "开启"（启动过程中需要）
        """
        start_time = time.time()
        while True:
            status = self.check_selected_device_status(selected_android_option_name)
            # 已启动
            if status == "started":
                self.animation.Hide()
                self.switch_off_button()
                break
            # 启动中、未启动
            elif status in ["unstarted", "starting"]:
                if time.time() - start_time < self.device_timeout:
                    self.devices = self.client.devices()
                    self.devices_info[selected_android_option_name]["status"] = "starting"
                    await asyncio.sleep(0.5)
                else:
                    # 启动超时
                    self.animation.Hide()
                    self.switch_on_button()
                    # wx.MessageBox('请重新启动模拟器', '警告', wx.YES_NO | wx.ICON_ERROR)
                    break
            else:
                self.animation.Show()
                wx.CallAfter(self.sb.SetStatusText, '状态信息:关闭中', 2)
                self.switch_on_button()
                break

    @staticmethod
    async def process_concurrent(func):
        """
        使用asyncio.gather实现协程并发
        """
        await asyncio.gather(func())

    def listener_start_thread(self, selected_android_option_name):
        """
        启用监听开启线程
        """
        # 为当前线程创建独享的事件循环，避免多线程间的事件循环干扰
        start_loop = asyncio.new_event_loop()  # 创建独立的事件循环
        asyncio.set_event_loop(start_loop)  # 设置事件循环为当前线程的循环
        listen_start_device = functools.partial(self.listen_start_device, selected_android_option_name)
        start_loop.run_until_complete(self.process_concurrent(listen_start_device))  # run_until_complete：等待运行完毕
        start_loop.close()  # 关闭事件循环

    def start_device(self, event):
        """
        未检测到启动设备时，启动对应的安卓模拟器
        """
        selected_android_option_name = self.get_choice_android_device_name()
        status = self.check_selected_device_status(selected_android_option_name)
        # 未启动
        if status == "unstarted":
            self.animation.Show()
            wx.CallAfter(self.sb.SetStatusText, '状态信息:启动中', 2)
            # 异步调用开启模拟器
            start_simulator = functools.partial(self.start_simulator, selected_android_option_name)
            asyncio.run(start_simulator())
            # 异步监听开启状态
            threading.Thread(target=self.listener_start_thread, args=(selected_android_option_name,)).start()
        elif status == "starting":
            wx.CallAfter(self.sb.SetStatusText, '状态信息:启动中', 2)
        elif status == "started":
            self.animation.Hide()
            wx.CallAfter(self.sb.SetStatusText, '状态信息:已启动', 2)
            self.switch_off_button()
        #    status == "unstarting"
        else:
            self.animation.Show()
            wx.CallAfter(self.sb.SetStatusText, '状态信息:关闭中', 2)
            self.switch_on_button()

    async def start_simulator(self, selected_android_option_name):
        """
        开启安卓模拟器
        """
        emulator_path = self.get_emulator_path()
        await asyncio.create_subprocess_shell(
            f'{emulator_path} -avd {selected_android_option_name}',
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    def check_device_in_adb_devices(self, selected_android_option_name):
        """
        检查设备是否在 "adb devices" 已连接设备
        :return: 是/否
        """
        # 查看设备信息下是否记录有当前设备
        if selected_android_option_name in self.devices_info:
            status = self.devices_info[selected_android_option_name]["status"]
            # 未启动
            if status == "unstarted":
                del self.devices_info[selected_android_option_name]
                return "unstarted"
            # 关闭中
            elif status == "unstarting":
                device = self.devices_info[selected_android_option_name]["server"]
                cmd = f'adb -s {device.serial} devices'
                output = subprocess.getoutput(cmd)
                # 关闭中
                if device.serial in output:
                    return "unstarting"
                # 未启动
                else:
                    del self.devices_info[selected_android_option_name]
                    return "unstarted"
            # 已启动、启动中
            else:
                device = self.devices_info[selected_android_option_name]["server"]
                cmd = f'adb -s {device.serial} devices'
                output = subprocess.getoutput(cmd)
                if device.serial not in output:
                    del self.devices_info[selected_android_option_name]
                    return "unstarted"
                return status
        else:
            device = self.devices_info[selected_android_option_name]["server"]
            # 通过判断adb服务是否有这个安卓模拟器来决定是否已完全关闭
            cmd = f'adb -s {device.serial} devices'
            output = subprocess.getoutput(cmd)
            if device.serial in output:
                return "started"
            else:
                # 未启动
                if self.devices_info.get(selected_android_option_name):
                    del self.devices_info[selected_android_option_name]
                return "unstarted"

    async def listen_stop_device(self, selected_android_option_name):
        """
        异步监听安卓模拟器是否已完全关闭
        :param selected_android_option_name: 选中的安卓模拟器名称
        """
        while True:
            # 检查关闭模拟器指令是否成功执行
            if hasattr(self, "simulator_exit_code"):
                # 如果关闭失败
                if self.simulator_exit_code is None or self.simulator_exit_code != 0:
                    self.animation.Hide()
                    self.switch_off_button()
                    wx.MessageBox('安卓模拟器关闭失败', '警告', wx.YES_NO | wx.ICON_ERROR)
                    break

            status = self.check_device_in_adb_devices(selected_android_option_name)
            # 已关闭
            if status == "unstarted":
                self.animation.Hide()
                self.switch_on_button()
                break
            # 已启动
            elif status == 'started':
                self.devices_info[selected_android_option_name]["status"] = "started"
                await asyncio.sleep(0.5)
            # 关闭中
            elif status == "unstarting":
                self.devices_info[selected_android_option_name]["status"] = "unstarting"
                await asyncio.sleep(0.5)
            # 启动中
            else:
                self.animation.Show()
                wx.CallAfter(self.sb.SetStatusText, '状态信息:启动中', 2)
                self.switch_off_button()
                break

    def listener_stop_thread(self, selected_android_option_name):
        """
        启用关闭监听线程
        :param selected_android_option_name: 选中的安卓模拟器名称
        """
        # 为当前线程创建独享的事件循环，避免多线程间的事件循环干扰
        stop_loop = asyncio.new_event_loop()  # 创建独立的事件循环
        asyncio.set_event_loop(stop_loop)  # 设置事件循环为当前线程的循环
        listen_stop_device = functools.partial(self.listen_stop_device, selected_android_option_name)
        stop_loop.run_until_complete(self.process_concurrent(listen_stop_device))
        stop_loop.close()  # 关闭事件循环

    def stop_device(self, event):
        """
        关闭按钮
        """
        selected_android_option_name = self.get_choice_android_device_name()
        # 关闭前检查是否在开启状态
        status = self.check_device_in_adb_devices(selected_android_option_name)
        if status == 'started':
            self.animation.Show()
            wx.CallAfter(self.sb.SetStatusText, '状态信息:关闭中', 2)
            # 异步调用关闭模拟器
            asyncio.run(self.close_simulator(selected_android_option_name=selected_android_option_name))
            # 异步监听关闭状态
            threading.Thread(target=self.listener_stop_thread, args=(selected_android_option_name,)).start()
        elif status == 'unstarting':
            wx.CallAfter(self.sb.SetStatusText, '状态信息:关闭中', 2)
        elif status == 'unstarted':
            self.animation.Hide()
            self.switch_on_button()
        #   status == 'starting'
        else:
            self.animation.Show()
            wx.CallAfter(self.sb.SetStatusText, '状态信息:启动中', 2)
            self.switch_off_button()

    async def close_simulator(self, device=None, selected_android_option_name=None):
        """
        关闭安卓模拟器
        :return:
        """
        if not device:
            device = self.devices_info[selected_android_option_name]["server"]
        process = await asyncio.create_subprocess_shell(
            f'adb -s {device.serial} emu kill',
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        self.simulator_exit_code = await process.wait()

    def open_click_config(self, event):
        """
        打开点赞配置面板
        :param event:
        """
        self.config_click_frame = ClickWindow(None)
        self.config_click_frame.Bind(wx.EVT_CLOSE, self.on_close_click_config_frame)
        self.config_click_frame.Show()

    @staticmethod
    def open_comment_config(evt):
        """
        打开评论配置面板
        """
        app = QApplication([])
        ex = CommentWindow()
        ex.show()
        app.exec_()

    def on_close_click_config_frame(self, evt):
        """
        关闭窗口
        :param evt: 当前窗口
        """
        # 获取并存储配置的值
        self.config_click_Tinfo = self.config_click_frame.on_get_values(None)
        # 将事件继续传递给下一个事件处理函数
        evt.Skip()

    def on_task_completed(self, result):
        """
        提示弹窗
        :param result: 提示信息
        """
        wx.MessageBox(result, "提示")

    async def application_program_main(self, device):
        """
        启动应用程序
        :param device: 模拟器服务
        """
        app = App_Program(self.panel, device.serial, self.Application_program_name)
        # 启动atx-agent
        await app.start_atx_agent()
        await asyncio.sleep(1)
        # 检查应用程序
        check_status = await app.check_application_program()
        if check_status:
            # 启动应用程序
            activate_status = await app.start_application_program()
            if activate_status:
                return app

    def start_control(self, evt):
        """
        开始控件
        """
        # 开始前准备工作
        threading.Thread(target=self.before_start_control_check).start()

    def before_start_control_check(self):
        """
        开始前准备工作
        """
        selected_android_option_name = self.get_choice_android_device_name()
        self.app_id = self.input_id.GetValue()
        self.current_click_num = int(self.input_click_num.GetValue())
        self.checked = self.confirm_click_checkbox.GetValue()
        self.comment_checked = self.confirm_comment_checkbox.GetValue()

        if not self.app_id:
            wx.MessageBox("用户ID不能为空！", "提示")
            return

        # 获取手动点赞框输入的点赞数量
        if not self.current_click_num and not self.checked and not self.comment_checked:
            wx.MessageBox('1.请输入点赞次数\n2.选中点赞任务\n3.选择评论任务', '提示', wx.OK | wx.ICON_INFORMATION)
            return
        elif self.current_click_num and self.current_click_num < 1:
            wx.MessageBox('点赞数量要大于0', '提示', wx.OK | wx.ICON_INFORMATION)
            return

        task_status = self.devices_info.get(selected_android_option_name, {}).get('task_status')

        if not task_status:
            task_status = "accept"
            if not self.devices_info.get(selected_android_option_name):
                self.devices_info[selected_android_option_name] = {}
            self.devices_info[selected_android_option_name]["task_status"] = "accept"

        # 防止未启动设备直接开始
        if self.devices_info.get(selected_android_option_name, {}).get("status") == "started":
            if not self.devices_info[selected_android_option_name].get("server"):
                if task_status == "accept":
                    self.wait_device_start(selected_android_option_name)
            else:
                # 避免人为关闭模拟器
                self.check_device_in_adb_devices(selected_android_option_name)
                if self.devices_info.get(selected_android_option_name):
                    device = self.devices_info[selected_android_option_name]["server"]
                    if self.devices_info.get(selected_android_option_name, {}).get('task_status') == "accept":
                        device_status = self.wait_device_full_start(device, selected_android_option_name)
                        if device_status:
                            self.before_start_control(selected_android_option_name)
                else:
                    if self.devices_info.get(selected_android_option_name, {}).get('task_status') == "accept":
                        self.wait_device_start(selected_android_option_name)
        else:
            if task_status == "accept":
                self.wait_device_start(selected_android_option_name)

    def wait_device_full_start(self, device, selected_android_option_name):
        """
        等待模拟器完全启动
        :param selected_android_option_name: 当前模拟器名称
        :param device: 模拟器服务
        :return: 是否成功
        """
        self.devices_info[selected_android_option_name]["task_status"] = "reject"
        cmd = f'adb -s {device.serial} shell getprop sys.boot_completed'
        start_time = time.time()

        while time.time() - start_time < self.device_timeout:
            output = subprocess.getoutput(cmd)
            if output == "1":
                logger.info("设备已完成启动")
                return True
            logger.info("启动中...")
            time.sleep(2)

        logger.warning("设备启动超时")
        return False

    def wait_device_start(self, selected_android_option_name):
        """
        启动并等待模拟器启动
        :param selected_android_option_name: 选中的安卓模拟器名称
        """
        choice = wx.MessageBox('是否启动', '安卓模拟器未启动', wx.YES_NO | wx.ICON_QUESTION)
        start_time = time.time()
        if choice == wx.YES:
            self.devices_info[selected_android_option_name]["task_status"] = "reject"
            # 启动
            self.start_device(None)

            while time.time() - start_time < self.device_timeout:
                if self.devices_info.get(selected_android_option_name).get("server"):
                    break
                logger.info("等待启动中...")
                time.sleep(1)

            device = self.devices_info[selected_android_option_name].get("server", "")
            if device:
                device_status = self.wait_device_full_start(device, selected_android_option_name)
                if device_status:
                    self.before_start_control(selected_android_option_name)
        else:
            self.devices_info[selected_android_option_name]["task_status"] = "accept"

    async def before_start(self, selected_android_option_name):
        """
        完成启动app、进入直播间、开始点赞
        :param selected_android_option_name: 选中的安卓模拟器名称
        """
        # 在主线程中等待开始前准备工作完成
        device = self.devices_info[selected_android_option_name]["server"]
        # 启动应用程序
        app = await self.application_program_main(device)
        if app:
            await asyncio.sleep(3)  # 给予app启动一定的加载时间
            # 进入直播间事件
            enter_live_broadcast_event = threading.Event()
            if self.Application_program_name == "抖音":
                douyin = DouYinRoom(device, self.app_id, app, enter_live_broadcast_event)
                await douyin.enter_live_broadcast_room()
            else:  # 小红书
                xhs = XHSRoom(device, self.app_id, app, enter_live_broadcast_event)
                await xhs.enter_live_broadcast_room()
            # 等待进入直播间
            if enter_live_broadcast_event.wait(timeout=3):
                # 当只输入了点赞数量，没选择执行任务时
                if self.current_click_num:
                    self.total_click_num -= 1
                    self.devices_info[selected_android_option_name]["batch_value"] = 0
                    self.start_task(self.click_simulator_control, device, selected_android_option_name)
                if self.checked:
                    self.click_date_start = datetime.now()
                    self.devices_info[selected_android_option_name]["batch_value"] = 0
                    self.start_task(self.click_task, device, selected_android_option_name)
                if self.comment_checked:
                    self.start_task(self.comment_control, device, selected_android_option_name)
            else:
                self.devices_info[selected_android_option_name]['task_status'] = 'accept'

    def before_start_control(self, selected_android_option_name):
        """
        开始前准备工作线程
        :param selected_android_option_name: 选中的安卓模拟器名称
        """
        start_loop = asyncio.new_event_loop()  # 创建独立的事件循环
        asyncio.set_event_loop(start_loop)  # 设置事件循环为当前线程的循环
        before_start = functools.partial(self.before_start, selected_android_option_name)
        start_loop.run_until_complete(self.process_concurrent(before_start))  # run_until_complete：等待运行完毕
        start_loop.close()  # 关闭事件循环

    def click_simulator_control(self, device, selected_android_option_name):
        """
        点赞开始后的准备事项
            更新累积点赞次数
            设置模拟器内部的鼠标点击间隔
            反馈成功/失败结果
            调整按钮控件
        :return:
        """
        total_likes = 0
        device_info = self.devices_info[selected_android_option_name]
        device_info["batch_value"] += 1
        batch_value = device_info["batch_value"]
        current_click_num = self.current_click_num + 1
        while current_click_num > 0 and device_info['is_running'].is_set():
            if not device_info["pause_resume"].is_set():
                if hasattr(self, "global_click_num"):
                    self.global_click_num += 1
                total_likes += 1
                current_click_num -= 1
                # 异步调用开始点赞，并传递参数total_likes
                wx.CallAfter(self.click_simulator, total_likes, device)
                wx.MilliSleep(400)

        # 判断此次点赞任务是否完成
        if total_likes - 1 == self.current_click_num:
            if hasattr(self, "click_status_static_text"):
                self.click_status_static_text.SetLabel(f"第{batch_value}批点赞任务，已完成。"
                                                       f"成功：{total_likes - 1}个")
            else:
                self.click_status_static_text = wx.StaticText(parent=self.panel,
                                                              label=f"第{batch_value}批点赞任务，已完成。"
                                                                    f"成功：{total_likes - 1}个",
                                                              pos=(10, 220))
        else:
            if hasattr(self, "click_status_static_text"):
                self.click_status_static_text.SetLabel(
                    f"第{batch_value}批点赞任务，未完成。失败：{self.current_click_num - total_likes}个")
            else:
                self.click_status_static_text = wx.StaticText(parent=self.panel,
                                                              label=f"第{batch_value}批点赞任务，未完成。"
                                                                    f"失败：{self.current_click_num - total_likes}个",
                                                              pos=(10, 220))
        # 如果是点赞任务，当任务完全结束时开启按钮
        if self.checked:
            if device_info.get("click_end_flag"):
                self.task_end_button_status(selected_android_option_name)
        # 当是单次点击任务时
        else:
            self.task_end_button_status(selected_android_option_name)

    def task_end_button_status(self, selected_android_option_name):
        """
        任务结束时按钮的状态
        """
        device_info = self.devices_info[selected_android_option_name]
        if selected_android_option_name == self.current_option:
            device_info["is_running"].clear()
            self.unstarted_buttons()
            self.pause_resume_button.SetLabel("暂停")
            device_info.update(
                {"start_button": True, "pause_resume_button": False, "cancel_button": False})
        else:
            device_info["is_running"].clear()
            device_info.update(
                {"start_button": True, "pause_resume_button": False, "cancel_button": False})
        device_info["task_status"] = "accept"

    def click_task(self, device, selected_android_option_name):
        """
        直播点赞任务控件
        :return:
        """
        if not hasattr(self, "self.config_click_Tinfo"):
            self.config_click_Tinfo = self.read_config()
        device_info = self.devices_info[selected_android_option_name]
        is_running = device_info["is_running"]
        for count, config_value in enumerate(self.config_click_Tinfo):
            click_num_total = int(config_value[0])  # 点赞总量
            self.click_T = float(config_value[1])  # 点赞间隔
            click_time_total = int(config_value[2]) * 60  # 换算分钟为秒数
            click_batch_total = int(config_value[3])  # 点赞批数
            if count == len(self.config_click_Tinfo) - 1:
                device_info["click_end_flag"] = True  # 用于记录点赞任务最后是执行完最后一次，来开启"开始"禁用"暂停/继续"按钮
            self.global_click_num = 0
            for index, value in enumerate(range(click_batch_total)):
                # 计算本次需要点赞的数量
                if index < click_batch_total - 1:
                    self.current_click_num = round(click_num_total / click_batch_total)
                    self.total_click_num -= 1
                else:
                    self.current_click_num = click_num_total - self.global_click_num
                    self.total_click_num -= 1
                # 开始点赞
                self.click_simulator_control(device, selected_android_option_name)
                # 点赞结束后，需要冷却时间
                click_date_end = datetime.now()
                time_cooling = (round(click_time_total / click_batch_total)) - (
                            click_date_end - self.click_date_start).seconds
                # time_cooling = 3 # 测试时间3秒
                if time_cooling > 0:
                    # 等待time_cooling秒
                    is_running.clear()
                    is_running.wait(timeout=time_cooling)
                    # 当取消按钮被点击，wait_event标记会为True，并取消上一步的等待，继续执行
                    if is_running.is_set():
                        is_running.set()  # 重置事件状态
                        break
                    else:
                        is_running.set()  # 重置事件状态
                self.click_date_start = click_date_end
        device_info["task_status"] = "accept"

    def click_simulator(self, total_likes, device):
        """
        开始点赞（模拟器内部的鼠标点击）
        :param total_likes: 当前任务总点赞次数
        :param device: 模拟器服务
        :return:
        """
        # 模拟点击屏幕上的点(302, 534)
        result = device.shell(f'input tap {self.click_X} {self.click_Y}')
        # 成功
        if result == "":
            self.total_click_num += 1
            if hasattr(self, "countdown_static_text1_auxiliary"):
                self.countdown_static_text1_auxiliary.SetLabel(f"请稍后，点赞中······（"
                                                               f"当前点赞任务：{self.current_click_num}，"
                                                               f"点赞间隔：{self.click_T}，"
                                                               f"累计点赞：{self.total_click_num}）")
            else:
                self.countdown_static_text1_auxiliary = wx.StaticText(parent=self.panel,
                                                                      label=f"请稍后，点赞中······（"
                                                                            f"当前点赞任务：{self.current_click_num}，"
                                                                            f"点赞间隔：{self.click_T}，"
                                                                            f"累计点赞：{self.total_click_num}）",
                                                                      pos=(10, 190))
        else:
            logger.info(f"第{total_likes}次点击失败")

    def cancel_control(self, evt):
        """
        取消按钮
            1.停止线程——点赞
            2.显示开始按钮
            3.禁用取消/暂停按钮
        """
        selected_android_option_name = self.get_choice_android_device_name()
        device_info = self.devices_info[selected_android_option_name]
        device_info["is_running"].clear()
        device_info["current_task"].join()
        if selected_android_option_name == self.current_option:
            self.unstarted_buttons()
            self.pause_resume_button.SetLabel("暂停")
            device_info.update(
                {"start_button": True, "pause_resume_button": False, "cancel_button": False})
        else:
            device_info.update(
                {"start_button": True, "pause_resume_button": False, "cancel_button": False})

    def pause_resume_control(self, evt):
        """
        暂停/继续按钮
        """
        selected_android_option_name = self.get_choice_android_device_name()
        device_info = self.devices_info[selected_android_option_name]
        pause_resume_flag = device_info["pause_resume"]
        if pause_resume_flag.is_set():
            pause_resume_flag.clear()
            self.pause_resume_button.SetLabel("暂停")
            device_info.update({"pause_status": True})
        else:
            pause_resume_flag.set()
            self.pause_resume_button.SetLabel("继续")
            device_info.update({"pause_status": False})

    def read_config(self):
        """
        读取点赞任务的配置文件
        :return: 文件默认数据
        """
        config_read = configparser.ConfigParser()
        config_path = os.path.join(ROOT_DIR, 'config', 'click_config.ini')
        config_read.read(config_path)
        # 配置文件默认值
        default_values = []
        for section in config_read.sections():
            num = config_read[section]['num']
            interval = config_read[section]['interval']
            time = config_read[section]['time']
            batch = config_read[section]['batch']
            default_values.append((num, interval, time, batch))
        return default_values

    def comment_control(self, device, selected_android_option_name):
        """
        评论控件（待完成：评论间隔，评论配置优化）
        """
        device_info = self.devices_info[selected_android_option_name]
        d = u2.connect(f"{device.serial}")

        excel_file = os.path.join(ROOT_DIR, 'config', 'comment_data.xlsx')
        # 读取Excel文件
        df = pd.read_excel(excel_file)
        # 获取DataFrame的形状
        num_rows, num_columns = df.shape

        for i in range(3):
            # 随机选择行和列的索引
            random_row_index = random.randint(0, num_rows - 1)
            random_column_index = random.randint(0, num_columns - 1)

            # 获取随机单元格的数据
            random_cell_data = df.iat[random_row_index, random_column_index]

            # 输入评论
            d(resourceId="com.ss.android.ugc.aweme:id/f32").click()
            d(focused=True).set_text(f"{random_cell_data}")
            d(resourceId="com.ss.android.ugc.aweme:id/jcq").click()

        self.pause_resume_button.Disable()
        self.start_button.Enable()
        device_info["task_status"] = "accept"


if __name__ == '__main__':
    # 创建应用程序对象
    app = wx.App()
    # 创建窗口对象
    frm = FeiboFrame(parent=None, title="", size=(500, 500))
    # 显示窗口
    frm.Show()
    # 进入主事件循环
    app.MainLoop()
