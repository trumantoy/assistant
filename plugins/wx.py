from wxauto import WeChat
import os

if __name__ == "__main__":
    wx = WeChat()
    while True:
        cmd = input().strip()
        if cmd.startswith("send-msg "):
            text = cmd[len("send-msg "):].strip()
            wx.SendMsg(text)
        elif cmd.startswith("send-file "):
            img_path = cmd[len("send-file "):].strip()
            if not os.path.exists(img_path): continue
            sessions = wx.GetSession()
            session = sessions[0]
            wx.SendFiles(filepath=img_path,who=session.name, exact=True)
        else:
            break