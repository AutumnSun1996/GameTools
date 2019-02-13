import re
from collections import defaultdict
import json

import numpy as np

from config_loader import config, logger
from simulator import SimulatorControl, parse_condition
from simulator.image_tools import cv_crop, cv_save, load_map, load_resources, load_scenes, get_multi_match, get_match
from simulator.win32_tools import drag, rand_click
from ocr import ocr


class FateGrandOrder(SimulatorControl):
    scene_check_max_repeat = 60
    section = "FGO"

    def __init__(self, map_name="CommonConfig"):
        super().__init__()
        self.combat_info = defaultdict(lambda: None)
        self.best_equips = []
        self.data = load_map(map_name, self.section)
        logger.info("Update Resources %s", list(self.data['Resources'].keys()))
        self.resources.update(self.data['Resources'])
        logger.info("Update Scenes %s", list(self.data['Scenes'].keys()))
        self.scenes.update(self.data['Scenes'])

    def refresh_assist(self):
        self.click_at_resource("助战更新")
        self.wait(0.8)
        self.click_at_resource("助战-确认更新")
        self.wait(3)

    @property
    def scroll_pos(self):
        self.wait_till(["$all", [["滚动条-上"], ["滚动条-下"]]])
        _, top_xy = self.search_resource("滚动条-上")
        _, bot_xy = self.search_resource("滚动条-下")
        top = top_xy[1]
        bottom = bot_xy[1]
        cross = bottom - top
        top0 = self.resources["滚动条范围"]["Offset"][1]
        total = self.resources["滚动条范围"]["Size"][1]
        return (bottom - top0 - cross) / (total - cross)

    def servant_scroll(self, line):
        if line < 3:
            mid_x = config.getint("Device", "MainWidth") / 2
            mid_y = config.getint("Device", "MainHeight") / 2
            drag(self.hwnd, (mid_x, mid_y), (mid_x, mid_y - mid_y * line * 0.5), 30)
            return
        _, top_xy = self.search_resource("滚动条-上")
        _, bot_xy = self.search_resource("滚动条-下")
        top = top_xy[1]
        bottom = bot_xy[1]
        x = (top_xy[0] + bot_xy[0]) // 2
        middle = (top + bottom) // 2
        cross = bottom - top
        dy = line * cross * 0.37
        drag(self.hwnd, (x, middle), (x, middle + dy), 30)

    def servant_scroll_to_top(self):
        _, top_xy = self.search_resource("滚动条-上")
        _, bot_xy = self.search_resource("滚动条-下")
        top = top_xy[1]
        bottom = bot_xy[1]
        x = (top_xy[0] + bot_xy[0]) // 2
        middle = (top + bottom) // 2
        drag(self.hwnd, (x, middle), (x, 0), 30)

    def choose_assist_servant(self):
        for target in self.best_equips:
            score, rect = self.assist_score(target)
            if score > self.data["AssistLimit"]:
                rand_click(self.hwnd, rect)
                return
        self.servant_scroll_to_top()
        ret, pos = self.search_resource("最后登录")

    def assist_score(self, target):
        res = self.resources['最后登录']
        equip = self.resources['助战选择-从者-礼装']
        w, h = equip['Size']
        dx, dy = res['Offset']
        ex, ey = equip['Offset']
        lt, rb = res['SearchArea']
        for x, y in get_multi_match(self.screen, res['ImageData'], res.get("MaxDiff", 0.05)):
            if not (lt[0] < x < rb[0] and lt[1] < y < rb[1]):
                continue
            sx = x+dx+ex
            sy = y+dy+ey
            equip_image = cv_crop(self.screen, (sx, sy, sx+w, sy+h))
            diff, _ = get_match(equip_image, target['ImageData'])
            if diff < target.get("MaxDiff", 0.05):
                return True, [sx, sy, sx+w, sy+h]
        return False, None

    def extract_combat_info(self, repeat=0):
        if not self.scene_changed:
            return
        if repeat > 3:
            self.notice("extract_combat_info Failed")
            return
        imgs  = [
            self.crop_resource("战斗轮次"),
            self.crop_resource("剩余敌人"),
            self.crop_resource("回合数"),
            self.crop_resource("从者1-NP"),
            self.crop_resource("从者2-NP"),
            self.crop_resource("从者3-NP"),
        ]
        info = ocr.images2text(*imgs)
        logger.info("Get Combat Info %s(%d)", info, repeat)
        errors = []
        try:
            now, total = [int(t) for t in re.search(r"^(\d).*?(\d)$", info[0]).groups()]
            if self.combat_info["BattleNow"] != now:
                self.combat_info["TurnOfBattle"] = 1
            else:
                self.combat_info["TurnOfBattle"] += 1
            self.combat_info["BattleNow"] = now
            self.combat_info["BattleTotal"] = total - now
            self.combat_info["BattleLeft"] = total - now
            
        except (AttributeError, IndexError, ValueError) as err:
            errors.append(err)

        try:
            match = re.search(r"(\d+)", info[1])
            if match:
                self.combat_info["EnemyLeft"] = int(match.group(1))
        except (AttributeError, IndexError, ValueError) as err:
            errors.append(err)

        try:
            match = re.search(r"(\d+)", info[2])
            if match:
                self.combat_info["Turn"] = int(match.group(1))
        except (AttributeError, IndexError, ValueError) as err:
            if self.combat_info["Turn"] is None:
                self.combat_info["Turn"] = 1
            else:
                self.combat_info["Turn"] += 1
            errors.append(err)

        try:
            self.combat_info["NP"] = [0, 0, 0]
            for i in range(3):
                match = re.findall(r"(\d+)", info[i+3])
                if match:
                    self.combat_info["NP"][i] = int(''.join(match))
        except (AttributeError, IndexError, ValueError) as err:
            errors.append(err)

        if errors:
            self.notice("OCR Errors %s" % errors)
            self.wait(1)
            self.make_screen_shot()
            self.extract_combat_info(repeat+1)

    def choose_skills(self):
        pass

    def update_background(self):
        """保存当前画面为宝具背景, 供之后的分析使用
        """
        for i in range(3):
            name = '宝具%d' % (i+1)
            self.resources[name]['ImageData'] = self.crop_resource(name)

    def choose_match(self, image, candidates):
        best = None
        best_diff = 1
        for name in candidates:
            diff, _ = get_match(image, self.resources[name]['ImageData'])
            if diff < best_diff:
                best_diff = diff
                best = name
        return best_diff, best

    def extract_card_info(self, image):
        # if self.resource_in_image(image, "眩晕"):
            # result = "--"
        # else:
        best_diff = 1
        color = ""
        for name in ["Buster", "Arts", "Quick"]:
            diff, _ = get_match(image, self.resources[name]["ImageData"])
            if diff < best_diff:
                best_diff = diff
                color = name[0]

        relation = None
        for name in ["克制", "抵抗"]:
            res = self.resources[name]
            diff, _ = get_match(image, res["ImageData"])
            if diff < res.get("MaxDiff", 0.02):
                relation = name
                break
        relation = {"克制": "+", "抵抗": "-"}.get(relation, "0")
        result = color + relation
        logger.info("Found Card: %s", result)
        return result

    def choose_cards(self):
        pass


# if __name__ == "__main__":
    # fgo = FateGrandOrder("通用配置")
    # print(fgo.resources.keys())
    # print(fgo.resources['战斗速度']['ImageData'].shape)
    # fgo.update_current_scene()
    # print(fgo.scene_history)
