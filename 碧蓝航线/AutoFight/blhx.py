"""
碧蓝航线通用功能

By AutumnSun
"""
import os
import time
from collections import deque

import ctypes
import win32con
import win32api

from config import logger
from image_tools import get_window_shot, cv_imread, cv_crop, get_diff, get_match
from win32_tools import drag, rand_click, click_at, get_window_hwnd, make_foreground

SCENE_LIST = [
    {
        "Name": "船坞已满",
        "Compare": [
            {"Rect": (310, 200, 900, 550), "Name": "船坞已满.png", "TreshHold": 5}
        ], "Actions": [
            # {"Type": "Call", "Target": go_top, "FirstOnly": True},
            {"Type": "Click", "Target": (400, 500, 580, 550)},
            {"Type": "Wait", "Time": 2},
            {"Type": "InnerCall", "Target": "retire"}
        ]
    },
    {
        "Name": "非自律战斗中",
        "Compare": [
            {"Rect": (83, 56, 235, 106), "Name": "开始自律.png", "TreshHold": 5}
        ],
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
        ],
        "Actions": [
            {"Type": "Wait", "Time": 15, "FirstOnly": True},
            {"Type": "Click", "Target": (630, 600, 720, 680)},
            {"Type": "Wait", "Time": 0.5},
        ]
    },
    {
        "Name": "战斗准备",
        "Compare": [
            {"Rect": (920, 610, 1200, 720), "Name": "出击.png", "TreshHold": 5}
        ],
        "Actions": [
            # 使可能存在的消息消失
            {"Type": "Click", "Target": (20, 280, 80, 450)},
            {"Type": "Wait", "Time": 2},
            # 心情检测
            {"Type": "InnerCall", "Target": "mood_detect"},
            {"Type": "Click", "Target": (920, 610, 1200, 720)},
            {"Type": "Wait", "Time": 1},
        ]
    },
    {
        "Name": "S胜",
        "Compare": [{"Rect": (320, 300, 980, 420), "Name": "S胜.png", "TreshHold": 5}],
        "Actions": [
            {"Type": "Click", "Target": (920, 610, 1200, 720)},
            {"Type": "Wait", "Time": 0.5},
        ]
    },
    {
        "Name": "A胜",
        "Compare": [{"Rect": (320, 300, 980, 420), "Name": "A胜.png", "TreshHold": 5}],
        "Actions": [
            {"Type": "Click", "Target": (920, 610, 1200, 720)},
            {"Type": "InnerCall", "Target": "notice", "kwargs": {"message": "A胜提醒"}},
            {"Type": "Wait", "Time": 0.5},
        ]
    },
    # {
    #     "Name": "点击继续",
    #     "Compare": [{"Rect": (280, 540, 1000, 600), "Name": "点击继续.png", "TreshHold": 5}],
    #     "Actions": [
    #         {"Type": "Click", "Target": (920, 610, 1200, 720)},
    #         {"Type": "Wait", "Time": 0.5},
    #     ]
    # },
    {
        "Name": "获得舰娘",
        "Compare": [{"Rect": (989, 590, 1055, 654), "Name": "性能.png", "TreshHold": 5}],
        "Actions": [{"Type": "Click", "Target": (1100, 500, 1200, 700)}, {"Type": "Wait", "Time": 0.5}, ]
    },
    {
        "Name": "获得道具",
        "Compare": [{"Rect": (500, 120, 800, 240), "Name": "获得道具.png", "TreshHold": 10}],
        "Actions": [
            {"Type": "Click", "Target": (920, 610, 1200, 720)},
            {"Type": "Wait", "Time": 1},
        ]
    },
    {
        "Name": "确认经验",
        "Compare": [{"Rect": (760, 600, 1280, 680), "Name": "确认经验.png", "TreshHold": 5}],
        "Actions": [
            {"Type": "Click", "Target": (1020, 610, 1200, 670)},
            {"Type": "InnerCall", "Target": "inc_fight_index", "FirstOnly": True},
            {"Type": "Wait", "Time": 5},
        ]
    },
    {
        "Name": "获得经验-S胜",
        "Compare": [{"Rect": (40, 60, 490, 140), "Name": "S胜-左上角.png", "TreshHold": 5}],
        "Actions": [
            # 点击右边空白区域
            {"Type": "Click", "Target": (1150, 200, 1250, 400)},
            {"Type": "Wait", "Time": 0.5},
        ]
    },
    {
        "Name": "获得经验-A胜",
        "Compare": [{"Rect": (40, 60, 490, 140), "Name": "A胜-左上角.png", "TreshHold": 5}],
        "Actions": [
            # 点击右边空白区域
            {"Type": "Click", "Target": (1150, 200, 1250, 400)},
            {"Type": "Wait", "Time": 0.5},
        ]
    },
    {
        "Name": "消息",
        "Compare": [
            {"Rect": (310, 200, 950, 250), "Name": "信息.png", "TreshHold": 5},
            {"Rect": (310, 480, 950, 580), "Name": "确认.png", "TreshHold": 5},
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
            # 心情检测
            {"Type": "InnerCall", "Target": "mood_detect"},
            # {"Type": "InnerCall", "Target": "critical"},
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
            {"Type": "Wait", "Time": 2},
        ]
    },
]


class AzurLaneControl:
    def __init__(self):
        self.hwnd = get_window_hwnd("夜神模拟器")
        self.scene_list = SCENE_LIST
        self.fallback_scene = {
            "Name": "无匹配场景",
            "Compare": [],
            "Actions": [{"Type": "Wait", "Time": 1}, ]
        }
        self.scene_history = deque(maxlen=10)
        self.last_check = 0
    
    @property
    def last_scene(self):
        if len(self.scene_history) < 2:
            return self.fallback_scene
        return self.scene_history[-2]
        
    @property
    def current_scene(self):
        if not self.scene_history:
            return self.fallback_scene
        return self.scene_history[-1]

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
            passed = diff <= info['TreshHold']
            logger.debug("Scene Check %s=%s: %.3f-%.2f %s", scene["Name"], passed,
                         diff,  info['TreshHold'], info['Name'])
            if not passed:
                return False
        return True

    def toggle_fleet(self):
        click_at(self.hwnd, 950, 700)
        time.sleep(2)

    def fight(self):
        raise NotImplementedError()

    def go_top(self):
        make_foreground(self.hwnd)

    def critical(self, message=None, title="", action=None):
        logger.critical(message)
        info = "自动战斗脚本将终止:\n%s\n是否将模拟器前置？" % message
        flag = win32con.MB_ICONERROR | win32con.MB_YESNO | win32con.MB_TOPMOST | win32con.MB_SETFOREGROUND | win32con.MB_SYSTEMMODAL
        title = "碧蓝航线自动脚本 - %s错误" % title
        res = win32api.MessageBox(0, info, title, flag)
        if res == win32con.IDYES:
            self.go_top()
        exit(0)

    def error(self, message=None, title="", action="继续"):
        logger.error(message)
        info = "等待手动指令:\n%s\n是否忽略并%s？" % (message, action)
        flag = win32con.MB_ICONINFORMATION | win32con.MB_YESNO | win32con.MB_TOPMOST | win32con.MB_SETFOREGROUND | win32con.MB_SYSTEMMODAL | win32con.MB_DEFBUTTON2
        title = "碧蓝航线自动脚本 - %s警告" % title
        res = win32api.MessageBox(0, info, title, flag)
        if res == win32con.IDNO:
            self.go_top()
            exit(0)

    def notice(self, message=None, title="", action="继续"):
        logger.warning(message)
        info = "出现异常情况:\n%s\n是否忽略并%s？" % (message, action)
        flag = win32con.MB_YESNO | win32con.MB_TOPMOST | win32con.MB_SETFOREGROUND
        title = "碧蓝航线自动脚本 - %s提醒" % title
        res = ctypes.windll.user32.MessageBoxTimeoutA(
            0, info.encode("GBK"), title.encode("GBK"), flag, 0, 3000)
        if res == win32con.IDNO:
            self.go_top()
            exit(0)

    def face_detect(self, image, color, size):
        diff, _ = get_match(image, cv_imread(
            "images/face-%s%s.png" % (color, size)))
        return diff < 0.02

    def mood_detect(self):
        image = get_window_shot(self.hwnd)
        if self.current_scene['Name'] == "舰队选择":
            size = "32x32"
            colors = {
                "yellow": self.error
            }
            action = "进入地图"
        elif self.current_scene['Name'] == "战斗准备":
            size = "26x25"
            colors = {
                "red": self.critical,
                "yellow": self.error,
                "green": self.notice
            }
            action = "继续战斗"
        color2mood = {"red": "红", "yellow": "黄", "green": "绿"}
        for color in colors:
            if self.face_detect(image, color, size):
                colors[color]("舰娘心情值低(%s色, %s界面)" % (
                    color2mood[color], self.current_scene['Name']), "舰娘心情值", action)
                # 检测顺序为红黄绿, 因此无需多次检测
                return

    def select_ships(self):
        image = get_window_shot(self.hwnd)

        targets = []
        rare = cv_imread("images/rare.png")
        common = cv_imread("images/common.png")
        h, w = rare.shape[:2]
        for y in [103, 335]:
            for i in range(7):
                x = 148 + 170 * i
                ship = cv_crop(image, (x, y, x+w, y+h))
                for needle in [rare, common]:
                    if get_diff(ship, needle) < 0.03:
                        targets.append((x-38, y+106))
                        break
                if len(targets) >= 10:
                    return targets[:10]
        return targets[:10]

    def retire(self):
        image = get_window_shot(self.hwnd)
        if get_diff(cv_crop(image, (910, 40, 1060, 80)), cv_imread("images/降序.png")) < 0.02:
            logger.debug("切换倒序显示")
            rand_click(self.hwnd, (910, 40, 1060, 80))
            time.sleep(1)
        waiting = 1
        targets = self.select_ships()
        if not targets:
            self.critical("自动退役失败")
        while targets:
            logger.info("退役舰娘*%d", len(targets))
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

    def update_current_scene(self):
        image = get_window_shot(self.hwnd)
        for scene in self.scene_list:
            passed = self.scene_match_check(scene, image)
            if passed:
                self.scene_history.append(scene)
                return scene

        self.scene_history.append(self.fallback_scene)
        return self.current_scene

    def check_scene(self):
        scene = self.update_current_scene()
        now = time.time()
        if self.last_scene != scene or now - self.last_check > 5:
            self.last_check = now
            logger.info("%s - %s", scene['Name'], scene['Actions'])
        else:
            logger.debug("%s - %s", scene['Name'], scene['Actions'])

        for action in scene['Actions']:
            if action.get('FirstOnly') and self.last_scene == scene:
                continue

            if action['Type'] == 'Wait':
                time.sleep(action['Time'])
            elif action['Type'] == 'InnerCall':
                target = getattr(self, action['Target'])
                args = action.get("args", [])
                kwargs = action.get("kwargs", {})
                try:
                    target(*args, **kwargs)
                except Exception as e:
                    self.critical(e, "程序")
            elif action['Type'] == 'Click':
                rand_click(self.hwnd, action['Target'])
            else:
                raise TypeError("Invalid Type %s" % action["Type"])


if __name__ == "__main__":
    logger.setLevel("DEBUG")
    controler = AzurLaneControl()
    print(controler.select_ships())
    print(controler.retire())
