import uiautomator2 as u2
d = u2.connect("emulator-5554")
# 抖音评论


d(resourceId="com.ss.android.ugc.aweme:id/j1+").click()
d.send_keys("YC515113Z", clear=True)
d(resourceId="com.ss.android.ugc.aweme:id/cw").click()
d(resourceId="com.ss.android.ugc.aweme:id/o2z").click()

# 输入评论
d(resourceId="com.ss.android.ugc.aweme:id/f32").click()
d.send_keys("1", clear=True)
d(resourceId="com.ss.android.ugc.aweme:id/jcq").click()