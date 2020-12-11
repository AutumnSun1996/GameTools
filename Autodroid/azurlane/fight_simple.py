"""
针对无空袭和伏击、无移动步数限制、无精英舰队或精英舰队位于固定位置的简单地图
"""

from .common_fight import CommonMap, FightMap, logger

class FightMap(CommonMap):
    def detect_map_init(self):
        """自动判断地图大小
        TODO: 实现
        """
        pass

    def detect_map(self):
        """自动判断地图相对位置、各位置当前状态
        TODO: 实现
        """
        pass

    def iter_map_all(self, callback, target_area=()):
        """移动地图
        """
        pass

    def iter_map_points(self, callback, targets=()):
        """移动地图到指定的位置后调用callback
        """
        pass

    def search_boss_full(self):
        self.search_boss_simple()
        self.iter_map(self.search_boss_simple, check_size=(3, 3))

    def search_boss_simple(self):
        if self.resource_in_screen("Boss"):
            self.boss = True
        return self.boss

    def fight(self):
        if self.boss is None:
            self.search_boss_full()
        else:
            self.search_boss_simple()
