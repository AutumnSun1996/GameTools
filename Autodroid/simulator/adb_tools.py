import os
import time
import re
import numpy as np
import cv2.cv2 as cv
from adb_shell.adb_device import AdbDeviceTcp, AdbDeviceUsb
from config_loader import config

ADB_PATH = config.get("Path", "ADB")

devices = {}


def init_device(name):
    lines = os.popen("{} devices -l".format(ADB_PATH)).read()
    mds = re.findall(r"(?m)^([\d\.]+):(\d+).+?model:(\w+) ", lines)
    mds = {name: (ip, int(port)) for ip, port, name in mds}
    ip, port = mds[name]
    device = AdbDeviceTcp(ip, port)
    device.connect()
    return device


def get_screencap(info):
    if info not in devices:
        devices[info] = init_device(info)
    device = devices[info]
    data = device.shell("screencap -p", decode=False)
    img = cv.imdecode(np.frombuffer(data, dtype="uint8"), cv.IMREAD_UNCHANGED)
    img = cv.cvtColor(img, cv.COLOR_BGRA2BGR)
    return img


def screen_record():
    ret = os.system(
        "{} shell screenrecord --time-limit 2 --bit-rate 40M --verbose /sdcard/tmp_screenrec.mp4".format(
            ADB_PATH
        )
    )
    print("shot", ret)
    ret = os.system(
        "{} pull /sdcard/tmp_screenrec.mp4 tmp/screenrec.mp4".format(ADB_PATH)
    )
    print("pull", ret)
    cap = cv.VideoCapture()
    if not cap.open("tmp/screenrec.mp4"):
        print("Open failed")
        return None
    frames_num = cap.get(cv.CAP_PROP_FRAME_COUNT)
    cap.set(cv.CAP_PROP_POS_FRAMES, frames_num - 1)
    ret, img = cap.read()
    print(ret)
    cap.release()
    return img


def click_at(x, y):
    os.system("{} shell input tap {} {}".format(ADB_PATH, x, y))


def drag(x0, y0, x1, y1):
    duration = 200
    os.system(
        "{} shell input swipe {} {} {} {} {}".format(ADB_PATH, x0, y0, x1, y1, duration)
    )


if __name__ == "__main__":
    img = screen_record()
    click_at(50, 200)
