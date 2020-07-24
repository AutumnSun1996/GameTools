from enum import IntEnum, auto
import tkinter as tk
from tkinter import simpledialog, Label

import cv2.cv2 as cv
import numpy as np
from PIL import Image, ImageTk
from shapely import geometry

from simulator import image_tools, win32_tools
from notebook.common import set_clip, show
from json_format import encode


class Status(IntEnum):
    Init = auto()
    LineStart = auto()
    LineEnd = auto()


anchors = []
cur_anchor = {"Status": Status.LineEnd, "Points": []}


def key(event):
    global anchors, cur_anchor
    print("pressed", event.keycode)
    if event.keycode == 8:
        if cur_anchor["Status"] > Status.Init:
            cur_anchor["Status"] -= 1
        elif len(anchors) > 1:
            anchors.remove(anchors[-1])
    elif event.char == "n" and cur_anchor["Status"] >= Status.LineEnd:
        cur_anchor = {"Status": Status.Init, "Points": []}
        anchors.append(cur_anchor)
        print(anchors)
    elif event.char == "s":
        print(anchors)


def on_click(event):
    global anchors, cur_anchor
    print("on_click", event.x, event.y)
    print(anchors)
    if cur_anchor["Status"] == Status.Init:
        pos = (event.x, event.y)
        cur_anchor["Points"] = [pos, pos]
        cur_anchor["Status"] = Status.LineStart
    else:
        print("Ignore", cur_anchor["Status"])


def on_move(event):
    global anchors, cur_anchor
    print("on_move", event.x, event.y)
    print(anchors)
    if cur_anchor["Status"] == Status.LineStart:
        cur_anchor["Points"][1] = (event.x, event.y)


def on_release(event):
    global anchors, cur_anchor
    print("on_release", event.x, event.y)
    print(anchors)
    if cur_anchor["Status"] == Status.LineStart:
        cur_anchor["Points"][1] = (event.x, event.y)
        cur_anchor["Status"] = Status.LineEnd
    # print()


def render():
    img = base_img.copy()
    for anchor in anchors:
        if anchor["Status"] >= Status.LineStart:
            cv.line(img, anchor["Points"][0], anchor["Points"][1], (0, 255, 0), 1)

    cv2image = cv.cvtColor(img, cv.COLOR_BGR2RGBA)  # 转换颜色从BGR到RGBA
    current_image = Image.fromarray(cv2image)
    imgtk = ImageTk.PhotoImage(image=current_image)
    panel.imgtk = imgtk
    panel.config(image=imgtk)
    root.after(20, render)


root = tk.Tk()
root.title("opencv + tkinter")
root.bind("<Key>", key)

panel = Label(root)  # initialize image panel
panel.bind("<Button-1>", on_click)
panel.bind("<B1-Motion>", on_move)
panel.bind("<ButtonRelease-1>", on_release)
panel.pack(padx=10, pady=10)

# nox_hwnd = win32_tools.get_window_hwnd("碧蓝航线模拟器")
# base_img = image_tools.get_window_shot(nox_hwnd)
base_img = image_tools.cv_imread("fgo/resources/指令卡预判.png")
img = base_img.copy()

render()

root.mainloop()
cv.destroyAllWindows()
