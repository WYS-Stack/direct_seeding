import wx
import wx.adv


class GifFrame(wx.Frame):
    def __init__(self, parent, title):
        super().__init__(parent, title=title, size=(400, 300))
        self.panel = wx.Panel(self)
        self.animation = wx.adv.AnimationCtrl(self.panel)
        self.animation.LoadFile("Spinner-1s-30px.gif")  # Replace with your GIF file path
        self.animation.SetPosition((360, 10))
        self.animation.Play()
        self.animation.Hide()

        self.start_button = wx.Button(self.panel, label="Start Animation",pos=(200, 10))
        self.Bind(wx.EVT_BUTTON, self.start_animation, self.start_button)
        self.stop_button = wx.Button(self.panel, label="Stop Animation",pos=(200, 100))
        self.Bind(wx.EVT_BUTTON, self.stop_animation, self.stop_button)

        self.Center()
        self.Show()

    def stop_animation(self, event):
        self.animation.Hide()

    def start_animation(self, event):
        self.animation.Show()


if __name__ == "__main__":
    app = wx.App(False)
    frame = GifFrame(None, "GIF Viewer")
    app.MainLoop()
