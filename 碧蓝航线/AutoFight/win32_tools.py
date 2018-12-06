import time

import win32api
import win32gui
import win32ui
import win32com.client
import win32con
import pywintypes
import numpy as np

from config import logger

def click_at(hwnd, x, y, ):
    # 向后台窗口发送单击事件，(x, y)为相对于窗口左上角的位置
    pos = win32api.MAKELONG(int(x), int(y))
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONDOWN,
                         win32con.MK_LBUTTON, pos)
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONUP, 0, pos)


def drag(hwnd, start, end, step=100, error=10):
    start = np.array(start, dtype='int')
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