import requests
import os
import wx
import traceback
import subprocess
import asyncio
import aiohttp
from lxml import html
from threading import Thread
from logger import logger


class App_Program:
    def __init__(self, panel, serial, Application_program_name):
        self.panel = panel
        self.serial = serial
        self.app_name = Application_program_name

        # 应用程序对应的来源地址和url
        application_package_name = {"抖音": {
                                        "package_name": "com.ss.android.ugc.aweme",
                                        "url": "https://apkpure.com/cn/douyin/com.ss.android.ugc.aweme/download"
                                               "#google_vignette"},
                                    "小红书": {
                                        "package_name": "com.xingin.xhs",
                                        "url": "https://apkpure.com/cn/%E5%B0%8F%E7%BA%A2%E4%B9%A6-%E2%80%93-%E4%BD"
                                               "%A0%E7%9A%84%E7%94%9F%E6%B4%BB%E6%8C%87%E5%8D%97/com.xingin.xhs"
                                               "/download"}}
        self.url = application_package_name[self.app_name]["url"]
        self.package_name = application_package_name[self.app_name]["package_name"]
        # 下载状态
        self.status_label = wx.StaticText(self.panel, label="", pos=((220, 40)))
        logger.info(f"----------当前序列号：{serial}--------------------")

    async def request_latest_download_info(self):
        """
        请求最新的下载信息
        """
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.69"
        }
        timeout = aiohttp.ClientTimeout(total=10)  # 设置超时时间为10秒
        conn = aiohttp.TCPConnector(limit_per_host=5)  # 设置每个主机的连接限制
        async with aiohttp.ClientSession(connector=conn, timeout=timeout) as session:
            async with session.get(self.url, headers=self.headers) as response:
                if response.status == 200:
                    data = await response.text()
                    # 使用lxml解析页面内容
                    tree = html.fromstring(data)
                    version_element = tree.xpath('/html/body/div[3]/main/div[1]/div/span[3]/span')[0]
                    version = version_element.text_content()
                    download_url = tree.xpath('/html/body/div[3]/main/div[7]/a[1]/@href')[0]
                    return version, download_url

    async def check_application_version(self):
        """
        检查应用程序版本号
        :return: 本地应用程序版本
        """
        cmd = "adb -s {} shell dumpsys package {} | grep 'versionName' | awk -F= '{{print $2}}'".format(self.serial,
                                                                                                        self.package_name)
        while True:
            application_version = subprocess.getoutput(cmd)
            logger.info(f"检测本地App版本：{application_version}")
            logger.info(f"{cmd}")

            if "." in application_version:
                return application_version

            await asyncio.sleep(1)

    async def compare_version(self, version, local_version):
        """
        比较版本大小
        :param version: 线上最新版本
        :param local_version: 本地版本
        :return: 版本之差
        """
        # 将版本号字符串分割成数字部分
        v1 = list(map(int, version.split('.')))
        v2 = list(map(int, local_version.split('.')))

        # 找到较长版本号的长度，以便在较短版本号的末尾添加零
        max_len = max(len(v1), len(v2))
        while len(v1) < max_len:
            v1.append(0)
        while len(v2) < max_len:
            v2.append(0)

        # 逐个比较版本号的数字部分
        for i in range(max_len):
            if v1[i] > v2[i]:
                return v1[i] - v2[i]
            elif v1[i] < v2[i]:
                return v1[i] - v2[i]

        # 如果所有数字部分都相同，版本号相同
        return 0

    async def check_application_program(self):
        """
        检查设备是否有该应用程序
        """
        cmd = f'adb -s {self.serial} shell pm list packages | grep {self.package_name}'
        logger.info(f"检查App是否存在：{cmd}")
        Application_program_status = subprocess.getoutput(cmd)
        version, download_url = await self.request_latest_download_info()
        logger.info(f"App最新版本：{version}")
        logger.info(f"App最新apk地址：{download_url}")
        # 应用程序存在时 比较版本
        if Application_program_status:
            logger.info("APP状态：存在")
            if version and download_url:
                # 已安装版本
                local_version = await self.check_application_version()
                # 版本不一致
                difference = await self.compare_version(version, local_version)
                if difference >= 2:
                    logger.info(f"App本地版本：{local_version}")
                    uninstall_status = await self.uninstall_application_program()
                    if uninstall_status == "Success":
                        wx.CallAfter(self.update_status, "卸载成功")
                    else:
                        wx.CallAfter(self.update_status, "卸载失败")
                    await self.start_download(version, download_url)
                    await self.install_Application_Program(version)
                else:
                    logger.info("App版本通过！")
            else:
                logger.info("App最新版本和下载地址请求错误！")
        # 应用程序不存在时 直接下载安装
        else:
            logger.info("APP状态：不存在")
            if version and download_url:
                await self.start_download(version, download_url)
                await self.install_Application_Program(version)
            else:
                logger.info("App最新版本和下载地址请求错误！")

    def download_file(self, url, file_name):
        """
        下载apk
        :param url: apk下载地址
        :param file_name: 文件名
        :return:
        """
        with requests.get(url, headers=self.headers, stream=True) as response:
            total_length = int(response.headers.get('content-length'))
            if response.status_code == 200:
                with open(file_name, 'wb') as file:
                    downloaded_length = 0
                    for chunk in response.iter_content(chunk_size=1024):
                        downloaded_length += len(chunk)
                        if chunk:
                            file.write(chunk)
                            progress = downloaded_length / total_length
                            wx.CallAfter(self.update_progress, progress)
                wx.CallAfter(self.update_status, "下载完成")
                logger.info("App下载完成")
            else:
                wx.CallAfter(self.update_status, "下载失败")
                logger.info("App下载失败")

    async def start_download(self, version, download_url):
        """
        开始下载
        :param version: 版本号
        :param download_url: apk下载地址
        :return:
        """
        file_name = f"{self.app_name}_{version}.apk"
        if not os.path.isfile(file_name):
            try:
                logger.info(f"开始下载{file_name}.apk")
                # 下载进度条
                self.progress = wx.Gauge(self.panel, range=100, pos=(220, 40))
                self.download_file(download_url, file_name)
            except Exception as e:
                logger.info(traceback.format_exc())
                wx.CallAfter(self.update_status, f"下载失败: {str(e)}")
        else:
            wx.CallAfter(self.update_status, "下载地址错误")
            logger.info("App下载地址错误")

    def update_progress(self, progress):
        """
        更新进度条
        :param progress:
        """
        self.progress.SetValue(int(progress * 100))

    def update_status(self, status):
        self.status_label.SetLabel(status)

    async def install_Application_Program(self, version):
        """
        安装应用程序
        """
        cmd = f'adb -s {self.serial} install -r ./{self.app_name}_{version}.apk'
        logger.info(f"开始安装App：{cmd}")
        self.install_status = subprocess.getoutput(cmd)
        if self.install_status.replace("Performing Streamed Install", "").strip() == "Success":
            wx.CallAfter(self.update_status, "安装成功")
            logger.info("APP安装成功")
        else:
            wx.CallAfter(self.update_status, "安装失败")
            logger.info("APP安装失败")

    async def uninstall_application_program(self):
        """
        卸载应用程序
        """
        cmd = f'adb -s {self.serial} uninstall {self.package_name}'
        logger.info(f"开始卸载APP：{cmd}")
        uninstall_status = subprocess.getoutput(cmd)
        if uninstall_status == "Success":
            logger.info("APP卸载成功")
        else:
            logger.info("APP卸载失败")
        return uninstall_status

    def get_Activity_name(self):
        """获取启动Activity名称"""
        cmd = "adb -s {} shell dumpsys package {} | grep -A 1 'MAIN' | grep 'Activity' | awk '{{print $2}}'".format(
            self.serial, self.package_name)
        self.Activity_name = subprocess.getoutput(cmd)

    def check_wifi_status(self):
        """
        检查wifi状态
        """
        cmd = f'adb -s {self.serial} shell dumpsys wifi | grep "Wi-Fi is"'
        logger.info(f"检测设备网络状态：{cmd}")
        wifi_status = subprocess.getoutput(cmd).strip("Wi-Fi is ")
        if wifi_status == "enabled":
            logger.info("当前网络状态：已连接")
        else:
            logger.info("当前网络状态：未连接")
            self.start_wifi()
            self.check_wifi_status()
        return wifi_status

    def start_wifi(self):
        """开启网络连接"""
        cmd = f"adb -s {self.serial} shell svc wifi enable"
        logger.info(f"开启网络连接：{cmd}")
        run_wifi_status = subprocess.getoutput(cmd)
        return run_wifi_status

    def check_application_program_running_status(self):
        """
        检查应用程序运行状态
        :return:
        """
        cmd = f'adb -s {self.serial} shell pidof -s {self.package_name}'
        logger.info(f"检测APP运行状态：{cmd}")
        running_status = subprocess.getoutput(cmd)
        return running_status

    async def start_application_program(self):
        """
        启动应用程序
        """
        self.get_Activity_name()
        self.check_wifi_status()

        # 检查引用程序运行状态
        running_status = self.check_application_program_running_status()
        if not running_status:
            cmd = f'adb -s {self.serial} shell am start -n {self.Activity_name}'
            logger.info(f"启动{self.app_name}APP：{cmd}")
            start_application_program_status = subprocess.getoutput(cmd)

            if start_application_program_status:
                # 再次检查运行状态
                running_status2 = self.check_application_program_running_status()
                if running_status2:
                    logger.info("APP启动成功")
                else:
                    logger.info("APP启动失败！")
            else:
                logger.info("APP启动失败！")
                choice = wx.MessageBox('是否尝试重启', 'APP启动失败', wx.YES_NO | wx.ICON_QUESTION)
                if choice == wx.YES:
                    logger.info("尝试重启APP中...")
                    start_application_program_status2 = subprocess.getoutput(cmd)
                    if start_application_program_status2:
                        logger.info("APP启动成功")
                    else:
                        logger.info("APP启动失败！")
        else:
            logger.info(f"{self.app_name}已启动！")

    async def force_restart_application_program(self):
        """
        强制重启应用程序
        :return:
        """
        cmd = f'adb -s {self.serial} shell am start -S -n {self.Activity_name}'
        logger.info(f"强制重启{self.app_name}APP：{cmd}")
        force_start_application_program_status = subprocess.getoutput(cmd)
        if force_start_application_program_status:
            logger.info("强制重启成功")
        else:
            logger.info("强制重启失败！")
