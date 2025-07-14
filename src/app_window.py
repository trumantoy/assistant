import gi
gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk, Gio

import time
import cairo
import numpy as np
import os
import subprocess

@Gtk.Template(filename='ui/app_window.ui')
class AppWindow (Gtk.ApplicationWindow):
    __gtype_name__ = "AppWindow"

    listview1 = Gtk.Template.Child('listview1')
    listview2 = Gtk.Template.Child('listview2')

    def __init__(self):
        # 获取命令输出
        self.wx = subprocess.Popen(["python", "-u", "-c", "while True: print(input('>>> '))"],stdin=subprocess.PIPE,text=True)
        
        model = Gtk.StringList.new(["aaa", "bbb", "ccc"])
        selection_model = Gtk.SingleSelection.new(model)
        self.listview1.set_model(selection_model)
        
        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", self.setup_listitem1)
        factory.connect("bind", self.bind_listitem1)
        self.listview1.set_factory(factory)

        model = Gtk.StringList.new(['https://picx.zhimg.com/v2-d6f44389971daab7e688e5b37046e4e4_720w.jpg?source=172ae18b'])
        selection_model = Gtk.SingleSelection.new(model)
        self.listview2.set_model(selection_model)

        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", self.setup_listitem2)
        factory.connect("bind", self.bind_listitem2)
        self.listview2.set_factory(factory)

    def setup_listitem1(self, factory, list_item):
        text = Gtk.Label()
        list_item.set_child(text)

    def bind_listitem1(self, factory, list_item):
        item = list_item.get_item()
        label = list_item.get_child()

        # 添加双击控制器
        click_controller = Gtk.GestureClick()
        click_controller.set_button(1)  # 左键
        click_controller.connect("pressed", self.on_listitem1_click)
        label.add_controller(click_controller)

        label.set_label(item.get_string())
    
    def setup_listitem2(self, factory, list_item):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        picture = Gtk.Picture()
        picture.set_size_request(100, 100)  # 设置图片显示大小
        click_controller = Gtk.GestureClick()
        click_controller.set_button(1)  # 左键
        click_controller.connect("pressed", self.on_item_double_click)
        picture.add_controller(click_controller)

        box.append(picture)
        list_item.set_child(box)

    # 新增方法：处理listitem1点击事件
    def on_listitem1_click(self, controller, n_press, x, y):
        if n_press == 2:  # 双击
            label = controller.get_widget()
            item_value = label.get_label()
            self.wx.stdin.write(f"send-msg {item_value}\n")
            self.wx.stdin.flush()

    def bind_listitem2(self, factory, list_item):
        item = list_item.get_item()
        box = list_item.get_child()
        picture = box.get_first_child()
        file = Gio.File.new_for_uri(item.get_string())
        picture.set_file(file)

    def on_item_double_click(self, controller, n_press, x, y):
        if n_press == 2:  # 双击
            picture = controller.get_widget()
            file = picture.get_file()

            success, contents, etag = file.load_contents(None)
            
            if success:
                import tempfile
                temp_dir = tempfile.gettempdir()  # 获取系统临时目录
        
                filename = os.path.basename(file.get_uri().split("?")[0])
                save_path = os.path.join(temp_dir, filename)  # 保存到临时目录
            
                with open(save_path, "wb") as f:
                    f.write(contents)
                
                self.wx.stdin.write(f"send-file {save_path}\n")
                self.wx.stdin.flush()
            else:
                print("异步下载失败: 无法获取文件内容")
                
