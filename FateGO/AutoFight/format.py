import os
import shutil
import json


def text_width(text):
    width = sum([1 if ord(char) < 0x7f else 2 for char in text])
    return width


def dumps(obj):
    return json.dumps(obj, indent=None, ensure_ascii=False)


def encode(obj, prefix, level):
    js_text = prefix + dumps(obj)
    if isinstance(obj, (str, int, float)):
        result = js_text
    elif level * 2 + text_width(js_text) < 80:
        # print("Direct:", js_text)
        result = js_text
    # 宽度大于120
    elif isinstance(obj, dict):
        lines = []
        for key, value in obj.items():
            key_str = ('  ' * level) + '  ' + dumps(key) + ": "
            lines.append(encode(value, key_str, level+1))
            # print("For", key, "Get",)
            # print(lines[-1])
        result = prefix + '{\n' + ',\n'.join(lines) + '\n' + ('  ' * level) + '}'
    elif isinstance(obj, (list, tuple)):
        lines = []
        for value in obj:
            key_str = ('  ' * level) + '  '
            lines.append(encode(value, key_str, level+1))
            # print("For", key, "Get",)
            # print(lines[-1])
        result = prefix + '[\n' + ',\n'.join(lines) + '\n' + ('  ' * level) + ']'
    else:
        raise TypeError("Can't Handle %s" % obj)
    # print('obj:', obj, 'prefix:', prefix, 'level:', level, 'Result:', result, sep='\n')
    return result


def jsonformat(path, backup=True):
    path = os.path.realpath(path)
    if backup:
        basename, ext = os.path.splitext(path)
        shutil.copy2(path, basename + '.bak' + ext)
    with open(path, "r", -1, "UTF-8") as fl:
        text = encode(json.load(fl), '', 0)
    with open(path, "w", -1, "UTF-8") as fl:
        fl.write(text)
    print(path, "Reformated.")

if __name__ == "__main__":
    jsonformat('config/resources.json')
    jsonformat('config/scenes.json')
    jsonformat('config/fightConfig.json')
    jsonformat(r'D:\QiuShiyang\Document\GameRoutes\碧蓝航线\AutoFight\config\resources.json')
    jsonformat(r'D:\QiuShiyang\Document\GameRoutes\碧蓝航线\AutoFight\config\scenes.json')
    jsonformat(r'D:\QiuShiyang\Document\GameRoutes\碧蓝航线\AutoFight\maps\斯图尔特的硝烟SP3.json')
    jsonformat(r'D:\QiuShiyang\Document\GameRoutes\碧蓝航线\AutoFight\maps\围剿斯佩伯爵SP3.json')
    
