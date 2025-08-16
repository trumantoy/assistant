import sys
sys.path.append('.')

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk, Gio, GObject  # 添加 GObject 导入

import threading
import pystray
from PIL import Image
from app_window import *

# pyinstaller -w src/app.py --collect-all=pystray --collect-all=gi --add-data "c:/msys64/mingw64/lib/girepository-1.0:gi_typelibs" --noconfirm

if __name__ == '__main__':
    GLib.set_application_name('私域助手')
    settings = Gtk.Settings.get_default()
    settings.set_property('gtk-application-prefer-dark-theme', True)
    
    global t
    t = None
    
    def do_activate(app): 
        builder = Gtk.Builder.new_from_file('ui/app.ui')
        app_window = builder.get_object('app_window')

        def quit_window(app_window,hook_close):
            app_window.disconnect(hook_close)
            app_window.close()
            icon.stop()

        def do_close_request(sender):
            sender.unmap() 
            return True

        hook_close = app_window.connect("close-request", do_close_request)
        menu = (pystray.MenuItem('显示', lambda: app_window.map(), default=True), 
                pystray.Menu.SEPARATOR, 
                pystray.MenuItem('退出', lambda: quit_window(app_window,hook_close)))
        
        image = Image.open("icon/tray.png")
        icon = pystray.Icon("icon", image, "私域助手", menu)

        t = threading.Thread(target=icon.run)
        t.start()
        
        app.connect('shutdown',lambda app: icon.stop())
        app.add_window(app_window)
        
    app = Gtk.Application(application_id="xyz.assistant.app")
    app.connect('activate',do_activate)
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)