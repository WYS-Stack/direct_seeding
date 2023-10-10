# 项目简介（学习使用）
功能介绍：
- 通过模拟器实现抖音、小红书直播间的自动点赞评论功能
- （后续）脱离模拟器实现以上功能，使用官方接口；（小红书目前只能模拟器）

功能优化：
- 目前由于新添了同时操作多台设备，bug还有很多，耐心修复中...

界面优化：
- 目前使用了wxpython和pyqt5（目前学习过程中，后续可能会选择更加高效炫酷的语言编写界面）

# 环境
1. 模拟器
2. brew install android-platform-tools # Mac环境下安装adb环境
3. pip install -U uiautomator2
4. pip install -U weditor
5. python -m uiautomator2 init # 启动所有模拟器后执行
6. 其余环境

# 打包命令
```shell
pyinstaller --onefile --windowed --icon=app.icns feibo.py
```

# 界面元素选取
```shell
weditor
```
