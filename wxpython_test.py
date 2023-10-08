import wx

class MyFrame(wx.Frame):
    def __init__(self, parent, id=wx.ID_ANY, title="", pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=wx.DEFAULT_FRAME_STYLE):
        super(MyFrame, self).__init__(parent, id, title, pos, size, style)

        self.panel = wx.Panel(self)
        self.text_ctrl = wx.TextCtrl(self.panel, style=wx.TE_PROCESS_ENTER)
        self.history_popup = None
        self.history_filename = 'config/history.txt'
        self.history_list = self.read_history(self.history_filename)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.text_ctrl, 0, wx.EXPAND | wx.ALL, 10)
        self.panel.SetSizer(sizer)

        self.text_ctrl.Bind(wx.EVT_TEXT, self.on_text_change)
        self.text_ctrl.Bind(wx.EVT_TEXT_ENTER, self.on_text_enter)
        self.text_ctrl.Bind(wx.EVT_SET_FOCUS, self.on_text_focus)
        self.text_ctrl.Bind(wx.EVT_KILL_FOCUS, self.on_text_lost_focus)
        self.text_ctrl.Bind(wx.EVT_KEY_DOWN, self.on_key_down)

        self.virtual_button = wx.Button(self.panel, label="Virtual Button")
        self.virtual_button.SetFocus()
        self.virtual_button.Hide()

    def read_history(self,filename):
        """
        读取历史记录
        :param filename: 历史记录文件名
        """
        history = []
        try:
            with open(filename, 'r') as file:
                history = file.read().splitlines()
        except FileNotFoundError:
            pass
        return history

    def write_history(self):
        """
        写入历史记录
        """
        with open(self.history_filename, 'w') as file:
            file.write('\n'.join(self.history_list))

    def on_text_change(self, event):
        """
        文本框内容发生改变时，展示不同的历史记录
        :param event:
        """
        entered_text = self.text_ctrl.GetValue()
        print(entered_text)
        if entered_text:
            matching_items = [item for item in self.history_list if entered_text.lower() in item.lower()]
            print(matching_items)
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
        :param event:
        """
        entered_text = self.text_ctrl.GetValue()
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
        :param event:
        """
        if self.history_popup and self.history_popup.GetSelection() != wx.NOT_FOUND:
            selected_item = self.history_popup.GetString(self.history_popup.GetSelection())
            self.history_popup.Destroy()
            self.text_ctrl.SetValue(selected_item)
            # 设置光标在文本的末尾
            self.text_ctrl.SetInsertionPointEnd()

        if self.history_popup:
            self.history_popup.Destroy()

    def on_text_focus(self, event):
        """
        获得焦点时（默认展示4个历史记录）
        :param event:
        """
        entered_text = self.text_ctrl.GetValue()
        if not self.history_popup and not entered_text:
            self.show_history_popup(self.history_list)
        else:
            self.on_text_change(None)

    def on_text_lost_focus(self,event):
        """
        离开焦点时
        :return:
        """
        if self.history_popup:
            self.history_popup.Hide()
        self.on_text_enter(None)

    def on_key_down(self, event):
        """
        获取键盘的键位
        :param event:
        :return:
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

    def handle_down_key(self):
        """
        ⬇️下键
        """
        entered_text = self.text_ctrl.GetValue()
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

    def handle_up_key(self):
        """
        ⬆️上键
        """
        if self.history_popup:
            if self.selected_index > -1:
                self.selected_index -= 1
                self.history_popup.SetSelection(self.selected_index)

    def handle_return_key(self):
        """
        回车键
        """
        if self.history_popup and self.selected_index != -1:
            selected_item = self.history_choices[self.selected_index]
            self.text_ctrl.SetValue(selected_item)
            # 设置光标在文本的末尾
            self.text_ctrl.SetInsertionPointEnd()
            self.history_popup.Destroy()

    def show_history_popup(self,data):
        """
        展示历史记录
        :param data: 展示数据
        """
        # 存储历史记录选项的成员变量
        self.history_choices = data[:4]
        self.history_popup = wx.ListBox(self.panel, choices=self.history_choices, style=wx.LB_SINGLE)
        self.history_popup.Bind(wx.EVT_LISTBOX, self.on_listbox_select)
        # 历史记录框大小
        if len(data[:4]) > 0:
            self.history_popup.SetSize((self.text_ctrl.GetSize().GetWidth(), 16 + 18 * len(data[:4])))
        else:
            self.history_popup.Hide()
        # 历史记录框位置
        self.history_popup.SetPosition(
            (self.text_ctrl.GetPosition().x, self.text_ctrl.GetPosition().y + self.text_ctrl.GetSize().GetHeight()))
        self.selected_index = -1

if __name__ == "__main__":
    app = wx.App()
    frame = MyFrame(None, title="AutoComplete Example", size=(300, 200))
    frame.Show()
    app.MainLoop()
