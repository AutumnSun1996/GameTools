import argparse
import logging
import os
from datetime import datetime
import cv2.cv2 as cv

from simulator import image_tools, win32_tools
logging.basicConfig(level="DEBUG")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("title", default="FGO1", help="Title of Simulator")
    parser.add_argument("save_dir", nargs="?", default=None, help="Dir to save shot.")
    args = parser.parse_args()

    if args.save_dir is None:
        args.save_dir = args.title + "/shots"

    hwnd = win32_tools.get_window_hwnd(args.title)
    img = image_tools.get_window_shot(hwnd)
    path = os.path.join(args.save_dir, "Shot-{:%Y-%m-%d_%H%M%S}.jpg".format(datetime.now()))

    window_name = "Screen Shot Preview"
    cv.namedWindow(window_name, cv.WINDOW_AUTOSIZE)
    cv.imshow(window_name, img)
    key = cv.waitKey(5000)
    if key == -1:
        print("Time out.")
    else:
        print("Pressed", key)
    if key != 27:
        image_tools.cv_save(path, img)
        print(path, "Saved.")
    cv.destroyAllWindows()


if __name__ == "__main__":
    main()
