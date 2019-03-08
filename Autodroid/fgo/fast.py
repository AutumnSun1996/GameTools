import re
from collections import defaultdict

from simulator.control import parse_condition
from simulator.win32_tools import rand_click
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
        names = self.fgo.assist_servant_names
        if isinstance(names, str):
            names = re.findall(r"\w+", names)
        self.servant_names = set(names)

        names = self.fgo.assist_equip_names
        if isinstance(names, str):
            names = re.findall(r"\w+", names)
        self.equip_names = set(names)

    def check_servant_name(self, name):
        """确认助战从者是否为指定的从者"""
        info = {
            "Name": name,
            "MainSize": [1280, 720],
            "SearchArea": [[300, 60], [420, 100]],
            "Size": [400, 32],
            "Type": "Dynamic",
            "Image": name+".png"
        }
        self[name] = self.fgo.resource_in_image(info, image=self.image)
        logger.info("check_servant_name %s: %s", name, self[name])

    def check_servant_equip(self, name):
        """确认助战从者是否携带指定的礼装"""
        info = {
            "Name": name,
            "MainSize": [1280, 720],
            "Offset": [5, 135],
            "Size": [158, 45],
            "Type": "Static",
            "Image": name+".png"
        }
        self[name] = self.fgo.resource_in_image(info, image=self.image)
        logger.info("check_servant_equip %s: %s", name, self[name])

    def check(self, name):
        """判断助战从者是否满足指定条件"""
        if name in self:
            return self[name]

        if name == "助战-宝具可用":
            self[name] = self.fgo.crop_resource("助战-宝具", image=self.image).max() > 240
        elif name == "RecheckCount":
            self[name] = [s["Name"] for s in self.fgo.scene_history].count("助战选择")
        elif name.startswith("助战-") and name[3:] in self.servant_names:
            self.check_servant_name(name)
        elif name.startswith("礼装-") and name[3:] in self.equip_names:
            self.check_servant_equip(name)
        else:
            self[name] = self.fgo.resource_in_image(name, image=self.image)

        return self[name]


class FGOSimple(FGOBase):
    def check_assist(self):
        self.make_screen_shot()
        _, pos = self.search_resource("助战从者定位")
        for offset in pos:
            info = AssistInfo(self, offset)
            if parse_condition(self.data['Strategy']['AssistCondition'], self, info.check):
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
            self.make_screen_shot()
            if parse_condition(item.get("Condition", True), self, self.combat_info.__getitem__):
                logger.info("Skill Strategy Passed: %s", item)
                self.do_actions(item["Actions"])
            else:
                logger.info("Skill Strategy Skipped: %s", item)

    def use_skills(self, *skills):
        for skill in skills:
            self.combat_info["SkillCheck<{0}-{1}>".format(*skill)] = self.combat_info["Turn"]
            if skill[0] == 0:
                self.click_at_resource("御主技能")
                self.wait(1)
                target = "御主技能列表"
                index = skill[1] - 1

                skill_img = self.crop_resource(target, index=index)
                if self.resource_in_image("御主技能-还剩", skill_img):
                    # 为保证连续使用御主技能时不出错, 再次点击收回御主技能菜单
                    self.click_at_resource("御主技能")
                    self.wait(1)
                    logger.debug("Ignore 御主技能 For CD: %s: %s %s", skill, target, index)
                    continue
            else:
                target = "从者技能列表"
                index = (skill[0]-1) * 3 + (skill[1] - 1)

                skill_img = self.crop_resource(target, index=index)
                if self.resource_in_image("从者技能-剩余", skill_img):
                    logger.debug("Ignore 从者技能 For CD: %s: %s %s", skill, target, index)
                    continue

            logger.debug("Use Skill %s: %s %s", skill, target, index)
            self.combat_info["SkillUse<{0}-{1}>".format(*skill)] = self.combat_info["Turn"]
            self.click_at_resource(target, index=index)
            self.wait(1)
            if len(skill) == 3:
                self.click_at_resource("技能目标列表", index=skill[2]-1)
                self.wait(1)
            elif len(skill) == 4:
                self.click_at_resource("换人目标列表", index=skill[2]-1)
                self.wait(1)
                self.click_at_resource("换人目标列表", index=skill[3]-1)
                self.wait(1)
                self.click_at_resource("进行更替")
                self.wait(3)

            # self.wait(1)
            self.make_screen_shot()
            self.wait_till_scene("选择技能", 0.5, 20)
            self.wait(0.5)

            if self.parse_scene_condition([["技能无法使用"]]):
                self.click_at_resource("关闭")
                self.wait(0.5)
                self.make_screen_shot()
            elif self.parse_scene_condition(["$any", [["从者信息"], ["技能信息"], ["选择技能目标"], ["选择换人目标"]]]):
                self.click_at_resource("右侧空白区域")
                self.wait(0.5)
                self.make_screen_shot()

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
        if not self.combat_info:
            self.extract_combat_info()
        else:
            self.extract_np_info()
        logger.info("CombatInfo: %s", self.combat_info)

        for check in self.data["Strategy"]["UseNP"]:
            idx = check["Target"]
            if self.combat_info["NP%d" % idx] >= 100 and\
                    parse_condition(check["Condition"], self, self.combat_info.__getitem__):
                name = "宝具%s" % (check["Target"])
                logger.info("使用宝具: %s(NP=%s, Condition=%s)", name, self.combat_info["NP%d" % idx], check["Condition"])
                choice.append(self.get_resource_rect(name))

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

        card_choice = []
        for card_choice in self.data["Strategy"]["CardChoice"]:
            if parse_condition(card_choice["Condition"], self, self.combat_info.__getitem__):
                break

        choice += [None, None, None]
        for idx, order in card_choice["Choice"]:
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
