import os
import time

import numpy as np

from config import logger
from image_tools import get_window_shot, cv_imread, cv_crop, get_diff, get_match
from win32_tools import drag, rand_click, click_at, get_window_hwnd, make_foreground

scene_list = [
    {
        "Name": "船坞已满",
        "Compare": [
            {"Rect": (310, 200, 900, 550),
                "Name": "船坞已满.png", "TreshHold": 5}
        ], "Actions": [
            # {"Type": "Call", "Target": go_top, "FirstOnly": True},
            {"Type": "Click", "Target": (400, 500, 580, 550)},
            {"Type": "Wait", "Time": 2},
            {"Type": "InnerCall", "Target": "retire"}
        ]
    },
    {
        "Name": "非自律战斗中",
        "Compare": [{"Rect": (83, 56, 235, 106), "Name": "开始自律.png", "TreshHold": 5}],
        "Actions": [
            {"Type": "Click", "Target": (83, 56, 235, 106)},
            {"Type": "Wait", "Time": 0.5},
            {"Type": "Click", "Target": (1100, 200, 1200, 550)},
            {"Type": "Wait", "Time": 1},
        ]
    },
    {
        "Name": "潜艇未出击",
        "Compare": [
            {"Rect": (610, 570, 740, 715),
                "Name": "潜艇未出击.png", "TreshHold": 5},
            {"Rect": (665, 676, 684, 714),
                "Name": "潜艇数量1.png", "TreshHold": 1},
        ], "Actions": [{"Type": "Wait", "Time": 15, "FirstOnly": True}, {"Type": "Click", "Target": (630, 600, 720, 680)}, {"Type": "Wait", "Time": 0.5}, ]
    },
    {
        "Name": "战斗准备",
        "Compare": [{"Rect": (920, 610, 1200, 720), "Name": "出击.png", "TreshHold": 5}],
        "Actions": [
            {"Type": "InnerCall", "Target": "face_detect"},
            {"Type": "Click", "Target": (920, 610, 1200, 720)},
            {"Type": "Wait", "Time": 1},
        ]
    },
    {
        "Name": "S胜",
        "Compare": [{"Rect": (320, 300, 980, 420), "Name": "S胜.png", "TreshHold": 5}],
        "Actions": [{"Type": "Click", "Target": (920, 610, 1200, 720)}, {"Type": "Wait", "Time": 0.5}, ]
    },
    {
        "Name": "A胜",
        "Compare": [{"Rect": (320, 300, 980, 420), "Name": "A胜.png", "TreshHold": 5}],
        "Actions": [{"Type": "Click", "Target": (920, 610, 1200, 720)}, {"Type": "Wait", "Time": 0.5}, ]
    },
    {
        "Name": "点击继续",
        "Compare": [{"Rect": (280, 540, 1000, 600), "Name": "点击继续.png", "TreshHold": 5}],
        "Actions": [{"Type": "Click", "Target": (920, 610, 1200, 720)}, {"Type": "Wait", "Time": 0.5}, ]
    },
    {
        "Name": "获得舰娘",
        "Compare": [{"Rect": (989, 590, 1055, 654), "Name": "性能.png", "TreshHold": 5}],
        "Actions": [{"Type": "Click", "Target": (1100, 500, 1200, 700)}, {"Type": "Wait", "Time": 0.5}, ]
    },
    {
        "Name": "获得道具",
        "Compare": [{"Rect": (500, 120, 800, 240), "Name": "获得道具.png", "TreshHold": 10}],
        "Actions": [{"Type": "Click", "Target": (920, 610, 1200, 720)}, {"Type": "Wait", "Time": 0.5}, ]
    },
    {
        "Name": "确认经验",
        "Compare": [{"Rect": (760, 600, 1280, 680), "Name": "确认经验.png", "TreshHold": 5}],
        "Actions": [
            {"Type": "Click", "Target": (1020, 610, 1200, 670)},
            {"Type": "Wait", "Time": 3},
        ]
    },
    {
        "Name": "获得经验-S胜",
        "Compare": [{"Rect": (40, 60, 490, 140), "Name": "S胜-左上角.png", "TreshHold": 5}],
        "Actions": [{"Type": "Click", "Target": (1020, 610, 1200, 670)}, {"Type": "Wait", "Time": .5}, ]
    },
    {
        "Name": "获得经验-A胜",
        "Compare": [{"Rect": (40, 60, 490, 140), "Name": "A胜-左上角.png", "TreshHold": 5}],
        "Actions": [{"Type": "Click", "Target": (1020, 610, 1200, 670)}, {"Type": "Wait", "Time": .5}, ]
    },
    {
        "Name": "消息",
        "Compare": [
            {"Rect": (310, 200, 950, 250),
                "Name": "信息.png", "TreshHold": 5},
            {"Rect": (310, 480, 950, 580),
                "Name": "确认.png", "TreshHold": 5},
        ],
        "Actions": [{"Type": "Click", "Target": (550, 500, 720, 550)}, {"Type": "Wait", "Time": .5}, ]
    },
    {
        "Name": "进入地图确认",
        "Compare": [{"Rect": (840, 480, 1020, 540), "Name": "立刻前往.png", "TreshHold": 5}],
        "Actions": [{"Type": "Click", "Target": (840, 480, 1020, 540)}, {"Type": "Wait", "Time": .5}, ]
    },
    {
        "Name": "舰队选择",
        "Compare": [{"Rect": (960, 630, 1180, 680), "Name": "立刻前往2.png", "TreshHold": 5}],
        "Actions": [
            {"Type": "Click", "Target": (1000, 630, 1150, 680)},
            {"Type": "Wait", "Time": 4},
        ]
    },
    {
        "Name": "战斗地图",
        "Compare": [{"Rect": (840, 670, 1280, 740), "Name": "切换-迎击.png", "TreshHold": 5}],
        "Actions": [
            # {"Type": "Call", "Target": go_top, "FirstOnly": True},
            {"Type": "InnerCall", "Target": "fight"},
            {"Type": "InnerCall", "Target": "inc_fight_index"},
            {"Type": "Wait", "Time": 2},
        ]
    },
]


class AzurLaneControl:
    def __init__(self):
        self.hwnd = get_window_hwnd("夜神模拟器")
        self.scene_list = scene_list
        self.last_scene = None

    @staticmethod
    def get_fight_index():
        with open('fightIndex.txt', 'r') as fl:
            fight_idx = int(fl.read())
        return fight_idx

    @staticmethod
    def inc_fight_index():
        with open('fightIndex.txt', 'r') as fl:
            fight_idx = int(fl.read())
        logger.debug("增加Fight Index: %d -> %d", fight_idx, fight_idx+1)
        with open('fightIndex.txt', 'w') as fl:
            fl.write("%d" % (fight_idx + 1))

    @staticmethod
    def set_fight_index(index=0):
        with open('fightIndex.txt', 'w') as fl:
            fl.write("%d" % index)

    @staticmethod
    def scene_match_check(scene, image):
        for info in scene['Compare']:
            a = cv_imread(os.path.join('images', info['Name']))
            b = cv_crop(image, info['Rect'])
            diff = get_diff(a, b) * 50
            if diff > info['TreshHold']:
                return False
        return True

    def toggle_fleet(self):
        click_at(self.hwnd, 950, 700)

    def fight(self):
        raise NotImplementedError()

    def go_top(self):
        make_foreground(self.hwnd)

    def critical(self, message):
        self.go_top()
        info = "需要手动操作: (%s)" % message
        logger.critical(info)
        input(info)

    def warning(self, message):
        # self.go_top()
        info = "出现异常情况: (%s)" % message
        logger.warning(info)
        # input(info)

    def face_detect(self):
        # 使可能存在的消息消失
        rand_click(self.hwnd, (20, 280, 80, 450))
        time.sleep(2)

        image = get_window_shot(self.hwnd)
        diff, pos = get_match(image, cv_imread("images/face-yellow.png"))
        if diff < 0.02:
            self.warning("舰娘心情值低(黄脸)")

        diff, pos = get_match(image, cv_imread("images/face-red.png"))
        if diff < 0.02:
            self.critical("舰娘心情值低(红脸)")

    def select_ships(self):
        image = get_window_shot(self.hwnd)
        targets = []
        rare = cv_imread("images/rare.png")
        common = cv_imread("images/common.png")
        h, w = rare.shape[:2]
        for y in [426, 194]:
            for i in range(7):
                x = 148 + 170 * i
                ship = cv_crop(image, (x, y, x+w, y+h))
                for needle in [rare, common]:
                    if get_diff(ship, needle) < 0.015:
                        targets.append((x-38, y+106))
                        break
                if len(targets) >= 10:
                    return targets[:10]
        return targets[:10]

    def retire(self):
        logger.debug("滑动到最后一页")
        drag(self.hwnd, (1250, 180), (1250, 1000))
        time.sleep(0.3)
        drag(self.hwnd, (1250, 500), (1250, 1000))
        time.sleep(1)
        waiting = 1
        targets = self.select_ships()
        if len(targets) == 0:
            self.critical("自动退役失败")
        while targets:
            logger.debug("退役舰娘*%d", len(targets))
            for x, y in targets:
                rand_click(self.hwnd, (x-10, y-10, x+10, y+10))
                time.sleep(0.3)

            logger.debug("确定")
            rand_click(self.hwnd, (1020, 680, 1210, 730))
            time.sleep(waiting)
            logger.debug("确认退役")
            rand_click(self.hwnd, (920, 630, 1100, 670))
            time.sleep(waiting)
            logger.debug("点击继续")
            rand_click(self.hwnd, (920, 630, 1100, 670))
            time.sleep(waiting)
            logger.debug("装备拆解")
            rand_click(self.hwnd, (920, 630, 1100, 670))
            time.sleep(waiting)
            logger.debug("确认拆解")
            rand_click(self.hwnd, (680, 500, 860, 550))
            time.sleep(waiting)
            logger.debug("点击继续")
            rand_click(self.hwnd, (680, 500, 860, 550))
            time.sleep(waiting*2)
            targets = self.select_ships()

        time.sleep(waiting)
        logger.debug("返回之前界面")
        rand_click(self.hwnd, (830, 680, 980, 730))
        time.sleep(3)

    def get_current_scene(self):
        image = get_window_shot(self.hwnd)
        for scene in self.scene_list:
            passed = self.scene_match_check(scene, image)
            if passed:
                return scene
        return {
            "Name": "无匹配场景",
            "Compare": [],
            "Actions": [{"Type": "Wait", "Time": 1}, ]
        }

    def check_scene(self):
        scene = self.get_current_scene()

        if self.last_scene == scene:
            nochange = "(Not change)"
        else:
            nochange = ""

        logger.info("%s - %s %s" % (scene['Name'], scene['Actions'], nochange))

        for action in scene['Actions']:
            if action.get('FirstOnly') and self.last_scene == scene:
                continue

            if action['Type'] == 'Wait':
                time.sleep(action['Time'])
            elif action['Type'] == 'InnerCall':
                target = getattr(self, action['Target'])
                target()
            elif action['Type'] == 'Click':
                rand_click(self.hwnd, action['Target'])
            else:
                raise TypeError("Invalid Type %s" % action["Type"])
        self.last_scene = scene


if __name__ == "__main__":
    control = AzurLaneControl()
    print(control.select_ships())
