import uiautomator2 as u2
d = u2.connect("emulator-5554")

# 小红书评论
d(resourceId="com.xingin.xhs:id/eoo").click()
d.send_keys("Hello", clear=True)
d(resourceId="com.xingin.xhs:id/gfm").click()
