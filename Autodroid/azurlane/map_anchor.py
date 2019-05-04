"""
碧蓝航线战斗棋盘地图分析和定位
"""
import time
import itertools

from shapely import geometry
import numpy as np

from config_loader import logger, config
from simulator.image_tools import get_match, cv, get_multi_match, load_map
from simulator.win32_tools import drag, click_at

from .azurlane import AzurLaneControl


trans_matrix = np.mat([[0.9973946527568224, 0.3603604397038424, -26.031979896145074],
                       [0.0003077413569570231, 1.6993955643161198, -11.85941523333576],
                       [1.341898625115588e-06, 0.0005934941602383196, 1.0]])


def ord_distance(anchor_name, target_name):
    """计算2个棋盘坐标的距离. 该值大致反映了定位的误差大小"""
    dx = (ord(target_name[0]) - ord(anchor_name[0])) * 100
    dy = (ord(target_name[1]) - ord(anchor_name[1])) * 100
    return np.linalg.norm([dx, dy])

def get_anchors(self):
    """在屏幕上搜索匹配的锚点
    """
    res = []
    for anchor in self.data['Anchors'].values():
        logger.debug("Check Anchor %s", anchor['Name'])
        diff, pos = get_match(self.screen, anchor['ImageData'])
        pos = np.add(pos, anchor['Offset'])
        if diff < anchor.get("MaxDiff", 0.03):
            res.append([pos, anchor['OnMap']])
    return res

def get_max_convex(anchors, count=4):
    if len(anchors) < count:
        raise ValueError("Need At Least %d anchors, got %d" % (count, len(anchors)))
    best = None
    best_area = 0
    for idx in itertools.combinations(range(len(anchors)), count):
        poly = geometry.Polygon([anchors[i][0] for i in idx]).convex_hull
        area = poly.area
        if best_area < area:
            best_area = area
            best = idx
    return [anchors[i] for i in best]

def on_map_offset(name):
    x = 100 * (ord(name[0]) - ord("A"))
    y = 100 * (ord(name[1]) - ord("1"))
    return [x, y]

def get_perspective_transform(anchors):
    src = []
    dst = []
    for anchor in anchors:
        src.append(anchor[0])
        dst.append(on_map_offset(anchor[1]))
    src = np.reshape(src, (-1, 2)).astype("float32")
    dst = np.reshape(dst, (-1, 2)).astype("float32")
    matrix, mask = cv.findHomography(src, dst)
    return matrix

def name2pos(name, matrix):
    inv = np.linalg.inv(matrix)
    inv /= inv[2, 2]
    src = on_map_offset(name)
    src = np.reshape(src, (1, -1, 2)).astype("float32")
    return cv.perspectiveTransform(src, inv).reshape(2)

def pos2name(pos, matrix):
    src = np.reshape(pos, (1, -1, 2)).astype("float32")
    x, y = cv.perspectiveTransform(src, matrix).reshape(2)
    x = chr(int(np.round(ord("A") + x/100)))
    y = chr(int(np.round(ord("1") + y/100)))
    return x+y


class FightMap(AzurLaneControl):
    """地图操作"""
    map_name = None

    def __init__(self, map_name=None):
        super().__init__()
        if map_name is None:
            return
        self.map_name = map_name
        self.data = load_map(self.map_name, self.section)
        logger.info("Update Resources %s", self.data['Resources'].keys())
        self.resources.update(self.data['Resources'])
        logger.info("Update Scenes %s", self.data['Scenes'].keys())
        self.scenes.update(self.data['Scenes'])
        self._trans_matrix = None
        self._inv_trans = None

    def update_trans_matrix(self):
        anchors = get_anchors(self)
        logger.info("Found %d Anchors", len(anchors))
        if len(anchors) >= 4:
            logger.debug("Anchors: %s", anchors)
            self._trans_matrix = get_perspective_transform(anchors)
            if self._trans_matrix is None or self._trans_matrix[1][1] < 0:
                logger.warning("Discard Bad TransMatrix. (%s From %s)", self._trans_matrix, anchors)
                self._trans_matrix = None
        if self._trans_matrix is None:
            if "TransMatrix" in self.data:
                logger.info("Update Trans Matrix With Map Defined Matrix")
                self._trans_matrix = np.mat(self.data["TransMatrix"])
            else:
                logger.info("Update Trans Matrix With Global Matrix")
                self._trans_matrix = trans_matrix
        _, self._inv_trans = cv.invert(self._trans_matrix)

    @property
    def trans_matrix(self):
        if self._trans_matrix is None:
            self.update_trans_matrix()
        return self._trans_matrix

    @property
    def inv_trans(self):
        if self._inv_trans is None:
            self.update_trans_matrix()
        return self._inv_trans
    
    def make_screen_shot(self):
        self._trans_matrix = None
        self._inv_trans = None
        return super().make_screen_shot()
    
    def image2square(self, image_pos):
        """根据透视变换矩阵将像素坐标变换到棋盘坐标"""
        image_pos = np.array([image_pos], dtype='float32').reshape((1, 1, 2))
        return cv.perspectiveTransform(image_pos, self.trans_matrix).reshape((2))


    def square2image(self, square_pos):
        """根据透视变换矩阵将棋盘坐标变换到像素坐标"""
        square_pos = np.array([square_pos], dtype='float32').reshape((1, 1, 2))
        return cv.perspectiveTransform(square_pos, self.inv_trans).reshape((2))

    def get_map_pos(self, anchor_name, anchor_pos, target_name):
        """根据锚点的像素坐标、锚点的棋盘坐标、目标点的棋盘坐标，计算目标点的像素坐标"""
        dx = (ord(target_name[0]) - ord(anchor_name[0])) * 100
        dy = (ord(target_name[1]) - ord(anchor_name[1])) * 100
        virtual_anchor_pos = self.image2square(anchor_pos)
        virtual_target_pos = np.add(virtual_anchor_pos, [dx, dy])
        target_pos = self.square2image(virtual_target_pos)
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
        self.anchors = [val for val in self.data['Anchors'].values()]

        self.anchors.sort(key=lambda a: ord_distance(a['OnMap'], target))
        # max_len = 3 * len(self.anchors) // 4
        for anchor in self.anchors:
            diff, anchor_pos = get_match(self.screen, anchor["ImageData"])
            if diff < anchor.get("MaxDiff", 0.05):
                map_anchor = anchor_pos + np.array(anchor['Offset'])
                logger.debug("找到%s(%.3f): %s. 坐标%s:%s",
                             anchor['Name'], diff, anchor_pos, anchor['OnMap'], map_anchor)
                return True, self.get_map_pos(anchor['OnMap'], map_anchor, target)
            logger.debug("未找到%s. 最优结果%.3f.", anchor['Name'], diff)
        return False, None

    def click_at_map(self, target, repeat=0):
        """点击指定的棋盘坐标"""
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
            FightMap.click_at_map(self, target, repeat+1)
            return

        x, y = target_pos
        x_min, y_min, x_max, y_max = self.get_resource_rect("可移动区域")
        if x < x_min or x > x_max or y < y_min or y > y_max:
            logger.debug("目标不在中间区域")
            self.move_map_to(x, y)
            FightMap.click_at_map(self, target, repeat+1)
            return
        logger.info("点击%s: (%d, %d)", target, x, y)
        click_at(self.hwnd, x, y)

    def get_best_anchor(self):
        """在屏幕上搜索最佳的锚点
        当前使用匹配程度最高的锚点
        """
        res = []
        for anchor in self.data['Anchors'].values():
            logger.debug("Check Anchor %s", anchor['Name'])
            diff, pos = get_match(self.screen, anchor['ImageData'])
            pos = np.add(pos, anchor['Offset'])
            res.append([diff, pos, anchor['OnMap']])
        res.sort(key=lambda a: a[0])
        diff, pos, name = res[0]
        if diff > 0.06:
            raise ValueError("Best Match Diff %.3f" % diff)
        return name, pos

    def find_on_map(self, anchor_name, anchor_pos, target_name, reshot=True):
        """在屏幕上搜索并返回指定的anchor出现的所有棋盘坐标"""
        if reshot:
            self.make_screen_shot()
        anchor_pos_s = self.image2square(anchor_pos)
        logger.debug("find_on_map %s by %s at %s", target_name, anchor_name, anchor_pos)
        target = self.resources[target_name]
        name_x, name_y = anchor_name

        points = np.array(self.resources["地图区域"]["Points"]).reshape((1, -1, 2))
        result = set()
        for x, y in np.reshape(self.search_resource(target_name)[1], (-1, 2)):
            if cv.pointPolygonTest(points, (x, y), False) < 0:
                # 不在地图区域内, 忽略
                continue
            pos = np.add(target['Offset'], [x, y])
            offset = self.image2square(pos) - anchor_pos_s
            dx, dy = np.round(offset / 100).reshape((2)).astype('int')
            name = chr(ord(name_x) + dx) + chr(ord(name_y) + dy)
            result.add(name)
        logger.debug("find_on_map %s by %s at %s: %s", target_name, anchor_name, anchor_pos, result)
        return result
