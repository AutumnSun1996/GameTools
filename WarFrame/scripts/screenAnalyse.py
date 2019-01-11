import ctypes
import os
import json

from PIL import Image, ImageFont, ImageDraw
import cv2.cv2 as cv
import numpy as np
import win32con
import win32gui
import win32ui


def cv_imread(file_path):
    """读取图片
    为支持中文文件名, 不能使用cv.imread
    """
    return cv.imdecode(np.fromfile(file_path, dtype='uint8'), cv.IMREAD_UNCHANGED)


def cv_save(path, image):
    """保存图片
    为支持中文文件名, 不能使用cv.imread
    """
    ext = os.path.splitext(path)[1]
    data = cv.imencode(ext, image)[1]
    data.tofile(path)


def rescale_item(item, rx, ry):
    """将每个点按rx, ry进行缩放"""
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        return {key: rescale_item(val, rx, ry) for key, val in item.items()}
    if isinstance(item, list):
        if isinstance(item[0], int):
            return (int(np.round(item[0] * rx)), int(np.round(item[1] * ry)))
        if isinstance(item[0], float):
            return (item[0] * rx, item[1] * ry)
        # 解决退役失败问题
        # (x for x in xs) 返回的是生成器, 改为返回list
        return [rescale_item(sub, rx, ry) for sub in item]
    raise ValueError("Invalid Item %s" % item)


def cv_crop(data, rect):
    """图片裁剪"""
    min_x, min_y, max_x, max_y = rect
    return data[min_y:max_y, min_x:max_x]


def split_bgra(bgra):
    """将BGRA图像分离为BGR图像和Mask"""
    bgr = bgra[:, :, :3]
    h, w = bgr.shape[:2]
    a = bgra[:, :, 3].reshape(h, w, 1)
    mask = np.concatenate((a, a, a), axis=2)
    return bgr, mask


def get_all_match(image, needle):
    """在image中搜索needle"""
    if len(needle.shape) == 3 and needle.shape[2] == 4:
        needle, mask = split_bgra(needle)
        match = 1 - cv.matchTemplate(image, needle, cv.TM_CCORR_NORMED, mask=mask)
    else:
        match = cv.matchTemplate(image, needle, cv.TM_SQDIFF_NORMED)
    return match


def get_multi_match(image, needle, thresh):
    """在image中搜索多个needle的位置

    重合的部分返回重合部分中心对应的坐标
    """
    match = get_all_match(image, needle)
    # 模拟用背景图片
    draw = np.zeros(image.shape[:2], dtype='uint8')
    h, w = needle.shape[:2]
    for y, x in zip(*np.where(match < thresh)):
        cv.rectangle(draw, (x, y), (x+w, y+h), 255, -1)
    # 连通域分析
    _, _, _, centroids = cv.connectedComponentsWithStats(draw)
    # 中心坐标转化为左上角坐标
    centroids[:, 0] -= w / 2
    centroids[:, 1] -= h / 2
    # 删去背景连通域并将数值转化为int型
    return centroids[1:, :].astype('int')


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


def get_shot(hwnd, box=None):
    # 对后台应用程序截图，程序窗口可以被覆盖，但如果最小化后只能截取到标题栏、菜单栏等。
    window_w, window_h = detect_window_size(hwnd)
    if box is None:
        dx = 0
        dy = 0
        w = window_w
        h = window_h
    else:
        dx, dy, w, h = box
        if dx+w > window_w or dy+h > window_h:
            raise ValueError("截图区域超出窗口! 请检查配置")

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


def get_window_shot(hwnd, box=None):
    # logger.debug("截图: %dx%d at %dx%d", w, h, dx, dy)
    if box is None:
        box = [8, 31, 1920, 1017]
    else:
        box = np.add(box, [8, 31, 0, 0])
    return get_shot(hwnd, box)


def make_text(text, size, color="#FFFFFF", background="#000000"):
    font = ImageFont.truetype('resources/FGO-Main-Font.ttf', size)
    # 根据文字大小创建图片
    img = Image.new("RGB", font.getsize(text), background)
    drawBrush = ImageDraw.Draw(img)  # 创建画刷，用来写文字到图片img上
    drawBrush.text((0, 0), text, fill=color, font=font)
    return cv.cvtColor(np.array(img), cv.COLOR_RGBA2BGRA)


def extract_text(image, font_size, text='0123456789/'):
    result = []
    for char in text:
        number = make_text(char, font_size)
        match = get_all_match(image, number)
        last = -10
        for x in np.where(match < 0.06)[1]:
            if x - last > 2:
                result.append((x, char))
            last = x
    result.sort(key=lambda a: a[0])
    return ''.join(item[1] for item in result)


def get_window_hwnd(title):
    return win32gui.FindWindow(None, title)


if __name__ == "__main__":
    import sys
    import datetime
    hwnd = get_window_hwnd("Warframe")
    print(hwnd)
    screen = get_window_shot(hwnd)
    print(sys.argv)
    cv_save("shot-{:%Y-%m-%d_%H%M%S}.png".format(datetime.datetime.now()), screen)
    if len(sys.argv) == 1:
        cv.imshow("ScreenShot", screen)
        cv.waitKey(0)
