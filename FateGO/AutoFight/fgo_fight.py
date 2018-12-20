import numpy as np


from config import config
from image_tools import cv_crop, extract_text, get_all_match, get_match
from win32_tools import rand_click, drag
from baidu_ocr import ocr
from simulator import SimulatorControl
try:
    __builtin__ = __builtins__
except NameError:
    pass


def parse_condtion(cond, obj):
    """通用条件解析"""
    if isinstance(cond, list) and cond:
        # 仅对非空的list进行解析
        if cond[0] in {"$sum", "$all", "$any", "$max", "$min"}:
            cmd = getattr(__builtin__, cond[0][1:])
            cond = cmd((parse_condtion(sub, obj) for sub in cond[1:]))
        elif cond[0] in {"$chr", "$bool", "$int", "$float", "$ord", "$len"}:
            cmd = getattr(__builtin__, cond[0][1:])
            cond = cmd(parse_condtion(cond[1], obj))
        elif cond[0] in {"$eq", "$gt", "$ge", "$ne", "$lt", "$le"}:
            cmd = getattr(parse_condtion(cond[1], obj), "__%s__" % cond[0][1:])
            cond = cmd(parse_condtion(cond[2], obj))
        elif cond[0] == "$not":
            cond = not parse_condtion(cond[1], obj)
        elif cond[0] == "$attr":
            if len(cond) == 2:
                cond = getattr(obj, parse_condtion(cond[1], obj))
            else:
                cond = getattr(parse_condtion(cond[1], obj), parse_condtion(cond[2], obj))
        elif cond[0] == "$val":
            if len(cond) == 2:
                cond = obj[parse_condtion(cond[1], obj)]
            else:
                cond = obj[parse_condtion(cond[1], obj), parse_condtion(cond[2], obj)]
    return cond


def contact_images(*images, sep=1):
    """将多张图片纵向拼接

    用于一次性识别多个字段
    """
    width = max([images.shape[1] for images in images])
    height = sum([images.shape[0] + sep for images in images]) - sep
    background = np.zeros((height, width, 3), dtype='uint8')
    x = 0
    y = 0
    for image in images:
        h, w = image.shape[:2]
        background[y:y+h, x:x+w, :] = image
        y += h + sep
    return background


class AssistServant:
    def __init__(self, control, offset):
        self.s = control
        self.offset = offset
        self.info = {}

    def update_from_select(self, image, offset):
        self.offset = offset
        sub_image = {}
        for name in ['礼装', '等级', '职阶', '宝具', '技能']:
            sub_image[name] = cv_crop(image, self.s.get_resource_rect('助战选择-从者-%s' % name))
        info = {}

    def update_from_combat(self, info):
        self.info.update(info)


class CombatServant:
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

    def crop_resource(self, name, offset=None, image=None):
        if offset is None:
            dx, dy = 0, 0
        else:
            dx, dy = offset
        if image is None:
            image = self.screen
        x, y, x1, y1 = self.get_resource_rect(name)
        return cv_crop(image, (x+dx, y+dy, x1+dx, y1+dy))

    def choose_assist_servant(self, wanted_score):
        for target in self.best_equips:
            score, rect = self.assist_score(target)
            if score > wanted_score:
                rand_click(self.hwnd, rect)
                return
        self.servant_scroll_to_top()
        ret, pos = self.resource_in_screen("最后登录")

    def assist_score(self, target):
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

    def extract_combat_info(self):
        info = ocr.image2text(contact_images(
            self.crop_resource("战斗轮次"),
            self.crop_resource("剩余敌人"),
            self.crop_resource("回合数"),
        ))

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
