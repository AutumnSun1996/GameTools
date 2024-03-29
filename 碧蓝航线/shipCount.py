import re

with open("common.js", "r", -1, "UTF-8") as fl:
    content =  fl.read()

shipOwnInfo = re.search('(?s)var shipOwnInfo = `(.+?)`', content).group(1)


count = {"x": 0, " ": 0}
regShip = r'\[([x ])\]([^\s(),]+)(?:\(([^\s]+)\))?'
for own, name, name2 in re.findall(regShip, shipOwnInfo):
    count[own] += 1
print("已获取: {}/{}".format(count["x"], sum(count.values())))
