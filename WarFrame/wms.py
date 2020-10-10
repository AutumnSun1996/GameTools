import pyquery
import requests
import re
import json
import pandas as pd
import win32clipboard

trans_url = "https://warframe.huijiwiki.com/wiki/UserDict"
print("获取翻译。。。")
trans_content = pyquery.PyQuery(trans_url)("#mw-content-text").html()
trans_items = re.findall(
    '<tr><th>([^<>]+?)</th><td class="value">"([^<>]+?)"</td></tr>',
    trans_content.replace("&amp;", "&"),
)
trans_dict = {k: v for v, k in trans_items}
retrans_dict = {k: v for k, v in trans_items}

ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36"


def get_wm_data(url):
    print("Get From:", url)
    res = requests.get(url, headers={"User-Agent": ua})
    pq = pyquery.PyQuery(res.text)
    script = pq("script#application-state").html()
    return json.loads(script)


print("获取物品列表。。。")
wm_url = "https://warframe.market/"
wm_info = get_wm_data(wm_url)
wm_items = {item["item_name"]: item["url_name"] for item in wm_info["items"]["en"]}


add_ons = [
    ("Primed ", ""),
    ("", ""),
    ("", " Set"),
    ("", " Prime"),
    ("", " Prime Set"),
    ("", " Vandal"),
    ("", " Vandal Set"),
    ("", " Wraith"),
    ("", " Wraith Set"),
    ("Wraith ", " Set"),
    ("Prisma ", ""),
    ("", " Ayatan Sculpture"),
    ("Rakta ", ""),
    ("Sancti ", ""),
    ("Secura ", ""),
    ("Synoid ", ""),
    ("Telos ", ""),
]


def en2ch(name):
    if name in retrans_dict:
        return retrans_dict[name]
    for en, ch in trans_items:
        name = name.replace(en, ch)
    return name


def get_item_data(unit_name):
    unit_name = trans_dict.get(unit_name, unit_name)
    for pre, suf in add_ons:
        tmp = pre + unit_name + suf
        #         print(tmp, tmp in wm_items)
        if tmp in wm_items:
            unit_name = tmp
            break

    url = wm_url + "items/" + wm_items[unit_name]
    info = get_wm_data(url)
    info["name"] = unit_name
    return info


def set_clipboard_text(text):
    win32clipboard.OpenClipboard()
    win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
    win32clipboard.CloseClipboard()


def set_message(df):
    name = df.index.name
    if name.endswith(" Set"):
        name = "[" + name[:-4] + "] Set"
    else:
        name = "[" + name + "]"
    set_clipboard_text(
        "/w {1.name} Hi! I want to buy: {0} for {1[platinum]} platinum.".format(
            name, df.iloc[0]
        )
    )


def order_filter(order):
    return order["user"]["region"] == "en"


def orders2df(info):
    orders = [
        {
            "order_type": item["order_type"],
            "platform": item["platform"],
            "platinum": item["platinum"],
            "quantity": item["quantity"],
            "visible": item["visible"],
            "rank": item.get("mod_rank"),
            "user_name": item["user"]["ingame_name"],
            "user_status": item["user"]["status"],
        }
        for item in info["payload"]["orders"]
        if order_filter(item)
    ]
    df = pd.DataFrame(orders).set_index("user_name")
    if "mod_max_rank" not in info["include"]["item"]["items_in_set"][0]:
        df.drop("rank", axis=1, inplace=True)
    else:
        df.dropna(subset=["rank"], inplace=True)
    df.index.name = info["name"]
    return df


def filt_orders(df, order_type="sell", rank=None, copy=True):
    sell_orders = df[
        (df["order_type"] == order_type)
        & (df["user_status"] == "ingame")
        & df["visible"]
    ]
    try:
        sell_orders = sell_orders.drop(["platform", "user_status", "visible"], axis=1)
    except:
        pass
    if rank is not None:
        sell_orders = sell_orders[sell_orders["rank"] == rank]
    sell_orders = sell_orders.sort_values("platinum", ascending=(order_type == "sell"))
    if copy:
        set_message(sell_orders)
    return sell_orders  # [['platinum', 'quantity']]


def get_set_data(item_name):
    info = get_item_data(item_name)
    return show_set_data(info)


def show_set_data(info):
    data = orders2df(info)
    sell = filt_orders(data, "sell", copy=False)

    items = []
    print(en2ch(info["name"]))
    print(sell.iloc[0]["platinum"])
    items.append({"Name": info["name"], "Data": data})
    total = 0
    for item in info["include"]["item"]["items_in_set"]:
        if not item["set_root"]:
            part_info = get_item_data(item["en"]["item_name"])
            data = orders2df(part_info)
            sell = filt_orders(data, "sell", copy=False)
            items.append({"Name": item["en"]["item_name"], "Data": data})
            print(en2ch(item["en"]["item_name"]))
            print(sell.iloc[0]["platinum"])
            total += sell.iloc[0]["platinum"]
    print(total)
    return items


def show_item_data(item_name, order_type="sell", ranks=None, copy=True, deal_set=True):
    info = get_item_data(item_name)
    if deal_set and info["name"].endswith(" Set"):
        show_set_data(info)
        return

    print(en2ch(info["name"]))
    data = orders2df(info)

    if "rank" not in data.columns:
        sell = filt_orders(data, order_type, copy=copy)
        print(sell.head())
        return

    if ranks is None:
        ranks = [0, "max"]

    if "max" in ranks:
        ranks.remove("max")
        max_rank = data["rank"].max()
        if max_rank:
            ranks.append(max_rank)

    for rank in ranks:
        sell = filt_orders(data, order_type, rank, copy=copy)
        print(sell.head())
        print()
    # return data


def main():
    while True:
        name = input("名称:")
        if name == "":
            return
        try:
            if name.startswith("buy "):
                show_item_data(name[4:], "buy")
            else:
                show_item_data(name)
        except Exception as err:
            print(err)


if __name__ == "__main__":
    main()

    for name in "诡计 速攻 狂怒 节奏 消磁".split(" "):
        show_item_data(name + "赋能", ranks=["max"], deal_set=False)

