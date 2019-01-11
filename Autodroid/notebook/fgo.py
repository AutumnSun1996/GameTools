from .common import *

from fgo.fgo_fight import FateGrandOrder

const["section"] = "fgo"


def init_map(name="通用配置"):
    const["s"] = FateGrandOrder(name)
    const["s"].make_screen_shot()
    return const["s"]
