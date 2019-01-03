from .common import *

from azurlane.common_fight import FightMap

const["section"] = "azurlane"

def check_anchor_on_map(data, on_map):
    pass

def init_map(name):
    const["s"] = FightMap(name)
    const["s"].make_screen_shot()
    return const["s"]
