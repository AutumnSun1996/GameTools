"""
模拟器通用功能

By AutumnSun
"""
import os
import ctypes
import time
import datetime
import traceback
from collections import deque
from threading import Timer
from collections import defaultdict
import operator
import builtins

import numpy as np
import win32con
import win32api

from config_loader import config, set_logging_dir
from .image_tools import get_window_shot, cv_crop, get_diff, get_match, get_multi_match, get_all_match, \
    cv_save, load_scenes, load_resources, load_image, update_resource
from .win32_tools import rand_click, get_window_hwnd, make_foreground, heartbeat

import logging
logger = logging.getLogger(__name__)


def parse_condition(cond, obj, extra=None):
    """通用条件解析"""
    cond_in = str(cond)
    if isinstance(cond, list) and cond:
        cond = [parse_condition(sub, obj, extra) for sub in cond]
        cond_in = cond_in + "=" + str(cond)
        # 仅对非空的list进行解析
        need_extra = False
        if isinstance(cond[0], str) and cond[0].startswith("$"):
            if cond[0] == "$":
                logger.debug("get obj")
                cond = obj
            elif cond[0][1:] in dir(operator):
                cmd = getattr(operator, cond[0][1:])
                # logger.debug("operator %s", cmd)
                cond = cmd(*cond[1:])
            elif cond[0][1:] in dir(builtins):
                cmd = getattr(builtins, cond[0][1:])
                # logger.debug("builtin %s", cmd)
                cond = cmd(*cond[1:])
            elif cond[0] == "$method":
                cmd = getattr(obj, parse_condition(cond[1], obj, extra))
                cond = cmd(*cond[2:])
            elif cond[0] == "$random":
                thresh = parse_condition(cond[1], obj, extra)
                cond = np.random.rand() < thresh
            elif cond[0] == "$call":
                cmd = parse_condition(cond[1], obj, extra)
                cond = cmd(*cond[2:])
            else:
                logger.info("no match: %s", cond[0])
                need_extra = True
        else:
            logger.debug("no $: %s", cond)
            need_extra = True
        if need_extra and extra:
            try:
                cond = extra(*cond)
                logger.debug("ExtraParse: %s %s=%s", extra, cond_in, cond)
            except TypeError:
                pass
    logger.debug("Parse: %s=%s", cond_in, cond)
    return cond


class SimulatorControl:
    """模拟器通用控制
    """
    fallback_scene = {
        "Name": "无匹配场景",
        "Condition": True,
        "Actions": [{"Type": "Wait", "Time": 1}]
    }
    section = "Main"
    scene_check_max_repeat = 5

    def __init__(self):
        self.hwnd = get_window_hwnd(config.get(self.section, "WindowTitle"))
        set_logging_dir(os.path.join(self.section, "logs"))
        self.scene_history = deque(maxlen=50)
        self.scene_history_count = defaultdict(lambda: 0)
        self.last_change = time.time()
        self.screen = None
        self.actions_done = False
        self.scenes = load_scenes(self.section)
        self.resources = load_resources(self.section)
        self.last_manual = 0
        self.stop = False
        self.resource_pos_buffer = {}

    @property
    def since_last_manual(self):
        return time.time() - self.last_manual

    def manual(self):
        if self.scene_changed or self.since_last_manual > 30:
            self.go_top()
            win32api.MessageBeep()
            self.last_manual = time.time()

    @property
    def last_scene(self):
        """上一次检测出的场景"""
        if len(self.scene_history) < 2:
            return None
        return self.scene_history[-2]

    @property
    def last_scene_name(self):
        """上一次检测出的场景名称"""
        if self.last_scene is None:
            return None
        return self.last_scene["Name"]

    @property
    def current_scene(self):
        """最近检测出的场景"""
        if not self.scene_history:
            self.scene_history.append(self.fallback_scene)
        return self.scene_history[-1]

    @property
    def current_scene_name(self):
        """最近检测出的场景名称"""
        return self.current_scene["Name"]

    @property
    def scene_changed(self):
        """最近检测出的场景"""
        return self.current_scene != self.last_scene

    def make_screen_shot(self):
        """获取窗口截图"""
        self.resource_pos_buffer = {}
        self.screen = get_window_shot(self.hwnd)
        return self.screen

    def search_resource(self, info, image=None, index=None):
        """判断资源是否存在于画面内

        返回 found, pos
        found: 是否找到
        pos: 找到目标的左上角坐标
        """
        if isinstance(info, str):
            if info not in self.resources:
                logger.warning("No resource: %s", info)
                return False, []
            info = self.resources[info]
            use_buffer = True
        elif isinstance(info, dict):
            try:
                update_resource(info, self.section)
            except FileNotFoundError:
                logger.exception("No resource: %s", info)
                return False, []
            use_buffer = False
        else:
            raise TypeError("Invalid resource: {}".format(info))

        name = info["Name"]
        if info.get("ImageData") is None:
            self.error("No ImageData for %s" % info)
            return False, []
        if image is None:
            image = self.screen
        else:
            use_buffer = False

        if use_buffer and name in self.resource_pos_buffer:
            logger.debug("Check Resource With Buffer: %s=%s", name, self.resource_pos_buffer[name])
            return self.resource_pos_buffer[name]

        if info["Type"] == "Static":
            x, y = info["Offset"]
            w, h = info["Size"]
            target = info['ImageData']
            part = cv_crop(image, (x, y, x+w, y+h))
            diff = get_diff(part, target)
            # 有位置限制, 可以使用较为宽松的阈值
            logger.debug("Diff for %s@%s=%.3f", name, (x, y), diff)
            ret = diff <= info.get('MaxDiff', 0.06)
            if ret:
                pos = [x, y]
            else:
                pos = []
        elif info["Type"] in {"Dynamic", "Anchor"}:
            target = info['ImageData']
            if "SearchArea" in info:
                xy, wh = info["SearchArea"]
                logger.debug("Search in %s+%s", xy, wh)
                x, y = xy
                w, h = wh
                part = cv_crop(image, (x, y, x+w, y+h))
            else:
                x = y = 0
                part = image
            diff, pos = get_match(part, target)
            logger.debug("Diff for %s@%s=%.3f", name, pos, diff)
            if diff > info.get('MaxDiff', 0.02):
                ret = False
                pos = []
            else:
                ret = True
                pos = np.add(pos, [x, y])
        elif info["Type"] == "MultiStatic":
            target = info['ImageData']
            w, h = info["Size"]
            pos = []
            ret = False
            if index is not None:
                positions = [info["Positions"][index]]
            else:
                positions = info["Positions"]
            for x, y in positions:
                cropped = cv_crop(image, (x, y, x+w, y+h))
                diff = get_diff(cropped, target)
                logger.debug("Diff for %s@%s=%.3f", name, (x, y), diff)
                if diff <= info.get('MaxDiff', 0.03):
                    pos.append((x, y))
                    ret = True
        elif info["Type"] == "MultiDynamic":
            target = info['ImageData']
            if "SearchArea" in info:
                xy, wh = info["SearchArea"]
                logger.debug("Search in %s+%s", xy, wh)
                x, y = xy
                w, h = wh
                part = cv_crop(image, (x, y, x+w, y+h))
            else:
                x = y = 0
                part = image
            pos = get_multi_match(part, target, info.get("MaxDiff", 0.02))
            pos = [[dx+x, dy+y] for dx, dy in pos]
            ret = bool(pos)
        else:
            self.critical("Invalid Type %s", info['Type'])
            return False, []
        if use_buffer:
            self.resource_pos_buffer[name] = (ret, pos)
        logger.debug("Check Resource: %s=%s", name, (ret, pos))
        return ret, pos

    def resource_in_image(self, info, image, index=None):
        """判断资源是否存在于给出的画面内. 可接受资源名字符串或资源定义dict, 返回bool判断
        """
        return self.search_resource(info, image, index)[0]

    def resource_in_screen(self, name, index=None):
        """判断资源是否存在于画面内. 仅接受资源名字符串, 返回bool判断
        """
        if not isinstance(name, str):
            return name
        if name not in self.resources:
            logger.warning("resource_in_screen: No Resouce %s", name)
            return False
        return self.search_resource(name, index=index)[0]

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

    def click_at_resource(self, name, wait=False, index=None, offset=None, hold=0):
        """点击资源

        wait 为等待资源出现的时间
        """
        if wait:
            if not self.wait_resource(name, 1, wait):
                return
        res = self.resources[name]
        logger.info("Click at <%s> resource: %s", res["Type"], name)
        if res['Type'] == 'Static':
            x, y = res['Offset']
            dx, dy = res.get("ClickOffset", (0, 0))
            cw, ch = res.get("ClickSize", res.get("Size"))
            rand_click(self.hwnd, (x+dx, y+dy, x+dx+cw, y+dy+ch), hold)
        elif res['Type'] == 'MultiStatic':
            logger.info("index=%s", index)
            x, y = res['Positions'][index]
            dx, dy = res.get("ClickOffset", res.get("Offset", (0, 0)))
            cw, ch = res.get("ClickSize", res.get("Size"))
            rand_click(self.hwnd, (x+dx, y+dy, x+dx+cw, y+dy+ch), hold)
        elif res['Type'] == 'Dynamic':
            if offset is None:
                _, offset = self.search_resource(name)
            x, y = offset
            dx, dy = res.get("ClickOffset", res.get("Offset", (0, 0)))
            cw, ch = res.get("ClickSize", res.get("Size"))
            rand_click(self.hwnd, (x+dx, y+dy, x+dx+cw, y+dy+ch), hold)
        elif res['Type'] == 'MultiDynamic':
            if offset is None:
                _, pos = self.search_resource(name)
                offset = pos[index]
            x, y = offset
            dx, dy = res.get("ClickOffset", res.get("Offset", (0, 0)))
            cw, ch = res.get("ClickSize", res.get("Size"))
            rand_click(self.hwnd, (x+dx, y+dy, x+dx+cw, y+dy+ch), hold)
        else:
            self.error("Want to click at <%s> resource: %s", res["Type"], name)

    def crop_resource(self, name, offset=None, image=None, index=0):
        """截取资源所在位置的当前截图"""
        if image is None:
            image = self.screen
        if isinstance(name, dict):
            res = name
            name = res["Name"]
        else:
            res = self.resources[name]
        if offset is None:
            if res["Type"] == "MultiStatic":
                x, y = res["Positions"][index]
            elif res["Type"] == "MultiDynamic":
                ret, pos = self.search_resource(name, image=image)
                if not ret:
                    raise ValueError("Resource[%s] not in Image" % name)
                x, y = pos[index]
            elif res["Type"] == "Dynamic":
                ret, pos = self.search_resource(name, image=image)
                if not ret:
                    raise ValueError("Resource[%s] not in Image" % name)
                x, y = pos
            else:
                x, y = 0, 0
        else:
            x, y = offset

        dx, dy = res.get("CropOffset", res.get("Offset", (0, 0)))
        w, h = res.get("CropSize", res["Size"])
        bbox = (x+dx, y+dy, x+w+dx, y+h+dy)
        logger.info("crop_resource<%s>[%s] %s", res["Type"], name, bbox)
        return cv_crop(image, bbox)

    def parse_scene_condition(self, condition):
        def resource_check(name):
            return self.resource_in_screen(name)
        try:
            res = parse_condition(condition, self, resource_check)
        except Exception as err:
            logger.exception("parse_scene_condition Failed: %s", condition)
            raise err
        return res

    def wait_till(self, condition, interval=1, repeat=5):
        """等待画面满足给定条件"""
        if repeat < 0:
            self.error("Can't find resource %s" % condition)
            return False
        self.make_screen_shot()
        if self.parse_scene_condition(condition):
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
        if isinstance(scene, str):
            scene = self.scenes[scene]

        if reshot:
            self.make_screen_shot()

        res = self.parse_scene_condition(scene["Condition"])
        if res:
            logger.info("Check scene %s: %s=%s", scene["Name"], scene["Condition"], res)
        elif logger.isEnabledFor(logging.DEBUG):
            logger.debug("Check scene %s: %s=%s", scene["Name"], scene["Condition"], res)
        return res

    def go_top(self):
        """使模拟器窗口前置"""
        make_foreground(self.hwnd)

    def save_record(self, prefix=None, area=None):
        if prefix is None:
            prefix = "Shot-" + self.current_scene_name
        if area is None:
            image = self.screen
        else:
            image = self.crop_resource(area)
            if isinstance(area, dict):
                area = area["Name"]
            if isinstance(area, str):
                prefix += '-%s' % area
        name = "{0}/shots/{2:%Y%m%d}/{1}@{2:%Y%m%d_%H%M%S}.jpg".format(self.section, prefix, datetime.datetime.now())
        cv_save(name, image)

    def critical(self, message=None, title="", action=None):
        """致命错误提醒"""
        logger.critical(message)
        self.save_record("Critical")

        info = "自动战斗脚本将终止:\n%s\n是否将模拟器前置？" % message
        flag = win32con.MB_ICONERROR | win32con.MB_YESNO | win32con.MB_TOPMOST \
            | win32con.MB_SETFOREGROUND | win32con.MB_SYSTEMMODAL
        title = "自动脚本%s - %s错误" % (self.section, title)
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
        title = "自动脚本%s - %s警告" % (self.section, title)
        res = win32api.MessageBox(0, info, title, flag)
        if res == win32con.IDNO:
            self.go_top()
            exit(0)

    def wait_mannual(self, message=None, title="", action="继续"):
        """等待手动操作"""
        logger.info("等待手动操作: %s", message)

        info = "等待手动指令:\n%s" % message
        # flag = win32con.MB_ICONINFORMATION | win32con.MB_YESNO | win32con.MB_TOPMOST \
        #     | win32con.MB_SETFOREGROUND | win32con.MB_SYSTEMMODAL
        flag = win32con.MB_YESNO | win32con.MB_SETFOREGROUND
        title = "自动脚本 - 等待手动指令"
        res = ctypes.windll.user32.MessageBoxTimeoutA(
            0, info.encode("GBK"), title.encode("GBK"), flag, 0, 4000)
        if res == win32con.IDNO:
            self.go_top()
            exit(0)
        else:
            input("Paused...")

    def notice(self, message=None, title="", action="继续"):
        """提醒"""
        logger.warning(message)
        info = "出现异常情况:\n%s\n是否忽略并%s？" % (message, action)
        flag = win32con.MB_YESNO | win32con.MB_TOPMOST | win32con.MB_SETFOREGROUND
        title = "自动脚本%s - %s提醒" % (self.section, title)
        res = ctypes.windll.user32.MessageBoxTimeoutA(
            0, info.encode("GBK"), title.encode("GBK"), flag, 0, 3000)
        if res == win32con.IDNO:
            self.go_top()
            exit(0)

    def update_current_scene(self, candidates=None, repeat=None):
        """等待指定的场景或全局场景"""
        if repeat is None:
            repeat = self.scene_check_max_repeat
        logger.debug("update_current_scene(%d) in %s", repeat, candidates)
        if repeat == 0:
            self.error("场景判断失败! 上一场景: %s" % self.current_scene)
            # 若选择忽略错误，则返回“无匹配场景”
            scene = self.fallback_scene
            self.scene_history.append(scene)
            self.scene_history_count[scene["Name"]] += 1
            return self.fallback_scene

        if candidates is None:
            if self.current_scene is None or self.current_scene.get("Next") is None:
                logger.debug("update candidates to full list")
                candidates = list(self.scenes.keys())
            else:
                candidates = self.current_scene["Next"]
                if isinstance(candidates, dict):
                    repeat = candidates.get("Repeat", repeat)
                    candidates = candidates["Candidates"]
                logger.debug("update candidates: Next for %s: %s", self.current_scene["Name"], candidates)

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
                if key not in self.scenes:
                    logger.warning("Scene %s Unkown", key)
                    continue
                scene = self.scenes[key]
            if self.scene_match_check(scene, False):
                self.scene_history.append(scene)
                self.scene_history_count[scene["Name"]] += 1
                return scene

        for key in self.scenes:
            scene = self.scenes[key]
            if scene.get("Global"):
                if self.scene_match_check(scene, False):
                    self.scene_history.append(scene)
                    self.scene_history_count[scene["Name"]] += 1
                    return scene

        self.do_actions(self.current_scene.get("ActionsWhenWait", [{"Type": "Wait", "Time": 1}]))

        return self.update_current_scene(candidates, repeat-1)

    def get_resource_rect(self, key):
        """获取资源的bbox"""
        x, y = self.resources[key]["Offset"]
        w, h = self.resources[key]["Size"]
        return (x, y, x+w, y+h)

    def do_actions(self, actions=None):
        """执行指定的操作"""
        if actions is None:
            actions = self.current_scene["Actions"]
        for action in actions:
            if "Condition" in action and not parse_condition(action["Condition"], self):
                continue

            if 'WaitCondition' in action:
                self.wait_till(action['WaitCondition'])
            elif 'WaitScene' in action:
                self.wait_till_scene(action['WaitScene'])

            if action['Type'] == 'Wait':
                self.wait(action['Time'])
            elif action['Type'] == 'InnerCall':
                target = getattr(self, action['Target'])
                args = action.get("args", [])
                kwargs = action.get("kwargs", {})
                max_retry = action.get("MaxRetry", 5)
                retry = 0
                while retry < max_retry:
                    try:
                        target(*args, **kwargs)
                    except RuntimeError:
                        retry += 1
                        if not self.scene_match_check(self.current_scene_name, True):
                            logger.warning("Scene changed from %s, abort left actions", self.current_scene_name)
                            return
                    except Exception:
                        self.critical(traceback.format_exc(), "程序")
                    else:
                        max_retry = -1
            elif action['Type'] == 'Click':
                self.click_at_resource(
                    name=action['Target'],
                    wait=action.get("Wait", False),
                    index=action.get("Index", None),
                    hold=action.get("Hold", 0)
                )
            elif action['Type'] == 'MultiActions':
                self.do_actions(action['Actions'])
            else:
                self.critical("Invalid Action %s" % action)

            if action.get("Break"):
                break

    @property
    def since_last_change(self):
        """返回从上次场景变化到当前时间的秒数"""
        return time.time() - self.last_change

    def check_scene(self, stop_checker=None):
        """判断当前场景, 执行对应的操作"""
        self.actions_done = False
        scene = self.update_current_scene()
        heartbeat()
        now = time.time()
        if self.scene_changed:
            nochange = ""
            self.last_change = now
        else:
            nochange = "(No Change)"

        logger.info("%s - %s%s", scene['Name'], scene['Actions'], nochange)
        if stop_checker and stop_checker(self):
            # 执行动作前预先判断是否已处于停止条件
            return
        self.do_actions(scene['Actions'])
        self.actions_done = True

    def main_loop(self, stop_checker=None):
        """进行`判断停止条件-判断场景-判断停止条件`循环"""
        while not self.stop:
            self.check_scene(stop_checker)
            if stop_checker and stop_checker(self):
                self.stop = True

    def close(self):
        self.stop = True
        logger.warning("Closing by set stop=%s", self.stop)


if __name__ == "__main__":
    logger.setLevel("DEBUG")
    controler = SimulatorControl()
    print(controler.update_current_scene())
    # print(controler.select_ships())
    # print(controler.retire())
