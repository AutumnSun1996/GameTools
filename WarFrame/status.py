import random
chance = 0.25*(1+0.6*2)
print(chance)
total = 19.3+31.0+13.5+25.2
ratio = [19.3*4,31.0*4,13.5*4,25.2,total * 0.9,total * 1.8]
status = [["切"],["穿"],["冲"],["病毒"], ["火", "火2"],["腐蚀"]]

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

