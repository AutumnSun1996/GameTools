from .common import *

from fgo.fast import FGOSimple as FateGrandOrder

const["section"] = "fgo"

def init_map(name="通用配置", section="FGO"):
    FateGrandOrder.section = section
    const["s"] = FateGrandOrder(name)
    const["s"].make_screen_shot()
    return const["s"]
