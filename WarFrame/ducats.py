"""
Prime部件兑换杜卡德金币比例展示
"""
import pyquery
import requests
import re
import json
import pandas as pd
import os
import time

ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36"


def get_wm_data(url):
    cache = "WFA_Lexicon-WFA5/ducats-cache.json"
    if os.path.exists(cache) and os.path.getmtime(cache) > time.time() - 3600:
        print("Use cache", cache)
        with open(cache, "r", -1, "UTF8") as f:
            json_str = f.read()
    else:
        print("Get From:", url)
        res = requests.get(url, headers={"User-Agent": ua})
        pq = pyquery.PyQuery(res.text)
        json_str = pq("script#application-state").html()
        with open(cache, "w", -1, "UTF8") as f:
            f.write(json_str)
    return json.loads(json_str)


print("获取物品列表。。。")
wm_url = "https://warframe.market/tools/ducats"
wm_info = get_wm_data(wm_url)

ducats = wm_info['payload']['previous_day']


with open("WFA_Lexicon-WFA5/WF_Sale.json", "r", -1, "UTF8") as f:
    wm_items = {r.pop('marketId'): r for r in json.load(f)}

for record in wm_info['payload']['previous_day'][:40]:
    record.update(wm_items[record['item']])
    print("{ducats_per_platinum_wa:5.2f}={ducats:3d}/{wa_price:5.2f}:   {en:40}  {zh}".format(**record))

