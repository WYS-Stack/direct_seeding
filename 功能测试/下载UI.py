import wx
import requests
from threading import Thread
import os
# https://d.apkpure.com/b/APK/com.ss.android.ugc.aweme?version=latest
class DownloadApp(wx.Frame):
    def __init__(self, parent, id, title):
        super(DownloadApp, self).__init__(parent, id, title, size=(400, 200))

        self.panel = wx.Panel(self)
        self.url_label = wx.StaticText(self.panel, label="下载链接:")
        self.url_text = wx.TextCtrl(self.panel)
        self.download_button = wx.Button(self.panel, label="下载")
        self.progress = wx.Gauge(self.panel, range=100)
        self.status_label = wx.StaticText(self.panel, label="")

        self.download_button.Bind(wx.EVT_BUTTON, self.start_download)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.url_label, 0, wx.ALL, 5)
        self.sizer.Add(self.url_text, 0, wx.EXPAND | wx.ALL, 5)
        self.sizer.Add(self.download_button, 0, wx.ALL, 5)
        self.sizer.Add(self.progress, 0, wx.EXPAND | wx.ALL, 5)
        self.sizer.Add(self.status_label, 0, wx.ALL, 5)

        self.panel.SetSizerAndFit(self.sizer)
        self.Show(True)

    def start_download(self, event):
        url = self.url_text.GetValue()

        if url:
            # 使用多线程执行下载任务
            download_thread = Thread(target=self.download_file, args=(url,))
            download_thread.start()
        else:
            self.update_status("请输入有效的下载链接")

    def download_file(self, url):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.69"
            }
            response = requests.get(url,headers=headers, stream=True)
            total_length = int(response.headers.get('content-length'))

            file_name = "downloaded_file.apk"
            with open(file_name, 'wb') as file:
                downloaded_length = 0
                for data in response.iter_content(chunk_size=1024):
                    downloaded_length += len(data)
                    file.write(data)
                    progress = (downloaded_length / total_length) * 100
                    wx.CallAfter(self.update_progress, progress)

            wx.CallAfter(self.update_status, "下载完成")
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            wx.CallAfter(self.update_status, f"下载失败: {str(e)}")

    def update_progress(self, progress):
        self.progress.SetValue(int(progress))

    def update_status(self, status):
        self.status_label.SetLabel(status)

if __name__ == '__main__':
    app = wx.App()
    DownloadApp(None, -1, "下载应用程序")
    app.MainLoop()
