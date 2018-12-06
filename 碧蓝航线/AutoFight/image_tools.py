import win32gui
import win32ui
import win32con

import cv2.cv2 as cv
import numpy as np

from config import logger, options


def cv_imread(file_path):
    return cv.imdecode(np.fromfile(file_path, dtype='uint8'), -1)


def cv_crop(data, rect):
    min_x, min_y, max_x, max_y = rect
    return data[min_y:max_y, min_x:max_x]


def get_diff(a, b):
    return cv.matchTemplate(a, b, cv.TM_SQDIFF_NORMED)[0, 0]


def get_match(image, needle):
    match = cv.matchTemplate(image, needle, cv.TM_SQDIFF_NORMED)
    minVal, maxVal, minLoc, maxLoc = cv.minMaxLoc(match)
    return minVal, np.array(minLoc)


def get_window_shot(hwnd):
    # 对后台应用程序截图，程序窗口可以被覆盖，但如果最小化后只能截取到标题栏、菜单栏等。

    # 获取句柄窗口的大小信息
    # 可以通过修改该位置实现自定义大小截图
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    w = right - left
    h = bottom - top

    # 返回句柄窗口的设备环境、覆盖整个窗口，包括非客户区，标题栏，菜单，边框
    hwndDC = win32gui.GetWindowDC(hwnd)

    # 创建设备描述表
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)

    # 创建内存设备描述表
    saveDC = mfcDC.CreateCompatibleDC()

    # 创建位图对象
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
    saveDC.SelectObject(saveBitMap)

    # 截图至内存设备描述表
    saveDC.BitBlt((0, 0), (w, h), mfcDC, (0, 0), win32con.SRCCOPY)

    # 将截图保存到文件中
    # saveBitMap.SaveBitmapFile(saveDC, 'screenshot.bmp')

    # 获取位图信息
    bmpinfo = saveBitMap.GetInfo()
    bmpdata = saveBitMap.GetBitmapBits(True)
    # 生成图像
    image_data = np.frombuffer(bmpdata, 'uint8')
    image_data = image_data.reshape(
        (bmpinfo['bmHeight'], bmpinfo['bmWidth'], 4))

    # 内存释放
    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)

    if (w, h) != options.ORIGIN_WINDOW_SIZE:
        image_data = cv.resize(
            image_data, options.ORIGIN_WINDOW_SIZE, interpolation=cv.INTER_CUBIC)
        logger.warning("Resize From %s To %s", (w, h),
                       options.ORIGIN_WINDOW_SIZE)

    return cv.cvtColor(image_data, cv.COLOR_BGRA2BGR)


if __name__ == "__main__":
    import win32_tools
    hwnd = win32_tools.get_window_hwnd("夜神模拟器")
    image = get_window_shot(hwnd)

    anchor = cv_imread("images/anchor-D7.png")
    diff, pos = get_match(image, anchor)
    if diff < 0.05:
        pass
    print(diff, pos)
