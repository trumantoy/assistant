import gi
gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk, Gio

import time
import os
import subprocess

@Gtk.Template(filename='ui/app_window.ui')
class AppWindow (Gtk.ApplicationWindow):
    __gtype_name__ = "AppWindow"

    listview1 = Gtk.Template.Child('listview1')
    listview2 = Gtk.Template.Child('listview2')

    def __init__(self):
        self.set_resizable(False)

        model = Gtk.StringList.new(["项目1", "项目2", "项目3"])
        selection_model = Gtk.SingleSelection.new(model)
        self.listview1.set_model(selection_model)
        
        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", self.setup_listitem1)
        factory.connect("bind", self.bind_listitem1)
        self.listview1.set_factory(factory)

        model = Gtk.StringList.new([
            'https://picx.zhimg.com/v2-d6f44389971daab7e688e5b37046e4e4_720w.jpg?source=172ae18b',
            'https://ts3.tc.mm.bing.net/th/id/OIP-C.8X0x4T7APkN7J7q7yOYy3gHaE7?r=0&rs=1&pid=ImgDetMain&o=7&rm=3',
            'https://picx.zhimg.com/v2-6ca9e1a5c977ad26a53fcc11a7ba9f57_720w.jpg?source=172ae18b'
            ])
        
        selection_model = Gtk.SingleSelection.new(model)
        self.listview2.set_model(selection_model)

        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", self.setup_listitem2)
        factory.connect("bind", self.bind_listitem2)
        self.listview2.set_factory(factory)
  

    def setup_listitem1(self, factory, list_item):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # 添加双击控制器
        click_controller = Gtk.GestureClick()
        click_controller.set_button(1)  # 左键
        click_controller.connect("pressed", self.on_listitem1_click)
        box.add_controller(click_controller)

        label = Gtk.Label()
        label.set_wrap(True)  # 启用自动换行
        label.set_halign(Gtk.Align.START)  # 左对齐
        box.append(label)
        list_item.set_child(box)

    def bind_listitem1(self, factory, list_item):
        item = list_item.get_item()
        box = list_item.get_child()
        label = box.get_first_child()
        label.set_label(item.get_string())
        
    # 新增方法：处理listitem1点击事件
    def on_listitem1_click(self, controller, n_press, x, y):
        if n_press == 2:  # 双击
            box = controller.get_widget()
            label = box.get_first_child()
            item_value = label.get_label()
            self.wx.stdin.write(f"send-msg {item_value}\n")
            self.wx.stdin.flush()

    def setup_listitem2(self, factory, list_item):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        picture = Gtk.Picture()
        picture.set_size_request(100, 100)  # 设置图片显示大小
        click_controller = Gtk.GestureClick()
        click_controller.set_button(1)  # 左键
        click_controller.connect("pressed", self.on_item_double_click)
        box.add_controller(click_controller)

        box.append(picture)
        list_item.set_child(box)

    def bind_listitem2(self, factory, list_item):
        item = list_item.get_item()
        box = list_item.get_child()
        picture = box.get_first_child()
        file = Gio.File.new_for_uri(item.get_string())
        picture.set_file(file)

    def on_item_double_click(self, controller, n_press, x, y):
        if n_press == 2:  # 双击
            box = controller.get_widget()
            picture = box.get_first_child()
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
                
