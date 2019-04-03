import sys

from simulator.win32_tools import rand_click
from fgo.fast import FGOSimple

from config_loader import logging

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")


class FGOUpgrade(FGOSimple):
    def choose_exp_cards(self, cols=3, rows=7, stop=False):
        info = self.resources["卡位列表"]
        x0, y0 = info["Offset"]
        dx, dy = info["PositionDelta"]
        w, h = info["Size"]
        for i in range(rows):
            for j in range(cols):
                x, y = (x0+dx*i, y0+dy*j)
                logger.info("ClickAt %s", (x, y, x+w, y+h))
                rand_click(self.hwnd, (x, y, x+w, y+h))
                self.wait(0.3)
                if stop is not None:
                    self.make_screen_shot()
                    if self.parse_scene_condition(stop):
                        return


if __name__ == "__main__":
    if len(sys.argv) > 1:
        section = sys.argv[1]
    else:
        section = "FGO2"

    if len(sys.argv) > 2:
        gold_only = int(sys.argv[2])
    else:
        gold_only = 0

    FGOUpgrade.section = section
    FGOUpgrade.gold_only = gold_only

    fgo = FGOUpgrade("升级")
    fgo.make_screen_shot()
    print(fgo.parse_scene_condition(["选卡"]))

    logger.info("Starting...")
    fgo.check_scene()
    logger.info("FGO Scene: %s", fgo.current_scene)
    fgo.main_loop()
