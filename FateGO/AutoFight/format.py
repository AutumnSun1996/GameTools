import json


d = {
    "角色1技能1": {
        "Name": "角色1技能1",
        "MainSize": [
            1280,
            720
        ],
        "Offset": [
            38,
            546
        ],
        "Size": [
            64,
            64
        ],
        "Type": "Static"
    },
    "角色1技能2": {
        "Name": "角色1技能2",
        "MainSize": [
            1280,
            720
        ],
        "Offset": [
            132,
            546
        ],
        "Size": [
            64,
            64
        ],
        "Type": "Static"
    },
    "退役-白色舰娘": {
        "Name": "退役-白色舰娘",
        "MainSize": [
            1920,
            1080
        ],
        "ClickOffset": [
            -67,
            99
        ],
        "ClickSize": [
            20,
            20
        ],
        "Positions": [
            [
                217,
                109
            ],
            [
                217,
                457
            ],
            [
                472,
                109
            ],
            [
                472,
                457
            ],
            [
                727,
                109
            ],
            [
                727,
                457
            ],
            [
                982,
                109
            ],
            [
                982,
                457
            ],
            [
                1237,
                109
            ],
            [
                1237,
                457
            ],
            [
                1492,
                109
            ],
            [
                1492,
                457
            ],
            [
                1747,
                109
            ],
            [
                1747,
                457
            ]
        ],
        "Size": [
            60,
            10
        ],
        "Type": "MultiStatic",
        "Image": "白色舰娘.png"
    },
}


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


# print(encode(d, '', 0))
with open(r'D:\QiuShiyang\Document\GameRoutes\碧蓝航线\AutoFight\config\scenes.bak.json', 'r', -1, "UTF-8") as fl:
    text = encode(json.load(fl), '', 0)
with open(r'D:\QiuShiyang\Document\GameRoutes\碧蓝航线\AutoFight\config\scenes.json', 'w', -1, "UTF-8") as fl:
    fl.write(text)
