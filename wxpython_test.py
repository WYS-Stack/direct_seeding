import wx
import threading
import time

class MyFrame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(300, 200))
        self.panel = wx.Panel(self)
        self.tasks = {}
        self.current_option = None  # 存储当前选中的选项

        self.start_button = wx.Button(self.panel, label="开始")
        self.pause_button = wx.Button(self.panel, label="暂停", style=wx.BU_LEFT)
        self.cancel_button = wx.Button(self.panel, label="取消")
        self.choice = wx.Choice(self.panel, choices=["选项1", "选项2"])
        self.choice.SetSelection(0)

        self.Bind(wx.EVT_BUTTON, self.on_start, self.start_button)
        self.Bind(wx.EVT_BUTTON, self.on_pause, self.pause_button)
        self.Bind(wx.EVT_BUTTON, self.on_cancel, self.cancel_button)
        self.Bind(wx.EVT_CHOICE, self.on_choice, self.choice)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.start_button, 0, wx.ALL, 10)
        sizer.Add(self.pause_button, 0, wx.ALL, 10)
        sizer.Add(self.cancel_button, 0, wx.ALL, 10)
        sizer.Add(self.choice, 0, wx.ALL, 10)

        self.panel.SetSizer(sizer)
        self.disable_buttons()

    def disable_buttons(self):
        # 禁用按钮
        self.start_button.Enable()
        self.pause_button.Disable()
        self.cancel_button.Disable()

    def enable_buttons(self):
        # 启用按钮
        self.start_button.Enable()
        self.pause_button.Enable()
        self.cancel_button.Enable()

    def on_start(self, event):
        # 当“开始”按钮被点击时
        option = self.choice.GetString(self.choice.GetSelection())
        # 如果选项不存在于timers字典或选项的线程未启动
        if option not in self.tasks or not self.tasks[option]["thread"].is_alive():
            self.tasks[option] = {}
            self.tasks[option]["thread"] = threading.Thread(target=self.countdown_thread, args=(option,))
            is_running = threading.Event()
            is_running.set()
            self.tasks[option]['is_running'] = is_running
            paused = threading.Event()
            self.tasks[option]["paused"] = paused
            self.enable_buttons()
            self.start_button.Disable()
            self.tasks[option].update({"start_status": False, "pause_status": True, "cancel_status": True})
            self.current_option = option

            self.tasks[option]["thread"].start()

    def on_pause(self, event):
        # 当“暂停”按钮被点击时
        option = self.choice.GetString(self.choice.GetSelection())
        if option in self.tasks:
            if self.tasks[option]["paused"].is_set():
                self.tasks[option]["paused"].clear()
                self.pause_button.SetLabel("暂停")
                self.tasks[option].update({"pause_status": True})
            else:
                self.tasks[option]["paused"].set()
                self.pause_button.SetLabel("继续")
                self.tasks[option].update({"pause_status": False})

    def on_cancel(self, event):
        # 当“取消”按钮被点击时
        option = self.choice.GetString(self.choice.GetSelection())
        if option in self.tasks:
            self.tasks[option]["is_running"].clear()
            self.tasks[option]["thread"].join()
            if option == self.current_option:
                self.disable_buttons()
                self.start_button.SetLabel("开始")
                self.pause_button.SetLabel("暂停")
                self.tasks[option].update({"start_status": True, "pause_status": False, "cancel_status": False})
            else:
                self.tasks[option].update({"start_status": True, "pause_status": False, "cancel_status": False})

    def on_choice(self, event):
        # 当选项框的选项被切换时
        option = self.choice.GetString(self.choice.GetSelection())
        self.current_option = option
        if option in self.tasks and self.tasks[option]["is_running"].is_set():
            self.enable_buttons()
            if self.tasks[option]["is_running"].is_set():
                self.start_button.Disable()
                if self.tasks[option]["paused"].is_set():
                    self.pause_button.SetLabel("继续")
                    self.tasks[option].update({"pause_status": False})
                else:
                    self.pause_button.SetLabel("暂停")
                    self.tasks[option].update({"pause_status": True})
        else:
            self.disable_buttons()
            self.pause_button.SetLabel("暂停")
            if option in self.tasks:
                state = self.tasks[option]
                self.start_button.Enable(state["start_status"])
                self.pause_button.Enable(state["pause_status"])
                self.cancel_button.Enable(state["cancel_status"])

    def countdown_thread(self, option):
        # 倒计时线程函数
        countdown = 10
        while countdown > 0 and self.tasks[option]["is_running"].is_set():
            if not self.tasks[option]["paused"].is_set():
                print(f"倒计时 ({option}): {countdown}")
                time.sleep(1)
                countdown -= 1
        if self.tasks[option]["is_running"].is_set():
            if option == self.current_option:
                print(f"倒计时 ({option}) 结束")
                self.tasks[option]["is_running"].clear()
                self.disable_buttons()
                self.start_button.SetLabel("开始")
                self.pause_button.SetLabel("暂停")
                self.tasks[option].update({"start_status": True, "pause_status": False, "cancel_status": False})
            else:
                print(f"倒计时 ({option}) 结束")
                self.tasks[option]["is_running"].clear()
                self.tasks[option].update({"start_status": True, "pause_status": False, "cancel_status": False})

app = wx.App()
frame = MyFrame(None, -1, "倒计时示例")
frame.Show()
app.MainLoop()
