from azurlane.fight_mainline import MainFight as AzurLaneBase

import logging

logger = logging.getLogger(__name__)


class AzurLane(AzurLaneBase):
    def press(self):
        dt = self.since_last_change

        for name in ["航母就绪", "鱼雷就绪"]:
            if self.resource_in_screen(name):
                self.click_at_resource(name)
                self.wait(0.3)

        if dt > 36 and self.resource_in_screen("潜艇数量1"):
            self.click_at_resource("潜艇按钮")
            self.wait(0.3)

        if dt > 60:
            self.wait(1)
            return
        if dt < 7:
            target = "左"
        elif int(dt / 5) % 2:
            target = "上"
        else:
            target = "下"
        logger.info("Press %s at %.3f", target, dt)
        print(int(dt) // 5)
        self.click_at_resource(target, hold=1)
        self.wait(0.3)


if __name__ == "__main__":
    m = AzurLane("埃塞克斯演习")
    while True:
        m.check_scene()
