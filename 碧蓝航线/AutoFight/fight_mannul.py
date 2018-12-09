"""
手动战斗用脚本
"""
import time

import win32api

from config import logger
from map_anchor import FightMap


class SP4Control(FightMap):
    def __init__(self):
        super().__init__()
        self.scene_list.append({
            "Name": "进入档案确认",
            "Compare": ["进入档案确认"],
            "Actions": [{"Type": "Click", "Target": "进入档案确认"}, {"Type": "Wait", "Time": 0.5}, ]
        })

    def fight(self):
        if self.last_scene['Name'] in {"战斗地图", "无匹配场景"}:
            return
        self.go_top()
        win32api.MessageBeep()


if __name__ == "__main__":
    import datetime
    sp4 = SP4Control()
    start_index = sp4.get_fight_index()
    while True:
        sp4.check_scene()