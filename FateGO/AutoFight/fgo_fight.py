import numpy as np

from image_tools import cv_crop, extract_text, get_all_match, get_match
from simulator import SimulatorControl


class FateGrandOrder(SimulatorControl):
    def __init__(self):
        super().__init__()
        self.combat_info = {
            "BattleNow": None,
            "BattleTotal": None,
            "EnemyLeft": None,
            "Turn": None
        }

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
        """保存当前画面为背景, 供之后的分析使用
        """
        for i in range(3):
            name = '宝具背景%d' % (i+1)
            rect = self.get_resource_rect(name)
            self.resources[name]['ImageData'] = cv_crop(self.screen, rect)

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