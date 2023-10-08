import asyncio

import wx
import threading

class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="非阻塞操作示例", size=(300, 200))
        panel = wx.Panel(self)
        self.button = wx.Button(panel, label="开始操作", pos=(10, 10))
        self.Bind(wx.EVT_BUTTON, self.on_button_click, self.button)

    async def process_concurrent(self,func):
        """
        使用asyncio.gather实现协程并发
        """
        await asyncio.gather(func())

    async def listen_before_start(self):
        # 在主线程中等待操作完成
        self.task_completed_event.wait()
        print("我拿到数据了")

    def listener_before_start_thread(self):
        start_loop = asyncio.new_event_loop()  # 创建独立的事件循环
        asyncio.set_event_loop(start_loop)  # 设置事件循环为当前线程的循环
        start_loop.run_until_complete(self.process_concurrent(self.listen_before_start))  # run_until_complete：等待运行完毕
        start_loop.close()  # 关闭事件循环

    def on_button_click(self, event):
        # 创建事件对象
        self.task_completed_event = threading.Event()
        # 在单独的线程中运行阻塞操作
        threading.Thread(target=self.long_running_task).start()
        # 异步监听准备状态
        threading.Thread(target=self.listener_before_start_thread).start()

    def long_running_task(self):

        # 模拟一个长时间运行的操作
        import time
        time.sleep(5)
        result = "操作完成"
        print(result)
        # 设置事件，通知主线程操作已完成
        self.task_completed_event.set()

        wx.CallAfter(self.on_task_completed, result)

    def on_task_completed(self, result):
        # 长时间运行的操作完成后更新界面
        wx.MessageBox(result, "提示")

if __name__ == "__main__":
    app = wx.App(False)
    frame = MyFrame()
    frame.Show()
    app.MainLoop()
