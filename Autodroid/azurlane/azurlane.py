"""
碧蓝航线通用功能

By AutumnSun
"""
import time
import json

from config_loader import logger, config
from simulator import SimulatorControl
from simulator.win32_tools import rand_click
from collections import defaultdict

class AzurLaneControl(SimulatorControl):
    """碧蓝航线通用控制
    """
    section = "AzurLane"
    status_path = "%s/data/fightStatus.json" % section
    retire_choices = ["退役-白色舰娘", "退役-蓝色舰娘"]

    def get_fight_status(self):
        """战斗次数计数"""
        try:
            with open(self.status_path, 'r') as fl:
                status = json.load(fl)
            status["FightIndex"] = status["VirtualFightIndex"] + status["TrueFightIndex"]
        except FileNotFoundError:
            status = defaultdict(lambda: 0)
        return status

    def inc_fight_index(self):
        """增加战斗次数"""
        status = self.get_fight_status()
        logger.debug("增加Fight Index: %d -> %d", status["FightIndex"], status["FightIndex"]+1)
        status["FightIndex"] += 1
        self.seve_fight_status(status)

    def seve_fight_status(self, status):
        """设置战斗次数"""
        with open(self.status_path, 'w') as fl:
            json.dump(status, fl, ensure_ascii=False)

    def fight(self):
        """处理战斗内容. 随每个地图变化"""
        pass

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
            if self.resource_in_screen(name):
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
            for x, y in self.search_resource(name)[1]:
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