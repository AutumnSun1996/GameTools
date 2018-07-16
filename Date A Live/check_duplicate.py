#!bin/python3
import re

RE_CHAP = re.compile('(?m)^[\s\t]*,"[^",\d]*(\d+).+$')

def list_dup(path=r"D:\Document\Books\www.mianhuatang.la\鱼人二代_校花的贴身高手\Chapters.csv"):
    with open(path, 'r', -1, "UTF-8") as fin:
        text = fin.read()
    chapters = RE_CHAP.findall(text)
    print("GET", chapters)
    count = {}
    dup = {}
    for idx, item in enumerate(chapters):
        item = int(item)
        print("item", idx, item)
        if item not in count:
            count[item] = [idx]
        else:
            count[item].append(idx)
            dup[item] = count[item].copy()
    return dup

if __name__ == "__main__":
    dups = list_dup()
    print(dups)
    # test = """
	# ,"第01章 神奇的任务","text0/0.xhtml","917149.html"
	# ,"第02章 骗局","text0/1.xhtml","917150.html"
	# ,"第03章 王心妍","text0/2.xhtml","917151.html"
	# ,"第04章 你找谁？","text0/3.xhtml","917152.html"
	# ,"第05章 怎么像找对象？","text0/4.xhtml","917153.html"
	# ,"第06章 挡箭牌","text0/5.xhtml","917154.html"
    # """
    # print(RE_CHAP.findall(test))