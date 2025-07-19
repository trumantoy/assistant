import gi
gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk, Gio, Gdk, GObject

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
        # 创建自定义标题栏
        header = Gtk.HeaderBar()
        header.set_show_title_buttons(False)  # 禁用默认标题栏按钮
    
       # 新增磁吸按钮
        self.magnetic_button = Gtk.ToggleButton()
        self.magnetic_button.set_icon_name("view-pin-symbolic")  # 使用图钉图标
        self.magnetic_button.set_active(False)  # 默认开启
        self.magnetic_button.connect("toggled", self.on_magnetic_toggled)
        header.pack_start(self.magnetic_button)  # 添加到标题栏左侧

        # 添加自定义关闭按钮
        close_button = Gtk.Button()
        close_button.set_icon_name("window-close")  # 设置关闭图标
        close_button.connect("clicked", lambda b: self.close())  # 绑定关闭事件
        header.pack_end(close_button)  # 将按钮添加到标题栏右侧        
        
        self.set_titlebar(header)

        # 创建右键菜单模型
        menu = Gio.Menu()
        menu.append("添加", "win.add_script")
        menu.append("删除", "win.delete_script")
        
        action_add_script = Gio.SimpleAction.new("add_script", None)
        action_add_script.connect("activate", self.add_script)
        self.add_action(action_add_script)

        action_delete_script = Gio.SimpleAction.new("delete_script", None)
        action_delete_script.connect("activate", self.delete_script)
        self.add_action(action_delete_script)

        # 创建弹出菜单
        self.popover = Gtk.PopoverMenu()
        self.popover.set_menu_model(menu)

        # 添加右键点击控制器
        click_controller = Gtk.GestureClick(button=3)  # 右键
        def listview1_right_clicked(c, n, x, y):
            i = self.listview1.get_model().get_selected()

            rect = Gdk.Rectangle()
            rect.x = x
            rect.y = y
            self.popover.set_pointing_to(rect)
            self.popover.popup()
            self.listview1.get_model().set_selected(i)

        click_controller.connect("pressed", listview1_right_clicked)
        self.add_controller(click_controller)
        self.popover.set_parent(self)

        model = Gtk.StringList.new([
            '您好！我是人工客服有什么可以帮您！',
            '在的哟，请说',
            '亲亲，现在活动咨询的人数非常多，回复有点慢多多谅解，您稍等哈，这边会一一为您解答！',
            '亲亲看您这么会议价，家里的财政大权一定是您掌握的吧~我都要和您取取经，等以后我成 家了，也要这么会过日子，持家有道~',
            '您还的这个价格，我确实很为难。都是手工活，利润不高，您也让我们有点微薄的利润， 能给工人一口饭吃呢，您手下留情哦~~~',
            '亲亲这价格我确实给不到，非常抱歉哈~ 您也可以多对比对比其它的商家，这价格您也许 在淘宝上可以买家，但是品质和作工以及服务就很难说了~',
            '非常抱歉，给您带来了困扰，亲可以麻烦您拍照一下，用尺子测量尺寸的照片发过来我看下吗？',
            '亲，可以退回来我们帮您改一下，不收手工费，需要您承担来回运费哦。',
            '亲稍等，这边马上帮您联系快递核实下情况，您放心一定会帮您解决的，一会给您回复哈。'])

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

        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE  # 隐藏窗口

        # self.wx = subprocess.Popen([r'C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.12_3.12.2800.0_x64__qbz5n2kfra8p0\python3.12.exe',"plugins/wx.py"],
        self.wx = subprocess.Popen(['plugins/wx.exe'],
            text=True,encoding='utf-8',
            stdin=subprocess.PIPE,
            startupinfo=startupinfo)


    def on_magnetic_toggled(self, button):
        """磁吸按钮切换回调"""
        if button.get_active(): GLib.idle_add(self.update_window_position,button)

    def add_script(self, action, param):
        # 获取 listview1 的选择模型
        selection_model = self.listview1.get_model()
        # 从选择模型中获取底层的 StringList 模型
        string_model = selection_model.get_model()
        # 向 StringList 模型中添加新的字符串项
        string_model.append("新话术")

    def delete_script(self, action, param):
        # 获取 listview1 的选择模型
        selection_model = self.listview1.get_model()
        # 从选择模型中获取底层的 StringList 模型
        string_model = selection_model.get_model()
        # 删除选中的字符串项
        string_model.remove(selection_model.get_selected())

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

    def update_window_position(self, toggled_button):
        next = toggled_button.get_active()

        if self.is_suspended() or not self.get_mapped():
            return next

        if self.popover.get_visible():
            return next

        wechat_hwnd = FindWindowW("WeChatMainWndForPC", None)
        wx_rect = RECT()
        if not GetWindowRect(wechat_hwnd, ctypes.byref(wx_rect)):    
            return next
        
        wx_height = wx_rect.bottom - wx_rect.top
        if self.get_height() != wx_height:
            self.set_default_size(self.get_width(), wx_height)

        if 'app_hwnd' not in vars(self):
            self.app_hwnd = FindWindowW('gdkSurfaceToplevel', "私域助手")

        app_hwnd = self.app_hwnd

        rect = RECT()
        if not GetWindowRect(app_hwnd, ctypes.byref(rect)):
            return next
        wx_rect.right -= 10
        wx_rect.top -= 3
        if rect.left != wx_rect.right or rect.top != wx_rect.top:
            SetWindowPos(app_hwnd, wechat_hwnd, wx_rect.right, wx_rect.top - 10, 0,0, SWP_NOSIZE)
        else:
            SetWindowPos(app_hwnd, wechat_hwnd, 0, 0, 0,0, SWP_NOMOVE | SWP_NOSIZE)
        return next

    def setup_listitem1(self, factory, list_item):
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        # 添加发送按钮
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        button = Gtk.Button()
        button.set_icon_name("go-previous-symbolic")  # 设置发送图标
        button.connect("clicked", self.send_msg_clicked, list_item)
        vbox.set_valign(Gtk.Align.CENTER)
        vbox.append(button)

        box.append(vbox)

        view = Gtk.ScrolledWindow()
        view.set_hexpand(True)
        label = Gtk.EditableLabel()
        label.set_margin_bottom(10)
        view.set_child(label)

        box.append(view)
        
        list_item.set_child(box)

        # 添加鼠标移动控制器
        motion_controller = Gtk.EventControllerMotion()
        motion_controller.connect("enter", self.on_listitem1_enter, list_item)
        motion_controller.connect("leave", self.on_listitem1_leave, list_item)
        box.add_controller(motion_controller)

    def on_listitem1_enter(self, controller, x, y, list_item):
        """鼠标进入列表项时的回调"""
        self.listview1.get_model().set_selected(list_item.get_position())

    def on_listitem1_leave(self, controller, list_item):
        """鼠标离开列表项时的回调"""
        self.listview1.get_model().unselect_item(list_item.get_position())

    def bind_listitem1(self, factory, list_item):
        item = list_item.get_item()
        box = list_item.get_child()
        vbox = box.get_first_child()
        btn = vbox.get_first_child()
        
        view = vbox.get_next_sibling()
        label = view.get_child().get_child()
        label.set_tooltip_text(item.get_string())
        label.set_text(item.get_string())
        
        label.set_max_width_chars(2)
        
    # 新增方法：处理listitem1点击事件
    def send_msg_clicked(self, sender,list_item):
        item_value = list_item.get_item().get_string()
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
                
