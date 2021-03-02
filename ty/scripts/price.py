import re
from collections import defaultdict, namedtuple
import logging
import sqlite3
import numpy as np
import functools

from data import recipe_data, trade_data

logger = logging.getLogger(__name__)


item_idx_map = {}
idx_item_map = {}

cost_ratio = np.sqrt(1)
tax = {
    "云券": 0.01,
    "云币": 0.1,
}


def check_name(name):
    if name not in item_idx_map:
        idx = len(item_idx_map)
        item_idx_map[name] = idx
        idx_item_map[idx] = name


def item2arr(item):
    arr = np.zeros(len(item_idx_map))
    for name in item:
        arr[item_idx_map[name]] = item[name]
    return arr


def arr2item(arr):
    res = {}
    for idx, count in enumerate(arr):
        if not np.isclose(count, 0):
            res[idx_item_map[idx]] = count
    return res


def zero():
    return 0


def counter():
    return defaultdict(zero)


def merge_count(*items):
    """对dict形式的数量统计进行合并"""
    info = counter()
    for item in items:
        for key in item:
            info[key] += item[key]
    return dict(info)


def load_items(text):
    """根据文本解析物品数量列表"""
    info = counter()
    for item in text.split("+"):
        try:
            count, name = re.search(r"^([.\d]*)([-·\w]+)\s*$", item).groups()
            if not count:
                count = 1
            count = float(count)
        except Exception:
            logger.exception("Failed to parse %r", item)
            raise
        check_name(name)
        info[name] += count
    return dict(info)


def load_recipe_data(text):
    """解析转换配方文本数据"""
    typ = None
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("#"):
            if "=" not in line:
                typ = line.lstrip("#").strip()
            continue
        if "=" not in line:
            continue
        cost, result = line.split("=")
        cost, result = load_items(cost), load_items(result)
        name = ",".join(list(result))
        yield typ, name, cost, result


def load_trade_data(text):
    """解析摆摊交易价格文本数据"""
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("#"):
            continue
        if "=" not in line:
            continue
        item, price = line.split("=")
        price = float(price)

        item_info = load_items(item)
        name = ",".join(list(item_info.keys()))
        yield "购买", name, {"云币": price}, item_info
        yield "出售", name, merge_count(item_info, {"云券": np.floor(price * tax["云券"])}), {
            "云币": price - np.floor(price * tax["云币"])
        }


def init_all_recipe():
    check_name("云券")
    Recipe = namedtuple("Recipe", ["type", "name", "cost", "result"])
    recipes = []
    for item in load_recipe_data(recipe_data):
        recipes.append(Recipe(*item))
    for item in load_trade_data(trade_data):
        recipes.append(Recipe(*item))

    return recipes


class VirtualFont(object):
    @staticmethod
    @functools.lru_cache
    def measure(text):
        n = 0
        for char in text:
            if 0x20 <= ord(char) <= 0x7F:
                n += 1
            elif char == "·":
                n += 1
            else:
                n += 2
        return n


def ljust(text, width, pad_by=" ", font=VirtualFont):
    size = font.measure(text)
    pad_size = font.measure(pad_by)
    n_pad = (width - size) // pad_size
    if n_pad > 0:
        text += n_pad * pad_by
    return text


def learn_relative_value(recipes):
    from sklearn.linear_model import LinearRegression as LRClass

    known_value = [
        ({"云币": 1e8}, 1e8),
        # ({"云券": 1e8}, 1e6),
    ]
    X = []
    X_true = []
    y = []
    for _, _, cost, result in recipes:
        cost_arr, res_arr = item2arr(cost), item2arr(result)
        X.append(res_arr - cost_ratio * cost_arr)
        X_true.append(res_arr - cost_arr)
        y.append(0)

    for item, value in known_value:
        X.append(item2arr(item))
        y.append(value)

    lr = LRClass(fit_intercept=False, positive=True)
    lr.fit(X, y)

    max_width = max([VirtualFont.measure(name) for name in item_idx_map])
    for name in item_idx_map:
        data = item2arr({name: 1})
        value = lr.predict([data])[0]
        print("{} {:>10.2f}".format(ljust(name, max_width + 1), value))

    y_pred = lr.predict(X_true)
    res = list(zip(recipes, y_pred))
    res.sort(key=lambda a: a[1])
    for recipe, value in res:
        r = recipe
        if (
            "八音盒" in str(r)
            or "铜矿石" in r.result
            or "椰木" in r.result
            or "精炼矿石" in r.result
        ):
            cost_value, res_value = lr.predict(
                [item2arr(recipe.cost), item2arr(recipe.result)]
            )
            print(
                "{v:8.2f} {r[0]}.{r[1]} {r[2]}{cv:.2f} {r[3]}{rv:.2f}".format(
                    v=res_value - cost_value, r=recipe, cv=cost_value, rv=res_value
                )
            )
            continue


if __name__ == "__main__":
    recipes = init_all_recipe()
    print("给出{}个物品的{}个配方".format(len(item_idx_map), len(recipes)))
    learn_relative_value(recipes)
