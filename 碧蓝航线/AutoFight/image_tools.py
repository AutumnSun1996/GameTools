import os

import cv2.cv2 as cv
import numpy as np
import ctypes
import win32con
import win32gui
import win32ui


from config import logger, config


def cv_imread(file_path):
    """读取图片
    为支持中文文件名, 不能使用cv.imread
    """
    return cv.imdecode(np.fromfile(file_path, dtype='uint8'), -1)


def cv_save(path, image):
    """保存图片
    为支持中文文件名, 不能使用cv.imread
    """
    ext = os.path.splitext(path)[1]
    data = cv.imencode(ext, image)[1]
    data.tofile(path)


def rescale_item(item, rx, ry):
    """将每个点按rx, ry进行缩放"""
    if isinstance(item[0], int):
        return (int(np.round(item[0] * rx)), int(np.round(item[1] * ry)))
    else:
        # 解决退役失败问题
        # (x for x in xs) 返回的是生成器, 改为返回list
        return [rescale_item(sub, rx, ry) for sub in item]


def update_resource(resource, folder='.'):
    """根据当前配置更新资源属性, 加载图片并进行缩放"""
    dw = config.getint("Device", "MainWidth")
    dh = config.getint("Device", "MainHeight")
    sdw, sdh = resource["MainSize"]
    for key in resource:
        if isinstance(resource[key], list):
            resource[key] = rescale_item(resource[key], dw/sdw, dh/sdh)
    if resource.get("Image"):
        img_path = os.path.join(folder, resource["Image"])
        resource["ImageData"] = cv.resize(cv_imread(img_path), resource["Size"], cv.INTER_CUBIC)


def cv_crop(data, rect):
    """图片裁剪"""
    min_x, min_y, max_x, max_y = rect
    return data[min_y:max_y, min_x:max_x]



def get_all_match(image, needle):
    """在image中搜索needle"""
    match = cv.matchTemplate(image, needle, cv.TM_SQDIFF_NORMED)
    return match

def get_match(image, needle):
    """在image中搜索needle"""
    match = get_all_match(image, needle)
    min_val, _, min_loc, _ = cv.minMaxLoc(match)
    return min_val, np.array(min_loc)

def get_diff(a, b):
    """比较图片差异"""
    return get_match(a, b)[0]



def detect_window_size(hwnd):
    """获取窗口的大小信息"""
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    dpi = ctypes.windll.user32.GetDpiForWindow(hwnd)
    w = right - left
    h = bottom - top
    if dpi != 96:
        w = int(w * dpi / 96)
        h = int(h * dpi / 96)
    return w, h


def get_window_shot(hwnd):
    # 对后台应用程序截图，程序窗口可以被覆盖，但如果最小化后只能截取到标题栏、菜单栏等。

    # 使用自定义的窗口边缘和大小设置
    dx = config.getint("Device", "EdgeOffsetX")
    dy = config.getint("Device", "EdgeOffsetY")
    w = config.getint("Device", "MainWidth")
    h = config.getint("Device", "MainHeight")
    window_w, window_h = detect_window_size(hwnd)
    if dx+w > window_w or dy+h > window_h:
        raise ValueError("截图区域超出窗口! 请检查配置文件")
    # logger.debug("截图: %dx%d at %dx%d", w, h, dx, dy)

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
    saveDC.BitBlt((0, 0), (w, h), mfcDC, (dx, dy), win32con.SRCCOPY)
    # 获取位图信息
    bmpinfo = saveBitMap.GetInfo()
    bmpdata = saveBitMap.GetBitmapBits(True)
    # 生成图像
    image_data = np.frombuffer(bmpdata, 'uint8')
    image_data = image_data.reshape((bmpinfo['bmHeight'], bmpinfo['bmWidth'], 4))
    image_data = cv.cvtColor(image_data, cv.COLOR_BGRA2BGR)
    # 内存释放
    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)

    return image_data


if __name__ == "__main__":
    import win32_tools
    logger.setLevel("DEBUG")
    nox_hwnd = win32_tools.get_window_hwnd("碧蓝航线模拟器")
    print(nox_hwnd)
    cv.imshow("ScreenShot", get_window_shot(nox_hwnd))
    cv.waitKey(0)
    # screen_shot = get_window_shot(nox_hwnd)

    # target = cv_imread("images/作战补给.png")
    # diff, pos = get_match(screen_shot, target)
    # print(diff, pos)

    # anchor = cv_imread("images/SP地图.png")
    # diff, pos = get_match(screen_shot, anchor)
    # print(diff, pos)
    # cv.imwrite("images/screen.png", screen_shot)
