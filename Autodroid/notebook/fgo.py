from .common import *

from fgo.fast import FGOSimple as FateGrandOrder

const["section"] = "fgo"


def save_assist_equip(name, index=0):
    s = const["s"]

    if not name.startswith("礼装/"):
        name = "礼装/" + name
    part = s.crop_resource("助战从者定位", index=index)
    x, y = 8, 136
    w, h = 150, 42
    equip = cv_crop(part, (x, y, x + w, y + h))
    equip = cv.cvtColor(equip, cv.COLOR_BGR2BGRA)
    mask = np.ones((h, w), dtype="uint8") * 255
    mask[21:h, 20:90,] = 0
    mask[32:h, 90:120,] = 0
    mask[16:h, 120:w,] = 0
    equip[:, :, 3] = mask
    show(equip)
    save_crop(name, equip, (x, y))


def save_assist_name(name, index=0):
    s = const["s"]
    part = s.crop_resource("助战从者定位", index=index)
    name_info = s.resources["助战-从者名称"]
    ret, offset = s.search_resource(name_info["Name"], image=part)
    if not ret:
        raise ValueError("助战-从者名称 Not Found")
    name_img = s.crop_resource(name_info, image=part, offset=offset)
    dx, _ = name_info["CropOffset"]
    x = offset[0] + dx
    h, w = name_img.shape[:2]
    if not name.startswith("助战/"):
        name = "助战/" + name
    info = {
        "Name": name,
        "MainSize": [1280, 720],
        "SearchArea": [[x - 10, 60], [w + 20, 100]],
        "Size": [w, h],
        "Type": "Dynamic",
        "Image": name + ".png",
    }
    path = "fgo/resources/" + name + ".png"
    cv_save(path, name_img)
    set_clip(name[3:])
    check_resource(info, part)


def init_map(name="通用配置", section="FGO"):
    FateGrandOrder.section = section
    const["s"] = FateGrandOrder(name)
    const["s"].make_screen_shot()
    reset_log()
    return const["s"]
