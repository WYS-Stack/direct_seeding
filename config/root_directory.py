import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 应用程序对应的来源地址和url
applications = {
    "抖音": {
        "apk_id": 1,
        "package_name": "com.ss.android.ugc.aweme",
        "url": "https://d.toutiao.com/mGFG?apk=1"
    },
    "小红书": {
        "apk_id": 2,
        "package_name": "com.xingin.xhs",
        # 官方下载地址
        # "url": "https://dc.xiaohongshu.com/file/pkgs/base/xiaohongshu.apk"
        "url": "https://www.wandoujia.com/apps/6233739"
    }
}
