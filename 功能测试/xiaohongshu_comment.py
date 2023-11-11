import uiautomator2 as u2
d = u2.connect("emulator-5554")

# 小红书评论
# d(text="说点什么…").click()
# d(text="说点什么...").click()
# d(focused=True).set_text("1111")
if d(resourceId="com.xingin.xhs.alpha_live:id/sendMsgBtn").exists:
    print(1111)
    d(resourceId="com.xingin.xhs.alpha_live:id/sendMsgBtn").click_exists()

