import time

import win32api

from fgo.fgo_simple import FGOSimple


class ManualFight(FGOSimple):
    def __init__(self):
        FGOSimple.__init__(self, "手动")
        self.last_manual = time.time()

    @property
    def since_last_manual(self):
        return time.time() - self.last_manual

    def manual(self):
        if self.scene_changed or self.since_last_manual > 30:
            self.go_top()
            win32api.MessageBeep()
            self.last_manual = time.time()


if __name__ == "__main__":
    f = ManualFight()
    while True:
        f.check_scene()
