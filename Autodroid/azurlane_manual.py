import time

import win32api

from azurlane.common_fight import CommonMap

if __name__ == "__main__":
    m = CommonMap("通用地图")
    start_index = m.get_fight_status()["FightIndex"]
    while True:
        m.check_scene()
