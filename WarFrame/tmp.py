equinox_str_bonus_max = 51

nidus_str = (373 + equinox_str_bonus_max) / 100
nidus_bonus = nidus_str * 0.25 + 1

rhino_str = (373 + equinox_str_bonus_max) / 100
rhino_bonused_str = rhino_str * nidus_bonus
rhino_bonus = rhino_bonused_str * 0.5 + 1

equinox_str = (95 + 50 + equinox_str_bonus_max) / 100
equinox_bonused_str = equinox_str
equinox_dmg = 150
equinox_dmg_str_bonused = equinox_dmg * equinox_bonused_str
equinox_dmg_rhino_bonused = equinox_dmg_str_bonused * 1

slash_dmg = equinox_dmg_rhino_bonused * 0.35

for key, val in locals().copy().items():
    if "__" not in key:
        print("{:30s}:{:.2f}".format(key, val))
exit()

equinox_str_bonus_max = 80

nidus_str = (373 + equinox_str_bonus_max) / 100
nidus_bonus = nidus_str * 0.25 + 1

rhino_str = (373 + equinox_str_bonus_max) / 100
rhino_bonused_str = rhino_str * nidus_bonus
rhino_bonus = rhino_bonused_str * 0.5 + 1

equinox_str = (100 + equinox_str_bonus_max) / 100
equinox_bonused_str = equinox_str * nidus_bonus
equinox_dmg = 150
equinox_dmg_str_bonused = equinox_dmg * equinox_bonused_str
equinox_dmg_rhino_bonused = equinox_dmg_str_bonused * rhino_bonus

slash_dmg = equinox_dmg_rhino_bonused * 0.35

for key, val in locals().copy().items():
    if "__" not in key:
        print("{:30s}:{:.2f}".format(key, val))
exit()
import random
import math
import itertools

def choose(chance, ratio, status):
    if random.random() > chance:
        return []
    choice = random.random()
    idx = 0
    while choice > 0:
        choice -= ratio[idx]
        idx += 1
    return status[idx-1]
    
def status_sim(chance, hit, ratio):
    print("触发几率:", chance, "击中", hit)
    status = [["切"],["穿"],["冲"],["病毒"], ["火", "火2"],["腐蚀"]]

    t = sum(ratio)
    ratio = [r / t for r in ratio]

    size = 10000
    total = 0
    status_ct = 0
    for i in range(size):
        enemy = set()
        for k in range(hit):
            enemy.update(choose(chance=chance, ratio=ratio, status=status))
        status_ct += len(enemy)
        total += 1.6 ** len(enemy)
    print("状态数:", status_ct/size, "加成:", total/size)
    return total/size
"""
damage = 19.3+31.0+13.5+25.2
chance = 0.36
ratio = [19.3*4,31.0*4,13.5*4,25.2]
status_sim(chance*(1+0.4), 5, ratio=ratio)
status_sim(chance*(1+0.4), 10, ratio=ratio)

ratio = [19.3*4,31.0*4,13.5*4,25.2,damage * 0.6]
status_sim(chance*(1+0.4+0.6), 5, ratio=ratio)
status_sim(chance*(1+0.4+0.6), 10, ratio=ratio)

ratio = [19.3*4,31.0*4,13.5*4,25.2,0,damage * 1.2]
status_sim(chance*(1+0.4+0.6*2), 5, ratio=ratio)
status_sim(chance*(1+0.4+0.6*2), 10, ratio=ratio)
"""
# 滑爆触发双修分析
"""

"""

strikes = [{"Name": "瘟疫奇沃", "伤害":79.0, "攻速": -0.033, "暴击": 0.18, "触发":0.22, "暴伤":2.0},
    {"Name": "瘟疫克里帕丝", "伤害":70.0, "攻速": +0.033, "暴击": 0.22, "触发":0.18, "暴伤":2.2}]

handles = [line.split("\t") for line in """石当	+28.0	双手	0.783
斯卡拉	-4.0	双手	1.000
查亚普	+0.0	双手	0.917
瘟疫柏克文	+7.0	双手	0.883
克鲁斯查	+14.0	双手	0.850""".splitlines()]
# print(handles)
handles = [{"Name":item[0], "伤害": float(item[1]), "攻速": float(item[3])} for item in handles]

links = [line.split("\t") for line in """
伊克瓦纳 II 如杭	+14.0	-0.067	-8.0%	+14.0%
伊克瓦纳 II 翟	-4.0	+0.083	-8.0%	+14.0%
伊克瓦纳 翟 II	-8.0	+0.167	-4.0%	+7.0%
伊克瓦纳 如杭 II	+28.0	-0.133	-4.0%	+7.0%
伊克瓦纳 翟	-4.0	+0.083	-4.0%	+7.0%
伊克瓦纳 如杭	+14.0	-0.067	-4.0%	+7.0%
# 翟	-4.0	+0.083	+0.0%	+0.0%
# 翟 II	-8.0	+0.167	+0.0%	+0.0%
# 如杭	+14.0	-0.067	+0.0%	+0.0%
# 如杭 II	+28.0	-0.133	+0.0%	+0.0%
# 瓦吉特 翟 II	-8.0	+0.167	+7.0%	-4.0%
# 瓦吉特 如杭 II	+28.0	-0.133	+7.0%	-4.0%
# 瓦吉特 翟	-4.0	+0.083	+7.0%	-4.0%
# 瓦吉特 如杭	+14.0	-0.067	+7.0%	-4.0%
# 瓦吉特 II 翟	-4.0	+0.083	+14.0%	-8.0%
# 瓦吉特 II 如杭	+14.0	-0.067	+14.0%	-8.0%
""".strip().splitlines() if line[0] != "#"]
print(links)
links = [{"Name":item[0], "伤害":float(item[1]), "攻速": float(item[2]), "暴击": float(item[3][:-1])/100, "触发": float(item[4][:-1])/100} for item in links]

all_posible = []
for a, b, c in itertools.product(strikes, handles, links):
    tmp = {}
    tmp["Name"] = " ".join([a["Name"], b["Name"], c["Name"]])
    tmp["伤害"] = a["伤害"] + b["伤害"] + c["伤害"]
    tmp["攻速"] = a["攻速"] + b["攻速"] + c["攻速"]
    tmp["暴击"] = a["暴击"] + c["暴击"]
    tmp["触发"] = a["触发"] + c["触发"]
    tmp["暴伤"] = a["暴伤"]
    # tmp["dps0"] = tmp["伤害"] * tmp["攻速"]
    # tmp["dps1"] = tmp["dps0"] * (1-tmp["暴击"]) + tmp["dps0"] * tmp["暴伤"] * tmp["暴击"]
    tmp["dps"] = tmp["伤害"] * tmp["攻速"]
    all_posible.append(tmp)
all_posible.sort(key=lambda a:a["dps"])
for tmp in all_posible:
    print("{0[伤害]:5.1f}*{0[攻速]:6.3f}={0[dps]:5.2f} With {0[Name]}".format(tmp))
    # print(tmp)
    
    
exit()

# 71.0* 1.050=103.18 With 瘟疫奇沃 斯卡拉 瓦吉特 II 翟

# 71.0* 1.050=74.55 With 瘟疫奇沃 斯卡拉 伊克瓦纳 II 翟

# 78.0* 1.017=79.33 With 瘟疫奇沃 瘟疫柏克文 伊克瓦纳 翟 II
# 78.0* 1.017=79.33 With 瘟疫奇沃 瘟疫柏克文 翟 II
# 78.0* 1.017=79.33 With 瘟疫奇沃 瘟疫柏克文 瓦吉特 翟 II
# 76.0* 1.050=79.80 With 瘟疫克里帕丝 克鲁斯查 伊克瓦纳 翟 II
# 76.0* 1.050=79.80 With 瘟疫克里帕丝 克鲁斯查 翟 II
# 76.0* 1.050=79.80 With 瘟疫克里帕丝 克鲁斯查 瓦吉特 翟 II
 

"""瘟疫克里帕斯

滑爆触发双修

必需：
剑风P
狂暴P/狂战士
致残突击+急进猛突
异况超量+活动1+活动2
漂移接触
压迫点P
肢解

紫卡属性：攻速，滑爆，范围

滑爆：
实际爆率 (14 + 90) * (1 + 1.65 * 2.5) = 533
加成 (0.33 * (1 + 6 * (4.18 - 1))) + (0.67 * (1 + 5 * (4.18 - 1))) = 17.949

暴击：

触发：
假设触发数为5
加成 1.6**5 = 10.486
爆率 14
加成 0.14 * 2.2 + (1-0.14) = 1.168
最终加成 12.248

双修：
实际爆率 (14) * (1 + 1.65 * 2.5) = 71.75
加成 0.7175 * 2.2 + (1-0.7175) = 1.861
假设触发数为4
加成 1.6**4 = 6.554
最终加成 12.197
"""


def crit_acc(爆率, 爆伤, text):
    基础倍数 = math.floor(爆率)
    几率 = 爆率 - 基础倍数
    if 基础倍数 == 0:
        实际加成 = 几率 * 爆伤 + (1 - 几率) * 1
    else:
        实际加成 = 几率 * (1 + (爆伤 - 1) * (基础倍数 + 1))
        实际加成 += (1 - 几率) * (1 + (爆伤 - 1) * 基础倍数)
    print("{}:{:.3f}".format(text, 实际加成))
    return 实际加成
    
def compare(爆率=0.14, 爆伤=2.2):
    print("爆率:{:.2f}; 爆伤:{}".format(爆率, 爆伤))
    crit_acc(爆率, 爆伤, "基础加成")
    a1 = crit_acc(爆率 * (1 + 1.65 * 2.5), 爆伤, "急进猛突加成")
    crit_acc(爆率, 爆伤 * 1.9, "肢解加成")
    a3 = crit_acc(爆率 * (1 + 1.65 * 2.5), 爆伤 * 1.9, "同时加成")
    print((a3 - a1) / a1)

def choose(chance, ratio, status):
    if random.random() > chance:
        return []
    choice = random.random()
    idx = 0
    while choice > 0:
        choice -= ratio[idx]
        idx += 1
    return status[idx-1]
        
def status_sim(chance=0.2, hit=10):
    print("触发几率:", chance, "击中", hit)
    damage = 19.3+31.0+13.5+25.2
    ratio = [19.3*4,31.0*4,13.5*4,25.2,damage * 0.9,damage * 1.8]
    status = [["切"],["穿"],["冲"],["病毒"], ["火", "火2"],["腐蚀"]]

    t = sum(ratio)
    ratio = [r / t for r in ratio]

    size = 10000
    total = 0
    status_ct = 0
    for i in range(size):
        enemy = set()
        for k in range(hit):
            enemy.update(choose(chance=chance, ratio=ratio, status=status))
        status_ct += len(enemy)
        total += 1.6 ** len(enemy)
    print("状态数:", status_ct/size, "加成:", total/size)
    return total/size
    
# for status in [0.2, 0.25, 0.4, 0.65]:
    # status_sim(status, 5)
    # status_sim(status)
    # print()
# exit()
for crit, status in [(0.14, 0.32), (0.18, 0.25), (0.22, 0.18), (0.29, 0.14), (0.36, 0.10)]:
    compare(crit)
    print()
