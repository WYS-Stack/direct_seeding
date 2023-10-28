# 项目简介（学习使用）
功能介绍：
- **通过执行模拟器命令实现抖音、小红书直播间的自动点赞评论功能，可多台模拟器同时启动进行不同操作**
- （后续）脱离模拟器实现以上功能，使用接口；（小红书目前只能模拟器）
- （后续）添加创建模拟器，（本地）和（远程）两种方式操作

功能优化：
- 目前由于新添了很多新功能，bug还有很多，正在努力检测、努力修复中...

界面优化：
- 目前界面一部分使用了wxpython、一部分pyqt5（在学习过程中，后续可能会选择添加高效炫酷的界面）

# 环境
1. 模拟器
2. brew install android-platform-tools # Mac环境下安装adb环境
3. pip install -r requirements.txt # 环境安装
4. python -m uiautomator2 init # **启动**所有模拟器后执行

# 运行
```python
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