import requests
import pyquery
from urllib.parse import urljoin
import json
import re


def get_pq(url):
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
    }
    res = requests.get(url, headers=headers)
    if res.encoding == "ISO-8859-1":
        res.encoding = res.apparent_encoding
    return pyquery.PyQuery(res.text)


def get_build_info():
    print("更新建造表...")
    base_url = "http://wiki.joyme.com/blhx/建造模拟器"
    pq = get_pq(base_url)
    res = pq(".LotusRoot")

    for a in res("a").items():
        a.attr("href", urljoin(base_url, a.attr("href")))

    names = [item.outerHtml() for item in res("span.Lotus").items()]

    ship = [item for item in res("div.Root").items()]

    result = []
    for name, info in zip(names, ship):
        result.append(name)
        result.append(info.outer_html())

    with open("建造.html", "r", -1, "UTF-8") as fin:
        source = pyquery.PyQuery(fin.read())

    source("div.LotusRoot").html("\n".join(result))

    with open("建造.html", "w", -1, "UTF-8") as fl:
        fl.write(source.outer_html())
    print("建造.html已更新.")


def update_ship_info():
    print("更新舰娘列表")
    pq_trans = get_pq("http://wiki.joyme.com/blhx/重樱船名称对照表")
    pq_trans("#FlourPackage tr").eq(0).remove()
    name_trans = {item("td").eq(1).text(): item("td").eq(0)("rb").text()[
        :1] for item in pq_trans("#FlourPackage tr").items()}
    name_trans = {k: "{0}({1})".format(k, v) for k, v in name_trans.items()}
    rare_dict = {
        "舰娘头像外框白色.png": "常见",
        "舰娘头像外框蓝色.png": "稀有",
        "舰娘头像外框紫色.png": "精锐",
        "舰娘头像外框金色.png": "超稀有",
        "舰娘头像外框最高方案.png": "方案",
    }

    pq = get_pq("http://wiki.joyme.com/blhx/舰娘图鉴")
    type_names = {"con_"+li.attr("id"): li.text()
                  for li in pq('#mw-content-text > div.MenuBox li').items()}

    all_ship = {}
    all_ship2 = {t: {r: [] for r in rare_dict.values()}
                 for t in type_names.values()}
    ship_count = 0
    with open("common.js", "r", -1, "UTF-8") as fl:
        content = fl.read()
    reg_info = r"(?s)var shipOwnInfo = `(.+?)`"
    shipOwnInfo = re.search(reg_info, content).group(1)
    own_now = []
    reg_own = r"\[x\]([^\s(),]+)(?:\(([^\s]+)\))?"
    for name, name2 in re.findall(reg_own, shipOwnInfo):
        own_now.append(name)
        if name2:
            own_now.append(name2)
    own_now = set(own_now)

    own_count = 0

    for ship_type in pq('#mw-content-text > div.Contentbox2 > div').items():
        cur_type = type_names.get(ship_type.attr("id"))
    #     print(item)
    #     print()
        for item in ship_type('div[style="float:left;"]').items():
            name = name_trans.get(item.text(), item.text())
            if name.endswith(".改"):
                continue
            rare = rare_dict.get(item('img[data-file-width="95"]').attr("alt"))
            all_ship[name] = {"稀有度": rare, "种类": cur_type}
            ship_count += 1
            if item.text() in own_now:
                all_ship2[cur_type][rare].append("[x]" + name)
                own_count += 1
            else:
                all_ship2[cur_type][rare].append("[ ]" + name)

    all_ship2["改造"] = {}
    for item in pq('#mw-content-text > div[style="float:left;"]').items():
        name = name_trans.get(item.text(), item.text())
        rare = rare_dict.get(item('img[data-file-width="95"]').attr("alt"))
        if name.endswith(".改"):
            ship_count += 1
            name0 = name_trans.get(name[:-2], name[:-2])
            all_ship[name0]["改"] = rare
            ship_type = all_ship[name0]["种类"]
            if ship_type not in all_ship2["改造"]:
                all_ship2["改造"][ship_type] = []
            if name in own_now:
                all_ship2["改造"][ship_type].append("[x]" + name)
                own_count += 1
            else:
                all_ship2["改造"][ship_type].append("[ ]" + name)
        elif name not in all_ship:
            ship_count += 1
            print(name)
            all_ship[name] = {"稀有度": rare}
        if rare == "方案":
            all_ship[name]["方案"] = True
    print("拥有舰娘{}/{}".format(own_count, ship_count))
    text = []
    for t in all_ship2:
        if not any(all_ship2[t].values()):
            continue
        text.append("- %s:" % t)
        for r in all_ship2[t]:
            if all_ship2[t][r]:
                #             all_ship2[t][r].sort(key=lambda a:a[3:])
                text.append("  - %s:\n    - %s" %
                            (r, ", ".join(all_ship2[t][r])))
    ship_info = "\n".join(text)
    
    new_content = re.sub(reg_info, "var shipOwnInfo = `\n{}\n`".format(ship_info), content)
    if new_content == content:
        print("common.js 已是最新.")
        return

    with open("common.js", "w", -1, "UTF-8") as fl:
        fl.write(new_content)
    print("common.js 已更新.")


def get_drop(name):
    pq = get_pq("http://wiki.joyme.com/blhx/"+name)
    drop = {"关卡": name, "舰娘": {}}
    for item in pq(".table-DropList > tr").items():
        drop_type = item("th").text()
        if drop_type == "图纸":
            drop["图纸"] = [blueprint.text()
                          for blueprint in item("td span").items()]
        else:
            drop["舰娘"][drop_type] = [ship.text()
                                     for ship in item("td span").items()]
    print("关卡{}获取成功.".format(name))
    return drop


def update_drop_info():
    print("更新掉落表...")
    drop_list = []
    for chap in range(1, 13):
        for node in range(1, 5):
            name = '{}-{}'.format(chap, node)
            drop_list.append(get_drop(name))

    with open("DropList.js", "w", -1, "UTF-8") as fl:
        fl.write("var dropList=" + json.dumps(drop_list,
                                              indent="  ", ensure_ascii=False) + ";")
    print("DropList.js已更新.")


def main():
    functions = [
        ["退出", exit],
        ["更新掉落表", update_drop_info],
        ["更新舰娘列表", update_ship_info],
        ["更新建造表", get_build_info],
    ]
    for idx, item in enumerate(functions):
        print("{0:2d}: {1[0]}".format(idx, item))
    choice = int(input("选择:"))
    functions[choice][1]()


if __name__ == "__main__":
    main()
