import pyquery
import requests
import re
import numpy as np
import time

# 对舰输出, 生存能力， 防空性能
weights = {
    "默认": [10, 10, 1],
    "航母": [20, 10, 1],
    "战列": [20, 10, 1],
    "轻巡": [30, 20, 5],
    "重巡": [30, 20, 1],
    "驱逐": [30, 20, 2],
}
show_count = 12
own_now = [s for s in re.findall(r"[^\s（）]+", """
#后排主力:
#维修:
#航母: 列克星敦 齐柏林 蛟（苍龙） 约克城
#轻航: 突击者 长岛 兰利 竞技神 鹞（祥凤） 博格 
#战列/战巡: 罗德尼 纳尔逊 宾夕法尼亚 反击 声望 内华达 田纳西 加利福尼亚 俄克拉荷马 亚利桑那
#重炮: 黑暗界 恐怖

#前排先锋:
#重巡: 波特兰 希佩尔 印第安纳波利斯 什罗普郡 肯特 北安普敦 伦敦 芝加哥 萨福克 德意志 
#轻巡: 圣地亚哥 菲尼克斯 利安得 布鲁克林 阿贾克斯 蒙彼利埃 海伦娜 克利夫兰
#驱逐:
Z46 
拉菲 标枪 吸血鬼 
Z23 Z25 Z35 
格里德利 撒切尔 西姆斯 哈曼 女将 命运女神 天后 萩（阳炎） ？ ？ Z19 弗莱彻
卡辛 唐斯 克雷文 麦考尔 奥利克 富特 斯彭斯 小猎兔犬 大斗犬 彗星 新月 小天鹅 狐提 Z20
#潜艇:
U-47 伊58
""") if not s.endswith(":") or s.startswith("#")]

# print(own_now)
def accept(ship):
    if not ship.get("对舰输出"):
        return False

    for name in own_now:
        if name in ship["Name"]:
            return True
    return False

nums = re.compile("(\d+\.)?\d+")

def get_info_online(entry):
    TypeDict = {"zhanlie": "战列", "quzhu": "驱逐", "hangmu": "航母", "qingxun": "轻巡", "zhongxun": "重巡"}
    # print("{!r} {!r} {!r}".format(entry, entry.parent(), entry.attr("class")))
    ship_type = re.compile("\d+([a-z]+)shuchu").search(entry.parent().attr("class")).group(1)
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
        cur_ship[each[:idx]] = float(re.compile("[.\d]+").search(each).group(0))
    return cur_ship

def get_info_local(entry):
    ship_types = "驱逐 轻巡 重巡 战列 航母 其他".split(" ")
    info = [item.text() for item in span("div.panel-body > p").items()]
    cur_ship = {
        "Name": info[0],
        "Type": ship_types[len(entry.parent().prevAll())-1],
        "Extra": "",
    }
    if entry("div.panel-footer"):
        cur_ship["Extra"] = "(" + entry("div.panel-footer").text() + ")"
    for each in info[1:]:
        idx = each.find("：")
        cur_ship[each[:idx]] = float(nums.search(each).group(0))
    return cur_ship

def get_list(url):
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Cookie": "Hm_lvt_dcb5060fba0123ff56d253331f28db6a=1531287514,1531290019,1531299417; Hm_lpvt_dcb5060fba0123ff56d253331f28db6a=1531299417",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
    }
    try:
        res = requests.get(url, headers=headers)
        res.encoding = res.apparent_encoding
    except Exception as e:
        print("Get Local Content", e)
        with open("./天梯榜数据.html", "r", -1, "UTF-8") as fl:
            pq = pyquery.PyQuery(fl.read())
    else:
        print("Get Online Content")
        with open("./天梯榜数据.html", "w", -1, "UTF-8") as fl:
            fl.write(res.text)
        pq = pyquery.PyQuery(res.text)
    return [get_info_online(s) for s in pq("#LTputintable span.itemhover").items()]

ship_list = get_list("http://wiki.joyme.com/blhx/%E7%A2%A7%E8%93%9D%E8%88%AA%E7%BA%BFWIKI%E5%A4%A9%E6%A2%AF%E6%A6%9C")
print(len(ship_list))

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
    except Exception as e:
        print(s)
        print("Error", e)
        return 0

def str_width(text):
    return sum([1 if ord(c) < 0x7F else 2 for c in text])

def set_name_format(ship, size=10):
    suffix = size - str_width(ship["Name"])
    if suffix > 0:
        ship["Name"] += (" " * suffix)

for ship_type in "驱逐 轻巡 重巡 战列 航母 其他".split(" "):
# for ship_type in "驱逐 轻巡 重巡".split(" "):
    filted_ships = [ship for ship in ship_list if (ship["Type"] == ship_type and accept(ship))]
    filted_ships.sort(key=score)
    if len(filted_ships) == 0:
        continue
    width = max([str_width(ship["Name"]) for ship in filted_ships[:show_count]])
    for idx, ship in enumerate(filted_ships[:show_count]):
        set_name_format(ship, width + 2)
        print("{0:3d}({1[Score]:3.0f}):{1[Type]} {1[Name]}输出{1[对舰输出]:.0f} 生存{1[生存能力]:.0f} 防空{1[防空性能]:.0f} {1[Extra]}".format(idx+1, ship))
    # time.sleep(1)
    print()
