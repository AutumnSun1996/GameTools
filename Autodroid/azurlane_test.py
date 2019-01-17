import time

import win32api

from azurlane.common_fight import CommonMap

try:
    __builtin__ = __builtins__
except NameError:
    pass


class ManualFight(CommonMap):
    def __init__(self):
        CommonMap.__init__(self, "通用地图")
        self.last_manual = 0

    @property
    def since_last_manual(self):
        return time.time() - self.last_manual

    def manual(self):
        if self.scene_changed or self.since_last_manual > 30:
            self.go_top()
            win32api.MessageBeep()
            self.last_manual = time.time()


if __name__ == "__main__":
    print(__builtin__)
    import datetime
    m = ManualFight()
    start_index = m.get_fight_status()["FightIndex"]
    while True:
        m.check_scene()
