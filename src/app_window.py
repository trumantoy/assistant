import gi
gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk, Gio, Gdk

import time
import os
import subprocess


import ctypes
from ctypes import wintypes

# 加载 user32.dll
user32 = ctypes.windll.user32

# 定义 RECT 结构体
class RECT(ctypes.Structure):
    _fields_ = [
        ("left", wintypes.LONG),
        ("top", wintypes.LONG),
        ("right", wintypes.LONG),
        ("bottom", wintypes.LONG)
    ]

# 定义 FindWindowW 和 GetWindowRect 函数
FindWindowW = user32.FindWindowW
FindWindowW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
FindWindowW.restype = wintypes.HWND

GetWindowRect = user32.GetWindowRect
GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(RECT)]
GetWindowRect.restype = wintypes.BOOL

# 使用 Win32 API 获取当前活动窗口句柄
GetActiveWindow = user32.GetActiveWindow
GetActiveWindow.argtypes = []
GetActiveWindow.restype = wintypes.HWND


# 定义 SetWindowPos 函数
SetWindowPos = user32.SetWindowPos
SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND, wintypes.INT, wintypes.INT,wintypes.INT, wintypes.INT, wintypes.UINT]
SetWindowPos.restype = wintypes.BOOL

MoveWindow = user32.MoveWindow
MoveWindow.argtypes = [wintypes.HWND, wintypes.INT, wintypes.INT, wintypes.INT, wintypes.INT, wintypes.BOOL]
MoveWindow.restype = wintypes.BOOL

ShowWindow = user32.ShowWindow
ShowWindow.argtypes = [wintypes.HWND, wintypes.INT]
ShowWindow.restype = wintypes.BOOL

# 新增 SetWindowLong 函数定义
SetWindowLong = user32.SetWindowLongW
SetWindowLong.argtypes = [wintypes.HWND, wintypes.INT, wintypes.LONG]
SetWindowLong.restype = wintypes.LONG

GetWindowLong = user32.GetWindowLongW
GetWindowLong.argtypes = [wintypes.HWND, wintypes.INT]
GetWindowLong.restype = wintypes.LONG

# 定义窗口状态常量
SW_SHOWNORMAL = 1
SW_SHOWMINIMIZED = 2
SW_SHOWMAXIMIZED = 3

GWL_EXSTYLE = -20
WS_EX_TOOLWINDOW = 0x00000080
SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SWP_NOACTIVATE = 0x0010


@Gtk.Template(filename='ui/app_window.ui')
class AppWindow (Gtk.ApplicationWindow):
    __gtype_name__ = "AppWindow"

    listview1 = Gtk.Template.Child('listview1')
    listview2 = Gtk.Template.Child('listview2')

    def __init__(self):
        self.set_resizable(False)
    
        # 创建自定义标题栏
        header = Gtk.HeaderBar()
        header.set_show_title_buttons(False)  # 禁用默认标题栏按钮
    
        # 添加自定义关闭按钮
        close_button = Gtk.Button()
        close_button.set_icon_name("window-close-symbolic")  # 设置关闭图标
        close_button.connect("clicked", lambda b: self.close())  # 绑定关闭事件
        header.pack_end(close_button)  # 将按钮添加到标题栏右侧        
        
        self.set_titlebar(header)

        # 创建右键菜单模型
        menu = Gio.Menu()
        menu.append("编辑", "win.edit_script")
        menu.append("添加", "win.add_script")
        
        action_edit_script = Gio.SimpleAction.new("edit_script", None)
        action_edit_script.connect("activate", self.edit_script)
        self.add_action(action_edit_script)

        action_add_script = Gio.SimpleAction.new("add_script", None)
        action_add_script.connect("activate", self.add_script)
        self.add_action(action_add_script)

        # 创建弹出菜单
        self.popover = Gtk.PopoverMenu()
        self.popover.set_menu_model(menu)

        # 添加右键点击控制器
        click_controller = Gtk.GestureClick(button=3)  # 右键
        def right_clicked(c, n, x, y):
            rect = Gdk.Rectangle()
            rect.x = x
            rect.y = y
            self.popover.set_pointing_to(rect)
            self.popover.popup()

        click_controller.connect("pressed", right_clicked)
        self.add_controller(click_controller)
        self.popover.set_parent(self)

        model = Gtk.StringList.new(["项目1111", "项目2", "项目3"])
        selection_model = Gtk.SingleSelection.new(model)
        selection_model.set_autoselect(False)  # 禁用自动选择
        selection_model.set_can_unselect(True)  # 允许取消选择
        self.listview1.set_model(selection_model)
        self.listview1.set_single_click_activate(False)
        selection_model.unselect_all()
                
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

        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE  # 隐藏窗口
        
        self.wx = subprocess.Popen(['plugins/wx.exe'],
            text=True,encoding='gbk',
            stdin=subprocess.PIPE,
            startupinfo=startupinfo)
        
        GLib.idle_add(self.update_window_position)

    def edit_script(self, action, param):
        # 获取当前选中的 ListViewItem
        selection_model = self.listview1.get_model()
        if selection_model.get_selected() is not None:
            selected_index = selection_model.get_selected()
            item = selection_model.get_item(selected_index)
            # 创建编辑对话框
            dialog = Gtk.Dialog(title="编辑话术", transient_for=self)
            entry = Gtk.Entry(text=item.get_string())
            dialog.get_content_area().append(entry)
            dialog.add_buttons("取消", Gtk.ResponseType.CANCEL, "保存", Gtk.ResponseType.OK)
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                new_text = entry.get_text()
                # 更新 ListViewItem 的文本
                item.set_string(new_text)
            dialog.destroy()

    def add_script(self, action, param):
        # 创建添加对话框
        dialog = Gtk.Dialog(title="添加话术", transient_for=self)
        entry = Gtk.Entry()
        dialog.get_content_area().append(entry)
        dialog.add_buttons("取消", Gtk.ResponseType.CANCEL, "添加", Gtk.ResponseType.OK)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            new_text = entry.get_text()
            # 创建新的 ListViewItem 并添加到列表
            list_store = self.listview1.get_model()
            new_item = Gio.ListItem()
            new_item.set_string(new_text)
            list_store.append(new_item)
        dialog.destroy()

    def get_wechat_window_position_and_size(self):
        # 微信窗口类名通常为 'WeChatMainWndForPC'，标题可能为空
        hwnd = FindWindowW("WeChatMainWndForPC", None)
        if hwnd == 0:
            print("未找到微信窗口")
            return None

        rect = RECT()
        if GetWindowRect(hwnd, ctypes.byref(rect)):
            width = rect.right - rect.left
            height = rect.bottom - rect.top
            return rect.left, rect.top, width, height
        else:
            print("无法获取微信窗口位置和大小")
            return None

    def update_window_position(self):
        if self.is_suspended():
            return True

        if self.popover.get_visible():
            return True

        wechat_hwnd = FindWindowW("WeChatMainWndForPC", None)
        wx_rect = RECT()
        if not GetWindowRect(wechat_hwnd, ctypes.byref(wx_rect)):    
            return True
        
        wx_height = wx_rect.bottom - wx_rect.top
        if self.get_height() != wx_height:
            self.set_size_request(400, wx_height)

        if 'app_hwnd' not in vars(self):
            self.app_hwnd = FindWindowW('gdkSurfaceToplevel', "私域助手")

        app_hwnd = self.app_hwnd

        rect = RECT()
        if not GetWindowRect(app_hwnd, ctypes.byref(rect)):
            return True
        
        if rect.left != wx_rect.right or rect.top != wx_rect.top - 10:
            SetWindowPos(app_hwnd, wechat_hwnd, wx_rect.right, wx_rect.top - 10, 0,0, SWP_NOSIZE)
        else:
            SetWindowPos(app_hwnd, wechat_hwnd, 0, 0, 0,0, SWP_NOMOVE | SWP_NOSIZE)
        return True

    def setup_listitem1(self, factory, list_item):
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                
        # 添加发送按钮
        send_button = Gtk.Button()
        send_button.set_icon_name("mail-send-symbolic")  # 设置发送图标
        send_button.connect("clicked", self.send_msg_clicked)
        send_button.set_size_request(20, -1)
        box.append(send_button)
        label = Gtk.Label()
        box.append(label)
        
        list_item.set_child(box)

    def bind_listitem1(self, factory, list_item):
        item = list_item.get_item()
        box = list_item.get_child()
        btn = box.get_first_child()
        label = btn.get_next_sibling()
        label.set_label(item.get_string())
        
    # 新增方法：处理listitem1点击事件
    def send_msg_clicked(self, sender):
        label = sender.get_next_sibling()
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
                
