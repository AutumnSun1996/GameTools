import pyquery
import re
import numpy as np

nums = re.compile("(\d+\.)?\d+")

with open("输出.html", "r", -1, "UTF-8") as fl:
    html = pyquery.PyQuery(fl.read())

ship = []
types = "驱逐	轻巡	重巡	战列	航母	其他".split("	")

for span in html("td > span").items():
    info = [item.text() for item in span("div.panel-body > p").items()]
    cur_ship = {
        "Name": info[0],
        "Type": types[len(span.parent().prevAll())-1],
        "Extra": "",
    }
    if span("div.panel-footer"):
        cur_ship["Extra"] = "(" + span("div.panel-footer").text() + ")"
    for each in info[1:]:
        idx = each.find("：")
        cur_ship[each[:idx]] = float(nums.search(each).group(0))
    ship.append(cur_ship)
    # print(cur_ship)

def accept(s):
    if s["Type"] in "其他":
        return False
    for name in "Z23 Z46 卡辛 唐斯 弗莱彻 长岛 兰利 竞技神 标枪 希佩尔 圣地亚哥 齐柏林 突击者 列克星敦 克雷文 麦考尔 罗德尼 鹞 祥凤 纳尔逊 宾夕法尼亚 反击 声望 女将".split(" "):
        if name in s["Name"]:
            return True
    return False


def harm_mean(arr, weight=None):
    arr = 1 / np.array(arr)
    if weight is not None:
        arr = np.array(arr) * np.array(weight) / np.mean(weight)
    return 1 / arr.mean()
    
def score(s):
    weights = {
        "航母": [2, 1.5, 0.1],
        "战列": [1.5, 1.5, 1],
    }
    try:
        s["Score"] = harm_mean([s["对舰输出"], s["生存能力"], s["防空性能"]/10], weights.get(s["Type"]))
        return -s["Score"]
    except Exception as e:
        print(s, e)
        return 0

filted_ships = [s for s in ship if accept(s)]

filted_ships.sort(key=score)

for idx, ship in enumerate(filted_ships):
    print("{0:3d}({1[Score]:3.0f}):{1[Type]} {1[Name]}{1[Extra]}  \t输出{1[对舰输出]:.0f} 生存{1[生存能力]:.0f} 防空{1[防空性能]:.0f}".format(idx, ship))