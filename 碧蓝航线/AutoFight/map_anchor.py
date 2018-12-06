import os
import time

import numpy as np

from config import logger
from image_tools import cv_imread, cv_crop, get_match, get_window_shot
from win32_tools import drag, click_at


def ord_distance(a, b):
    # 计算2个棋盘坐标的加权曼哈顿距离
    dist = 0
    for ca, cb, weight in zip(a, b, [2, 1]):
        dist += abs(ord(ca) - ord(cb)) * weight
    return dist


def get_map_pos(origin, origin_name, target_name):
    # 根据锚点的像素坐标、锚点的棋盘坐标、目标点的棋盘坐标，计算目标点的像素坐标
    dx, dy = target_name
    x0, y0 = origin_name
    dx = ord(dx) - ord(x0)
    dy = ord(dy) - ord(y0)
    x = origin[0] + 120 * dx
    y = origin[1] + 90 * dy
    logger.debug("找到%s: (%d, %d)", target_name, x, y)
    return x, y


class FightMap:
    def __init__(self, hwnd, anchors, ):
        self.hwnd = hwnd
        self.anchors = anchors

    def move_map_to(self, x, y):
        # 移动战斗棋盘使目标点趋近中心位置
        diff_x = 580 - x
        diff_y = 380 - y
        drag(self.hwnd, (580, 380), (580 + diff_x, 380 + diff_y))
        time.sleep(1)

    def click_at_map(self, target):
        # 根据棋盘坐标点击战斗地图
        logger.info("搜索%s", target)
        image = get_window_shot(self.hwnd)
        target_pos = None
        self.anchors.sort(key=lambda a: ord_distance(a['OnMap'], target))
        for anchor in self.anchors:
            anchor_img = cv_imread(os.path.join("images", anchor['Name']))
            diff, anchor_pos = get_match(image, anchor_img)
            if diff < anchor.get("MaxDiff", 0.05):
                map_anchor = anchor_pos + np.array(anchor['Translate'])
                logger.debug("找到%s(%.3f): %s. 坐标%s:%s",
                             anchor['Name'], diff, anchor_pos, anchor['OnMap'], map_anchor)
                target_pos = get_map_pos(map_anchor, anchor['OnMap'], target)
                break
            logger.debug("未找到%s. 最优结果%.3f.", anchor['Name'], diff)

        if target_pos is None:
            logger.debug("未找到anchor, 重置地图")
            self.move_map_to(2000, 1000)
            self.move_map_to(300, 0)
            return self.click_at_map(target)

        x, y = target_pos
        x_min, y_min, x_max, y_max = (135, 215, 1210, 625)
        if x < x_min or x > x_max or y < y_min or y > y_max:
            logger.debug("目标不在中间区域")
            self.move_map_to(x, y)
            return self.click_at_map(target)
        else:
            logger.debug("点击%s: (%d, %d)", target, x, y)
            click_at(self.hwnd, x, y)
