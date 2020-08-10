def represent(data, level="    ", list_limit=5, dict_limit=20, str_limit=200):
    """生成复杂dict的描述字符串
    """

    def _multi_repr(data, keys, _level="", limit=None):
        """生成子项的描述字符串
        """
        need_dots = False
        # 数量较多时只显示前limit项
        if limit is not None and len(keys) > limit:
            keys = keys[:limit]
            need_dots = True

        items = []
        for k in keys:
            # 子项的value不应包含prefix, 但子项为list/dict时, 其子项需继承prefix
            items.append(
                "\n{}{}: {}".format(
                    _level,
                    repr(k),
                    _represent(data[k], prefix="", _level=_level + level),
                )
            )
        # 有隐藏项时添加"..."和数量说明
        if need_dots:
            items.append("\n{}...({}/{})".format(_level, len(keys), len(data)))
        return "".join(items)

    def _represent(data, prefix, _level, key=""):
        # dict和list, 基于_multi_repr生成所有子项描述
        if isinstance(data, dict):
            keys = list(sorted(data.keys()))
            text = _multi_repr(data, keys, _level, dict_limit)
            return "{}dict({}):{}".format(prefix, len(data), text)
        if isinstance(data, list):
            keys = list(range(len(data)))
            text = _multi_repr(data, keys, _level, list_limit)
            return "{}list({}):{}".format(prefix, len(data), text)

        # 字符串类型
        if isinstance(data, (str, bytes)):
            if len(data) > str_limit:
                text = repr(data[:str_limit]) + "..."
            else:
                text = repr(data)
            return "{}str({}): {}".format(prefix, len(data), text)

        # 数字和bool类型
        if isinstance(data, (int, float, bool)):
            return "{}{}: {}".format(prefix, type(data).__name__, repr(data))
        # 其他未知类型
        return "{}{}: {}".format(prefix, type(data), repr(data))

    return _represent(data, prefix="", _level="", key="")


def flatten(fields):
    """返回基于fields生成的一维list

    assert flatten("ABC") == ["ABC"]
    assert flatten([[["A"]], "B"]) == ["A", "B"]
    assert flatten([[[]], "A"]) == ["A"]
    """
    if not isinstance(fields, (list, tuple)):
        return [fields]

    flat = []
    for field in fields:
        if isinstance(field, (list, tuple)):
            flat.extend(flatten(field))
        else:
            flat.append(field)
    return flat


def extract(data, path):
    """
    """
    if isinstance(path, str):
        path = path.split("/")
    obj = data
    for k in path:
        obj = obj[k]
    return obj
