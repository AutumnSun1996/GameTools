import time

import numpy as np

from config import logger, config
from image_tools import get_match
from win32_tools import drag, click_at

from azurlane import AzurLaneControl


def get_map_pos(origin, origin_name, target_name):
    """根据锚点的像素坐标、锚点的棋盘坐标、目标点的棋盘坐标，计算目标点的像素坐标"""
    dx, dy = target_name
    x0, y0 = origin_name
    # 越靠下的格子越宽, 对该情况做一个简单的线性拟合
    diff = 1 + (ord(dy) - ord('1')) / 30
    dx = ord(dx) - ord(x0)
    dy = ord(dy) - ord(y0)
    x = int(np.round(origin[0] + config.getint("Device", "CellWidth") * dx * diff))
    y = int(np.round(origin[1] + config.getint("Device", "CellHeight") * dy))
    return x, y


def ord_distance(a, b):
    """计算2个棋盘坐标的实际距离. 该值大致反映了定位的误差大小"""
    dist = get_map_pos((0, 0), a, b)
    return np.linalg.norm(dist)


class FightMap(AzurLaneControl):
    """地图操作"""
    map_name = None

    def __init__(self):
        super().__init__()
        self.anchors = None

    def move_map_to(self, x, y):
        """移动战斗棋盘使目标点趋近中心位置"""
        x_min, y_min, x_max, y_max = self.get_resource_rect("可移动区域")
        center_x = (x_min + x_max) / 2
        center_y = (y_min + y_max) / 2
        diff_x = center_x - x
        diff_y = center_y - y
        drag(self.hwnd, (center_x, center_y), (center_x + diff_x, center_y + diff_y))
        time.sleep(1)

    def reset_map(self):
        """重置战斗棋盘位置"""
        x_min, y_min, x_max, y_max = self.get_resource_rect("可移动区域")
        for i in range(3):
            self.move_map_to(x_max, y_max)
            time.sleep(0.2)
        self.move_map_to(x_min, y_min)

    def locate_target(self, target, reshot=True):
        """搜索指定的棋盘坐标, 返回像素坐标"""
        if reshot:
            self.make_screen_shot()
        if self.anchors is None:
            self.anchors = [val for val in self.resources.values()
                            if val["Type"] == "Anchor" and val["MapName"] == self.map_name]

        self.anchors.sort(key=lambda a: ord_distance(a['OnMap'], target))
        # max_len = 3 * len(self.anchors) // 4
        for anchor in self.anchors:
            diff, anchor_pos = get_match(self.screen, anchor["ImageData"])
            if diff < anchor.get("MaxDiff", 0.05):
                map_anchor = anchor_pos + np.array(anchor['Offset'])
                logger.debug("找到%s(%.3f): %s. 坐标%s:%s",
                             anchor['Name'], diff, anchor_pos, anchor['OnMap'], map_anchor)
                return get_map_pos(map_anchor, anchor['OnMap'], target)
            logger.debug("未找到%s. 最优结果%.3f.", anchor['Name'], diff)
        return None

    def click_at_map(self, target, repeat=0):
        """点击指定的棋盘坐标"""
        if not self.resource_in_screen("迎击"):
            logger.warning("非战斗地图. 停止搜索目标")
            return
        if repeat >= 5:
            self.critical("地图搜索失败")

        # 根据棋盘坐标点击战斗地图
        logger.debug("搜索%s", target)

        target_pos = self.locate_target(target)
        if not target_pos:
            logger.debug("未找到anchor, 重置地图")
            self.reset_map()
            self.click_at_map(target, repeat+1)
            return

        x, y = target_pos
        x_min, y_min, x_max, y_max = self.get_resource_rect("可移动区域")
        if x < x_min or x > x_max or y < y_min or y > y_max:
            logger.debug("目标不在中间区域")
            self.move_map_to(x, y)
            self.click_at_map(target, repeat+1)
            return
        logger.info("点击%s: (%d, %d)", target, x, y)
        click_at(self.hwnd, x, y)
