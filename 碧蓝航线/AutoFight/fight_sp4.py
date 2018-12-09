"""
传颂之物联动SP4专用脚本
"""
import time

from config import logger
from map_anchor import FightMap

NEW_SCENES = {
    "活动地图": {
        "Name": "活动地图",
        "Condition": "梦幻的交汇SP4",
        "Actions": [
            {"Type": "Click", "Target": "梦幻的交汇SP4"},
            {"Type": "Wait", "Time": 0.5},
            {"Type": "InnerCall", "Target": "reset_fight_index"}
        ]
    }
}


class SP4Control(FightMap):
    def __init__(self):
        super().__init__()
        self.scenes.update(NEW_SCENES)
        self.fight_idx_offset = 4
        self.map_name = "梦幻的交汇SP4"
    
    def reset_fight_index(self):
        self.fight_idx_offset = 0
        fight_idx = self.get_fight_index() + self.fight_idx_offset
        mod = fight_idx % 6
        logger.warning("Current Fight Index: %d (%d)", fight_idx, mod)
        if mod != 0:
            self.fight_idx_offset += 6-mod
            logger.info("Reset Fight Index From %d To %d", fight_idx, fight_idx+6-mod)

    def fight(self):
        if self.last_scene['Name'] == "战斗地图":
            if len(self.scene_history) > 3 and self.scene_history[-3]['Name'] == "战斗地图":
                logger.info("第三次回到在战斗界面. 增加虚拟战斗次数")
                logger.info("history: %s", [scene["Name"] for scene in self.scene_history])
                self.fight_idx_offset += 1
            else:
                logger.info("第二次回到战斗界面, 重做前次动作.")
        fight_idx = self.get_fight_index() + self.fight_idx_offset
        mod = fight_idx % 6
        logger.info("Fight index: %d (%d)", fight_idx, mod)
        if mod == 0:
            time.sleep(2)
            logger.info("触发扫描-E6")
            self.click_at_map("E6")
            # click_at(645, 460, hwnd)
            time.sleep(8)
            logger.info("前往待命-E4")
            self.click_at_map("E4")
            # click_at(645, 280, hwnd)
            time.sleep(3)
            logger.info("切换2队")
            self.click_at_resource("切换舰队")
            # reset_map_pos()
            time.sleep(2)
            logger.info("左边精英-D4")
            self.click_at_map("D4")
            # click_at(535, 300, hwnd)
            # self.set_fight_index(1)
            time.sleep(6)
        elif mod == 1:
            # reset_map_pos()
            logger.info("左边小舰队-C5")
            time.sleep(2)
            self.click_at_map("C5")
            # click_at(400, 390, hwnd)
            # self.set_fight_index(2)
            time.sleep(2)
        elif mod == 2:
            # reset_map_pos()
            logger.info("上边小舰队-E3")
            self.click_at_map("E3")
            # click_at(665, 210, hwnd)
            # self.set_fight_index(3)
            time.sleep(4)
        elif mod == 3:
            # reset_map_pos()
            logger.info("右边精英-F4")
            self.click_at_map("F4")
            # click_at(790, 300, hwnd)
            # self.set_fight_index(4)
            time.sleep(2)
        elif mod == 4:
            # reset_map_pos()
            logger.info("右边小舰队-G5")
            self.click_at_map("G5")
            # click_at(925, 400, hwnd)
            # self.set_fight_index(5)
            time.sleep(2)
        elif mod == 5:
            logger.info("切换1队")
            self.click_at_resource("切换舰队")
            time.sleep(2)
            # reset_map_pos()
            logger.info("Boss-E1")
            self.click_at_map("E1")
            # click_at(655, 80, hwnd)
            # self.set_fight_index(0)
            time.sleep(2)
        time.sleep(1)


if __name__ == "__main__":
    import datetime
    sp4 = SP4Control()
    start_index = sp4.get_fight_index()
    while True:
        sp4.check_scene()
        if sp4.current_scene["Name"] == "活动地图":
            new_fight = sp4.get_fight_index() - start_index
            logger.info("战斗次数:%d(%d)", sp4.get_fight_index(), new_fight)
            if sp4.get_fight_index() >= 21398+60:
                exit(0)
