import sys
from datetime import datetime, timedelta
from dateutil.parser import parse
from fgo.fast import FGOSimple

import logging
logger = logging.getLogger(__name__)

start_time = datetime.now()
def stop_checker(s):
    if s.current_scene_name == "AP不足":
        if s.scene_history_count["AP不足"] >= 0:
            return True
        now = datetime.now()
        if not s.actions_done and now - start_time > timedelta(hours=3) and now > parse("2019-03-10 03:15:00"):
            return True
    if s.current_scene_name == "获得物品" and s.actions_done:
        logger.warning("On 获得物品; %s", s.scene_history_count)
    return False


def main(map_name):
    logger.warning("%s Start", map_name)
    fgo = FGOSimple(map_name)
    try:
        fgo.main_loop(stop_checker)
        # input("Pause...")
    except KeyboardInterrupt:
        pass
    logger.warning("(OnExit) Scene Count: %s", fgo.scene_history_count)

    # if datetime.now() > target_time:
    #     fgo.wait(10)
    #     win32api.SendMessage(fgo.hwnd, win32con.WM_CLOSE, 0, 0)


if __name__ == "__main__":
    section = "FGO"
    if len(sys.argv) > 1:
        section = sys.argv[1]
    FGOSimple.section = section

    map_name = "情人节/大号狂本"
    if len(sys.argv) > 2:
        map_name = sys.argv[2]
    # fgo = FGOSimple("刷材料")
    # fgo = FGOSimple("主号换人礼装速刷")
    # fgo = FGOSimple("主号赝作速刷")
    # main("主号剧情推进")
    # main("情人节/大号弓本")
    main(map_name)
    # main("情人节/大号术本")
    # fgo = FGOSimple("主号赝作速刷-术本")
    # fgo = FGOSimple("主号赝作速刷-杀本")
