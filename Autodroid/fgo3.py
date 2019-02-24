import win32api
import win32con
from datetime import datetime
from dateutil.parser import parse
from fgo.fast import FGOSimple

import logging
logger = logging.getLogger(__name__)

def stop_checker(s):
    if s.current_scene_name == "AP不足" and s.scene_history_count["AP不足"] >= 36:
        return True
    if s.current_scene_name == "获得物品" and s.actions_done:
        logger.warning("On 获得物品; %s", s.scene_history_count)
    return False


def main(map_name):
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
    FGOSimple.section = "FGO3"
    # fgo = FGOSimple("XY赝作速刷-枪本")
    main("XY赝作速刷-终本2")

    target_time = parse("2019-02-24 04:06:00")
