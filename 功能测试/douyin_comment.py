import uiautomator2 as u2
d = u2.connect("emulator-5554")
# 抖音评论

d.click(0.9, 0.765)
d(resourceId="com.ss.android.ugc.aweme:id/ft3").click()
d.send_keys("1", clear=True)
d(resourceId="com.ss.android.ugc.aweme:id/i24").click()
