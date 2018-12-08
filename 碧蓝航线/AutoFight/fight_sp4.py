"""
传颂之物联动SP4专用脚本
"""
import time

from config import logger
from map_anchor import FightMap

ANCHORS = [
    {
        "Name": "anchor-D7.png",
        "OnMap": "D7",
        "Translate": (60, 40),
    },
    {
        "Name": "anchor-E5.png",
        "OnMap": "E5",
        "Translate": (46, 20)
    },
    {
        "Name": "anchor-A4.png",
        "OnMap": "A4",
        "Translate": (0, 50)
    },
    {
        "Name": "anchor-I4.png",
        "OnMap": "I4",
        "Translate": (50, 45)
    },
    {
        "Name": "anchor-I5.png",
        "OnMap": "I5",
        "Translate": (50, 10)
    },
    {
        "Name": "Boss.png",
        "OnMap": "E1",
        "Translate": (31, 45)
    },
]


SCENE_MAP = {
    "Name": "SP地图",
    "Compare": [{"Rect": (1070, 670, 1260, 730), "Name": "作战补给.png", "TreshHold": 7}],
    "Actions": [
        {"Type": "Click", "Target": (630, 370, 680, 420)},
        {"Type": "Wait", "Time": 0.5},
        {"Type": "InnerCall", "Target": "reset_fight_index"}
    ]
}


class SP4Control(FightMap):
    def __init__(self):
        super().__init__(ANCHORS)
        self.scene_list.append(SCENE_MAP)
        self.fight_idx_offset = 0
    
    def get_fight_index(self):
        return super().get_fight_index() + self.fight_idx_offset
    
    def reset_fight_index(self):
        fight_idx = self.get_fight_index()
        mod = fight_idx % 6
        logger.warning("Current Fight Index: %d (%d)", fight_idx, mod)
        if mod != 0:
            self.set_fight_index(fight_idx+6-mod)
            logger.warning("Reset Fight Index From %d To %d", fight_idx, fight_idx+6-mod)

    def fight(self):
        if self.last_scene['Name'] == "战斗地图":
            logger.info("停留在战斗界面. 增加虚拟战斗次数")
            logger.info("history: %s", [scene["Name"] for scene in self.scene_history])
            self.fight_idx_offset += 1
        fight_idx = self.get_fight_index()
        mod = fight_idx % 6
        logger.info("Fight index: %d (%d)", fight_idx, mod)
        if mod == 0:
            logger.info("触发扫描-E6")
            self.click_at_map("E6")
            # click_at(645, 460, hwnd)
            time.sleep(8)
            logger.info("前往待命-E4")
            self.click_at_map("E4")
            # click_at(645, 280, hwnd)
            time.sleep(3)
            logger.info("切换2队")
            self.toggle_fleet()
            # reset_map_pos()
            # time.sleep(2)
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
            self.toggle_fleet()
            # reset_map_pos()
            logger.info("Boss-E1")
            self.click_at_map("E1")
            # click_at(655, 80, hwnd)
            # self.set_fight_index(0)
            time.sleep(2)
        time.sleep(1)


if __name__ == "__main__":
    sp4 = SP4Control()
    while True:
        sp4.check_scene()
