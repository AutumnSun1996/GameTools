from PIL import Image
from PIL import ImageDraw, ImageFont
import matplotlib.pyplot as plt
import itertools
import win32clipboard
import yaml

from simulator.win32_tools import *
from simulator.image_tools import *
from json_format import encode
import logging.config

from IPython.display import display

const = {"s": None, "section": None}


def reset_log():
    logging.config.dictConfig(
        yaml.safe_load(
            """
    version: 1
    formatters:
        default:
            format: '%(asctime)s - %(levelname)s - %(name)s - %(filename)s[%(lineno)d] - %(message)s'
    handlers:
        console:
            class : logging.StreamHandler
            formatter: default
            level   : DEBUG
            stream  : ext://sys.stdout
    loggers:
        __main__:
            level   : DEBUG
            handlers: [console]
        config_loader:
            level   : DEBUG
            handlers: [console]
        simulator:
            level   : DEBUG
            handlers: [console]
        azurlane:
            level   : DEBUG
            handlers: [console]
        fgo:
            level   : DEBUG
            handlers: [console]
    root:
        level   : DEBUG
        handlers: [console]
    """
        )
    )


def get_clip():
    win32clipboard.OpenClipboard()
    text = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
    win32clipboard.CloseClipboard()
    return text


def set_clip(text):
    print(text)
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(
        win32con.CF_UNICODETEXT, text.encode("UTF-16-LE") + b"\x00"
    )
    win32clipboard.CloseClipboard()


def tojson(item, prefix=""):
    return encode(item, prefix, 0)


def toyaml(item):
    return yaml.safe_dump(item, allow_unicode=True)


def to_res_text(item):
    return encode(item, '"%s": ' % item["Name"], 0) + ","


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
    display(Image.fromarray(img.astype("uint8"), mode))


def show_matches(img, needle, thresh=0.1):
    match = get_all_match(img, needle)
    h, w = needle.shape[:2]
    draw = img.copy()
    for y, x in zip(*np.where(match < thresh)):
        print(x, y)
        cv.rectangle(draw, (x, y), (x + w, y + h), (255, 255, 255), 1)
    show(draw)


def show_crop(x, y, w, h, img=None, show_full=False):
    if img is None:
        img = const["s"].screen
    cropped = cv_crop(img, (x, y, x + w, y + h))
    h, w = cropped.shape[:2]
    show(cropped)
    if show_full:
        draw = img.copy()
        cv.rectangle(draw, (x, y), (x + w, y + h), (255, 255, 255), 2)
        show(draw)
    return cropped, (x, y)


def save_crop(name, cropped, offset=None):
    section = const["section"]
    path = "%s/resources/%s.png" % (section, name)
    cv_save(path, cropped)
    logger.info("%s Saved.", os.path.realpath(path))
    if offset is None:
        return
    h, w = cropped.shape[:2]
    info = {
        "Name": name,
        "MainSize": [
            config.getint("Device", "MainWidth"),
            config.getint("Device", "MainHeight"),
        ],
        "Offset": list(offset),
        "Size": [w, h],
        "Type": "Static",
        "Image": name + ".png",
    }

    # set_clip('{}: {},'.format(tojson(name), tojson(info)))
    set_clip(hocon.dump({name: info}))


def show_anchor(x, y, w, h, dx, dy, img=None, show_full=True):
    if img is None:
        img = const["s"].screen
    cropped = cv_crop(img, (x, y, x + w, y + h))
    h, w = cropped.shape[:2]
    show(cropped)
    if show_full:
        draw = img.copy()
        cv.rectangle(draw, (x, y), (x + w, y + h), (255, 255, 255), 2)
        cv.circle(draw, (x + dx, y + dy), 5, (255, 255, 255), -1)
        cv.circle(draw, (x + dx, y + dy), 3, (0, 0, 0), -1)
        show(draw)
    return cropped, (dx, dy)


def save_anchor(name, cropped, offset):
    h, w = cropped.shape[:2]
    section = const["section"]
    anchor = {
        "Name": name,
        "MainSize": [
            config.getint("Device", "MainWidth"),
            config.getint("Device", "MainHeight"),
        ],
        "Offset": offset,
        "Size": [w, h],
        "Type": "Anchor",
        "Image": name + ".png",
    }
    # set_clip('{}: {},'.format(tojson(name), tojson(anchor)))
    set_clip(hocon.dump({name: anchor}))

    path = "%s/resources/%s.png" % (section, name)
    cv_save(path, cropped)
    logger.info("%s Saved.", os.path.realpath(path))


def save_map_anchor(map_name, on_map, cropped, offset):
    h, w = cropped.shape[:2]
    section = const["section"]
    name = map_name + "-" + on_map
    anchor = {
        "Name": name,
        "MainSize": [
            config.getint("Device", "MainWidth"),
            config.getint("Device", "MainHeight"),
        ],
        "Offset": offset,
        "Size": (w, h),
        "Type": "Anchor",
        "OnMap": on_map,
        "Image": name + ".png",
    }
    # set_clip('{}: {},'.format(tojson(name), tojson(anchor)))
    set_clip(toyaml({name: anchor}))

    path = "%s/resources/%s.png" % (section, name)
    cv_save(path, cropped)
    logger.info("%s Saved.", os.path.realpath(path))


def check_anchor(name):
    ret, pos = const["s"].search_resource(name)
    print(ret, pos)
    if not ret:
        return
    res = const["s"].resources[name]
    dx, dy = res["Offset"]
    w, h = res["Size"]
    show(res["ImageData"])
    draw = const["s"].screen.copy()
    if len(np.array(pos).shape) == 1:
        pos = [pos]
    for x, y in pos:
        cv.rectangle(draw, (x, y), (x + w, y + h), (255, 255, 255), 2)
        cv.circle(draw, (x + dx, y + dy), 5, (255, 255, 255), -1)
        cv.circle(draw, (x + dx, y + dy), 3, (0, 0, 0), -1)
    show(draw)


def check_scales(needle, scales, target=None, show=True, show_full=False):
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
            best = {"diff": diff, "scale": scale, "size": [w, h], "pos": pos}
        if show:
            show_crop(*pos, w, h, img=target, show_full=show_full)
    return best


def check_resource(info, image=None):
    s = const["s"]
    if image is None:
        image = s.screen

    draw = image.copy()

    if isinstance(info, str):
        if "\n" in info:
            try:
                info = hocon.loads(info)
            except hocon.ParseBaseException:
                info = yaml.safe_load(info)

            keys = list(info.keys())
            if len(keys) == 1:
                info = info[keys[0]]
                if "Name" not in info:
                    info["Name"] = keys[0]

    if isinstance(info, str):
        name = info
        info = s.resources[name]
    else:
        name = info["Name"]
        update_resource(info, s.section)
        s.resources[name] = info

    if "ImageData" in info:
        target = info["ImageData"]
        print("Target")
        show(target)

    if "SearchArea" in info:
        xy, wh = info["SearchArea"]
        x, y = xy
        w, h = wh
        cv.rectangle(draw, (x, y), (x + w, y + h), (255, 0, 0), 1)

    if "ImageData" in info:
        ret, offsets = s.search_resource(name, image)
        if not ret and "Static" in info["Type"]:
            diff, offset = get_match(image, info["ImageData"])
            print("best match:", diff, offset)
            dx, dy = offset
            w, h = info["Size"]
            cv.rectangle(draw, (dx, dy), (dx + w, dy + h), (255, 255, 255), 1)

    if info["Type"] == "Static":
        offsets = [info["Offset"]]
    elif info["Type"] == "MultiStatic":
        offsets = info["Positions"]
    elif "ImageData" in info:
        # ret, offsets = s.search_resource(name, image)
        print("search_resource:", ret, offsets)
    else:
        print("Invalid Info:", info)
        offsets = []

    for offset in np.reshape(offsets, (-1, 2)):
        dx, dy = offset
        w, h = info["Size"]
        cv.rectangle(draw, (dx, dy), (dx + w, dy + h), (255, 255, 0), 1)

        if "ClickOffset" in info or "ClickSize" in info:
            x, y = info.get("ClickOffset", info.get("Offset", (0, 0)))
            w, h = info.get("ClickSize", info["Size"])
            cv.rectangle(
                draw, (x + dx, y + dy), (x + dx + w, y + dy + h), (0, 255, 0), 1
            )

        if "CropOffset" in info or "CropSize" in info:
            x, y = info.get("CropOffset", info.get("Offset", (0, 0)))
            w, h = info.get("CropSize", info["Size"])
            cv.rectangle(
                draw, (x + dx, y + dy), (x + dx + w, y + dy + h), (0, 0, 255), 1
            )
    show(draw)


def image_intersection(imgs):
    h, w = imgs[0].shape[:2]
    result = np.zeros((h, w, 4), dtype="uint8")
    result[:, :, :3] = imgs[0]
    mask = np.ones((h, w), dtype="bool")
    for a, b in itertools.combinations(imgs, 2):
        mask &= (a == b).sum(axis=2) == 3
        show(mask)
    result[:, :, 3] = mask * 255
    return result
