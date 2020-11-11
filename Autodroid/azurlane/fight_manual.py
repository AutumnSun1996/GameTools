"""
手动战斗用脚本
"""
import time

import win32con
import ctypes
import win32api
from simulator import toast
import logging
from .common_fight import CommonMap

logger = logging.getLogger(__name__)


class Manual(CommonMap):
    def manual(self):
        if self.no_quiet:
            self.go_top()
            toast.show_toast(
                "需要手动操作",
                "当前场景: %s" % self.current_scene["Name"],
                2000,
            )
            return

        res = toast.show_toast(
            "需要手动操作",
            "当前场景: %s" % self.current_scene["Name"],
            5000,
        )
        if res == "SHOW":
            self.go_top()

    def fight(self):
        since_last_manual = time.time() - self.last_manual
        if since_last_manual < 10:
            return
        if not self.scene_changed and since_last_manual < 60:
            return
        print("MANUAL", since_last_manual, self.scene_changed)
        self.manual()
        self.last_manual = time.time()


if __name__ == "__main__":
    import datetime

    m = Manual()
    start_index = m.get_fight_index()
    while True:
        m.check_scene()
