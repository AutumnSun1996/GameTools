from .common import *

from fgo.fgo_fight import FateGrandOrder

const["section"] = "FGO"

class SimpleFGO(FateGrandOrder):
    section = "FGO2"
    def __init__(self, map_name):
        FateGrandOrder.__init__(self, map_name)
        self.last_manual = 0

    @property
    def since_last_manual(self):
        return time.time() - self.last_manual

    def manual(self):
        if self.scene_changed or self.since_last_manual > 30:
            self.go_top()
            win32api.MessageBeep()
            self.last_manual = time.time()


def init_map(name="通用配置"):
    const["s"] = SimpleFGO(name)
    const["s"].make_screen_shot()
    return const["s"]
