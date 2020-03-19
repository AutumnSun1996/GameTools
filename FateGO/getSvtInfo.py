import requests
import io
import pandas as pd
import json
import re

# res = requests.get("https://fgo.wiki/w/英灵图鉴")

# print(res.status_code)
# with open("英灵图鉴.html", "w", -1, "UTF8") as fl:
#     fl.write(res.text)

with open("英灵图鉴.html", "r", -1, "UTF8") as fl:
    content = fl.read()

override_data = re.search(r'(?m)override_data = (".+");?$', content)
rawstr = re.search(r'(?m)var raw_str = (".+");?$', content)


rawstr = io.StringIO(json.loads(rawstr.group(1)))
raw = pd.read_csv(rawstr)
print(raw)

source = pd.read_csv(r"D:\QiuShiyang\Document\GameRoutes\Autodroid\fgo\data\svtId.csv", sep="\t")
print(source)

extra = []
for item in json.loads(override_data.group(1)).split(";"):
    cols = item.split(",")
    info = {}
    for c in cols:
        if not c:
            continue
        k, v = c.split("=")
        info[k] = v
    extra.append(info)
print(pd.DataFrame(extra))
