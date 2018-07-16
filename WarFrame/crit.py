# 近战DPS计算
import math
item = {
    "名称": "阿特拉克斯",
    "爆率": 0.25,
    "爆伤": 3,
    "触发": 0.2,
    "范围": 11,
    "基础伤害": {
        "数值": 100,
        "比例": {
            "切割": 0.9,
            "冲击": 0.05,
            "穿刺": 0.05,
        }
    }
}

def 基伤加成(基础数值, 等级加成):
    def tmp(weapon, rank):
        mult = 基础数值 + rank * 等级加成
        weapon["基础伤害"]["数值"] *= 1 + mult/100
    return tmp
    
def 单项加成(名称, 基础数值, 等级加成):
    def tmp(weapon, rank):
        mult = 基础数值 + rank * 等级加成
        weapon[名称] *= 1 + mult/100
    return tmp

def 元素加成(名称, 基础数值, 等级加成):
    def tmp(weapon, rank):
        mult = (基础数值 + rank * 等级加成) / 100
        if "额外伤害" not in weapon:
            weapon["额外伤害"] = {}
        if 名称 not in weapon["额外伤害"]:
            weapon["额外伤害"][名称] = 0
            
        weapon["额外伤害"][名称] += weapon["基础伤害"]["数值"] * mult
    return tmp

def 急进猛突加成(连击倍率):
    def tmp(weapon, rank):
        加成 = (15 + 15 * rank) / 100
        爆率 = weapon["爆率"]
        if 连击倍率 > 1:
            爆率 = 爆率 * (1 + 加成 * 连击倍率)
        基础倍数 = math.floor(爆率)
        几率 = 爆率 - 基础倍数
        if 基础倍数 == 0:
            实际加成 = 几率 * weapon["爆伤"] + (1 - 几率) * 1
        else:
            实际加成 = 几率 * (1 + (weapon["爆伤"] - 1) * (基础倍数 + 1))
            实际加成 += (1 - 几率) * (1 + (weapon["爆伤"] - 1) * 基础倍数)
        print(连击倍率, 爆率, 实际加成)
        if "额外加成" not in weapon:
            weapon["额外加成"] = []
        weapon["额外加成"].append(实际加成)
        return 实际加成
    return tmp

def 异况超量加成(触发数):
    def tmp(weapon, rank):
        mult = 1.1 + 0.1 * rank
        实际加成 = mult**触发数
        if "额外加成" not in weapon:
            weapon["额外加成"] = []
        weapon["额外加成"].append(实际加成)
        return 实际加成
    return tmp



mods = {
    "压迫点 Prime": {
        "消耗": 4,
        "最高等级": 10,
        "加成": 基伤加成(15, 15)
    },

}

def dict_copy(source):
    result = {}
    for key in source:
        if isinstance(source[key], dict):
            result[key] = dict_copy(source[key])
        elif isinstance(source[key], list):
            result[key] = source[key][:]
        else:
            result[key] = source[key]
    return result

base_weapon = dict_copy(item)

result = 急进猛突加成(a)(base_weapon, 10)
print(result)

print(base_weapon)
# 基伤加成(15,15)(base_weapon, 10)
单项加成("爆伤", 15, 15)(base_weapon, 5)
单项加成("爆率", 10, 10)(base_weapon, 5)
# 元素加成("电", 10, 10)(base_weapon, 8)

for i in range(5):
    a = 1 + 0.5 * i
    急进猛突加成(a)(base_weapon, 10)
print(base_weapon)

for i in range(3, 7):
    异况超量加成(i)(base_weapon, 5)
print(base_weapon)
