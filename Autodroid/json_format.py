import os
import shutil
import json
import yaml

import numpy as np

config = {"MaxLineWidth": 80}


def numpy2json(item):
    if isinstance(item, (np.ndarray, np.number)):
        return item.tolist()
    return item


def text_width(text):
    width = sum([1 if ord(char) < 0x7F else 2 for char in text])
    return width


def dumps(obj):
    return json.dumps(obj, indent=None, ensure_ascii=False, default=numpy2json)


def encode(obj, prefix, level):
    js_text = prefix + dumps(obj)
    if isinstance(obj, (str, int, float)):
        result = js_text
    elif level * 2 + text_width(js_text) < config["MaxLineWidth"]:
        # print("Direct:", js_text)
        result = js_text
    # 宽度大于120
    elif isinstance(obj, dict):
        lines = []
        for key, value in obj.items():
            key_str = ("  " * level) + "  " + dumps(key) + ": "
            lines.append(encode(value, key_str, level + 1))
            # print("For", key, "Get",)
            # print(lines[-1])
        result = prefix + "{\n" + ",\n".join(lines) + "\n" + ("  " * level) + "}"
    elif isinstance(obj, (list, tuple)):
        lines = []
        for value in obj:
            key_str = ("  " * level) + "  "
            lines.append(encode(value, key_str, level + 1))
            # print("F，or", key, "Get",)
            # print(lines[-1])
        result = prefix + "[\n" + ",\n".join(lines) + "\n" + ("  " * level) + "]"
    else:
        raise TypeError("Can't Handle %s" % obj)
    # print('obj:', obj, 'prefix:', prefix, 'level:', level, 'Result:', result, sep='\n')
    return result


def jsonformat(path, backup=True):
    # path = os.path.realpath(path)
    with open(path, "r", -1, "UTF-8") as fl:
        content = fl.read()
    data = json.loads(content)
    new_content = encode(data, "", 0)
    basename, ext = os.path.splitext(path)
    with open(basename + ".yaml", "w", -1, "UTF-8") as f:
        yaml.dump(data, f, allow_unicode=True)
    if content == new_content:
        print("No Change: ", path)
        return
    if backup:
        basename, ext = os.path.splitext(path)
        shutil.copy2(path, basename + ".bak" + ext)
    with open(path, "w", -1, "UTF-8") as fl:
        fl.write(new_content)
    print("Reformated:", path)


def do_format(folder, max_width=80):
    config["MaxLineWidth"] = max_width
    for root, _, files in os.walk(folder):
        if "resources" in root:
            continue
        for name in files:
            if name.endswith(".bak.json"):
                continue
            if not name.endswith(".json"):
                continue
            target = os.path.join(root, name)
            try:
                jsonformat(target)
            except Exception as err:
                print(target, err)


if __name__ == "__main__":
    do_format("fgo", 80)
    do_format("azurlane", 70)
    # print(encode({
    #         "Name": "助战-奶光",
    #         "MainSize": [1280, 720],
    #         "SearchArea": [[300, 60], [420, 100]],
    #         "Size": [400, 32],
    #         "Type": "Dynamic",
    #         "Image": "助战-奶光.png"
    #     }, "", 0))
