import os
import wx
import configparser


# 配置页面
class ClickWindow(wx.Frame):
    def __init__(self, parent):
        super().__init__(parent, title='配置', size=(500, 250), pos=(900, 200))

        self.panel = wx.Panel(self)

        # 静态文本和对应的输入框
        labels = [
            ('点赞总量', '每次点赞间隔', '点赞总时间', '点赞总批数'),
            ('', '', '', ''),
            ('', '', '', ''),
            ('', '', '', '')
        ]
        # 读取配置文件获取结果
        config_read = configparser.ConfigParser()
        current_parent_path = os.path.dirname(os.path.abspath(__file__))
        config_read.read(current_parent_path+'/config/config.ini')
        # 配置文件默认值
        default_values = []
        for section in config_read.sections():
            num = config_read[section]['num']
            interval = config_read[section]['interval']
            time = config_read[section]['time']
            batch = config_read[section]['batch']
            default_values.append((num, interval, time, batch))

        # 创建静态文本和输入框
        self.static_text_controls = []
        self.input_controls = []

        for row in range(len(labels)):
            for col, label in enumerate(labels[row]):
                if row == 0:
                    static_text = wx.StaticText(self.panel, label=label, pos=(20 + col * 120, 10 + row * 30))
                    self.static_text_controls.append(static_text)
                else:
                    input_box = wx.TextCtrl(self.panel, pos=(20 + col * 120, 10 + row * 30), size=(100, -1))
                    input_box.SetValue(default_values[row - 1][col])  # 设置输入框的默认值
                    self.input_controls.append(input_box)

        # 创建获取输入框值的按钮
        button = wx.Button(self.panel, label='保存', pos=(395, 130))
        button.Bind(wx.EVT_BUTTON, self.on_get_values)

    def on_get_values(self, event):

        self.config_values = [control.GetValue() for control in self.input_controls]

        # 将值转换成所需的形式
        self.config_values_output = [
            (self.config_values[i], self.config_values[i + 1], self.config_values[i + 2], self.config_values[i + 3]) for
            i in range(0, len(self.config_values), 4)]
        # 将转换后的值写入配置文件
        config = configparser.ConfigParser()
        for i, value in enumerate(self.config_values_output):
            section_name = f'Section{i + 1}'
            config[section_name] = {}
            config[section_name]['num'] = value[0]
            config[section_name]['interval'] = value[1]
            config[section_name]['time'] = value[2]
            config[section_name]['batch'] = value[3]
        current_parent_path = os.path.dirname(os.path.abspath(__file__))

        with open(current_parent_path + '/config/config.ini', 'w') as configfile:
            config.write(configfile)


if __name__ == '__main__':
    app = wx.App()
    new_frame = ClickWindow(None)
    new_frame.Show()
    app.MainLoop()
