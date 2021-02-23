graycode = "000 001 011 010 110 111 101 100".split()
subtemper_names = "叛逆 守序 高冷 亲和 感性 理性".split()
temper_names = """
守序 亲和 理性 好人卡持有者
叛逆 亲和 理性 正义的恶魔
守序 高冷 理性 王者绝非偶然
守序 亲和 感性 正义的伙伴
叛逆 高冷 感性 疯得很正经
守序 高冷 感性 冷漠是我的面具
叛逆 亲和 感性 放荡不羁爱自由
叛逆 高冷 理性 王之姿俯视世界
""".strip().splitlines()


temper_map = {}
temper_remap = {}
for line in temper_names:
    a, b, c, name = line.split()
    code = tuple(subtemper_names.index(k) % 2 for k in [a, b, c])
    temper_map[code] = name
    temper_remap[name] = code

for code in graycode:
    a, b, c = map(int, code)
    print(a, b, c)
    ta = subtemper_names[a]
    tb = subtemper_names[b + 2]
    tc = subtemper_names[c + 4]
    print(ta, tb, tc, temper_map[(a, b, c)])


def distance(a, b):
    delta = 0
    for k1, k2 in zip(a, b):
        delta += abs(k1 - k2)
    return delta


def next_codes(code):
    origin = list(code)
    for i in range(len(code)):
        tmp = origin.copy()
        tmp[i] = 1 - tmp[i]
        yield tuple(tmp)


def check_path(path):
    global best_weight, best_path
    if len(path) < 8:
        return None
    weight = 0
    for idx, code in enumerate(path):
        weight += code_weight.get(code, 0) / (idx + 1)
    
    if best_weight is None or best_weight < weight:
        weights = [code_weight.get(c, 0) for c in path]
        print("New Best:", weight, weights, path)
        best_weight = weight
        best_path = path


def search_for_path(path):
    if len(path) == 8:
        check_path(path)
        return
    current = path[-1]
    for code in next_codes(current):
        if code in path:
            # 避免重复搜索
            continue
        search_for_path(path + [code])


wanted = """
荒烈/白泽 王之姿俯视世界 200
赛花/霜果 冷漠是我的面具 16
艾尼娅 好人卡持有者 16
苍鸢 放荡不羁爱自由 12
拨拨 正义的恶魔 2
岚 疯得很正经 1
"""

# wanted = """
# 荒烈/白泽 王之姿俯视世界 16
# 赛花/霜果 冷漠是我的面具 200
# 艾尼娅 好人卡持有者 16
# 苍鸢 放荡不羁爱自由 12
# 拨拨 正义的恶魔 2
# 岚 疯得很正经 1
# """

first = [0, ""]
code_weight = {}
for line in wanted.strip().splitlines():
    name, temper, weight = line.split()
    weight = int(weight)
    code_weight[temper_remap[temper]] = weight
    if first is None or first[0] < weight:
        first = [weight, temper]


best_weight = None
best_path = []
start = temper_remap[first[1]]
search_for_path([start])

print(best_path)
for code in best_path:
    a, b, c = code
    ta = subtemper_names[a]
    tb = subtemper_names[b + 2]
    tc = subtemper_names[c + 4]
    print(code, ta, tb, tc, temper_map[code])
