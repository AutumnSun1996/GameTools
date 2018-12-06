import time

from config import logger
from map_anchor import FightMap
from blhx import AzurLaneControl

anchors = [
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


scene_map = {
    "Name": "SP地图",
    "Compare": [{"Rect": (1070, 670, 1260, 730), "Name": "作战补给.png", "TreshHold": 7}],
    "Actions": [
        {"Type": "Click", "Target": (630, 370, 680, 420)},
        {"Type": "Wait", "Time": 0.5},
        {"Type": "InnerCall", "Target": "reset_fight_index"}
    ]
}


class SP4Control(AzurLaneControl):
    def __init__(self):
        AzurLaneControl.__init__(self)
        self.scene_list.append(scene_map)
        self.map = FightMap(self.hwnd, anchors)

    def reset_fight_index(self):
        fight_idx = self.get_fight_index()
        mod = fight_idx % 6
        if mod != 0:
            self.set_fight_index(fight_idx+mod)
            logger.warning("Reset Fight Index From %d To %d", fight_idx, fight_idx+mod)

    def fight(self):
        fight_idx = self.get_fight_index()
        logger.info("Fight index: %d", fight_idx)
        fight_idx = fight_idx % 6
        if fight_idx == 0:
            logger.info("触发扫描")
            self.map.click_at_map("E6")
            # click_at(645, 460, hwnd)
            time.sleep(10)
            logger.info("前往待命")
            self.map.click_at_map("E4")
            # click_at(645, 280, hwnd)
            time.sleep(4)
            logger.info("切换2队")
            self.toggle_fleet()
            time.sleep(2)
            # reset_map_pos()
            # time.sleep(2)
            logger.info("左边精英-D4")
            self.map.click_at_map("D4")
            # click_at(535, 300, hwnd)
            # self.set_fight_index(1)
            time.sleep(6)
        elif fight_idx == 1:
            # reset_map_pos()
            logger.info("左边小舰队-C5")
            self.map.click_at_map("C5")
            # click_at(400, 390, hwnd)
            # self.set_fight_index(2)
            time.sleep(2)
        elif fight_idx == 2:
            # reset_map_pos()
            logger.info("上边小舰队-E3")
            self.map.click_at_map("E3")
            # click_at(665, 210, hwnd)
            # self.set_fight_index(3)
            time.sleep(4)
        elif fight_idx == 3:
            # reset_map_pos()
            logger.info("右边精英-F4")
            self.map.click_at_map("F4")
            # click_at(790, 300, hwnd)
            # self.set_fight_index(4)
            time.sleep(2)
        elif fight_idx == 4:
            # reset_map_pos()
            logger.info("右边小舰队-G5")
            self.map.click_at_map("G5")
            # click_at(925, 400, hwnd)
            # self.set_fight_index(5)
            time.sleep(2)
        elif fight_idx == 5:
            logger.info("切换1队")
            self.toggle_fleet()
            time.sleep(2)
            # reset_map_pos()
            logger.info("Boss-E1")
            self.map.click_at_map("E1")
            # click_at(655, 80, hwnd)
            # self.set_fight_index(0)
            time.sleep(2)
        time.sleep(2)


if __name__ == "__main__":
    sp4 = SP4Control()
    while True:
        sp4.check_scene()
