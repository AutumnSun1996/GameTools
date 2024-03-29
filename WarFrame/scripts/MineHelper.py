import time

T0 = time.time()
import logging

DEBUG = True
logging.basicConfig(
    level="DEBUG" if DEBUG else "WARNING",
    filename="tmp.log",
    format="%(asctime)s:%(levelname)s:%(funcName)s[%(lineno)d]:%(message)s",
)
logger = logging.getLogger()
logger.warning("Inited At %s", T0)

import os
import sys
import datetime
import win32gui
import win32ui
import win32con
import numpy as np
import cv2 as cv

logger.info("Import End")

# POS_PER_SEC = 258.07
POS_PER_SEC = 250
# CENTER = (1438, 940)
# RADIUS = 300
CENTER = (959, 530)
RADIUS = 185
PRE_RELEASE = 60
SAVE_SHOTS = True
MAX_PRESSING = 5

checked = 0


def get_match(image, needle):
    """在image中搜索needle"""
    match = get_all_match(image, needle)
    min_val, _, min_loc, _ = cv.minMaxLoc(match)
    return min_val, np.array(min_loc)


def cv_imread(file_path):
    """读取图片
    为支持中文文件名, 不能使用cv.imread
    """
    return cv.imdecode(np.fromfile(file_path, dtype='uint8'), cv.IMREAD_UNCHANGED)


def get_shot(
    hwnd, dx, dy, w, h,
):
    # 对后台应用程序截图，程序窗口可以被覆盖，但如果最小化后只能截取到标题栏、菜单栏等。
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


def split_bgra(bgra):
    """将BGRA图像分离为BGR图像和Mask"""
    bgr = bgra[:, :, :3]
    h, w = bgr.shape[:2]
    a = bgra[:, :, 3].reshape(h, w, 1)
    mask = np.concatenate((a, a, a), axis=2)
    return bgr, mask


def get_match_x(image, match):
    """在image中搜索needle的横向位置"""
    needle, mask = match
    match = 1 - cv.matchTemplate(image, needle, cv.TM_CCORR_NORMED, mask=mask)
    min_val, _, min_loc, _ = cv.minMaxLoc(match)
    return min_val, min_loc[0]


def check_screen(left, right, extra):
    global checked
    x, y = CENTER
    r = RADIUS
    screen = get_shot(0, x - r, y - r, 2 * r, 2 * r)

    rotated = cv.rotate(screen, cv.ROTATE_90_COUNTERCLOCKWISE)
    circle = cv.warpPolar(rotated, (300, 1000), (r, r), RADIUS, cv.WARP_POLAR_LINEAR)
    circle = cv.rotate(circle, cv.ROTATE_90_COUNTERCLOCKWISE)
    ring = circle[:150]
    if SAVE_SHOTS:
        dt = time.time() - T0
        name = "shots/ring-%s+%s.png" % (T0, dt)
        cv.imwrite(name, ring)
        logger.info("%s Saved.", name)

    diffe, xe = get_match_x(ring, extra)
    checked += 1
    xe += extra[0].shape[2] / 2
    if diffe < 0.2:
        logger.info("Found Extra=%s", xe)
        return xe
    diff0, x0 = get_match_x(ring, left)
    diff1, x1 = get_match_x(ring, right)
    x1 += right[0].shape[1]
    if diff0 > 0.3 or diff1 > 0.3:
        name = "shots/NoMatch-{}+{}.png".format(T0, time.time() - T0)
        cv.imwrite(name, ring)
        logger.warning(
            "Not Valid Match. diff=%s, %s, %s for %s", diffe, diff0, diff1, name
        )
        return None
    logger.info("Found left=%s, right=%s", x0, x1)
    return (x0 + x1) / 2


def check_mine():
    match_left = cv_imread("resources/MarkLeft.png")
    match_right = cv.rotate(match_left, cv.ROTATE_180)
    match_extra = cv_imread("resources/MarkExtra.png")
    match_left = split_bgra(match_left)
    match_right = split_bgra(match_right)
    match_extra = split_bgra(match_extra)
    logger.info("Res Loaded")
    while True:
        dt = time.time() - T0
        pos = dt * POS_PER_SEC
        target_pos = check_screen(match_left, match_right, match_extra)
        if target_pos is None:
            if dt > MAX_PRESSING:
                logger.warning("Timeout at %ss", dt)
                return
            continue
        left = (target_pos - pos - PRE_RELEASE) / POS_PER_SEC
        logger.info("Pos=%s, Target=%s, left=%s at %ss", pos, target_pos, left, dt)
        if 0 < left < 0.4:
            logger.info("Wait and check.")
            time.sleep(0.2)
            logger.info("Use previous target_pos %s.", target_pos)
            dt = time.time() - T0
            pos = dt * POS_PER_SEC
            left = (target_pos - pos - PRE_RELEASE) / POS_PER_SEC

        if left < 0:
            logger.info("Release.")
            return
        if left < 0.2:
            logger.info("Wait and release.", pos, target_pos, left)
            time.sleep(left)
            logger.info("Release in %ss", time.time() - T0)
            return
        logger.info("Wait.", pos, target_pos)
        # time.sleep(wait)


def shot():
    x, y = CENTER
    r = RADIUS
    screen = get_shot(0, x - r, y - r, 2 * r, 2 * r)
    logger.info("Screen Capurted")
    cv.imwrite("images/screen.png", screen)

    rotated = cv.rotate(screen, cv.ROTATE_90_COUNTERCLOCKWISE)
    logger.info("Rotate End")
    circle = cv.warpPolar(rotated, (300, 1000), (r, r), RADIUS, cv.WARP_POLAR_LINEAR)
    logger.info("warpPolar End")
    circle = cv.rotate(circle, cv.ROTATE_90_COUNTERCLOCKWISE)
    logger.info("Rotate End")
    ring = circle[:150]
    logger.info("All Transform End")
    cv.imwrite("images/ring.png", ring)
    logger.info("Saved")


def main():
    logger.info("Start Main")
    if sys.argv[1] == "test":
        pass
    elif sys.argv[1] == "shot":
        shot()
    else:
        check_mine()
        logger.warning("Checked=%d, fps=%.3f", checked, checked / (time.time() - T0))
    logger.info("End Main")


if __name__ == "__main__":
    logger.info("Check %s", sys.argv)
    try:
        T1 = T0
        T0 = datetime.datetime.strptime(sys.argv[2], "%Y%m%d%H%M%S.%f").timestamp()
        logger.info("Recorded T0 - Given T0=%s. Update T0 to %s", T1 - T0, T0)
    except Exception as err:
        logger.warning("Parse failed, use original T0=%s", T0)

    try:
        main()
    except Exception as e:
        logger.exception(str(e))
