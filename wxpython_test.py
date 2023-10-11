import uiautomator2 as u2
d = u2.connect("emulator-5554")

setting_flag = d(resourceId="com.ss.android.ugc.aweme:id/re+")
if setting_flag.exists:
    print("存在")
    text = setting_flag.get_text()  # 获取此处的文字
    print("值为：",text.split("抖音号: ")[1])

else:
    print("不存在")
