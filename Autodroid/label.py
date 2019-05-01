import sys
from enum import IntEnum, auto
import tkinter as tk
from tkinter import simpledialog, Label

import cv2.cv2 as cv
import numpy as np
from PIL import Image, ImageTk
from shapely import geometry

from simulator import image_tools, win32_tools
from notebook.common import set_clip, show, toyaml


class Status(IntEnum):
    Init = auto()
    RectStart = auto()
    RectEnd = auto()
    Line1Start = auto()
    Line1End = auto()
    Line2Start = auto()
    Line2End = auto()


anchors = []
cur_anchor = {"Status": Status.Line2End, "Name": None, "RectStart": None, "RectEnd": None,
              "Line1Start": None, "Line1End": None, "Line2Start": None, "Line2End": None}

section = "AzurLane"
map_name = sys.argv[1]


def extract_anchors(anchors):
    for anchor in anchors:
        name = "{}/{}".format(map_name, anchor["Name"])
        x, y = anchor["RectStart"]
        x2, y2 = anchor["RectEnd"]
        if x > x2:
            x, x2 = x2, x
        if y > y2:
            y, y2 = y2, y
        line1 = geometry.LineString([anchor["Line1Start"], anchor["Line1End"]])
        line2 = geometry.LineString([anchor["Line2Start"], anchor["Line2End"]])
        cross = line1.intersection(line2)
        dx, dy = cross.coords[0]

        cropped = image_tools.cv_crop(base_img, (x, y, x2, y2))
        path = "%s/resources/%s.png" % (section, name)
        show(cropped)
        image_tools.cv_save(path, cropped)

        yield name, {
            "Name": name,
            "Type": "Anchor",
            "MainSize": [1280, 720],
            "OnMap": anchor["Name"],
            "Size": [x2-x, y2-y],
            "Offset": [int(np.round(dx-x)), int(np.round(dy-y))],
            "Image": name+".png",
        }


def key(event):
    global anchors, cur_anchor
    print("pressed", event.keycode)
    if event.keycode == 8:
        if cur_anchor["Status"] > Status.Init:
            cur_anchor["Status"] -= 1
        elif len(anchors) > 1:
            anchors.remove(anchors[-1])
    elif event.char == "n" and cur_anchor["Status"] >= Status.Line2End:
        name = simpledialog.askstring("Input", "OnMapName")
        cur_anchor = {"Status": Status.Init, "Name": name, "RectStart": None, "RectEnd": None,
                      "Line1Start": None, "Line1End": None, "Line2Start": None, "Line2End": None}
        anchors.append(cur_anchor)
        print(anchors)
    elif event.char == "s":
        result = {key: val for key, val in extract_anchors(anchors)}
        text = toyaml(result)
        print(text)
        set_clip(text)


def on_click(event):
    global anchors, cur_anchor
    print("on_click", event.x, event.y)
    print(anchors)
    if cur_anchor["Status"] == Status.Init:
        cur_anchor["RectStart"] = (event.x, event.y)
        cur_anchor["Status"] = Status.RectStart
    elif cur_anchor["Status"] == Status.RectEnd:
        cur_anchor["Line1Start"] = (event.x, event.y)
        cur_anchor["Status"] = Status.Line1Start
    elif cur_anchor["Status"] == Status.Line1End:
        cur_anchor["Line2Start"] = (event.x, event.y)
        cur_anchor["Status"] = Status.Line2Start
    else:
        print("Ignore", cur_anchor["Status"])


def on_move(event):
    global anchors, cur_anchor
    print("on_move", event.x, event.y)
    print(anchors)
    if cur_anchor["Status"] == Status.RectStart:
        cur_anchor["RectEnd"] = (event.x, event.y)
    elif cur_anchor["Status"] == Status.Line1Start:
        cur_anchor["Line1End"] = (event.x, event.y)
    elif cur_anchor["Status"] == Status.Line2Start:
        cur_anchor["Line2End"] = (event.x, event.y)


def on_release(event):
    global anchors, cur_anchor
    print("on_release", event.x, event.y)
    print(anchors)
    if cur_anchor["Status"] == Status.RectStart:
        cur_anchor["RectEnd"] = (event.x, event.y)
        cur_anchor["Status"] = Status.RectEnd
    elif cur_anchor["Status"] == Status.Line1Start:
        cur_anchor["Line1End"] = (event.x, event.y)
        cur_anchor["Status"] = Status.Line1End
    elif cur_anchor["Status"] == Status.Line2Start:
        cur_anchor["Line2End"] = (event.x, event.y)
        cur_anchor["Status"] = Status.Line2End
    # print()


def render():
    img = base_img.copy()
    for anchor in anchors:
        if anchor["Status"] >= Status.RectStart:
            cv.rectangle(img, anchor["RectStart"], anchor["RectEnd"], (0, 255, 0), 1)
        if anchor["Status"] >= Status.Line1Start:
            cv.line(img, anchor["Line1Start"], anchor["Line1End"], (0, 255, 0), 1)
        if anchor["Status"] >= Status.Line2Start:
            cv.line(img, anchor["Line2Start"], anchor["Line2End"], (0, 255, 0), 1)

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

nox_hwnd = win32_tools.get_window_hwnd("碧蓝航线")
base_img = image_tools.get_window_shot(nox_hwnd)
img = base_img.copy()

render()

root.mainloop()
cv.destroyAllWindows()
