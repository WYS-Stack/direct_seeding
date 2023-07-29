import wx

class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        super(MyFrame, self).__init__(parent, title=title, size=(600, 600))
        panel = wx.Panel(self)
        panel.Bind(wx.EVT_MOTION, self.OnMove)
        wx.StaticText(parent=panel, label="Pos:", pos=(10, 20))
        self.posCtrl = wx.TextCtrl(parent=panel, pos=(50, 20), size=(200, -1))

    def OnMove(self, event):
        pos = event.GetPosition()
        self.posCtrl.SetValue("%s,%s" % (pos.x, pos.y))

if __name__ == "__main__":
    app = wx.App()
    frame = MyFrame(None, title="软件功能")
    frame.Show()
    app.MainLoop()