import random
chance = 0.2
ratio = [90*4,5*4,5*4,180,180]
status = [["切"],["穿"],["冲"],["爆炸", "击倒"],["腐蚀"]]

t = sum(ratio)
ratio = [r / t for r in ratio]

def choose(chance=chance, ratio=ratio):
    if random.random() > chance:
        return []
    choice = random.random()
    idx = 0
    while choice > 0:
        choice -= ratio[idx]
        idx += 1
    return status[idx-1]


size = 10000
nums = list(range(1,5)) + list(range(5, 50, 5))
total = {i: 0 for i in nums}
status_ct = {i: 0 for i in nums}
for i in range(size):
    enemy = set()
    last = 0
    for idx in nums:
        for k in range(last, idx):
            enemy.update(choose())
        last = idx
        status_ct[idx] += len(enemy)
        total[idx] += 1.6 ** len(enemy)
print(total)
#total = [t / size for t in total]
for idx in nums:
    print("{:2.0f}, {:.2f}, {:.2f}".format(idx, status_ct[idx]/size, total[idx]/size))