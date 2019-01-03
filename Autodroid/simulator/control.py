"""
模拟器通用功能

By AutumnSun
"""
import ctypes
import time
import datetime
import json
import traceback
from collections import deque
from threading import Timer

import numpy as np
import win32con
import win32api

from config_loader import logger, config
from .image_tools import get_window_shot, cv_crop, get_diff, get_match, get_multi_match, get_all_match, \
    cv_save, load_scenes, load_resources, load_image
from .win32_tools import rand_click, get_window_hwnd, make_foreground, heartbeat


def parse_condition(cond, obj, extra=None):
    """通用条件解析"""
    logger.debug("Parse: %s", cond)
    use_extra = False
    if isinstance(cond, list) and cond:
        # 仅对非空的list进行解析
        if cond[0] in {"$sum", "$all", "$any", "$max", "$min"}:
            cmd = eval(cond[0][1:])
            cond = cmd((parse_condition(sub, obj, extra) for sub in cond[1:]))
        elif cond[0] in {"$chr", "$bool", "$int", "$float", "$ord", "$len", "$abs"}:
            cmd = eval(cond[0][1:])
            cond = cmd(parse_condition(cond[1], obj, extra))
        elif cond[0] in {"$eq", "$gt", "$ge", "$ne", "$lt", "$le", "$add", "$sub", "$mul", "$truediv", "$mod", "$divmod"}:
            cmd = getattr(parse_condition(cond[1], obj, extra), "__%s__" % cond[0][1:])
            cond = cmd(parse_condition(cond[2], obj, extra))
        elif cond[0] == "$not":
            cond = not parse_condition(cond[1], obj, extra)
        elif cond[0] == "$attr":
            key = parse_condition(cond[-1], obj, extra)
            if len(cond) == 2:
                cond = getattr(obj, key)
            else:
                cond = getattr(parse_condition(cond[1], obj, extra), key)
        elif cond[0] == "$val":
            key = parse_condition(cond[-1], obj, extra)
            if len(cond) == 2:
                cond = obj[key]
            else:
                cond = parse_condition(cond[1], obj, extra)[key]
        else:
            use_extra = True
    else:
        use_extra = True
    if extra and use_extra:
        logger.debug("ExtraParse: %s", cond)
        cond = extra(cond)
    logger.debug("ParseResult: %s", cond)
    return cond


class SimulatorControl:
    """模拟器通用控制
    """
    fallback_scene = {
        "Name": "无匹配场景",
        "Condition": True,
        "Actions": [{"Type": "Wait", "Time": 1}]
    }
    section = None

    def __init__(self):
        self.hwnd = get_window_hwnd(config.get(self.section, "WindowTitle"))
        self.scene_history = deque(maxlen=10)
        self.last_change = time.time()
        self.screen = None
        self.scenes = load_scenes(self.section)
        self.resources = load_resources(self.section)

    @property
    def last_scene(self):
        """上一次检测出的场景"""
        if len(self.scene_history) < 2:
            return None
        return self.scene_history[-2]

    @property
    def current_scene(self):
        """最近检测出的场景"""
        if not self.scene_history:
            self.scene_history.append(self.fallback_scene)
        return self.scene_history[-1]

    def make_screen_shot(self):
        """获取窗口截图"""
        self.screen = get_window_shot(self.hwnd)
        return self.screen

    def resource_in_image(self, image, name):
        """判断资源是否存在于画面内

        未找到时返回False. 找到时根据资源类型, 返回不同的结果.
        """
        if name not in self.resources:
            logger.warning("No resource: %s", name)
            return False, []
        info = self.resources[name]
        if info.get("ImageData") is None:
            self.error("No ImageData for %s" % info)
            return False, []

        if info["Type"] == "Static":
            rect = self.get_resource_rect(name)
            target = info['ImageData']
            cropped = cv_crop(image, rect)
            diff = get_diff(cropped, target)
            # 有位置限制, 可以使用较为宽松的阈值
            ret = diff <= info.get('MaxDiff', 0.06)
            if ret:
                pos = rect[:2]
            else:
                pos = []
        elif info["Type"] in {"Dynamic", "Anchor"}:
            target = info['ImageData']
            diff, pos = get_match(image, target)
            if diff > info.get('MaxDiff', 0.02):
                ret = False
                pos = []
            else:
                ret = True
        elif info["Type"] == "MultiStatic":
            target = info['ImageData']
            w, h = info["Size"]
            pos = []
            ret = False
            for x, y in info["Positions"]:
                cropped = cv_crop(image, (x, y, x+w, y+h))
                diff = get_diff(cropped, target)
                if diff <= info.get('MaxDiff', 0.03):
                    pos.append((x, y))
                    ret = True
        elif info["Type"] == "MultiDynamic":
            target = info['ImageData']
            if "SearchArea" in info:
                xy, wh = info["SearchArea"]
                x, y = xy
                w, h = wh
                part = cv_crop(image, (x, y, x+w, y+h))
            else:
                x = y = 0
                part = image
            pos = get_multi_match(part, target, info.get("MaxDiff", 0.02))
            ret = len(pos) > 0
        else:
            self.critical("Invalid Type %s", info['Type'])
        logger.debug("Check Resource: %s=%s", name, pos)
        return ret, pos

    def search_resource(self, name):
        """判断资源是否存在于画面内

        未找到时返回False. 找到时根据资源类型, 返回不同的结果.
        """
        return self.resource_in_image(self.screen, name)

    def resource_in_screen(self, name):
        """判断资源是否存在于画面内. 仅返回bool判断
        """
        return self.search_resource(name)[0]

    def wait(self, dt):
        """等待固定时间

        """
        # TODO: 加入随机延时
        time.sleep(dt)

    def wait_resource(self, name, interval=1, repeat=5):
        """等待资源出现在画面内"""
        if repeat < 0:
            self.error("Can't find resource %s" % name)
            return False
        self.make_screen_shot()
        if self.resource_in_screen(name):
            return True
        self.wait(interval)
        return self.wait_resource(name, interval, repeat-1)

    def click_at_resource(self, name, wait=False):
        """点击资源

        wait 为等待资源出现的时间
        """
        if wait:
            if not self.wait_resource(name, 1, wait):
                return
        res = self.resources[name]
        logger.info("Click at <%s> resource: %s", res["Type"], name)
        if res['Type'] == 'Static':
            rect = self.get_resource_rect(name)
            rand_click(self.hwnd, rect)
        elif res['Type'] == 'Dynamic':
            _, pos = self.search_resource(name)
            x, y = pos
            dx, dy = res.get("ClickOffset", res.get("Offset", (0, 0)))
            cw, ch = res.get("ClickSize", res["Size"])
            rand_click(self.hwnd, (x+dx, y+dy, x+dx+cw, y+dy+ch))
        else:
            self.error("Want to click at <%s> resource: %s", res["Type"], name)

    def crop_resource(self, name, offset=None, image=None):
        """截取资源所在位置的当前截图"""
        if offset is None:
            dx, dy = 0, 0
        else:
            dx, dy = offset
        if image is None:
            image = self.screen
        res = self.resources[name]
        x, y = res.get("CropOffset", res.get("Offset", (0, 0)))
        w, h = res.get("CropSize", res["Size"])
        return cv_crop(image, (x+dx, y+dy, x+w+dx, y+h+dy))

    def wait_till(self, condition, interval=1, repeat=5):
        """等待画面满足给定条件"""
        if repeat < 0:
            self.error("Can't find resource %s" % condition)
            return False
        self.make_screen_shot()
        if parse_condition(condition, None, self.resource_in_screen):
            return True
        time.sleep(interval)
        return self.wait_till(condition, interval, repeat-1)

    def wait_till_scene(self, name, interval=1, repeat=5):
        """等待给定场景"""
        condition = self.scenes[name]["Condition"]
        return self.wait_till(condition, interval, repeat-1)

    def scene_match_check(self, scene, reshot):
        """检查场景是否与画面一致
        """
        logger.debug("Check scene: %s", scene)
        if reshot:
            self.make_screen_shot()

        res = parse_condition(scene["Condition"], self, self.resource_in_screen)
        if res:
            logger.debug("Scene Matched: %s", scene)
            self.scene_history.append(scene)
        return res

    def go_top(self):
        """使模拟器窗口前置"""
        make_foreground(self.hwnd)

    def save_record(self, prefix=None, area=None):
        if prefix is None:
            prefix = "Shot"
        if area is None:
            image = self.screen
        else:
            image = self.crop_resource(area)
            prefix += '-%s' % area
        name = "logs/{}-{:%Y-%m-%d_%H%M%S}.png".format(prefix, datetime.datetime.now())
        cv_save(name, image)

    def critical(self, message=None, title="", action=None):
        """致命错误提醒"""
        logger.critical(message)
        self.save_record("Critical")

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
        self.save_record("Error")

        info = "等待手动指令:\n%s\n是否忽略并%s？" % (message, action)
        flag = win32con.MB_ICONINFORMATION | win32con.MB_YESNO | win32con.MB_TOPMOST \
            | win32con.MB_SETFOREGROUND | win32con.MB_SYSTEMMODAL | win32con.MB_DEFBUTTON2
        title = "碧蓝航线自动脚本 - %s警告" % title
        res = win32api.MessageBox(0, info, title, flag)
        if res == win32con.IDNO:
            self.go_top()
            exit(0)

    def wait_mannual(self, message=None, title="", action="继续"):
        """等待手动操作"""
        logger.info("等待手动操作: %s", message)

        info = "等待手动指令:\n%s" % message
        flag = win32con.MB_ICONINFORMATION | win32con.MB_OK | win32con.MB_TOPMOST \
            | win32con.MB_SETFOREGROUND | win32con.MB_SYSTEMMODAL
        title = "碧蓝航线自动脚本 - 等待手动指令"
        res = win32api.MessageBox(0, info, title, flag)

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

    def update_current_scene_old(self, candidates=None):
        """判断当前场景"""
        if candidates is None:
            if self.current_scene is None or self.current_scene.get("Next") is None:
                candidates = list(self.scenes.keys())
            else:
                candidates = self.current_scene["Next"]
                logger.info("Next for %s: %s", self.current_scene["Name"], candidates)

        self.make_screen_shot()
        for key in candidates:
            scene = self.scenes[key]
            passed = self.scene_match_check(scene, False)

            logger.debug("Check Scene %s: %s=%s", scene["Name"], scene["Condition"], passed)
            if passed:
                return scene

        self.scene_history.append(self.fallback_scene)
        return self.fallback_scene

    def update_current_scene(self, candidates=None, interval=1, repeat=60):
        """等待指定的场景或全局场景"""
        logger.info("update_current_scene(%d) in %s", repeat, candidates)
        if repeat == 0:
            self.error("场景判断失败! 上一场景: %s" % self.current_scene)
            # 若选择忽略错误，则返回“无匹配场景”
            self.scene_history.append(self.fallback_scene)
            return self.fallback_scene

        if candidates is None:
            if self.current_scene is None or self.current_scene.get("Next") is None:
                logger.info("update candidates to full list")
                candidates = list(self.scenes.keys())
            else:
                candidates = self.current_scene["Next"]
                if isinstance(candidates, dict):
                    interval = candidates.get("Interval", interval)
                    repeat = candidates.get("Repeat", repeat)
                    candidates = candidates["Candidates"]
                logger.info("update candidates: Next for %s: %s", self.current_scene["Name"], candidates)

        self.make_screen_shot()
        for key in candidates:
            if isinstance(key, (list, tuple)):
                if key[0] == "History":
                    if len(self.scene_history) > key[1]:
                        scene = self.scene_history[-key[1]-1]
                    else:
                        logger.warning("Ignore %s for len(history)=%d", key, len(self.scene_history))
                        continue
                else:
                    self.error("Invalid Scene %s", key)
                    continue
            else:
                scene = self.scenes[key]
            if self.scene_match_check(scene, False):
                return scene

        for key in self.scenes:
            scene = self.scenes[key]
            if scene.get("Global"):
                if self.scene_match_check(scene, False):
                    return scene

        self.wait(interval)
        return self.update_current_scene(candidates, interval, repeat-1)

    def get_resource_rect(self, key):
        """获取资源的bbox"""
        x, y = self.resources[key]["Offset"]
        w, h = self.resources[key]["Size"]
        return (x, y, x+w, y+h)

    def do_actions(self, actions):
        """执行指定的操作"""
        for action in actions:
            if action.get('FirstOnly') and self.last_scene == self.current_scene:
                continue

            if "Condition" in action and not parse_condition(action["Condition"], self):
                continue

            if action['Type'] == 'Wait':
                self.wait(action['Time'])
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
            else:
                self.critical("Invalid Type %s" % action["Type"])

    @property
    def since_last_change(self):
        """返回从上次场景变化到当前时间的秒数"""
        return time.time() - self.last_change

    def check_scene(self):
        """判断当前场景, 执行对应的操作"""
        scene = self.update_current_scene()
        heartbeat()
        now = time.time()
        if self.last_scene != scene:
            nochange = ""
            self.last_change = now
        else:
            nochange = "(No Change)"

        logger.info("%s - %s%s", scene['Name'], scene['Actions'], nochange)
        self.do_actions(scene['Actions'])


if __name__ == "__main__":
    logger.setLevel("DEBUG")
    controler = SimulatorControl()
    print(controler.update_current_scene())
    # print(controler.select_ships())
    # print(controler.retire())
