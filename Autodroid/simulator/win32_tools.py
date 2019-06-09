import time

import win32con
import ctypes
import pywintypes
import win32api
import win32gui
import win32com.client
import numpy as np

from config_loader import config

import logging
logger = logging.getLogger(__name__)


def rescale_point(hwnd, point):
    dpi = ctypes.windll.user32.GetDpiForWindow(hwnd)
    x = point[0] + config.getint("Device", "EdgeOffsetX")
    y = point[1] + config.getint("Device", "EdgeOffsetY")
    # logger.debug("Rescale: %s -> %s", point, (x, y))
    return int(np.round(x * 96 / dpi)), int(np.round(y * 96 / dpi))


def click_at(hwnd, x, y, hold=0):
    # 向后台窗口发送单击事件，(x, y)为相对于窗口左上角的位置
    x, y = rescale_point(hwnd, (x, y))
    pos = win32api.MAKELONG(int(x), int(y))
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONDOWN,
                         win32con.MK_LBUTTON, pos)
    time.sleep(hold)
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONUP, 0, pos)


def rand_point(p, diff=0.2):
    if not isinstance(diff, (list, tuple)):
        diff = [diff, diff]

    res = []
    for i in range(2):
        if isinstance(diff[i], float) and 0 < diff[i] <= 1:
            delta = p[i] * diff[i]
        else:
            delta = diff[i]
        logger.debug("p[%d]=%.0f+-%.1f", i, p[i], delta)
        if delta == 0:
            res.append(delta)
        else:
            res.append(np.random.triangular(p[i] - delta, p[i], p[i] + delta))
    logger.debug("Randomrize %s +- %s to %s", p, diff, res)
    return res


def rand_drag(hwnd, start, end, step=100, start_delay=0):
    start = rescale_point(hwnd, start)
    end = rescale_point(hwnd, end)
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONDOWN,
                         win32con.MK_LBUTTON, win32api.MAKELONG(*start))
    time.sleep(start_delay)

    dx = abs(start[0]-end[0])
    dy = abs(start[1]-end[1])
    dist = np.sqrt(dx**2+dy**2)
    delta = [max(5, int(0.2*dx)), max(5, int(0.2*dy))]
    # 最少需要2个坐标
    count = max(int(dist / step), 2)
    points = np.zeros((count, 2))
    points[:, 0] = np.linspace(start[0], end[0], count)
    points[:, 1] = np.linspace(start[1], end[1], count)
    points = points.astype('int')
    for point in points:
        time.sleep(0.05)
        target = win32api.MAKELONG(*[int(n) for n in rand_point(point, delta)])
        win32gui.SendMessage(hwnd, win32con.WM_MOUSEMOVE,
                             win32con.MK_LBUTTON, target)
    time.sleep(0.1)
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONUP, 0, target)


def drag(hwnd, start, end, step=100, start_delay=0):
    start = rescale_point(hwnd, start)
    end = rescale_point(hwnd, end)
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONDOWN,
                         win32con.MK_LBUTTON, win32api.MAKELONG(*start))
    time.sleep(start_delay)

    count = int(np.linalg.norm(np.array(start) - np.array(end)) / step)
    # 最少需要2个坐标
    count = max(count, 2)
    points = np.zeros((count, 2))
    points[:, 0] = np.linspace(start[0], end[0], count)
    points[:, 1] = np.linspace(start[1], end[1], count)
    points = points.astype('int')
    for point in points:
        time.sleep(0.05)
        target = win32api.MAKELONG(*point)
        win32gui.SendMessage(hwnd, win32con.WM_MOUSEMOVE,
                             win32con.MK_LBUTTON, target)
    time.sleep(0.1)
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONUP, 0, target)


def rand_click(hwnd, rect, hold=0):
    x_min, y_min, x_max, y_max = rect
    x = np.random.triangular(x_min, (x_min + x_max) / 2, x_max)
    y = np.random.triangular(y_min, (y_min + y_max) / 2, y_max)
    click_at(hwnd, x, y, hold)


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
