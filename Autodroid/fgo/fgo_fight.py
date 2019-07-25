import re
from collections import defaultdict

import numpy as np
import requests

from config_loader import config
from simulator import SimulatorControl, parse_condition
from simulator.image_tools import cv_crop, cv_save, load_map, load_resources, load_scenes, get_multi_match, get_match, Affine
from simulator.win32_tools import drag, rand_drag, rand_click, rand_point
from ocr import ocr

import logging
logger = logging.getLogger(__name__)


class FateGrandOrder(SimulatorControl):
    scene_check_max_repeat = 60
    section = "FGO"

    def __init__(self, map_name="CommonConfig"):
        super().__init__()
        self.map_name = map_name
        logger.warning("Init %s", self)
        self.combat_info = defaultdict(lambda: 0)
        self.best_equips = []
        self.data = load_map(map_name, self.section)
        logger.info("Update Resources %s", list(self.data['Resources'].keys()))
        self.resources.update(self.data['Resources'])
        logger.info("Update Scenes %s", list(self.data['Scenes'].keys()))
        self.scenes.update(self.data['Scenes'])

    def __str__(self):
        return "<{}: {}>".format(self.__class__.__name__, self.map_name)

    def save_record(self, prefix=None, area=None, **extra_kwargs):
        if "comment" not in extra_kwargs:
            extra_kwargs["comment"] = {}
        extra_kwargs["comment"]["MapName"] = self.map_name
        super().save_record(prefix, area, **extra_kwargs)

    def update_combat_info(self, parse=False, **kwargs):
        if parse:
            for key in kwargs:
                kwargs[key] = parse_condition(kwargs[key], self, self.combat_info.__getitem__)
        logger.info("Update combat_info: %s", kwargs)
        self.combat_info.update(kwargs)
        logger.info("combat_info Now: %s", self.combat_info)

    def refresh_assist(self):
        logger.info("更新助战列表")
        self.click_at_resource("助战更新")
        self.wait(0.8)
        self.click_at_resource("助战-确认更新")
        self.wait(3)

    @property
    def scroll_pos(self):
        self.make_screen_shot()
        if not self.parse_scene_condition(["$all", [["滚动条-上"], ["滚动条-下"]]]):
            self.notice("No Scroll Bar")
            return 1
        _, top_xy = self.search_resource("滚动条-上")
        _, bot_xy = self.search_resource("滚动条-下")
        top = top_xy[1]
        bottom = bot_xy[1]
        cross = bottom - top
        top0 = self.resources["滚动条范围"]["Offset"][1]
        total = self.resources["滚动条范围"]["Size"][1]
        ratio = (bottom - top0 - cross) / (total - cross)
        logger.info("Scroll Ratio=%.3f", ratio)
        return ratio

    def servant_scroll(self, line):
        if not self.parse_scene_condition(["$all", [["滚动条-上"], ["滚动条-下"]]]):
            self.notice("Can't Scroll")
            return

        if abs(line) < 3:
            mid_x = config.getint("Device", "MainWidth") / 2
            mid_y = config.getint("Device", "MainHeight") / 2
            rand_drag(self.hwnd, rand_point([mid_x, mid_y], [50, 10]),
                      rand_point([mid_x, mid_y - mid_y * line * 0.5], [50, 10]), 30)
            return
        _, top_xy = self.search_resource("滚动条-上")
        _, bot_xy = self.search_resource("滚动条-下")
        width = self.resources["滚动条-上"]["Size"][0]
        top = top_xy[1]
        bottom = bot_xy[1]
        x = top_xy[0] + width / 2
        middle = (top + bottom) // 2
        cross = bottom - top
        dy = line * cross * 0.37
        rand_drag(self.hwnd, rand_point([x, middle], [width/6, cross / 6]), rand_point([x, middle + dy], [50, 10]), 30)
        # drag(self.hwnd, [x, middle], [x, middle + dy], 30)

    def servant_scroll_to_top(self):
        _, top_xy = self.search_resource("滚动条-上")
        _, bot_xy = self.search_resource("滚动条-下")
        top = top_xy[1]
        bottom = bot_xy[1]
        x = (top_xy[0] + bot_xy[0]) // 2
        middle = (top + bottom) // 2
        rand_drag(self.hwnd, (x, middle), (x, 0), 30)

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

    def get_np(self, np_img):
        gray = np_img.mean(axis=(0, 2))
        length = len(gray)
        light = []
        for i in range(length):
            if gray[i] > 110:
                light.append((2, (i+1) / length))
            elif gray[i] > 40:
                light.append((1, (i+1) / length))
            else:
                light.append((0, (i+1) / length))
        best = max(light)
        if best[0] == 2:
            return 100 + 100 * best[1]
        if best[0] == 1:
            return 100 * best[1]
        if best[0] == 0:
            return 0

    def extract_np_info(self, outcall=True):
        """提取NP信息
        outcall表示调用是否来自extract_combat_info以外的函数
        是则需要重新截屏、提取信息后log
        """
        if outcall:
            self.make_screen_shot()

        if self.current_scene_name == "选择指令卡":
            multi = 1.4
        else:
            multi = 1
        for i in range(3):
            self.combat_info["NP%d" % (i+1)] = self.get_np(self.crop_resource("从者%d-NP" % (i+1)) * multi)

        if outcall:
            logger.info("extract_np_info: %s", self.combat_info)

    def reset_combat_info(self):
        self.combat_info = defaultdict(lambda: 0)

    def extract_enemy_hp(self):
        """提取敌人HP信息"""
        hp_max = 0
        hp_max_idx = 0
        for i in range(3):
            img = self.crop_resource("战斗-敌人血量", index=i)
            check = img.mean(2).max(0)[::-1]
            if check.max() < 200 or img.std() < 50:
                hp = 0
            else:
                hp = 100 * np.where(check > 200)[0].max() / len(check)
            logger.info("敌人%d 血量数字长度%f", i, hp)
            self.combat_info["EnemyHP%d" % (i+1)] = hp
            if hp > hp_max:
                hp_max = hp
                hp_max_idx = i + 1
        self.combat_info["EnemyMaxHP"] = hp_max
        self.combat_info["MaxHPEnemyIdx"] = hp_max_idx

    def check_hard_enemy(self, thresh=60):
        self.extract_enemy_hp()
        if self.combat_info["EnemyMaxHP"] > thresh:
            self.click_at_resource("战斗-敌人位置", index=self.combat_info["MaxHPEnemyIdx"]-1)
        self.wait(2)

    def extract_combat_info(self, repeat=0):
        """提取战斗轮次、从者NP、敌人HP等信息"""
        if not self.scene_changed:
            return
        self.make_screen_shot()
        if repeat > 3:
            self.notice("extract_combat_info Failed")
            return
        imgs = [
            self.crop_resource("战斗轮次"),
            self.crop_resource("剩余敌人"),
            self.crop_resource("回合数")
        ]
        errors = []
        try:
            info = ocr.images2text(*imgs)
            logger.info("Get Combat Info OCR: %s(%d)", info, repeat)
        except (requests.HTTPError, requests.exceptions.ReadTimeout, requests.exceptions.ConnectTimeout) as err:
            info = []
            errors.append(err)

        try:
            now, total = [int(t) for t in re.search(r"^(\d).*?(\d)$", info[0]).groups()]
            if self.combat_info["BattleNow"] != now:
                self.combat_info["TurnOfBattle"] = 1
            else:
                self.combat_info["TurnOfBattle"] += 1
            self.combat_info["BattleNow"] = now
            self.combat_info["BattleTotal"] = total
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
            if not self.combat_info["Turn"]:
                self.combat_info["Turn"] = 1
            else:
                self.combat_info["Turn"] += 1
            errors.append(err)

        self.extract_np_info(False)
        # self.extract_enemy_hp()
        if errors:
            self.notice("OCR Errors %s" % errors)
            self.wait(1)
            self.make_screen_shot()
            self.extract_combat_info(repeat+1)
            return
        logger.info("extract_combat_info: %s", self.combat_info)

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
        result = ""
        if self.resource_in_image("无法行动", image):
            result += "无法行动"

        best_diff = 1
        color = ""
        for name in ["Buster", "Arts", "Quick"]:
            diff, _ = get_match(image, self.resources[name]["ImageData"])
            if diff < best_diff:
                best_diff = diff
                color = name[0]
        result += color

        if self.resource_in_image("克制", image):
            relation = "克制"
        elif self.resource_in_image("抵抗", image):
            relation = "抵抗"
        else:
            relation = "0"
        result += relation

        if self.resource_in_image("指令卡-助战", image):
            result += "-助战"

        logger.info("Found Card: %s", result)
        return result

    def choose_cards(self):
        pass

    def pre_cards_info(self):
        """提取技能选择画面中的指令卡信息"""
        cards = []
        info = self.resources["指令卡预判"]
        for i in range(5):
            x, y = info["Positions"][i]
            theta = info["Angles"][i]
            mat = Affine.move(4, 30) * Affine.rotate(theta) * Affine.move(-x, -y)
            card_image = Affine.warp(self.screen, mat, (100, 140))
            cards.append(self.extract_card_info(card_image))
        return cards


# if __name__ == "__main__":
    # fgo = FateGrandOrder("通用配置")
    # print(fgo.resources.keys())
    # print(fgo.resources['战斗速度']['ImageData'].shape)
    # fgo.update_current_scene()
    # print(fgo.scene_history)
