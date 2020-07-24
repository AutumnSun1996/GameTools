"""
碧蓝航线战斗棋盘地图分析和定位
"""
import time
import json
import itertools

from shapely import geometry
import numpy as np

from config_loader import logger, config
from simulator.image_tools import get_match, cv, get_multi_match, load_map, cv_crop
from simulator.win32_tools import drag, click_at, rand_click

from .azurlane import AzurLaneControl


trans_matrix = np.mat(
    [
        [0.9433189178530791, 0.2679732964804766, -158.43695741776074],
        [1.3417181644390942e-05, 1.5656008796635157, -92.70256198000683],
        [7.711117850185767e-07, 0.0005944962831996344, 1.0],
    ]
)
filter_kernel = np.array([[-4, -2, -4], [-2, 24, -2], [-4, -2, -4]])
target_size = (980, 725)
_, inv_trans = cv.invert(trans_matrix)
inv_trans = inv_trans / inv_trans[2, 2]


def ord_distance(anchor_name, target_name):
    """计算2个棋盘坐标的距离. 该值大致反映了定位的误差大小"""
    dx = (ord(target_name[0]) - ord(anchor_name[0])) * 100
    dy = (ord(target_name[1]) - ord(anchor_name[1])) * 100
    return np.linalg.norm([dx, dy])


def search_on_map(info, screen, pos_in_screen):
    offset = info["CropOffset"]
    size = info["CropSize"]
    wh = np.array(list(reversed(screen.shape[:2])))
    coef = 0.0005907301142274507

    diff_s = []
    results = []
    for x, y in pos_in_screen:
        r = coef * y + 1
        lt = np.asarray(offset) * r + [x, y]
        rb = lt + np.asarray(size) * r
        if lt.min() < 0:
            continue
        if np.any(rb > wh):
            continue
        part = cv_crop(screen, (*lt.astype("int"), *rb.astype("int")))
        part = cv.resize(part, tuple(size))
        diff, _ = get_match(part, info["ImageData"])
        if diff < info.get("MaxDiff", 0.2):
            diff_s.append(diff)
            results.append([x, y])
    logger.debug(
        "search_on_map found %s with diff%sfor %s", results, diff_s, info["Name"]
    )
    return diff_s, results


def on_map_offset(name):
    x = 100 * (ord(name[0]) - ord("A"))
    y = 100 * (ord(name[1]) - ord("1"))
    return [x, y]


class FightMap(AzurLaneControl):
    """地图操作"""

    map_name = None

    def __init__(self, map_name=None):
        super().__init__(map_name)
        self._pos_in_screen = None

    def save_record(self, prefix=None, area=None, **extra_kwargs):
        if "comment" not in extra_kwargs:
            extra_kwargs["comment"] = {}
        extra_kwargs["comment"]["MapName"] = self.map_name
        super().save_record(prefix, area, **extra_kwargs)

    def get_grid_centers(self):
        """返回格子中心点坐标列表，包括棋盘坐标和屏幕坐标"""
        warped = cv.warpPerspective(self.screen, trans_matrix, target_size)
        filtered_map = cv.filter2D(warped, 0, filter_kernel)
        _, poses = self.search_resource("Corner", image=filtered_map)
        if len(poses) < 3:
            raise RuntimeError("Less than 4 anchors found. ")

        poses = np.array(poses)
        poses += self.resources["Corner"]["Offset"]
        diff = poses % 100
        dx = np.argmax(np.bincount(diff[:, 0]))
        dy = np.argmax(np.bincount(diff[:, 1]))

        res = itertools.product(
            range(dx, target_size[0], 100), range(dy, target_size[1], 100)
        )
        res = (np.array(list(res), dtype="float") + 50).reshape(1, -1, 2)

        pos_in_screen = (
            cv.perspectiveTransform(res, inv_trans).reshape(-1, 2).astype("int")
        )
        return res.reshape(-1, 2), pos_in_screen

    @property
    def pos_in_screen(self):
        if self._pos_in_screen is None:
            _, self._pos_in_screen = self.get_grid_centers()
        return self._pos_in_screen

    def make_screen_shot(self):
        self._pos_in_screen = None
        return super().make_screen_shot()

    def screen2grid(self, image_pos):
        """根据透视变换矩阵将像素坐标变换到棋盘坐标"""
        image_pos = np.array([image_pos], dtype="float32").reshape((1, 1, 2))
        return cv.perspectiveTransform(image_pos, trans_matrix).reshape((2))

    def grid2screen(self, square_pos):
        """根据透视变换矩阵将棋盘坐标变换到像素坐标"""
        square_pos = np.array([square_pos], dtype="float32").reshape((1, 1, 2))
        return cv.perspectiveTransform(square_pos, inv_trans).reshape((2))

    def get_map_pos(self, anchor_name, anchor_pos, target_name):
        """根据锚点的像素坐标、锚点的棋盘坐标、目标点的棋盘坐标，计算目标点的像素坐标
        棋盘坐标名与棋盘坐标转换关系为"A1" => [0, 0], "B2" => [100, 100]
        """
        if isinstance(target_name, str):
            target_name = tuple(target_name)

        if isinstance(target_name[0], str):
            dx = (ord(target_name[0]) - ord(anchor_name[0])) * 100
        else:
            dx = target_name[0] - (ord(anchor_name[0]) - ord("A")) * 100
        if isinstance(target_name[1], str):
            dy = (ord(target_name[1]) - ord(anchor_name[1])) * 100
        else:
            dy = target_name[1] - (ord(anchor_name[1]) - ord("1")) * 100
        virtual_anchor_pos = self.screen2grid(anchor_pos)
        virtual_target_pos = np.add(virtual_anchor_pos, [dx, dy])
        target_pos = self.grid2screen(virtual_target_pos)
        return target_pos

    def move_map_to(self, x, y):
        """移动战斗棋盘使目标点趋近中心位置"""
        x_min, y_min, x_max, y_max = self.get_resource_rect("可移动区域")
        center_x = (x_min + x_max) / 2
        center_y = (y_min + y_max) / 2
        diff_x = center_x - x
        diff_y = center_y - y
        drag(self.hwnd, (center_x, center_y), (center_x + diff_x, center_y + diff_y))
        self.wait(2)

    def reset_map(self):
        """重置战斗棋盘位置"""
        x_min, y_min, x_max, y_max = self.get_resource_rect("可移动区域")
        for i in range(3):
            self.move_map_to(x_max, y_max)
            self.wait(0.2)
        self.move_map_to(x_min, y_min)

    def locate_target(self, target, reshot=True):
        """搜索指定的棋盘坐标, 返回像素坐标"""
        if reshot:
            self.make_screen_shot()
        name, pos = self.get_best_anchor()
        return True, self.get_map_pos(name, pos, target)

    def click_at_map(self, target, repeat=0):
        """点击指定的棋盘坐标
        param: target: str, 如 'D2', 'B5'
        """
        if not self.resource_in_screen("迎击"):
            logger.warning("非战斗地图. 停止搜索目标")
            return
        if repeat >= 5:
            self.critical("地图搜索失败")

        # 根据棋盘坐标点击战斗地图
        logger.debug("搜索%s", target)

        ret, target_pos = self.locate_target(target)
        if not ret:
            logger.debug("未找到anchor, 重置地图")
            self.reset_map()
            FightMap.click_at_map(self, target, repeat + 1)
            return

        x, y = target_pos
        points = np.reshape(self.resources["地图区域"]["Points"], (1, -1, 2)).astype(
            "float32"
        )
        # 需要检查四个角落
        for dx, dy in itertools.product([-20, 20], [-30, 10]):
            if cv.pointPolygonTest(points, (x + dx, y + dy), False) < 0:
                logger.debug("目标不在中间区域")
                self.move_map_to(x, y)
                FightMap.click_at_map(self, target, repeat + 1)
                return
        logger.info("点击%s: (%d, %d)", target, x, y)
        rand_click(self.hwnd, (x - 10, y - 20, x + 10, y), 0)

    def get_best_anchor(self):
        """在屏幕上搜索最佳的锚点
        当前使用匹配程度最高的锚点
        """
        res = []
        for anchor in self.data["Anchors"].values():
            diff, found = search_on_map(anchor, self.screen, self.pos_in_screen)
            # logger.debug("Check anchor %s: %s, %s", anchor["Name"], diff, found)
            if not diff:
                continue
            pos = found[np.argmin(diff)]
            return anchor["OnMap"], pos
        self.reset_map()
        raise RuntimeError("No Valid Anchor")

    def find_on_map(self, anchor_name, anchor_pos, target_name, reshot=True):
        """在屏幕上搜索并返回指定的anchor出现的所有棋盘坐标"""
        if reshot:
            self.make_screen_shot()
        anchor_pos_grid = self.screen2grid(anchor_pos)
        logger.debug("find_on_map %s by %s at %s", target_name, anchor_name, anchor_pos)
        target = self.resources[target_name]
        name_x, name_y = anchor_name

        points = np.reshape(self.resources["地图区域"]["Points"], (1, -1, 2)).astype(
            "float32"
        )
        _, pos = search_on_map(target, self.screen, self.pos_in_screen)
        results = set()
        for x, y in pos:
            if cv.pointPolygonTest(points, (x, y), False) < 0:
                # 不在地图区域内, 忽略
                continue
            offset = self.screen2grid((x, y)) - anchor_pos_grid
            dx, dy = np.round(offset / 100).reshape((2)).astype("int")
            name = chr(ord(name_x) + dx) + chr(ord(name_y) + dy)
            results.add(name)
        logger.debug(
            "find_on_map %s by %s at %s: %s",
            target_name,
            anchor_name,
            anchor_pos,
            results,
        )
        return results
