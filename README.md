# 项目简介（学习使用）
功能介绍：
- 通过模拟器实现抖音、小红书直播间的自动点赞评论功能
- （后续）脱离模拟器实现以上功能，使用官方接口；（小红书目前只能模拟器）
- （后续）添加创建模拟器，（本地）和（远程）两种

功能优化：
- 目前由于新添了很多新功能，bug还有很多，正在努力检测、努力修复中...

界面优化：
- 目前界面一部分使用了wxpython、一部分pyqt5（在学习过程中，后续可能会选择添加高效炫酷的界面）

# 环境
1. 模拟器
2. brew install android-platform-tools # Mac环境下安装adb环境
3. pip install -U uiautomator2
4. pip install -U weditor
5. python -m uiautomator2 init # 启动所有模拟器后执行
6. 其余环境

# 打包命令
```shell
pyinstaller --windowed --icon=app.icns feibo.py --add-data "config:config" --add-data "img:img" --add-data "logger:logger"
```

# 界面元素选取
```shell
weditor
```
