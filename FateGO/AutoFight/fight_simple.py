"""
低难度战斗策略
"""
import json

from config import logger, config
from win32_tools import rand_click
from image_tools import load_map, cv_crop, get_match
from fgo_fight import FateGrandOrder

def choose_match(cards, items):
    for name in items:
        for card in cards[:]:
            if card[1] == name:
                cards.remove(card)
                return card


class SimpleFight(FateGrandOrder):
    def __init__(self, map_name):
        FateGrandOrder.__init__(self, map_name)
        self.first_turn = True

    def choose_assist_servant(self):
        idx = 0
        while not self.resource_in_screen("助战1"):
            self.refresh_assist()
            idx += 1
            if idx > 5:
                self.error("无助战")

        self.first_turn = True
        self.click_at_resource("助战1")

    def choose_skills(self):
        self.wait(1)
        res = self.resources["战斗-敌人位置"]
        x, y = res["Positions"][1]
        dx, dy = res["ClickOffset"]
        dw, dh = res["ClickSize"]
        rand_click(self.hwnd, (x+dx, y+dy, x+dx+dw, y+dy+dh))
        if not self.first_turn:
            return
        self.wait(2)
        # self.click_at_resource("敌人2")
        self.first_turn = False
        for serv_idx, skill_idx in self.data['Strategy']['SkillsOnTurn1']:
            target = "角色%d技能%d" % (serv_idx, skill_idx)
            logger.info("Use Skill: %s", target)
            self.click_at_resource(target)
            self.wait(0.8)
            self.make_screen_shot()
            self.click_at_resource("右侧空白区域")
            self.wait_till_scene("选择技能", 1, 20)
            self.wait(0.8)

    def extract_card_info(self, image):
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
        self.make_screen_shot()
        self.wait(2)
        cards = self.resources["Cards"]
        w, h = cards["Size"]
        cx, cy = cards.get("ClickOffset", (0, 0))
        cw, ch = cards.get("ClickSize", (w, h))
        checker = []
        for x, y in cards["Positions"]:
            image = cv_crop(self.screen, (x, y, x+w, y+h))
            card_info = self.extract_card_info(image)
            click_rect = (x+cx, y+cy, x+cx+cw, y+cy+ch)
            checker.append([click_rect, card_info])
            
        for i in [1, 2, 3]:
            self.click_at_resource("宝具背景%d" % i)
            self.wait(0.8)
            
        for items in self.data["Strategy"]["CardChoice"]:
            choice = choose_match(checker, items)
            rand_click(self.hwnd, choice[0])
            self.wait(0.8)

if __name__ == "__main__":
    import datetime
    control = SimpleFight("圣诞")
    while True:
        control.check_scene()
