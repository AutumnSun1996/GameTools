"""
手动战斗用脚本
"""
import time

import win32con
import ctypes
import win32api
from win10toast import ToastNotifier

import logging
from .common_fight import CommonMap

logger = logging.getLogger(__name__)

toaster = ToastNotifier()


class Manual(CommonMap):
    def manual(self):
        if self.scene_changed or self.since_last_manual > 60:
            toaster.show_toast(
                "需要手动操作",
                "当前场景: %s" % self.current_scene["Name"],
                threaded=True,
                duration=10,
                callback_on_click=self.go_top,
            )
            self.last_manual = time.time()


if __name__ == "__main__":
    import datetime

    m = Manual()
    start_index = m.get_fight_index()
    while True:
        m.check_scene()
