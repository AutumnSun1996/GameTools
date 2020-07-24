import os
import sys
from datetime import datetime, timedelta
from dateutil.parser import parse

import argparse

import logging
from config import hocon

logger = logging.getLogger(__name__)


def make_stop_checker(args):
    def stop_checker(s):
        if s.current_scene_name == "外部地图" and not s.actions_done:
            now = datetime.now()
            if (
                args.end_in is not None
                and not s.actions_done
                and now - args.start_time > args.end_in
            ):
                return True
            if (
                args.fight_count is not None
                and s.scene_history_count["获得道具"] >= args.fight_count
            ):
                return True
        return False

    return stop_checker


def main(args):
    config_file = os.path.join("azurlane", "maps", args.map_name + ".conf")
    info = hocon.load(config_file)
    if "MapClass" in info:
        import importlib

        module_path, cls_name = info["MapClass"]
        m = importlib.import_module(module_path)
        map_cls = getattr(m, cls_name)
    else:
        from azurlane.common_fight import CommonMap as map_cls
    logger.warning("Use class %r", map_cls)
    az = map_cls(args.map_name)
    try:
        az.main_loop(make_stop_checker(args))
        # input("Pause...")
    except KeyboardInterrupt as e:
        logger.warning("(OnExit) Scene Count: %s", az.scene_history_count)
    except Exception as e:
        logger.warning("(OnExit) Scene Count: %s", az.scene_history_count)
        raise e


def parse_end_in(text):
    dt = [3, 0, 0]
    for idx, item in enumerate(text.split(":")):
        dt[idx] = int("0" + item)
    return timedelta(**dict(zip(["hours", "minutes", "seconds"], dt)))


if __name__ == "__main__":
    # help(conflictsparse.conflictsparse)
    parser = argparse.ArgumentParser()
    parser.add_argument("map_name", nargs="?", default="通用地图", help="地图名")
    parser.add_argument(
        "--end_in",
        "-t",
        metavar="HH[:MM[:SS]]",
        type=parse_end_in,
        default=None,
        help="脚本最大运行时间。",
    )
    parser.add_argument("--fight_count", "-n", type=int, default=None, help="自动战斗次数。")

    args = parser.parse_args()

    args.start_time = datetime.now()
    logger.warning("Start Args: %s", args)
    main(args)
