import sys
from datetime import datetime, timedelta
from dateutil.parser import parse
from fgo.fast import FGOSimple

import argparse

import logging
logger = logging.getLogger(__name__)


def make_stop_checker(args):
    def stop_checker(s):
        if s.current_scene_name == "AP不足":
            if s.scene_history_count["AP不足"] > args.add_ap:
                s.click_at_resource("AP不足-关闭")
                return True
            now = datetime.now()
            if not s.actions_done and now - args.start_time > args.end_in:
                s.click_at_resource("AP不足-关闭")
                return True
        if s.current_scene_name == "获得物品" and s.actions_done:
            logger.warning("On 获得物品; %s", s.scene_history_count)
            if s.scene_history_count["获得物品"] >= args.fight_count:
                return True
        return False
    return stop_checker


def main(args):
    FGOSimple.section = args.section
    fgo = FGOSimple(args.map_name)
    try:
        fgo.main_loop(make_stop_checker(args))
        # input("Pause...")
    except KeyboardInterrupt:
        pass
    logger.warning("(OnExit) Scene Count: %s", fgo.scene_history_count)

    # if datetime.now() > target_time:
    #     fgo.wait(10)
    #     win32api.SendMessage(fgo.hwnd, win32con.WM_CLOSE, 0, 0)


def parse_end_in(text):
    dt = [3, 0, 0]
    for idx, item in enumerate(text.split(":")):
        dt[idx] = int(item)
    return timedelta(**dict(zip(["hours", "minutes", "seconds"], dt)))


if __name__ == "__main__":
    # help(conflictsparse.conflictsparse)
    args = argparse.ArgumentParser()
    args.add_argument("section", nargs="?", default="FGO", help="模拟器ID")
    args.add_argument("map_name", nargs="?", default="通用配置", help="地图名")
    args.add_argument("--add_ap", "-ap", type=int, default=0, help="补充AP次数。默认为0，不补充")
    args.add_argument("--end_in", metavar="HH[:MM[:SS]]", type=parse_end_in, default=timedelta(hours=5),
                      help="脚本最大运行时间。默认为5小时")
    args.add_argument("--fight_count", "-n", type=int, default=100, help="自动战斗次数。默认为100")

    args = args.parse_args()

    args.start_time = datetime.now()
    logger.warning("Start Args: %s", args)
    # fgo = FGOSimple("刷材料")
    # fgo = FGOSimple("主号换人礼装速刷")
    # fgo = FGOSimple("主号赝作速刷")
    # main("主号剧情推进")
    # main("情人节/大号弓本")
    main(args)
    # main("情人节/大号术本")
    # fgo = FGOSimple("主号赝作速刷-术本")
    # fgo = FGOSimple("主号赝作速刷-杀本")
