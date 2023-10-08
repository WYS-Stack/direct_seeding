import wx

class MyFrame(wx.Frame):
    def __init__(self, parent, id=wx.ID_ANY, title="", pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=wx.DEFAULT_FRAME_STYLE):
        super(MyFrame, self).__init__(parent, id, title, pos, size, style)

        self.panel = wx.Panel(self)
        self.text_ctrl = wx.TextCtrl(self.panel, style=wx.TE_PROCESS_ENTER)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.text_ctrl, 0, wx.EXPAND | wx.ALL, 10)
        self.panel.SetSizer(sizer)

        self.text_ctrl.Bind(wx.EVT_SET_FOCUS, self.on_text_focus)
        self.text_ctrl.Bind(wx.EVT_KILL_FOCUS, self.on_text_lost_focus)



    def on_listbox_select(self, event):
        """
        将选中的历史记录填充到文本框，并关闭历史记录
        :param event:
        """
        if self.history_popup and self.history_popup.GetSelection() != wx.NOT_FOUND:
            print(self.history_popup.GetSelection())
            selected_item = self.history_popup.GetString(self.history_popup.GetSelection())
            self.history_popup.Destroy()
            self.text_ctrl.SetValue(selected_item)

        if self.history_popup:
            self.history_popup.Destroy()

    def on_text_focus(self, event):
        # 当文本框获得焦点时，触发此事件处理程序
        print("TextCtrl has gained focus.")
        self.history_list = ['Apple', 'Banana', 'Cherry', 'Date', 'Grapes']
        self.history_popup = wx.ListBox(self.panel, choices=self.history_list[:4], style=wx.LB_SINGLE)
        # self.panel.Layout()
        self.history_popup.Bind(wx.EVT_LISTBOX, self.on_listbox_select)
        # 历史记录框大小
        self.history_popup.SetSize((self.text_ctrl.GetSize().GetWidth(), 16 + 18 * len(self.history_list[:4])))
        # 历史记录框位置
        self.history_popup.SetPosition(
            (self.text_ctrl.GetPosition().x, self.text_ctrl.GetPosition().y + self.text_ctrl.GetSize().GetHeight()))
        event.Skip()

    def on_text_lost_focus(self, event):
        # 当文本框失去焦点时，触发此事件处理程序
        self.history_popup.Hide()
        # print(self.on_listbox_select(None))

        event.Skip()

if __name__ == "__main__":
    app = wx.App()
    frame = MyFrame(None, title="TextCtrl Focus Example", size=(300, 200))
    frame.Show()
    app.MainLoop()
