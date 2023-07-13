# 连接到 ADB 服务器，默认端口伟5037
from ppadb.client import Client as AdbClient
client = AdbClient(host="127.0.0.1", port=5037)
# 查看连接上的安卓设备
devices = client.devices()
print(devices[0].get_properties().get("ro.boot.qemu.avd_name"))
print(devices[0].get_properties().get("sys.boot_completed"))