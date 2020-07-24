import os
import time
import cv2 as cv

ADB_PATH = "D:\\Software\\adb\\adb.exe"


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
