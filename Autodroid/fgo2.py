import win32api
import win32con
from datetime import datetime
from dateutil.parser import parse
from fgo.fast import FGOSimple

import logging
logger = logging.getLogger(__name__)

target_time = parse("2019-02-26 02:15:00")

def stop_checker(s):
    if s.current_scene_name == "AP不足" and s.scene_history_count["AP不足"] >= 60:
        return True
    if s.current_scene_name in {"获得物品", "AP不足"} and s.actions_done:
        logger.warning("On %s: %s", s.current_scene_name, s.scene_history_count)
    if s.current_scene_name == "AP不足":
        if datetime.now() > target_time:
            return True
    return False


def main(map_name):
    fgo = FGOSimple(map_name)
    try:
        fgo.main_loop(stop_checker)
        # input("Pause...")
    except Exception:
        pass
    logger.warning("(OnExit) Scene Count: %s", fgo.scene_history_count)

    # if datetime.now() > target_time:
    #     fgo.wait(10)
    #     win32api.SendMessage(fgo.hwnd, win32con.WM_CLOSE, 0, 0)


if __name__ == "__main__":
    FGOSimple.section = "FGO2"
    # fgo = FGOSimple("C尼禄")
    # fgo = FGOSimple("R金时")
    # fgo = FGOSimple("石头号-弓阶")
    # fgo = FGOSimple("小号剧情推进")
    # fgo = FGOSimple("小号赝作速刷")
    # fgo = FGOSimple("小号赝作配置-枪本")
    # fgo = FGOSimple("小号赝作速刷-杀本")
    # fgo = FGOSimple("小号赝作速刷-术本")
    # main("小号赝作配置-骑本")
    main("小号剧情推进")
