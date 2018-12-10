"""
碧蓝航线通用功能

By AutumnSun
"""
import os
import time
import datetime
import json
import traceback
from collections import deque
from threading import Timer

import ctypes
import win32con
import win32api

from config import logger, config
from image_tools import get_window_shot, update_resource, cv_crop, get_diff, get_match, cv_save
from win32_tools import drag, rand_click, click_at, get_window_hwnd, make_foreground, heartbeat


class AzurLaneControl:
    """模拟器通用控制
    """

    def __init__(self):
        self.hwnd = get_window_hwnd(config.get("Path", "WindowTitle"))
        self.fallback_scene = {
            "Name": "无匹配场景",
            "Compare": [],
            "Actions": [{"Type": "Wait", "Time": 1}, ]
        }
        self.scene_history = deque(maxlen=10)
        self.last_check = 0
        self.screen = None
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
        """上一次检测出的场景"""
        if len(self.scene_history) < 2:
            return self.fallback_scene
        return self.scene_history[-2]

    @property
    def current_scene(self):
        """最近检测出的场景"""
        if not self.scene_history:
            return self.fallback_scene
        return self.scene_history[-1]

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

    def make_screen_shot(self):
        """获取窗口截图"""
        self.screen = get_window_shot(self.hwnd)
        return self.screen

    def resource_in_screen(self, name, reshot=True):
        """判断资源是否存在于画面内"""
        if reshot:
            self.make_screen_shot()
        if name not in self.resources:
            logger.warning("No resource: %s", name)
            return False
        info = self.resources[name]
        if info["Type"] == "Static":
            rect = self.get_resource_rect(name)
            if 'ImageData' not in info:
                self.error("No ImageData for %s" % info)
                return False
            target = info['ImageData']
            cropped = cv_crop(self.screen, rect)
            diff = get_diff(target, cropped)
            # 有位置限制, 可以使用较为宽松的阈值
            res = diff <= info.get('MaxDiff', 0.06)
        elif info["Type"] in {"Dynamic", "Anchor"}:
            target = info['ImageData']
            diff, res = get_match(self.screen, target)
            if diff <= info.get('MaxDiff', 0.02):
                res = False
        return res

    def wait_resource(self, name, interval=1, repeat=5):
        """等待资源出现在画面内"""
        if repeat == 0:
            self.error("Can't find resource %s" % name)
            return False
        if self.resource_in_screen(name):
            return True
        else:
            time.sleep(interval)
            return self.wait_resource(name, interval, repeat-1)

    def delayed_click(self, name, condition=None, delay=None):
        """等待固定时间后点击资源

        condition 不为None时将先检查condition
        """
        if delay:
            Timer(delay, self.delayed_click, [name, condition]).start()
            return
        if condition is not None:
            if not self.parse_condition(condition):
                logger.warning("%s=False, 取消点击%s", condition, name)
                return
        self.click_at_resource(name)

    def click_at_resource(self, name, wait=False):
        """点击资源

        wait 为等待资源出现的时间
        """
        if wait:
            if not self.wait_resource(name, 1, wait):
                return
        rect = self.get_resource_rect(name)
        rand_click(self.hwnd, rect)

    def scene_match_check(self, scene, reshot):
        """检查场景是否与画面一致
        """
        # logger.debug("Check scene: %s", scene)
        res = self.parse_condition(scene["Condition"], reshot)
        if res:
            self.scene_history.append(scene)
        return res

    def parse_condition(self, condition, reshot=True):
        """检查condition是否被满足
        """
        result = False
        if isinstance(condition, str):
            result = self.resource_in_screen(condition, reshot)
        elif not isinstance(condition, (list, tuple)):
            self.error("Invalid Condition: %s" % condition)
        elif condition[0] == "All":
            result = all([self.parse_condition(sub, reshot) for sub in condition[1:]])
        elif condition[0] == "Any":
            result = any([self.parse_condition(sub, reshot) for sub in condition[1:]])
        elif condition[0] == "Not":
            result = not self.parse_condition(condition[1], reshot)
        else:
            self.error("Invalid Condition: %s" % condition)
        return result

    def fight(self):
        """处理战斗内容. 随每个地图变化"""
        raise NotImplementedError()

    def go_top(self):
        """使模拟器窗口前置"""
        make_foreground(self.hwnd)

    def critical(self, message=None, title="", action=None):
        """致命错误提醒"""
        logger.critical(message)
        name = "Critical-{:%Y-%m-%d_%H%M%S}.png".format(datetime.datetime.now())
        cv_save(name, self.screen)

        info = "自动战斗脚本将终止:\n%s\n是否将模拟器前置？" % message
        flag = win32con.MB_ICONERROR | win32con.MB_YESNO | win32con.MB_TOPMOST \
            | win32con.MB_SETFOREGROUND | win32con.MB_SYSTEMMODAL
        title = "碧蓝航线自动脚本 - %s错误" % title
        res = win32api.MessageBox(0, info, title, flag)
        if res == win32con.IDYES:
            self.go_top()
        exit(0)

    def error(self, message=None, title="", action="继续"):
        """错误提醒"""
        logger.error(message)
        name = "Error-{:%Y-%m-%d_%H%M%S}.png".format(datetime.datetime.now())
        cv_save(name, self.screen)

        info = "等待手动指令:\n%s\n是否忽略并%s？" % (message, action)
        flag = win32con.MB_ICONINFORMATION | win32con.MB_YESNO | win32con.MB_TOPMOST \
            | win32con.MB_SETFOREGROUND | win32con.MB_SYSTEMMODAL | win32con.MB_DEFBUTTON2
        title = "碧蓝航线自动脚本 - %s警告" % title
        res = win32api.MessageBox(0, info, title, flag)
        if res == win32con.IDNO:
            self.go_top()
            exit(0)

    def notice(self, message=None, title="", action="继续"):
        """提醒"""
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
        image = get_window_shot(self.hwnd)

        targets = []
        # TODO: 将退役选择放到配置文件或json中
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
            # TODO: 解决偶尔的退役失败
            self.last_shot = image
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
            # TODO: 解决偶尔的退役失败
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
        """判断当前场景"""
        if candidates is None:
            candidates = list(self.scenes.keys())
        else:
            candidates = set(candidates)
            candidates.update(self.global_scenes)

        self.make_screen_shot()
        for key in candidates:
            scene = self.scenes[key]
            passed = self.scene_match_check(scene, False)

            logger.debug("Check Scene %s: %s=%s", scene["Name"], scene["Condition"], passed)
            if passed:
                return scene

        self.scene_history.append(self.fallback_scene)
        return self.fallback_scene

    def wait_for_scene(self, candidates, interval=1, repeat=5):
        """等待指定的场景或全局场景"""
        if repeat == 0:
            self.error("场景判断失败! 上一场景: %s" % self.current_scene)
            return
        self.make_screen_shot()
        for key in candidates:
            scene = self.scenes[key]
            if self.scene_match_check(scene, False):
                return scene

        for key in self.global_scenes:
            if self.scene_match_check(scene, False):
                return scene

        time.sleep(interval)
        return self.wait_for_scene(candidates, interval, repeat-1)

    def get_resource_rect(self, key):
        """获取资源的bbox"""
        x, y = self.resources[key]["Offset"]
        w, h = self.resources[key]["Size"]
        return (x, y, x+w, y+h)

    def check_scene(self):
        """判断当前场景, 执行对应的操作"""
        scene = self.update_current_scene()
        heartbeat()
        now = time.time()
        nochange = "" if self.last_scene != scene else "(No Change)"
        if not nochange or now - self.last_check > 10:
            self.last_check = now
            log = logger.info
        else:
            log = logger.debug
        log("%s - %s%s", scene['Name'], scene['Actions'], nochange)

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
                except Exception:
                    self.critical(traceback.format_exc(), "程序")
            elif action['Type'] == 'Click':
                self.click_at_resource(action['Target'], action.get("Wait", False))
            elif action['Type'] == 'DelayedClick':
                self.delayed_click(action["Target"], action.get("Recheck"), action.get("Delay"))
            else:
                self.critical("Invalid Type %s" % action["Type"])


if __name__ == "__main__":
    logger.setLevel("DEBUG")
    controler = AzurLaneControl()
    print(controler.update_current_scene())
    # print(controler.select_ships())
    # print(controler.retire())
