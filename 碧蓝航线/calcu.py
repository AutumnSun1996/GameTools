#! /usr/bin/env python
# -*- coding: utf-8 -*- 
import pyquery
import requests
import re
import numpy as np
import time

# 对舰输出, 生存能力， 防空性能
weights = {
    "默认": [30, 20, 1],
    "航母": [80, 15, 1],
    "战列": [60, 40, 1],
    "轻巡": [30, 20, 5],
    "重巡": [30, 40, 1],
    "驱逐": [30, 20, 1],
}
show_count = 12

filter_set = set()
def accept(ship):
    if not ship.get("对舰输出"):
        return False
    name = ship["Name"]
    if name.endswith("改"):
        name = name[:-1]

    if name not in own_now:
        ship["Extra"] = "NotOwn " + ship["Extra"]
        # return False

    if name in filter_set:
        return False
    else:
        filter_set.add(name)
        return True

nums = re.compile(r"(\d+\.)?\d+")

def get_info_online(entry):
    TypeDict = {"zhanlie": "战列", "quzhu": "驱逐", "hangmu": "航母", "qingxun": "轻巡", "zhongxun": "重巡"}
    # print("{!r} {!r} {!r}".format(entry, entry.parent(), entry.attr("class")))
    ship_type = re.compile(r"\d+([a-z]+)shuchu").search(entry.parent().attr("class")).group(1)
    info = [item.text() for item in entry("div.panel-body > p").items()]
    cur_ship = {
        "Name": info[0],
        "Type": TypeDict.get(ship_type, "其他"),
        "Extra": "",
    }
    if entry("div.panel-footer"):
        cur_ship["Extra"] = "(" + entry("div.panel-footer").text() + ")"
    for each in info[1:]:
        idx = each.find("：")
        cur_ship[each[:idx]] = float(re.compile(r"[.\d]+").search(each).group(0))
    return cur_ship

def get_list(url):
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
    }
    res = requests.get(url, headers=headers)
    if res.encoding == "ISO-8859-1":
        res.encoding = res.apparent_encoding
    pq = pyquery.PyQuery(res.text)
    return [get_info_online(s) for s in pq("#LTputintable span.itemhover").items()]


def harm_mean(arr, weight=None):
    arr = 1 / (np.array(arr) + 1)
    if weight is not None:
        arr = np.array(arr) * np.array(weight) / np.mean(weight)
    return (1 / arr.mean()) - 1
    
def score(s):
    try:
        # print(s)
        s["Score"] = harm_mean([s["对舰输出"], s["生存能力"], s["防空性能"]/10], weights.get(s["Type"]) or weights["默认"])
        return -s["Score"]
    except:
        # print(s)
        # print("Error", e)
        return 0

def str_width(text):
    return sum([1 if ord(c) < 0xFF else 2 for c in text])

def set_name_format(ship, size=10):
    suffix = size - str_width(ship["Name"])
    if suffix > 0:
        ship["Name"] += (" " * suffix)

if __name__ == '__main__':
    # for i in range(0xFF):
    #     print("{0:02X}, {0:3d}: {1}".format(i, chr(i)))
    # exit(0)
    with open("common.js", "r", -1, "UTF-8") as fl:
        text = fl.read()
    shipOwnInfo = re.search("(?ms)var shipOwnInfo = `(.+?)^`", text).group(1)
    own_now = set()
    for name, name2 in re.findall(r"\[x\]([^\s(),]+)(?:\(([^\s]+)\))?", shipOwnInfo):
        own_now.add(name)
        if name2:
            own_now.add(name2)

    print(own_now)

    ship_list = get_list("http://wiki.joyme.com/blhx/碧蓝航线WIKI天梯榜")
    print(len(ship_list))

    for ship_type in "驱逐 轻巡 重巡 战列 航母 其他".split(" "):
    # for ship_type in "驱逐 轻巡 重巡".split(" "):
        ship_list.sort(key=score)
        filted_ships = [ship for ship in ship_list if (ship["Type"] == ship_type and accept(ship))]
        if len(filted_ships) == 0:
            continue
        width = max([str_width(ship["Name"]) for ship in filted_ships[:show_count]])
        for idx, ship in enumerate(filted_ships[:show_count]):
            set_name_format(ship, width + 2)
            print("{0:3d}({1[Score]:4.0f}):{1[Type]} {1[Name]}输出{1[对舰输出]:4.0f} 生存{1[生存能力]:4.0f} 防空{1[防空性能]:4.0f} {1[Extra]}".format(idx+1, ship))
        # time.sleep(1)
        print()