# 项目简介（学习使用）
功能介绍：
- **通过执行模拟器命令实现抖音、小红书直播间的自动点赞评论功能，可多台模拟器同时启动进行不同操作**

# 环境（Mac）
1. 安卓模拟器（可以使用Android Studio下载的模拟器）
2. brew install android-platform-tools # Mac环境下安装adb环境
3. pip install -r requirements.txt # 环境安装
4. python -m uiautomator2 init # **启动**所有模拟器后执行

# 运行
```shell
python feibo.py 
```

# 打包命令
```shell
pyinstaller --windowed --icon=app.icns feibo.py --add-data "config:config" --add-data "img:img" --add-data "logger:logger"
```

# 界面元素选取
```shell
weditor
```

# 说明
程序界面ID内容为：点击直播账号右上角...下方显示出来的账号为准