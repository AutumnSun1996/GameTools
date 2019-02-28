from .common import *

from fgo.fast import FGOSimple as FateGrandOrder

const["section"] = "fgo"


def save_assist_equip(name, index=0):
    s = const["s"]
    part = s.crop_resource("助战从者定位", index=index)
    offset = (5, 135)
    equip = cv_crop(part, (5, 135, 5+158, 135+45))
    equip = cv.cvtColor(equip, cv.COLOR_BGR2BGRA)
    for i in range(44, 130):
        for j in range(32, 45):
            equip[j, i, 3] = 0
    for i in range(130, 158):
        for j in range(21, 45):
            equip[j, i, 3] = 0
    show(equip)
    save_crop(name, equip, offset)


def save_assist_name(name, index=0, width=100):
    s = const["s"]
    x = 310
    h = 32
    info = {
        "Name": name,
        "MainSize": [1280, 720],
        "SearchArea": [
            [x-10, 60],
            [width+20, 100]
        ],
        "Size": [width, h],
        "Type": "Dynamic",
        "Image": name+".png",
    }
    part = s.crop_resource("助战从者定位", index=index)
    name_part = s.crop_resource("助战-从者名称", image=part)
    name_part = name_part[:, :width, :]
    path = "fgo/resources/"+name+".png"
    cv_save(path, name_part)
    set_clip('{}: {},'.format(json.dumps(name, ensure_ascii=False), json.dumps(info, ensure_ascii=False)))

    update_resource(info, s.section)
    s.resources[name] = info
    check_resource(name, part)


def init_map(name="通用配置", section="FGO"):
    FateGrandOrder.section = section
    const["s"] = FateGrandOrder(name)
    const["s"].make_screen_shot()
    return const["s"]
