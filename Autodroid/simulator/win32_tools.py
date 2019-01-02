import time

import win32con
import ctypes
import pywintypes
import win32api
import win32gui
import win32com.client
import numpy as np

from config import logger, config


def rescale_point(hwnd, point):
    dpi = ctypes.windll.user32.GetDpiForWindow(hwnd)
    x = point[0] + config.getint("Device", "EdgeOffsetX")
    y = point[1] + config.getint("Device", "EdgeOffsetY")
    # logger.debug("Rescale: %s -> %s", point, (x, y))
    return int(np.round(x * 96 / dpi)), int(np.round(y * 96 / dpi))


def click_at(hwnd, x, y, ):
    # 向后台窗口发送单击事件，(x, y)为相对于窗口左上角的位置
    x, y = rescale_point(hwnd, (x, y))
    pos = win32api.MAKELONG(int(x), int(y))
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONDOWN,
                         win32con.MK_LBUTTON, pos)
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONUP, 0, pos)


def drag(hwnd, start, end, step=100):
    start = rescale_point(hwnd, start)
    end = rescale_point(hwnd, end)
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONDOWN,
                         win32con.MK_LBUTTON, win32api.MAKELONG(*start))

    count = int(np.linalg.norm(np.array(start) - np.array(end)) / step)
    # 最少需要2个坐标
    count = max(count, 2)
    points = np.zeros((count, 2))
    points[:, 0] = np.linspace(start[0], end[0], count)
    points[:, 1] = np.linspace(start[1], end[1], count)
    points = points.astype('int')
    for point in points:
        target = win32api.MAKELONG(*point)
        win32gui.SendMessage(hwnd, win32con.WM_MOUSEMOVE,
                             win32con.MK_LBUTTON, target)
        time.sleep(0.05)

    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONUP, 0, target)


def rand_click(hwnd, rect):
    x_min, y_min, x_max, y_max = rect
    x = np.random.triangular(x_min, (x_min + x_max) / 2, x_max)
    y = np.random.triangular(y_min, (y_min + y_max) / 2, y_max)
    click_at(hwnd, x, y)


def make_foreground(hwnd, retry=True):
    logger.warning("make foreground")
    try:
        win32gui.SetForegroundWindow(hwnd)
    except pywintypes.error as err:
        logger.warning(err)
        if retry:
            shell = win32com.client.Dispatch("WScript.Shell")
            shell.SendKeys('%')
            make_foreground(hwnd, False)


def get_window_hwnd(title):
    return win32gui.FindWindow(None, title)


def heartbeat():
    info = win32api.GetLastInputInfo()
    tick = win32api.GetTickCount()
    if tick - info > 30000:
        win32api.keybd_event(win32con.VK_CAPITAL, 0, 0, 0)
        win32api.keybd_event(win32con.VK_CAPITAL, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.1)
        win32api.keybd_event(win32con.VK_CAPITAL, 0, 0, 0)
        win32api.keybd_event(win32con.VK_CAPITAL, 0, win32con.KEYEVENTF_KEYUP, 0)


if __name__ == "__main__":
    nox_hwnd = get_window_hwnd("夜神模拟器")
    x0, y0, x1, y1 = (630, 370, 680, 420)
    click_at(nox_hwnd, (x0+x1) / 2, (y0+y1)/2)
