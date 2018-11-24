from itertools import combinations_with_replacement


fleet_main = ['战列', '正航', '轻航', '重炮', '维修']
fleet_scout = ['驱逐', '轻雷巡', '重雷巡', '炮巡']
fleets_extra = [{"潜艇": i} for i in [1, 2, 3]]


def all_fleets(choices, include=None):
    results = []
    for count in [1, 2, 3]:
        for choice in combinations_with_replacement(choices, count):
            tmp = {}
            for item in set(choice):
                tmp[item] = choice.count(item)
            if include is None or include(tmp):
                results.append(tmp)
    return results


def filt_all(fleet):
    if fleet.get('维修', 0) > 1:
        return False
    if fleet.get('重炮', 0) > 2:
        return False

    if fleet.get('重雷巡', 0) > 2:
        return False
    return True


fleets = fleets_extra
for main in all_fleets(fleet_main, filt_all):
    for scout in all_fleets(fleet_scout, filt_all):
        fleets.append(dict(**main, **scout))

if __name__ == "__main__":
    print('Get %d fleets' % len(fleets))
    from talents import show_talents
    for ship in fleet_main + fleet_scout + ['潜艇']:
        show_talents({ship: 1}, limit=10)
