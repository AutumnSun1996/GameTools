from helper import Record, get_session
from sqlalchemy import and_, or_
import yaml
import jsonpath
import pandas as pd

try:
    import simplejson as json
except ImportError:
    import json

uid = ""

sess = get_session()
rec = (
    sess.query(Record)
    .filter(
        and_(
            Record.params.like("%_userId={}%".format(uid)),
            Record.params.like("%_key=toplogin%"),
        )
    )
    .order_by(Record.timestamp.desc())
    .first()
)

info = json.loads(rec.resp_body)
print(rec.path)
print(rec.params)
print(rec.timestamp)


import pandas as pd
df = pd.read_csv("../Autodroid/fgo/data/svtId.csv", delimiter="\t")
svt_names = df.to_dict("records")
svt_names = {str(svt["svtId"]): svt["name_cn"] for svt in svt_names if svt["svtId"] != 0}

svts = {}
for svt in jsonpath.jsonpath(info, "$..userSvt[*]"):
    sid = str(svt["svtId"])
    if int(sid) > 9400000:
        continue
    tlv = int(svt["treasureDeviceLv1"])
    if sid not in svts:
        svts[sid] = {
            "Lv": tlv,
            "Name": svt_names.get(sid),
            "sid": sid,
            "NeedUpdate": False,
        }
        continue
    
    if svts[sid]["Lv"] >= 5:
        continue

    if tlv == 5:
        svts[sid]["Lv"] = 5
        svts[sid]["NeedUpdate"] = False
        continue
    
    svts[sid]["NeedUpdate"] = True

for svt in svts.values():
    if svt["NeedUpdate"]:
        print("可升级宝具:", svt)
