
from simulator.control import logger, parse_condition
from simulator.win32_tools import rand_click
from fgo.fgo_fight import FateGrandOrder


def choose_match(cards, items):
    for name in items:
        for card in cards[:]:
            if card[1] == name:
                cards.remove(card)
                return card


class FGOSimple(FateGrandOrder):
    def at_end(self):
        _, bot_xy = self.search_resource("滚动条-下")

    def choose_assist_servant(self, idx=5):
        if idx <= 0:
            self.error("无助战")
        while self.scroll_pos < 0.99:
            for name in self.data['Strategy']['Assist']:
                if self.resource_in_screen(name):
                    logger.info("选择助战: %s", name)
                    self.click_at_resource(name)
                    return
            self.servant_scroll(1.5)
            self.wait(1)
            self.make_screen_shot()

        self.refresh_assist()
        self.make_screen_shot()
        self.choose_assist_servant(idx-1)

    def choose_skills(self):
        for item in self.data["Strategy"]["Skills"]:
            if parse_condition(item["Condition"], self, self.combat_info.get):
                self.use_skills(item["Targets"])

    def use_skills(self, skills):
        for skill in skills:
            if skill[0] == 0:
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

    def choose_cards(self):
        self.wait(4)
        if self.combat_info["BattleNow"] == 1:
            self.click_at_resource("宝具背景2")
        elif self.combat_info["BattleNow"] == 2:
            self.click_at_resource("宝具背景1")
        elif self.combat_info["BattleNow"] == 3:
            self.click_at_resource("宝具背景3")

        self.wait(1)
        cards = self.resources["Cards"]
        w, h = cards["Size"]
        cx, cy = cards.get("ClickOffset", (0, 0))
        cw, ch = cards.get("ClickSize", (w, h))

        for x, y in cards["Positions"]:
            click_rect = (x+cx, y+cy, x+cx+cw, y+cy+ch)
            rand_click(self.hwnd, click_rect)
            self.wait(1)


if __name__ == "__main__":
    fgo = FGOSimple("每日任务")
    while 1:
        fgo.check_scene()
