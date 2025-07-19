from wxauto import WeChat
import os
import sys
import io

if __name__ == "__main__":    
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer,encoding='utf-8')
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer,encoding='utf-8')

    wx = WeChat()
    while True:
        cmd = input().strip()
        print(cmd)
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