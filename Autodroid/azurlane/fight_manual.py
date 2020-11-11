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
    def _manual(self):
        title = "需要手动操作"
        reason = []
        if self.scene_changed:
            reason += ["from {}".format(self.last_scene_name)]
        dt = time.time() - self.last_manual
        if dt > 60:
            reason += ["dt={:.1f}".format(dt)]
        reason = ",".join(reason)
        msg = "当前场景: {}\n({})".format(self.current_scene_name, reason)

        if self.no_quiet:
            self.go_top()
            toast.show_toast(title, msg, 2000, threaded=True)
            return

        res = toast.show_toast(title, msg, 5000)
        if res == "SHOW":
            self.go_top()

    def manual(self):
        since_last_manual = time.time() - self.last_manual
        if since_last_manual < 10:
            return
        if not self.scene_changed and since_last_manual < 60:
            return
        self._manual()
        self.last_manual = time.time()

    def fight(self):
        self.manual()


if __name__ == "__main__":
    import datetime

    m = Manual()
    start_index = m.get_fight_index()
    while True:
        m.check_scene()
