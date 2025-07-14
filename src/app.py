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

# 新增 Win32 API 函数定义
GetWindowPlacement = user32.GetWindowPlacement
GetWindowPlacement.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.UINT)]
GetWindowPlacement.restype = wintypes.BOOL

ShowWindow = user32.ShowWindow
ShowWindow.argtypes = [wintypes.HWND, wintypes.INT]
ShowWindow.restype = wintypes.BOOL

# 定义窗口状态常量
SW_SHOWNORMAL = 1
SW_SHOWMINIMIZED = 2
SW_SHOWMAXIMIZED = 3


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


def get_wechat_window_state(hwnd):
    placement = wintypes.UINT(0)
    if GetWindowPlacement(hwnd, ctypes.byref(placement)):
        return placement.value
    return None

def update_window_position(app_window):
    wechat_info = get_wechat_window_position_and_size()
    if wechat_info:
        wechat_left, wechat_top, wechat_width, wechat_height = wechat_info
        
        # 获取微信窗口句柄
        wechat_hwnd = FindWindowW("WeChatMainWndForPC", None)
        if wechat_hwnd:
            # 获取微信窗口状态
            wechat_state = get_wechat_window_state(wechat_hwnd)
            
            # 获取程序窗口句柄
            app_hwnd = GetActiveWindow()
            if not app_hwnd:
                app_hwnd = FindWindowW(None, "微信助手")
                
            if app_hwnd:
                # 同步窗口状态
                if wechat_state == SW_SHOWMINIMIZED or wechat_state == SW_SHOWMAXIMIZED:
                    ShowWindow(app_hwnd, SW_SHOWMINIMIZED)
                else:
                    ShowWindow(app_hwnd, SW_SHOWNORMAL)
                
                # 移动窗口到微信右侧
                SetWindowPos(app_hwnd,wechat_hwnd,wechat_left + wechat_width,wechat_top - 10,300,wechat_height,0x0040)
    return True


if __name__ == '__main__':
    GLib.set_application_name('微信助手')
    settings = Gtk.Settings.get_default()
    settings.set_property('gtk-application-prefer-dark-theme', True)


    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = subprocess.SW_HIDE  # 隐藏窗口
    
    wx = subprocess.Popen(['plugins/wx.exe'],
                        text=True,
                        stdin=subprocess.PIPE,
                        startupinfo=startupinfo)
    
    def do_activate(app): 
        builder = Gtk.Builder.new_from_file('ui/app.ui')
        app_window = builder.get_object('app_window')
        app_window.wx = wx
        app.add_window(app_window)

        # 获取微信窗口大小
        wechat_size = get_wechat_window_position_and_size()
        if wechat_size:
            _, _, width, height = wechat_size
            app_window.set_size_request(300, height)
        
        GLib.timeout_add(100, update_window_position, app_window)

    app = Gtk.Application(application_id="xyz.building3d.app")
    app.connect('activate',do_activate)

    exit_status = app.run(sys.argv)
    sys.exit(exit_status)