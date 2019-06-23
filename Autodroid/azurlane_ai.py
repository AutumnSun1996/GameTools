import sys
import time

import win32api

from azurlane.fight_simple import CommonMap

if __name__ == "__main__":
    if len(sys.argv) > 1:
        map_name = sys.argv[1]
    else:
        map_name = "AI-SP4"
    m = CommonMap(map_name)
    start_index = m.get_fight_status()["FightIndex"]
    while True:
        m.check_scene()
