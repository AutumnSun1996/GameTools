"""
碧蓝航线通用功能

By AutumnSun
"""
import os
import time
import json
import traceback
from collections import deque

import ctypes
import win32con
import win32api

from config import logger, config
from image_tools import get_window_shot, update_resource, cv_crop, get_diff, get_match, cv_save
from win32_tools import drag, rand_click, click_at, get_window_hwnd, make_foreground, heartbeat


class AzurLaneControl:
    def __init__(self):
        self.hwnd = get_window_hwnd(config.get("Path", "WindowTitle"))
        self.fallback_scene = {
            "Name": "无匹配场景",
            "Compare": [],
            "Actions": [{"Type": "Wait", "Time": 1}, ]
        }
        self.scene_history = deque(maxlen=10)
        self.last_check = 0
        with open(config.get("Path", "Scenes"), "r", -1, "UTF-8") as fl:
            self.scenes = json.load(fl)
        with open(config.get("Path", "Resources"), "r", -1, "UTF-8") as fl:
            self.resources = json.load(fl)
        self.global_scenes = set()
        folder = config.get("Path", "ResourcesFolder")
        for val in self.resources.values():
            update_resource(val, folder)
            if val.get("Global"):
                self.global_scenes.add(val["Name"])
        
            
    
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

    def resource_in_screen(self, name, image=None):
        if image is None:
            image = get_window_shot(self.hwnd)
        if name not in self.resources:
            logger.warning("No resource: %s", name)
            return False
        info = self.resources[name]
        if info["Type"] == "Static":
            rect = self.get_resource_rect(name)
            target = info['ImageData']
            cropped = cv_crop(image, rect)
            diff = get_diff(target, cropped)
            # 有位置限制, 可以使用较为宽松的阈值
            res = diff <= info.get('MaxDiff', 0.06)
        elif info["Type"] in {"Dynamic", "Anchor"}:
            target = info['ImageData']
            diff, res = get_match(image, target)
            if diff <= info.get('MaxDiff', 0.02):
                res = False
        return res
    
    def wait_resource(self, name, interval=1, repeat=5):
        if repeat == 0:
            self.error("Can't find resource %s" % name)
            return False
        if self.resource_in_screen(name):
            return True
        else:
            time.sleep(interval)
            return self.wait_resource(name, interval, repeat-1)
    
    def click_at_resource(self, name, wait=False):
        if wait:
            if not self.wait_resource(name):
                return
        rect = self.get_resource_rect(name)
        rand_click(self.hwnd, rect)

    def scene_match_check(self, scene, image):
        # logger.debug("Check scene: %s", scene)
        res = self.parse_condition(scene["Condition"], image)
        if res:
            self.scene_history.append(scene)
        return res
    
    def parse_condition(self, condition, image):
        if isinstance(condition, str):
            return self.resource_in_screen(condition, image)
        elif condition[0] == "All":
            for sub_cond in condition[1:]:
                if not self.parse_condition(sub_cond, image):
                    return False
            return True
        elif condition[0] == "Any":
            for sub_cond in condition[1:]:
                if self.parse_condition(sub_cond, image):
                    return True
            return False
        elif condition[0] == "Not":
            return not self.parse_condition(condition[1], image)
        else:
            raise ValueError("Invalid Condition: %s", condition)

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

    def mood_detect(self):
        if self.current_scene['Name'] == "舰队选择":
            colors = [
                # ("黄", self.error),
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
        image = get_window_shot(self.hwnd)

        targets = []
        blue = self.resources["退役-蓝色舰娘"]
        white = self.resources["退役-白色舰娘"]
        for item in [blue, white]:
            w, h = item["Size"]
            dx, dy = item["Offset"]
            for pos in item["Positions"]:
                x, y = pos
                ship = cv_crop(image, (x, y, x+w, y+h))
                diff = get_diff(ship, item["ImageData"])
                logger.debug("Ship %s: %s %.3f", pos, diff < 0.02, diff)
                if diff < 0.02:
                    targets.append((x+dx, y+dy))
                if len(targets) >= 10:
                    return targets[:10]
        logger.info("select_ships: %s", targets)
        if not targets:
            import datetime
            now = datetime.datetime.now()
            name = "noShipForRetire-{:%Y-%m-%d_%H%M%S}.png".format(now)
            cv_save(name, image)
        return targets[:10]

    def retire(self):
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
            for x, y in targets:
                rand_click(self.hwnd, (x-10, y-10, x+10, y+10))
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

    def update_current_scene(self, candidates=None):
        if candidates is None:
            candidates = list(self.scenes.keys())
        else:
            candidates = set(candidates)
            candidates.update(self.global_scenes)
        
        image = get_window_shot(self.hwnd)
        for key in candidates:
            scene = self.scenes[key]
            passed = self.scene_match_check(scene, image)
            
            logger.debug("Check Scene %s: %s=%s", scene["Name"], scene["Condition"], passed)
            if passed:
                return scene

        self.scene_history.append(self.fallback_scene)
        return self.fallback_scene
    
    def wait_for_scene(self, candidates, interval=1, repeat=5):
        if repeat == 0:
            raise ValueError("场景判断失败! 上一场景: %s" % self.current_scene)
        image = get_window_shot(self.hwnd)
        for key in candidates:
            scene = self.scenes[key]
            if self.scene_match_check(scene, image):
                return scene
        
        for key in self.global_scenes:
            if self.scene_match_check(scene, image):
                return scene
        
        time.sleep(interval)
        return self.wait_for_scene(candidates, interval, repeat-1)
        
    def get_resource_rect(self, key):
        x, y = self.resources[key]["Offset"]
        w, h = self.resources[key]["Size"]
        return (x, y, x+w, y+h)
        
    def check_scene(self):
        scene = self.update_current_scene()
        heartbeat()
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
                except:
                    self.critical(traceback.format_exc(), "程序")
            elif action['Type'] == 'Click':
                self.click_at_resource(action['Target'], action.get("Wait", False))
            else:
                raise TypeError("Invalid Type %s" % action["Type"])


if __name__ == "__main__":
    logger.setLevel("DEBUG")
    controler = AzurLaneControl()
    print(controler.update_current_scene())
    # print(controler.select_ships())
    # print(controler.retire())
