import wx
import threading
import asyncio
import subprocess

class ADBListener:
    def __init__(self, device, output_text):
        self.device = device
        self.output_text = output_text
        self.loop = asyncio.new_event_loop()

    async def listen_for_device(self):
        while True:
            cmd = 'adb devices'
            output = subprocess.getoutput(cmd)
            if self.device.serial in output:
                wx.CallAfter(self.append_output, "设备已连接\n")
                break
            else:
                wx.CallAfter(self.append_output, "暂时未连接\n")
                await asyncio.sleep(1)

    async def main(self):
        await self.listen_for_device()

        while True:
            wx.CallAfter(self.append_output, "我是主进程我还在\n")
            await asyncio.sleep(1)

    def append_output(self, text):
        self.output_text.AppendText(text)

    def run(self):
        self.loop.run_until_complete(self.main())

class Device:
    def __init__(self, serial):
        self.serial = serial

class MyFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super(MyFrame, self).__init__(*args, **kw)

        self.panel = wx.Panel(self)
        self.output_text = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.start_button = wx.Button(self.panel, label="启动监听")
        self.start_button.Bind(wx.EVT_BUTTON, self.on_start_button)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.output_text, 1, wx.EXPAND | wx.ALL, 10)
        sizer.Add(self.start_button, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        self.panel.SetSizer(sizer)

    def start_listener_thread(self):
        self.output_text.Clear()
        device = Device("emulator-5554")
        listener = ADBListener(device, self.output_text)
        listener.run()

    def on_start_button(self, event):
        threading.Thread(target=self.start_listener_thread).start()

if __name__ == "__main__":
    app = wx.App(False)
    frame = MyFrame(None, title="ADB Listener")
    frame.Show()
    app.MainLoop()
