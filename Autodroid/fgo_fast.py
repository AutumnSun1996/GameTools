import re
from collections import defaultdict

from simulator.control import logger, parse_condition
from simulator.win32_tools import rand_click
from fgo.fgo_simple import FGOSimple as FGOBase
from ocr.baidu_ocr import ocr

def choose_match(cards, items):
    for name in items:
        for card in cards[:]:
            if card[1] == name:
                cards.remove(card)
                return card


class FGOSimple(FGOBase):
    def choose_skills(self):
        if self.combat_info["Turn"] == 1:
            self.wait_till_scene("选择技能", 1, 20)
            self.wait(4)
        for item in self.data["Strategy"]["Skills"]:
            if parse_condition(item["Condition"], self, self.combat_info.__getitem__):
                logger.info("Skill Strategy Passed: %s", item)
                self.do_actions(item["Actions"])
        self.enemy_attack = None

    def use_skills(self, *skills):
        for skill in skills:
            if skill[0] == 0:
                self.click_at_resource("御主技能")
                self.wait(1)
                fmt = "御主技能{1}"
            else:
                fmt = "角色{0}技能{1}"
            logger.debug("Use Skill %s %s", fmt, skill)
            self.click_at_resource(fmt.format(*skill))
            self.wait(1)
            if len(skill) == 3:
                self.click_at_resource("目标%d-3" % skill[2])
                self.wait(1)
            elif len(skill) == 4:
                self.click_at_resource("目标%d-4" % skill[2])
                self.wait(1)
                self.click_at_resource("目标%d-4" % skill[3])
                self.wait(1)
            self.make_screen_shot()
            self.click_at_resource("右侧空白区域")
            self.wait_till_scene("选择技能", 1, 20)
            self.wait(0.5)

    def choose_card(self, card_names, card_rects, order):
        for item in order:
            if item in card_names:
                idx = card_names.index(item)
                break
        result = [card_names[idx], card_rects[idx]]
        card_names.remove(card_names[idx])
        card_rects.remove(card_rects[idx])
        return result
    
    def extract_np_info(self, repeat=0):
        if repeat > 3:
            self.error("OCR Failed")
            return
        try:
            imgs  = [
                self.crop_resource("从者1-NP"),
                self.crop_resource("从者2-NP"),
                self.crop_resource("从者3-NP"),
            ]
            info = ocr.images2text(*imgs)
            logger.info("Get NP Info %s(%d)", info, repeat)
            for i in range(len(info)):
                info[i] = int(re.search(r"(\d+)", info[i]).group(1))

            self.combat_info["NP"] = info
        except (AttributeError, IndexError, ValueError):
            self.wait(1)
            self.make_screen_shot()
            self.extract_combat_info(repeat+1)
    
    def choose_cards(self):
        choice = []
        self.wait(3)
        self.make_screen_shot()
        if not self.combat_info:
            self.extract_combat_info()
        self.extract_np_info()
        logger.info("CombatInfo: %s", self.combat_info)

        for idx in range(3):
            check = self.data["Strategy"]["UseNP"][idx]
            if self.combat_info["NP"][idx] >= 100 and parse_condition(check["Condition"], self, self.combat_info.__getitem__):
                name = "宝具背景%s" % (check["Target"])
                logger.info("使用宝具: %s", name)
                choice.append(self.get_resource_rect(name))

        # if self.combat_info["Turn"] == 1:
            # self.click_at_resource("宝具背景3")
        # elif self.combat_info["BattleNow"] == 2 and self.combat_info["TurnOfBattle"] == 1:
            # self.click_at_resource("宝具背景1")
            # self.wait(0.5)
            # self.click_at_resource("宝具背景3")
        # elif self.combat_info["BattleNow"] == 3:
            # self.click_at_resource("宝具背景1")
            # self.wait(0.5)
            # self.click_at_resource("宝具背景2")
            # self.wait(0.5)
            # self.click_at_resource("宝具背景3")

        self.wait(1)
        cards = self.resources["Cards"]
        w, h = cards["Size"]
        cx, cy = cards.get("ClickOffset", (0, 0))
        cw, ch = cards.get("ClickSize", (w, h))
        
        card_names = []
        card_rects = []
        for x, y in cards["Positions"]:
            card_img = self.crop_resource("Cards", offset=[x, y])
            click_rect = (x+cx, y+cy, x+cx+cw, y+cy+ch)
            card_names.append(self.extract_card_info(card_img))
            card_rects.append(click_rect)
        
        logger.info("Found Cards %s", card_names)
        
        choice += [None, None, None]
        for idx, order in self.data["Strategy"]["CardChoice"]:
            if choice[idx] is None:
                name, rect = self.choose_card(card_names, card_rects, order)
                choice[idx] = rect
                logger.info("Choose Card %s for idx %d", name, idx)

        for rect in choice:
            if rect is not None:
                rand_click(self.hwnd, rect)
                self.wait(0.5)

        for rect in card_rects:
            rand_click(self.hwnd, rect)
            self.wait(0.5)


if __name__ == "__main__":
    fgo = FGOSimple("刷材料")
    count = 0
    while 1:
        fgo.check_scene()
        print(fgo.current_scene_name)
        if fgo.current_scene_name == "获得物品":
            count += 1
            print(fgo.current_scene_name, count)
            if count >= 30:
                fgo.manual()
                break