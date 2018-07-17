import pyquery
import re
import numpy as np

# 对舰输出, 生存能力， 防空性能
weights = {
    "默认": [0, 1, 0],
    # "航母": [2, 1.5, 0.01],
    # "战列": [1.5, 1.5, 1],
    # "轻巡": [1.5, 1.5, 0.5],
    # "驱逐": [1, 1.5, 0.2]
}

own_now = re.findall("[^\s]+", """
鹞 祥凤 
齐柏林 突击者 列克星敦 长岛 兰利 竞技神 
罗德尼 纳尔逊 宾夕法尼亚 反击 声望 
波特兰 希佩尔 
圣地亚哥 蒙彼利埃
拉菲 标枪 吸血鬼 
Z23 Z25 Z35 Z46 
克雷文 麦考尔 卡辛 唐斯 女将 命运女神 天后
弗莱彻 富特 斯彭斯 

""")
def accept(ship):
    if ship["Type"] == "其他":
        return False
    return True
    for name in own_now:
        if name in ship["Name"]:
            return True
    return False

nums = re.compile("(\d+\.)?\d+")

with open("输出.html", "r", -1, "UTF-8") as fl:
    html = pyquery.PyQuery(fl.read())

ship_types = "驱逐	轻巡	重巡	战列	航母	其他".split("	")

ship_list = []
for span in html("td > span").items():
    info = [item.text() for item in span("div.panel-body > p").items()]
    cur_ship = {
        "Name": info[0],
        "Type": ship_types[len(span.parent().prevAll())-1],
        "Extra": "",
    }
    if span("div.panel-footer"):
        cur_ship["Extra"] = "(" + span("div.panel-footer").text() + ")"
    for each in info[1:]:
        idx = each.find("：")
        cur_ship[each[:idx]] = float(nums.search(each).group(0))
    ship_list.append(cur_ship)
    # print(cur_ship)

def harm_mean(arr, weight=None):
    arr = 1 / (np.array(arr) + 1)
    if weight is not None:
        arr = np.array(arr) * np.array(weight) / np.mean(weight)
    return 1 / arr.mean()
    
def score(s):
    try:
        # print(s)
        s["Score"] = harm_mean([s["对舰输出"], s["生存能力"], s["防空性能"]/10], weights.get(s["Type"]) or weights["默认"])
        return -s["Score"]
    except Exception as e:
        print(s)
        print("Error", e)
        return 0

for ship_type in ship_types:
    filted_ships = [ship for ship in ship_list if (ship["Type"] == ship_type and accept(ship))]
    filted_ships.sort(key=score)
    for idx, ship in enumerate(filted_ships[:12]):
        print("{0:3d}({1[Score]:3.0f}):{1[Type]} {1[Name]}{1[Extra]}  \t输出{1[对舰输出]:.0f} 生存{1[生存能力]:.0f} 防空{1[防空性能]:.0f}".format(idx+1, ship))
    print()
