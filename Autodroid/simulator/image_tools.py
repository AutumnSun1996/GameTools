import ctypes
import json
import os
import re
import yaml
import datetime

from pyhocon import ConfigFactory
import piexif
from PIL import Image, ImageFont, ImageDraw
import requests
import cv2.cv2 as cv
import numpy as np
import win32con
import win32gui
import win32ui

from config_loader import config
from config import hocon

import logging

logger = logging.getLogger(__name__)


def cv_imread(file_path):
    """读取图片
    为支持中文文件名, 不能使用cv.imread
    """
    return cv.imdecode(np.fromfile(file_path, dtype="uint8"), cv.IMREAD_UNCHANGED)


def cv_save(path, image):
    """保存图片
    为支持中文文件名, 不能使用cv.imread
    """
    ext = os.path.splitext(path)[1]
    data = cv.imencode(ext, image)[1]
    dirname = os.path.dirname(path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    data.tofile(path)


def get_xp_info(text):
    if not isinstance(text, str):
        text = json.dumps(text, ensure_ascii=False, separators=(",", ":"))
    return tuple((text + "\x00").encode("UTF-16-LE"))


def save_jpeg(
    path, image, now=None, title=None, subject=None, comment=None, keywords=None
):
    if not path.endswith((".jpg", ".jpeg")):
        path = path + ".jpg"
    image = Image.fromarray(cv.cvtColor(image, cv.COLOR_BGR2RGB))
    dirname = os.path.dirname(path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    exif_dict = {ifd: {} for ifd in ("0th", "Exif", "GPS", "1st")}
    exif_dict["0th"][piexif.ImageIFD.Artist] = "AutumnSun"
    exif_dict["0th"][piexif.ImageIFD.Software] = "AutoDroid"
    if now is None:
        now = datetime.datetime.now()
    exif_dict["Exif"][piexif.ExifIFD.DateTimeDigitized] = now.strftime(
        "%Y:%m:%d %H:%M:%S"
    )
    exif_dict["Exif"][piexif.ExifIFD.SubSecTimeDigitized] = "{:.0f}".format(
        now.microsecond
    )

    if title is not None:
        exif_dict["0th"][piexif.ImageIFD.ImageDescription] = title.encode("UTF-8")
    if subject is not None:
        exif_dict["0th"][piexif.ImageIFD.XPSubject] = get_xp_info(subject)
    if comment is not None:
        exif_dict["0th"][piexif.ImageIFD.XPComment] = get_xp_info(comment)
    if keywords is not None:
        exif_dict["0th"][piexif.ImageIFD.XPKeywords] = get_xp_info(keywords)
    exif_bytes = piexif.dump(exif_dict)
    image.save(path, "jpeg", exif=exif_bytes)


def rescale_item(item, rx, ry):
    """将每个点按rx, ry进行缩放"""
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        return {key: rescale_item(val, rx, ry) for key, val in item.items()}
    if isinstance(item, list):
        if len(item) == 2:
            if isinstance(item[0], int):
                return (int(np.round(item[0] * rx)), int(np.round(item[1] * ry)))
            if isinstance(item[0], float):
                return (item[0] * rx, item[1] * ry)
        if isinstance(item[0], list):
            # 解决退役失败问题
            # (x for x in xs) 返回的是生成器, 改为返回list
            return [rescale_item(sub, rx, ry) for sub in item]
    raise ValueError("Invalid Item %s" % item)


def update_resource(resource, section):
    """根据当前配置更新资源属性, 加载图片并进行缩放"""
    dw = config.getint("Device", "MainWidth")
    dh = config.getint("Device", "MainHeight")
    sdw, sdh = resource["MainSize"]
    if dw != sdw or dh != sdh:
        for key in resource:
            if re.search("Offset|Position|Size", key):
                resource[key] = rescale_item(resource[key], dw / sdw, dh / sdh)
    if (
        resource.get("Image", None) is not None
        or resource.get("ImageData", None) is not None
    ):
        load_image(resource, section)


def load_image(resource, section):
    if "ImageData" not in resource:
        img_path = os.path.join(
            config.get(section, "ResourcesFolder"), "Resources", resource["Image"]
        )
        resource["ImageData"] = cv_imread(img_path)
        if "Size" in resource:
            resource["ImageData"] = cv.resize(
                resource["ImageData"], tuple(resource["Size"]), cv.INTER_CUBIC
            )
        else:
            h, w = resource["ImageData"].shape[:2]
            resource["Size"] = [w, h]
    return resource["ImageData"]


def load_scenes(section):
    with open(config.get(section, "Scenes"), "r", -1, "UTF-8") as fl:
        items = yaml.load(fl)
    return items


def load_resources(section):
    with open(config.get(section, "Resources"), "r", -1, "UTF-8") as fl:
        items = yaml.load(fl)
    for resource in items.values():
        update_resource(resource, section)
    return items


def load_map(name, section, extra_property):
    path = os.path.join(config.get(section, "ResourcesFolder"), "maps", name + ".conf")
    data = hocon.load(path)
    if extra_property:
        new_args = hocon.loads("\n".join(extra_property))
        data = new_args.with_fallback(data)
    for item in data["Resources"].values():
        update_resource(item, section)
    if "Anchors" in data:
        for val in data["Anchors"].values():
            update_resource(val, section)
    return data


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
        bgr, a = split_bgra(needle)
        match = cv.matchTemplate(image, bgr, cv.TM_CCORR_NORMED, mask=a)
    else:
        match = cv.matchTemplate(image, needle, cv.TM_CCORR_NORMED)
    # 将所有nan变为1
    match = 1 - np.nan_to_num(match)
    best = match.min()
    if best < 0:
        logger.error(
            "MatchError for size {0[1]}x{0[0]}({0[2]}) in {1[1]}x{1[0]}: {2}".format(
                needle.shape, image.shape, best
            )
        )
        import pickle
        import datetime
        from utils import torch_imgdiff

        with open(
            "shots/MatchError@{:%Y-%m-%d_%H%M%S}.pkl".format(datetime.datetime.now()),
            "wb",
        ) as f:
            pickle.dump({"image": image, "needle": needle, "match": match}, f)

        return torch_imgdiff.get_all_match(image, needle)
    return match


def get_multi_match(image, needle, thresh):
    """在image中搜索多个needle的位置

    重合的部分返回重合部分中心对应的坐标
    """
    match = get_all_match(image, needle)
    h, w = needle.shape[:2]
    # 模拟填充所有找到的匹配位置
    draw = np.zeros(image.shape[:2], dtype="uint8")
    h, w = needle.shape[:2]
    for y, x in zip(*np.where(match < thresh)):
        cv.rectangle(draw, (x, y), (x + w, y + h), 255, -1)
    # 连通域分析
    _, _, _, centroids = cv.connectedComponentsWithStats(draw.astype("uint8"))
    # 删去背景连通域
    centroids = centroids[1:]
    # 中心坐标转化为左上角坐标
    centroids[:, 0] -= w / 2
    centroids[:, 1] -= h / 2
    # 将数值转化为int型
    return centroids.round().astype("int")


def get_match(image, needle):
    """在image中搜索needle"""
    diff = get_all_match(image, needle)
    loc = np.unravel_index(np.argmin(diff, axis=None), diff.shape)
    return diff[loc], loc[::-1]


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
    if dx + w > window_w or dy + h > window_h:
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
    image_data = np.frombuffer(bmpdata, "uint8")
    image_data = image_data.reshape((bmpinfo["bmHeight"], bmpinfo["bmWidth"], 4))
    image_data = cv.cvtColor(image_data, cv.COLOR_BGRA2BGR)
    # 内存释放
    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)

    return image_data


def make_text(text, size, color="#FFFFFF", background="#000000"):
    font = ImageFont.truetype("resources/FGO-Main-Font.ttf", size)
    # 根据文字大小创建图片
    img = Image.new("RGB", font.getsize(text), background)
    drawBrush = ImageDraw.Draw(img)  # 创建画刷，用来写文字到图片img上
    drawBrush.text((0, 0), text, fill=color, font=font)
    return cv.cvtColor(np.array(img), cv.COLOR_RGBA2BGRA)


def extract_text(image, font_size, text="0123456789/"):
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
    return "".join(item[1] for item in result)


class Affine:
    @staticmethod
    def move(dx, dy):
        return np.mat([[1, 0, dx], [0, 1, dy], [0, 0, 1]])

    @staticmethod
    def scale(fx, fy):
        return np.mat([[fx, 0, 0], [0, fy, 0], [0, 0, 1]])

    @staticmethod
    def rotate(theta):
        cos = np.cos(theta)
        sin = np.sin(theta)
        return np.mat([[cos, -sin, 0], [sin, cos, 0], [0, 0, 1]])

    @staticmethod
    def warp(src, mat, outsize):
        return cv.warpAffine(src, mat[:2, :].astype("float32"), outsize)


if __name__ == "__main__":
    import win32_tools
    import datetime

    logger.setLevel("DEBUG")
    nox_hwnd = win32_tools.get_window_hwnd("碧蓝航线模拟器")
    print(nox_hwnd)
    screen = get_window_shot(nox_hwnd)
    cv_save(
        "images/shot-{:%Y-%m-%d_%H%M%S}.png".format(datetime.datetime.now()), screen
    )
    cv.imshow("ScreenShot", screen)
    cv.waitKey(0)
