from PIL import Image
from PIL import ImageDraw, ImageFont
import matplotlib.pyplot as plt

from simulator.win32_tools import *
from simulator.image_tools import *

const = {"s": None, "section": None}


def show(img):
    if isinstance(img, Image.Image):
        display(img)
        return
    if len(img.shape) == 3:
        if img.shape[2] == 3:
            mode = "RGB"
            img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        elif img.shape[2] == 4:
            mode = "RGBA"
            img = cv.cvtColor(img, cv.COLOR_BGRA2RGBA)
        else:
            raise ValueError("Invalid Shape %s" % img.shape)
    elif len(img.shape) == 2:
        mode = "L"
        if img.max() <= 1 and img.min() >= 0:
            img = img * 255
    else:
        raise ValueError("Invalid Shape %s" % img.shape)
    display(Image.fromarray(img.astype('uint8'), mode))


def show_matches(img, needle, thresh=0.1):
    match = get_all_match(img, needle)
    h, w = needle.shape[:2]
    draw = img.copy()
    for y, x in zip(*np.where(match < thresh)):
        print(x, y)
        cv.rectangle(draw, (x, y), (x+w, y+h), (255, 255, 255), 1)
    show(draw)


def show_crop(x, y, w, h, img=None, show_full=False):
    if img is None:
        img = const["s"].screen
    cropped = cv_crop(img, (x, y, x+w, y+h))
    h, w = cropped.shape[:2]
    show(cropped)
    if show_full:
        draw = img.copy()
        cv.rectangle(draw, (x, y), (x+w, y+h), (255, 255, 255), 2)
        show(draw)
    return cropped, (x, y)


def save_crop(name, cropped, offset):
    h, w = cropped.shape[:2]
    section = const["section"]
    with open("%s/resources/%s.json" % (section, name), 'w', -1, "UTF-8") as fl:
        json.dump({
            "Name": name,
            "MainSize": [config.getint("Device", "MainWidth"), config.getint("Device", "MainHeight")],
            "Offset": offset,
            "Size": [w, h],
            "Type": "Static",
            "Image": name + '.png'
        }, fl, ensure_ascii=False)
    cv_save("%s/resources/%s.png" % (section, name), cropped)


def show_anchor(x, y, w, h, dx, dy, img=None):
    if img is None:
        img = const["s"].screen
    cropped = cv_crop(img, (x, y, x+w, y+h))
    h, w = cropped.shape[:2]
    show(cropped)

    draw = img.copy()
    cv.rectangle(draw, (x, y), (x+w, y+h), (255, 255, 255), 2)
    cv.circle(draw, (x+dx, y+dy), 5, (255, 255, 255), -1)
    cv.circle(draw, (x+dx, y+dy), 3, (0, 0, 0), -1)
    show(draw)
    return cropped, (dx, dy)


def save_anchor(name, cropped, offset):
    h, w = cropped.shape[:2]
    section = const["section"]
    with open("%s/resources/%s.json" % (section, name), 'w', -1, "UTF-8") as fl:
        json.dump({
            "Name": name,
            "MainSize": [config.getint("Device", "MainWidth"), config.getint("Device", "MainHeight")],
            "Offset": offset,
            "Size": [w, h],
            "Type": "Anchor",
            "Image": name + '.png'
        }, fl, ensure_ascii=False)
    cv_save("%s/resources/%s.png" % (section, name), cropped)


def check_anchor(name):
    ret, pos = const["s"].search_resource(name)
    print(ret, pos)
    if not ret:
        return
    res = const["s"].resources[name]
    dx, dy = res['Offset']
    w, h = res['Size']
    show(res['ImageData'])
    draw = const["s"].screen.copy()
    if len(np.array(pos).shape) == 1:
        pos = [pos]
    for x, y in pos:
        cv.rectangle(draw, (x, y), (x+w, y+h), (255, 255, 255), 2)
        cv.circle(draw, (x+dx, y+dy), 5, (255, 255, 255), -1)
        cv.circle(draw, (x+dx, y+dy), 3, (0, 0, 0), -1)
    show(draw)


def check_scales(needle, scales, target=None, show_full=False):
    if target is None:
        target = const["s"].screen

    best = {"diff": 1}

    for scale in scales:
        new_needle = cv.resize(needle, (0, 0), fx=scale, fy=scale)
        h, w = new_needle.shape[:2]
        diff, pos = get_match(target, new_needle)
        print(scale, (w, h))
        print(diff, pos)
        if best["diff"] > diff:
            best = {"diff": diff, "scale": scale, "size": [w, h]}
        show_crop(*pos, w, h, img=target, show_full=show_full)
    print(best)
