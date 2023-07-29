import wx

class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        super(MyFrame, self).__init__(parent, title=title, size=(600, 600))

        # 创建主布局管理器
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self.main_sizer)

        # 创建侧边栏
        self.sidebar_panel = wx.Panel(self)
        self.sidebar_sizer = wx.BoxSizer(wx.VERTICAL)
        self.sidebar_panel.SetSizer(self.sidebar_sizer)
        self.main_sizer.Add(self.sidebar_panel, 0, wx.EXPAND)

        # 设置侧边栏背景颜色
        self.sidebar_panel.SetBackgroundColour("dark grey")

        # 创建内容区域
        self.content_panel = wx.Panel(self)
        self.content_sizer = wx.BoxSizer(wx.VERTICAL)
        self.content_panel.SetSizer(self.content_sizer)
        self.main_sizer.Add(self.content_panel, 1, wx.EXPAND)

        # 设置内容区域背景颜色
        self.content_panel.SetBackgroundColour("light grey")

        # 创建侧边栏按钮
        self.button1 = wx.Button(self.sidebar_panel, label="功能1")
        self.button2 = wx.Button(self.sidebar_panel, label="功能2")

        # 隐藏按钮边框
        self.button1.SetWindowStyleFlag(wx.NO_BORDER)
        self.button2.SetWindowStyleFlag(wx.NO_BORDER)

        # 设置按钮的背景颜色
        self.button1.SetBackgroundColour("dark grey")
        self.button2.SetBackgroundColour("dark grey")

        # 注册按钮点击事件
        self.button1.Bind(wx.EVT_BUTTON, self.on_button1_click)
        self.button2.Bind(wx.EVT_BUTTON, self.on_button2_click)

        # 将按钮添加到侧边栏布局管理器
        self.sidebar_sizer.Add(self.button1, 0, wx.EXPAND | wx.ALL, 5)
        self.sidebar_sizer.Add(self.button2, 0, wx.EXPAND | wx.ALL, 5)

        # 初始化内容区域
        self.show_content1()



    def on_button1_click(self, event):
        self.show_content1()

    def on_button2_click(self, event):
        self.show_content2()

    def show_content1(self):
        # 清空内容区域
        self.content_sizer.Clear(True)

        # 添加内容1到内容区域
        text1 = wx.StaticText(self.content_panel, label="功能1的内容")
        self.content_sizer.Add(text1, 0, wx.ALIGN_CENTER)

        # 刷新内容区域布局
        self.content_panel.Layout()

    def show_content2(self):
        # 清空内容区域
        self.content_sizer.Clear(True)

        # 添加内容2到内容区域
        text2 = wx.StaticText(self.content_panel, label="功能2的内容")
        self.content_sizer.Add(text2, 0, wx.ALIGN_CENTER)

        # 刷新内容区域布局
        self.content_panel.Layout()

if __name__ == "__main__":
    app = wx.App()
    frame = MyFrame(None, title="软件功能")
    frame.Show()
    app.MainLoop()