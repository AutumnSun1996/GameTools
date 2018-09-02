import math

ship = {
    "名称": "皇家方舟",
    "装填": 55, 
    "装备": {
        "梭鱼T3": 2,
        "海燕T3": 1
    }
}

equipment_cd = {
    "海燕T3": 9.18,
    "Ju-87俯冲轰炸机T3": 11.57,
    "SB2C地狱俯冲者T3": 11.88,
    
    "梭鱼T3": 10.31,
    "剑鱼(818中队)T0": 10.97,
    "天山T3": 11.63,
    "流星T3": 11.37,

    "Me-155A舰载战斗机T3": 9.24,
    "零战五二型T3": 9.52,
    "F4U（VF-17“海盗”中队）T0": 10.20,
    "烈风T3": 10.44,
    "海毒牙T3": 10.60,
    "海怒T0": 10.61,
    "F6F地狱猫T3": 10.90,
}


def airstrike_cd(ship):
    print(ship["名称"])
    cd_change = math.sqrt(200 / (100 + ship["装填"]))
    weight_cd = 0
    count = 0
    for name in ship["装备"]:
        equiped_cd = equipment_cd[name] * cd_change
        print("{}: {:.2f}s".format(name, equiped_cd))
        weight_cd += ship["装备"][name] * equiped_cd
        count += ship["装备"][name]
    final_cd = weight_cd * 2.18 / count + 0.25 + 0.05
    print("空袭CD: {:.2f}s".format(final_cd))
    return final_cd

if __name__ == '__main__':
    airstrike_cd(ship)