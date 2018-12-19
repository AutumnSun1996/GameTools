import numpy as np


from config import config
from image_tools import cv_crop, extract_text, get_all_match, get_match
from win32_tools import rand_click, drag
from baidu_ocr import ocr
from simulator import SimulatorControl


class Servant:
    def __init__(self, control: SimulatorControl):
        self.s = control
        self.info = {}

    def update_from_select(self, image, offset):
        self.offset = offset
        sub_image = {}
        for name in ['礼装', '等级', '职阶', '宝具', '技能']:
            sub_image[name] = cv_crop(image, self.s.get_resource_rect('助战选择-从者-%s' % name))
        info = {}

    def update_from_combat(self, info):
        self.info.update(info)


class FateGrandOrder(SimulatorControl):
    def __init__(self):
        super().__init__()
        self.combat_info = {
            "BattleNow": None,
            "BattleTotal": None,
            "EnemyLeft": None,
            "Turn": None
        }
        self.best_equips = []

    def servant_scroll(self, line):
        _, top_xy = self.resource_in_screen("滚动条-上")
        _, bot_xy = self.resource_in_screen("滚动条-下")
        top = top_xy[1]
        bottom = bot_xy[1]
        x = (top_xy[0] + bot_xy[0]) // 2
        middle = (top + bottom) // 2
        cross = bottom - top
        dy = line * cross * 0.37
        drag(self.hwnd, (x, middle), (x, middle + dy), 30)

    def servant_scroll_to_top(self):
        _, top_xy = self.resource_in_screen("滚动条-上")
        _, bot_xy = self.resource_in_screen("滚动条-下")
        top = top_xy[1]
        bottom = bot_xy[1]
        x = (top_xy[0] + bot_xy[0]) // 2
        middle = (top + bottom) // 2
        drag(self.hwnd, (x, middle), (x, 0), 30)

    def choose_servant(self):
        for target in self.best_equips:
            ret, rect = self.equipment_check(target)
            if ret:
                rand_click(self.hwnd, rect)
                return

    def equipment_check(self, target):
        res = self.resources['最后登录']
        equip = self.resources['助战选择-从者-礼装']
        w, h = equip['Size']
        dx, dy = res['Offset']
        ex, ey = equip['Offset']
        lt, rb = res['SearchArea']
        match = get_all_match(self.screen, res['ImageData'])
        for y, x in zip(*np.where(match < res.get("MaxDiff", 0.05))):
            if not (lt[0] < x < rb[0] and lt[1] < y < rb[1]):
                continue
            sx = x+dx+ex
            sy = y+dy+ey
            equip_image = cv_crop(self.screen, (sx, sy, sx+w, sy+h))
            diff, _ = get_match(equip_image, target['ImageData'])
            if diff < target.get("MaxDiff", 0.05):
                return True, [sx, sy, sx+w, sy+h]
        return False, None

    def get_servant_info(self):
        pass

    def extract_combat_info(self):
        battle = cv_crop(self.screen, self.get_resource_rect("战斗轮次"))
        now, total = extract_text(battle, 22, '12345/').split('/')
        self.combat_info['BattleNow'] = int(now)
        self.combat_info['BattleTotal'] = int(total)

        enemies = cv_crop(self.screen, self.get_resource_rect("剩余敌人"))
        self.combat_info['EnemyLeft'] = int(extract_text(enemies, 22))

        turn = cv_crop(self.screen, self.get_resource_rect("回合数"))
        self.combat_info['Turn'] = int(extract_text(turn, 22))

    def choose_skill(self):
        self.extract_combat_info()
        if self.combat_info['Turn'] == 1:
            for c, s in [(1, 1), (1, 2), (2, 1), (2, 2), (2, 3)]:
                self.click_at_resource("角色%d技能%d" % (c, s))
                self.wait_till_scene("选择技能")
                self.wait(0.2)

    def update_background(self):
        """保存当前画面为宝具背景, 供之后的分析使用
        """
        for i in range(3):
            name = '宝具背景%d' % (i+1)
            rect = self.get_resource_rect(name)
            self.resources[name]['ImageData'] = cv_crop(self.screen, rect).copy()

    def choose_match(self, image, candidates):
        best = None
        best_diff = 1
        for name in candidates:
            data = self.resources[name]
            diff, _ = get_match(image, data['ImageData'])
            if diff < best_diff:
                best_diff = diff
                best = name
        return best_diff, best

    def extract_card_info(self):
        for cards in ['Buster', 'Arts', 'Quick']:
            pass

    def choose_card(self):
        pass


if __name__ == "__main__":
    fgo = FateGrandOrder()
    print(fgo.resources.keys())
    print(fgo.resources['战斗速度']['ImageData'].shape)
    fgo.update_current_scene()
    print(fgo.scene_history)
    # fgo.extract_combat_info()
    # print(fgo.combat_info)
    # fgo.click_at_resource("Attack")
