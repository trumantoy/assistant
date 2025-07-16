import sys
sys.path.append('.')

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk, Gio, GObject  # 添加 GObject 导入


from app_window import *

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

def get_wechat_window_position_and_size():
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


def update_window_position(app_window):
    wechat_hwnd = FindWindowW("WeChatMainWndForPC", None)
    app_hwnd = FindWindowW(None, "私域助手")

    wechat_size = get_wechat_window_position_and_size()
    wx_left, wx_top, wx_width, wx_height = wechat_size
    
    if app_window.is_suspended():
        return True

    if app_window.get_height() != wx_height:
        app_window.set_size_request(400, wx_height)

    rect = RECT()
    GetWindowRect(app_hwnd, ctypes.byref(rect))
    width = rect.right - rect.left
    height = rect.bottom - rect.top
    
    if rect.left != wx_left + wx_width or rect.top != wx_top - 10:
        SetWindowPos(app_hwnd, wechat_hwnd, wx_left + wx_width, wx_top - 10, 0,0, SWP_NOSIZE | SWP_NOACTIVATE)
    else:
        SetWindowPos(app_hwnd, wechat_hwnd, 0, 0, 0,0, SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE)
    
    # app_hwnd = FindWindowW(None, "微信助手")
    # current_style = GetWindowLong(app_hwnd, GWL_EXSTYLE)
    # ex_style = SetWindowLong(app_hwnd, GWL_EXSTYLE, current_style | WS_EX_TOOLWINDOW)

    return True

def do_close_request(sender):
    sender.unmap()
    return True

def show_window(app_window):
    app_window.map()

def quit_window(app_window,hook_close):
    app_window.disconnect(hook_close)
    app_window.close()

import threading
import pystray
from PIL import Image  


if __name__ == '__main__':
    GLib.set_application_name('私域助手')
    settings = Gtk.Settings.get_default()
    settings.set_property('gtk-application-prefer-dark-theme', True)

    def do_activate(app): 
        builder = Gtk.Builder.new_from_file('ui/app.ui')
        app_window = builder.get_object('app_window')
        app.add_window(app_window)
        hook_close = app_window.connect("close-request", do_close_request)
        menu = (pystray.MenuItem('显示', lambda: show_window(app_window), default=True), 
                    pystray.Menu.SEPARATOR, 
                    pystray.MenuItem('退出', lambda: quit_window(app_window,hook_close)))
            
        image = Image.open("db/images/test.jpg")
        icon = pystray.Icon("icon", image, "图标名称", menu)
        threading.Thread(target=icon.run, daemon=True).start()

        # GLib.timeout_add(200, update_window_position, app_window)

    app = Gtk.Application(application_id="xyz.building3d.app")
    app.connect('activate',do_activate)

    exit_status = app.run(sys.argv)
    sys.exit(exit_status)