import gi
gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk, Gio, Gdk, GObject

import time
import os
import pygetwindow as gw
import pyautogui as ag
import pyperclip as pc
import win32clipboard,win32gui,win32api,win32con,win32print
import ctypes

GWL_EXSTYLE = -20
WS_EX_APPWINDOW = 0x00040000  # 使窗口在任务栏显示图标
WS_EX_TOOLWINDOW = 0x00000080
SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SWP_NOACTIVATE = 0x0010

# 新增函数：使用 pywin32 获取屏幕缩放比例
def get_screen_scale():
    try:
        # 获取主显示器的设备上下文
        hdc = win32gui.GetDC(0)
        # 获取水平和垂直方向的 DPI
        dpi_x = win32print.GetDeviceCaps(hdc, win32con.LOGPIXELSX)
        dpi_y = win32print.GetDeviceCaps(hdc, win32con.LOGPIXELSY)
        # 释放设备上下文
        win32gui.ReleaseDC(0, hdc)
        # 计算缩放比例，标准 DPI 为 96
        scale_x = dpi_x / 96
        scale_y = dpi_y / 96
        return scale_x, scale_y
    except Exception as e:
        print(f"获取屏幕缩放比例失败: {e}")
        return 1.0, 1.0

@Gtk.Template(filename='ui/app_window.ui')
class AppWindow (Gtk.ApplicationWindow):
    __gtype_name__ = "AppWindow"

    view = Gtk.Template.Child('view')
    listview1 = Gtk.Template.Child('listview1')
    listview2 = Gtk.Template.Child('listview2')
    magnetic_button = Gtk.Template.Child('magnetic-button')
    close_button = Gtk.Template.Child('close-button')
    header = Gtk.Template.Child('header')
    title_label = Gtk.Template.Child('title-label')
    scale_x, scale_y = get_screen_scale()

    def __init__(self):
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
        self.listview1.add_controller(click_controller)
        self.popover.set_parent(self.listview1)

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

        GLib.idle_add(self.update_window_position,self.magnetic_button)

    @Gtk.Template.Callback()
    def magnetic_toggled(self, button):
        #  if button.get_active(): 
        pass

    @Gtk.Template.Callback()
    def close_button_clicked(self, button):
        self.close()

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

    def update_window_position(self, toggled_button):
        try:
            magnet = toggled_button.get_active()

            if self.is_suspended() or not self.get_mapped():
                return True

            if self.popover.get_visible():
                return True

            wx_windows : gw.Win32Window = gw.getWindowsWithTitle('微信')
            wx_windows = [wx_window for wx_window in wx_windows if win32gui.GetClassName(wx_window._hWnd) in ['Qt51514QWindowIcon','WeChatMainWndForPC','WeChatLoginWndForPC']]
            if not wx_windows: 
                self.view.set_visible_child_name('page1')
                self.set_default_size(600 * self.scale_x, 380 * self.scale_x)
                return True

            wx_window : gw.Win32Window = wx_windows[0]

            last_view_name = self.view.get_visible_child_name()
            if wx_window.width < 300 * self.scale_x:
                self.view.set_visible_child_name('page1')
                self.set_default_size(600 * self.scale_x, wx_window.height)
            else:
                self.view.set_visible_child_name('page2')
            
                if last_view_name == 'page1':
                    self.set_default_size(300 * self.scale_x, wx_window.height)

            if not magnet:
                return True
                    
            if self.get_height() != wx_window.height:
                self.set_default_size(self.get_default_size()[0], wx_window.height)

            if not hasattr(self,'app_window'):
                self.app_window = gw.getWindowsWithTitle(self.title_label.get_label())[0]
                ex_style = win32gui.GetWindowLong(self.app_window._hWnd, GWL_EXSTYLE)
                new_ex_style = (ex_style & ~WS_EX_APPWINDOW) | WS_EX_TOOLWINDOW
                win32gui.SetWindowLong(self.app_window._hWnd, GWL_EXSTYLE, new_ex_style)
                # result = SetParent(wx_window._hWnd,self.app_window._hWnd)
            
            wx_rect = wx_window.box
            if self.app_window.left != wx_rect.left + wx_rect.width - 10 or self.app_window.top != wx_rect.top - 10:
                self.app_window.moveTo(wx_rect.left + wx_rect.width - 10, wx_rect.top - 10)
            else:
                win32gui.SetWindowPos(self.app_window._hWnd,wx_window._hWnd, 0, 0, 0,0, SWP_NOMOVE | SWP_NOSIZE)
        except Exception as e:
            print(e)
            
        return True

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

        label = Gtk.EditableLabel()
        label.set_margin_bottom(10)

        box.append(label)
        
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
        
        label = vbox.get_next_sibling() 
        label.set_tooltip_text(item.get_string())
        label.set_text(item.get_string())
        
        label.set_max_width_chars(2)
        
    # 新增方法：处理listitem1点击事件
    def send_msg_clicked(self, sender,list_item):
        item_value = list_item.get_item().get_string()
        pc.copy(item_value)
        wx_windows : list[gw.Win32Window] = gw.getWindowsWithTitle('微信')
        wx_windows = [wx_window for wx_window in wx_windows if win32gui.GetClassName(wx_window._hWnd) in ['Qt51514QWindowIcon','WeChatMainWndForPC']]
        if not wx_windows: return
        wx_window = wx_windows[0]
        if wx_window.isMinimized:
            wx_window.restore()
        wx_window.activate()
        time.sleep(0.5)
        ag.hotkey('ctrl','v')
        ag.press('enter')
        
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

                class DROPFILES(ctypes.Structure):
                    _fields_ = [
                    ("pFiles", ctypes.c_uint),
                    ("x", ctypes.c_long),
                    ("y", ctypes.c_long),
                    ("fNC", ctypes.c_int),
                    ("fWide", ctypes.c_bool),
                ]
                    
                pDropFiles = DROPFILES()
                pDropFiles.pFiles = ctypes.sizeof(DROPFILES)
                pDropFiles.fWide = True
                matedata = bytes(pDropFiles)

                file = save_path.replace("/", "\\")
                data = file.encode("U16")[2:]+b"\0\0"

                try:
                    win32clipboard.OpenClipboard()
                    win32clipboard.EmptyClipboard()
                    win32clipboard.SetClipboardData(15, matedata+data)
                except Exception as e:
                    print(e)
                finally:
                    win32clipboard.CloseClipboard()

                wx_windows : gw.Win32Window = gw.getWindowsWithTitle('微信')
                wx_windows = [wx_window for wx_window in wx_windows if win32gui.GetClassName(wx_window._hWnd) in ['Qt51514QWindowIcon','WeChatMainWndForPC']]
                if not wx_windows: return
                wx_window = wx_windows[0]
                if wx_window.isMinimized:
                    wx_window.restore()
                wx_window.activate()
                time.sleep(0.5)
                ag.hotkey('ctrl','v')
                ag.press('enter')

            else:
                print("异步下载失败: 无法获取文件内容")
                
