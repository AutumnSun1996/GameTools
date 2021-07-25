import os
import sys
from datetime import datetime, timedelta
from dateutil.parser import parse

import argparse

import logging
from config import hocon
from azurlane import load_map

logger = logging.getLogger(__name__)


def main(args):
    az = load_map(args.map_name)
    az.no_quiet = args.no_quiet
    az.max_fight_count = args.fight_count
    try:
        az.main_loop()
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
    parser.add_argument(
        "--no-quiet", "-Q", action="store_true", help="关闭安静模式。手动模式下将直接置顶游戏窗口"
    )

    args = parser.parse_args()

    args.start_time = datetime.now()
    logger.warning("Start Args: %s", args)
    main(args)
