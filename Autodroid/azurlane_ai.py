import time

import win32api

from azurlane.fight_simple import CommonMap

if __name__ == "__main__":
    m = CommonMap("无伏击地图")
    start_index = m.get_fight_status()["FightIndex"]
    while True:
        m.check_scene()
