import time

import win32con
import ctypes
import pywintypes
import win32api
import win32gui
import win32com.client
import numpy as np

import logging
logger = logging.getLogger(__name__)



def get_window_hwnd(title):
    return win32gui.FindWindow(None, title)

hwnd = get_window_hwnd("Warframe")
print(hwnd)
win32gui.PostMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_SPACE, 0)
time.sleep(0.01)
win32gui.PostMessage(hwnd, win32con.WM_KEYUP, win32con.VK_SPACE, 0)

