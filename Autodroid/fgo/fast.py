import re
from collections import defaultdict

from simulator.control import parse_condition
from simulator.win32_tools import rand_click, rand_drag
from fgo.fgo_simple import FGOSimple as FGOBase
from ocr.baidu_ocr import ocr

import logging

logger = logging.getLogger(__name__)


def choose_match(cards, items):
    for name in items:
        for card in cards[:]:
            if card[1] == name:
                cards.remove(card)
                return card


class AssistInfo(dict):
    """从者信息提取"""

    def __init__(self, fgo, offset):
        super().__init__()
        self.fgo = fgo
        self.image = self.fgo.crop_resource("助战从者定位", offset=offset)

    def check_servant_name(self, name):
        """确认助战从者是否为指定的从者"""
        info = self.fgo.resources["助战-从者模板"].copy()
        info.update({"Name": name, "Image": name + ".png"})
        self[name] = self.fgo.resource_in_image(info, image=self.image)
        logger.info("check_servant_name %s: %s", name, self[name])

    def check_servant_equip(self, name):
        """确认助战从者是否携带指定的礼装"""
        info = self.fgo.resources["助战-礼装模板"].copy()
        info.update({"Name": name, "Image": name + ".png"})
        self[name] = self.fgo.resource_in_image(info, image=self.image)
        logger.info("check_servant_equip %s: %s", name, self[name])

    def extract_skill_level(self, name):
        idx = int(name[name.find("/") + 1 :])
        skill_img = self.fgo.crop_resource("助战-技能", image=self.image, index=idx - 1)
        # TODO: 截图lvl 1-6资源
        for lvl in range(10, 6, -1):
            info = {
                "MainSize": [1280, 720],
                "Name": "技能{} vs Lv.{}".format(idx, lvl),
                "Image": "助战/技能/{}.png".format(lvl),
                "Type": "Dynamic",
                "MaxDiff": 0.1,
            }
            if self.fgo.resource_in_image(info, image=skill_img):
                self[name] = lvl
                return
        self[name] = 0

    def check(self, name):
        """判断助战从者是否满足指定条件"""
        if name in self:
            return self[name]
        if not isinstance(name, str):
            logger.info("Check For %s", repr(name))
            return name

        if name == "助战-宝具可用":
            try:
                light = self.fgo.crop_resource("助战-宝具", image=self.image).max()
                self[name] = light > 240
            except ValueError:
                self[name] = False
        elif name == "RecheckCount":
            self[name] = [s["Name"] for s in self.fgo.scene_history].count("助战选择")
        elif name in self.fgo.resources:
            self[name] = self.fgo.resource_in_image(name, image=self.image)
        elif name.startswith("助战/"):
            self.check_servant_name(name)
        elif name.startswith("礼装/"):
            self.check_servant_equip(name)
        elif name.startswith("技能/"):
            self.extract_skill_level(name)
        return self[name]


class FGOSimple(FGOBase):
    def parse_fight_condition(self, condition):
        return parse_condition(condition, self, self.combat_info.__getitem__)

    def check_assist(self):
        self.make_screen_shot()
        _, pos = self.search_resource("助战从者定位")
        for offset in pos:
            info = AssistInfo(self, offset)
            if parse_condition(
                self.data["Strategy"]["AssistCondition"], self, info.check
            ):
                logger.info("选择助战: %s", info)
                self.combat_info["AssitInfo"] = info
                self.click_at_resource("助战从者定位", offset=offset)
                return True
            logger.info("跳过助战: %s", info)
        return False

    def choose_skills(self):
        if self.combat_info["Turn"] == 1:
            self.wait_till_scene("选择技能", 1, 20)
            self.wait(3)
        for item in self.data["Strategy"]["Skills"]:
            if self.stop:
                return
            self.make_screen_shot()
            if self.parse_fight_condition(item.get("Condition", True)):
                logger.info("Skill Strategy Passed: %s", item)
                self.do_actions(item["Actions"])
            else:
                logger.info("Skill Strategy Skipped: %s", item)

    def is_skill_ready(self, index, name="从者"):
        """根据技能截图检查技能是否可用"""
        skill_img = self.crop_resource(name + "技能列表", index=index)
        line = self.crop_resource(name + "技能状态", image=skill_img)
        line = line.mean(axis=2)
        if line.std() < 1 and line.mean() > 100 and skill_img.std() > 10:
            return True
        if self.resource_in_image(name + "技能CD中", skill_img):
            return False
        return False

    def use_skills(self, *skills, check=True):
        self.make_screen_shot()
        for skill in skills:
            if self.stop:
                return
            name = "SkillCheck<{0}-{1}>".format(*skill)
            self.combat_info[name] = self.combat_info["Turn"]
            if skill[0] == 0:
                self.click_at_resource("御主技能")
                self.wait(1)
                target = "御主技能列表"
                index = skill[1] - 1

                self.make_screen_shot()
                if check and not self.is_skill_ready(index, "御主"):
                    # 为保证连续使用御主技能时不出错, 再次点击收回御主技能菜单
                    self.click_at_resource("御主技能")
                    self.wait(1)
                    logger.info("Ignore 御主技能: %s: %s %s", skill, target, index)
                    continue
            else:
                target = "从者技能列表"
                index = (skill[0] - 1) * 3 + (skill[1] - 1)

                if check and not self.is_skill_ready(index, "从者"):
                    logger.info("Ignore 从者技能: %s: %s %s", skill, target, index)
                    continue

            logger.debug("Use Skill %s: %s %s", skill, target, index)
            self.combat_info[name] = self.combat_info["Turn"]
            self.click_at_resource(target, index=index)
            self.wait(1)
            if len(skill) == 3:
                self.click_at_resource("技能目标列表", index=skill[2] - 1)
                self.wait(1)
            elif len(skill) == 4:
                self.click_at_resource("换人目标列表", index=skill[2] - 1)
                self.wait(1)
                self.click_at_resource("换人目标列表", index=skill[3] - 1)
                self.wait(1)
                self.click_at_resource("进行更替")
                self.wait(3)
                self.make_screen_shot()

            # self.make_screen_shot()
            self.wait_till_scene("选择技能", 0.5, 20)
            self.wait(0.5)

            if self.parse_scene_condition(["技能-关闭"]):
                self.click_at_resource("技能-关闭")
                self.wait(0.5)
            elif self.parse_scene_condition(
                ["$any", [["从者信息"], ["技能信息"], ["选择技能目标"], ["选择换人目标"]]]
            ):
                self.click_at_resource("右侧空白区域")
                self.wait(0.5)

            self.wait(0.5 + self.data["Strategy"].get("ExtraSkillInterval", 0.5))

    def choose_card_idx(self, card_names, order):
        """
        根据order中的顺序, 在card_names中搜索第一个匹配的指令卡,
        返回其下标
        """
        for item in order:
            for idx, card in enumerate(card_names):
                if re.search(item, card):
                    return idx
        return 0

    def choose_card(self, card_names, card_rects, order):
        """
        根据order中的顺序, 在card_names中搜索第一个匹配的指令卡,
        从选项中删除该卡, 返回该卡的名称、坐标
        """
        idx = self.choose_card_idx(card_names, order)
        result = [card_names[idx], card_rects[idx]]
        card_names.remove(card_names[idx])
        card_rects.remove(card_rects[idx])
        return result

    def choose_cards(self):
        choice = []
        choice_names = []
        if not self.combat_info:
            self.extract_combat_info()
        else:
            self.extract_np_info()
        logger.info("CombatInfo: %s", self.combat_info)

        for check in self.data["Strategy"]["UseNP"]:
            idx = check["Target"]
            if self.combat_info["NP%d" % idx] >= 100 and self.parse_fight_condition(
                check["Condition"]
            ):
                name = "宝具%s" % (check["Target"])
                logger.info(
                    "使用宝具: %s(NP=%s, Condition=%s)",
                    name,
                    self.combat_info["NP%d" % idx],
                    check["Condition"],
                )
                choice.append(self.get_resource_rect(name))
                choice_names.append(name)

        self.wait(1)
        cards = self.resources["Cards"]
        w, h = cards["Size"]
        cx, cy = cards.get("ClickOffset", (0, 0))
        cw, ch = cards.get("ClickSize", (w, h))

        card_names = []
        card_rects = []
        for x, y in cards["Positions"]:
            card_img = self.crop_resource("Cards", offset=[x, y])
            click_rect = (x + cx, y + cy, x + cx + cw, y + cy + ch)
            card_names.append(self.extract_card_info(card_img))
            card_rects.append(click_rect)

        found_names = card_names.copy()
        card_choice = []
        for card_choice in self.data["Strategy"]["CardChoice"]:
            if self.parse_fight_condition(card_choice["Condition"]):
                break
        logger.info("CardChoice Strategy=%s", card_choice)
        choice += [None, None, None]
        choice_names += ["", "", ""]
        for idx, order in card_choice["Choice"]:
            if choice[idx] is None:
                name, rect = self.choose_card(card_names, card_rects, order)
                choice[idx] = rect
                choice_names[idx] = name

        logger.info("Found Cards %s", found_names)
        logger.info("Choose Cards %s", choice_names[:3])

        for rect in choice:
            if rect is not None:
                rand_click(self.hwnd, rect)
                self.wait(0.5)

        for rect in card_rects:
            rand_click(self.hwnd, rect)
            self.wait(0.5)

    def choose_exp_cards(self, cols=3, rows=7, stop=False):
        info = self.resources["卡位列表"]
        x0, y0 = info["Offset"]
        dx, dy = info["PositionDelta"]
        start = (x0, y0)
        end = (x0 + dx * 7, y0 + dy * 3)
        rand_drag(self.hwnd, start, end, start_delay=1)
        self.wait(1)


if __name__ == "__main__":
    # fgo = FGOSimple("刷材料")
    # fgo = FGOSimple("主号换人礼装速刷")
    fgo = FGOSimple("主号赝作速刷")

    count = 0
    while 1:
        fgo.check_scene()
        print(fgo.current_scene_name)
        if fgo.current_scene_name == "获得物品":
            count += 1
            print(fgo.current_scene_name, count)
            if count >= 1:
                fgo.manual()
                break
