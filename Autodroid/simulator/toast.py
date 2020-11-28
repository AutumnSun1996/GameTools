import tkinter as tk
import threading
import win32api
import win32con
from ctypes import Structure, c_long, windll, byref


class RECT(Structure):
    _fields_ = [
        ('left', c_long),
        ('top', c_long),
        ('right', c_long),
        ('bottom', c_long),
    ]

screen = RECT()
windll.user32.SystemParametersInfoW(win32con.SPI_GETWORKAREA, 0, byref(screen), 0)

def _show_toast(title, message, timeout=2000):
    ret = ["TIMEOUT"]
    root = tk.Tk()
    root.config(background="black")
    root.attributes("-topmost", True)
    # root.wm_attributes("-transparentcolor", "black")
    root.wm_overrideredirect(True)
    w, h = 300, 120
    root.geometry("{}x{}+{}+{}".format(w, h, screen.right - 10 - w, screen.bottom - 10 - h))

    def onclick(evt):
        if evt.x < 150:
            ret[0] = "SHOW"
        else:
            ret[0] = "IGNORE"
        root.destroy()

    root.bind("<Button-1>", onclick)

    tk.Label(text=title, font=("SimHei", 18), fg="white", background="black").pack(
        expand=True
    )
    tk.Label(text=message, font=("SimHei", 16), fg="white", background="black").pack(
        expand=True
    )
    tk.Label(
        text="显示        忽略", font=("SimHei", 14), fg="white", background="black"
    ).pack(expand=True)
    root.after(timeout, root.destroy)

    root.mainloop()
    return ret[0]


def show_toast(title, message, timeout=2000, beep=True, threaded=False):
    if beep:
        win32api.MessageBeep()
    if threaded:
        t = threading.Thread(target=_show_toast, args=(title, message, timeout))
        t.start()
        return t
    else:
        return _show_toast(title, message, timeout)

if __name__ == "__main__":
    show_toast("测试", "测试信息")