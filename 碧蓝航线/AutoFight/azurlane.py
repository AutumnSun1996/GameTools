"""
碧蓝航线通用功能

By AutumnSun
"""
import time

from config import logger
from win32_tools import rand_click
from simulator import SimulatorControl


class AzurLaneControl(SimulatorControl):
    """模拟器通用控制
    """
    retire_choices = ["退役-白色舰娘", "退役-蓝色舰娘"]

    @staticmethod
    def get_fight_index():
        """战斗次数计数"""
        with open('fightIndex.txt', 'r') as fl:
            fight_idx = int(fl.read())
        return fight_idx

    @staticmethod
    def inc_fight_index():
        """增加战斗次数"""
        with open('fightIndex.txt', 'r') as fl:
            fight_idx = int(fl.read())
        logger.debug("增加Fight Index: %d -> %d", fight_idx, fight_idx+1)
        with open('fightIndex.txt', 'w') as fl:
            fl.write("%d" % (fight_idx + 1))

    @staticmethod
    def set_fight_index(index=0):
        """设置战斗次数"""
        with open('fightIndex.txt', 'w') as fl:
            fl.write("%d" % index)

    def fight(self):
        """处理战斗内容. 随每个地图变化"""
        raise NotImplementedError()

    def mood_detect(self):
        """舰娘心情检测"""
        if self.current_scene['Name'] == "舰队选择":
            colors = [
                ("黄", self.error),
            ]
            action = "进入地图"
        elif self.current_scene['Name'] == "战斗准备":
            colors = [
                ("红", self.critical),
                ("黄", self.error),
                ("绿", self.notice),
            ]
            action = "继续战斗"
        for color in colors:
            name = "{0}-{1[0]}脸".format(self.current_scene['Name'], color)
            if self.resource_in_screen(name) is not False:
                color[1](
                    "舰娘心情值低(%s)" % (name),
                    "舰娘心情值", action)
                # 检测顺序为红黄绿, 因此无需多次检测
                return

    def select_ships(self):
        """选择退役舰娘"""
        self.make_screen_shot()
        targets = []
        for name in self.retire_choices:
            dx, dy = self.resources[name].get("ClickOffset", (-10, -10))
            w, h = self.resources[name].get("ClickSize", (20, 20))
            for x, y in self.resource_in_screen(name):
                targets.append((x+dx, y+dy, x+dx+w, y+dy+h))
        logger.info("select_ships: %s", targets)
        return targets[:10]

    def retire(self):
        """执行退役操作"""
        if self.resource_in_screen("降序"):
            logger.debug("切换倒序显示")
            self.click_at_resource("降序")
            time.sleep(1)
        waiting = 1
        targets = self.select_ships()
        if not targets:
            self.critical("自动退役失败")
        while targets:
            logger.info("退役舰娘*%d", len(targets))
            for rect in targets:
                rand_click(self.hwnd, rect)
                time.sleep(0.3)

            logger.debug("确定")
            self.click_at_resource("退役-确定", True)
            time.sleep(waiting)
            logger.debug("确定拆解")
            self.click_at_resource("退役-二次确定", True)
            time.sleep(waiting)
            logger.debug("点击继续")
            self.wait_resource("获得道具")
            self.click_at_resource("退役-二次确定")
            time.sleep(waiting)
            logger.debug("装备拆解")
            self.click_at_resource("退役-装备-确定", True)
            time.sleep(waiting)
            logger.debug("确定拆解")
            self.click_at_resource("退役-装备-拆解", True)
            time.sleep(waiting)
            logger.debug("点击继续")
            self.wait_resource("获得道具")
            self.click_at_resource("退役-装备-拆解")
            time.sleep(waiting)
            targets = self.select_ships()

        time.sleep(waiting)
        logger.debug("返回之前界面")
        self.click_at_resource("退役-取消", True)
        time.sleep(3)


if __name__ == "__main__":
    logger.setLevel("DEBUG")
    controler = AzurLaneControl()
    print(controler.select_ships())
    # print(controler.retire())
