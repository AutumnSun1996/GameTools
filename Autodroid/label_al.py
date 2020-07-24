import sys
import copy
from enum import IntEnum, auto
import tkinter as tk
from tkinter import simpledialog, Label
import itertools

import cv2.cv2 as cv
import numpy as np
from PIL import Image, ImageTk
from shapely import geometry

from simulator import image_tools, win32_tools
from notebook.azurlane import *

import itertools

trans_matrix = np.mat(
    [
        [0.9433189178530791, 0.2679732964804766, -158.43695741776074],
        [1.3417181644390942e-05, 1.5656008796635157, -92.70256198000683],
        [7.711117850185767e-07, 0.0005944962831996344, 1.0],
    ]
)
filter_kernel = np.array([[-4, -2, -4], [-2, 24, -2], [-4, -2, -4]])
target_size = (980, 725)
_, inv_trans = cv.invert(trans_matrix)
inv_trans = inv_trans / inv_trans[2, 2]


crop_set = {
    "CropOffset": [-30, -30],
    "CropSize": [60, 60],
}

anchor_template = {
    "CropOffset": [-40, -40],
    "CropSize": [80, 80],
    "Size": crop_set["CropSize"],
    "Type": "Anchor",
    "MainSize": [1280, 720],
}


def get_cadidates(screen):
    warped = cv.warpPerspective(screen, trans_matrix, target_size)
    filtered_map = cv.filter2D(warped, 0, filter_kernel)
    #     show(res)
    _, poses = s.search_resource("Corner", image=filtered_map)
    if len(poses) < 4:
        raise ValueError("Less than 4 anchors found. Stop.")
    poses = np.array(poses)
    poses += s.resources["Corner"]["Offset"]
    diff = poses % 100
    dx = np.argmax(np.bincount(diff[:, 0]))
    dy = np.argmax(np.bincount(diff[:, 1]))

    res = itertools.product(
        range(dx, target_size[0], 100), range(dy, target_size[1], 100)
    )
    res = (np.array(list(res), dtype="float") + 50).reshape(1, -1, 2)

    pos_in_screen = cv.perspectiveTransform(res, inv_trans).reshape(-1, 2).astype("int")
    return res.reshape(-1, 2).astype("int"), pos_in_screen


def crop_anchor(screen, x, y):
    offset = crop_set["CropOffset"]
    size = crop_set["CropSize"]
    wh = np.array(list(reversed(s.screen.shape[:2])))
    coef = 0.0005907301142274507

    diff_s = []
    results = []
    r = coef * y + 1
    lt = np.asarray(offset) * r + [x, y]
    rb = lt + np.asarray(size) * r
    if lt.min() < 0:
        return None
    if np.any(rb > wh):
        return None
    part = cv_crop(screen, (*lt.astype("int"), *rb.astype("int")))
    part = cv.resize(part, tuple(size))
    return part


def extract_anchors(anchors):
    res = {}
    for anchor in anchors:
        name = "{}/{}".format(map_name, anchor["Name"])
        x, y = anchor["Pos"]
        cropped = crop_anchor(s.screen, x, y)
        path = "%s/resources/%s.png" % (section, name)
        image_tools.cv_save(path, cropped)
        info = copy.deepcopy(anchor_template)
        info.update(
            {"Name": name, "OnMap": anchor["Name"], "Image": name + ".png",}
        )
        res[name] = info
    return res


def key(event):
    global anchors
    print("pressed", event.keycode)
    if event.keycode == 8 or event.keycode == 46:
        # delete
        print("Remove from", anchors)
        if anchors:
            anchors.remove(anchors[-1])
    elif event.char == "s":
        result = extract_anchors(anchors)
        text = hocon.dump(result)
        print(text)
        set_clip(text)


def get_nearest(point, candidates):
    near = None
    near_dist = np.inf
    for p in candidates:
        dist = np.linalg.norm(np.subtract(p, point))
        if dist < near_dist:
            near = p
            near_dist = dist
    return near


def get_name(compare, pos):
    old_ = cv.perspectiveTransform(
        np.array(compare["Pos"]).reshape(1, -1, 2).astype("float32"), trans_matrix
    )
    new_ = cv.perspectiveTransform(
        np.array(pos).reshape(1, -1, 2).astype("float32"), trans_matrix
    )
    diff = np.round((new_ - old_).reshape(2) / 100).astype("int")
    print(old_, new_, (new_ - old_), diff)
    name = np.add(diff, [ord(i) for i in compare["Name"]])
    name = "".join([chr(i) for i in name])
    return name


def on_click(event):
    global anchors, points
    print("on_click", event.x, event.y)
    pos = get_nearest((event.x, event.y), points)
    print("Nearest", pos)
    if not anchors:
        name = simpledialog.askstring("Input", "OnMapName")
    else:
        name = get_name(anchors[0], pos)
    anchors.append(
        {"Name": name, "Pos": tuple(pos),}
    )


def render():
    img = s.screen.copy()
    for pos in points:
        cv.circle(img, tuple(pos), 3, (255, 255, 255), -1)
    for anchor in anchors:
        x, y = anchor["Pos"]
        cv.putText(img, anchor["Name"], (x - 20, y), 0, 1, (255, 255, 0), 2)
    cv2image = cv.cvtColor(img, cv.COLOR_BGR2RGBA)  # 转换颜色从BGR到RGBA
    current_image = Image.fromarray(cv2image)
    imgtk = ImageTk.PhotoImage(image=current_image)
    panel.imgtk = imgtk
    panel.config(image=imgtk)
    root.after(20, render)


anchors = []

section = "AzurLane"

map_name = sys.argv[1]
s = init_map("通用地图")
_, points = get_cadidates(s.screen)
print("Init Points", points)
root = tk.Tk()
root.title("opencv + tkinter")
root.bind("<Key>", key)

panel = Label(root)  # initialize image panel
panel.bind("<Button-1>", on_click)
panel.pack(padx=10, pady=10)

render()

root.mainloop()
cv.destroyAllWindows()
