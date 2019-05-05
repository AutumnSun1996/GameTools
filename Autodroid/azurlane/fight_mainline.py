"""
针对常见地图，包括伏击、空袭
"""
from .common_fight import CommonMap, FightMap, logger


class MainFight(CommonMap):
    def __init__(self, *args):
        super().__init__(*args)
        self.click_target = None

    def click_at_map(self, target):
        FightMap.click_at_map(self, target)
        path = self.shortest_path(self.current_fleet, target)
        wait = (len(path)-1) * 0.7
        self.wait(wait)
        if target == self.other_fleet:
            self.other_fleet = self.current_fleet
        self.click_target = target
        # self.current_fleet = None # 由于空袭+伏击，无法确认当前舰队的下个位置

    def normal_fight(self, repeat=0):
        self.check_map()
        if self.current_fleet == self.click_target:
            logger.info("Reset ClickTarget")
            self.click_target = None

        if self.click_target is None:
            super().normal_fight(repeat)
        else:
            logger.info("ReClickAt %s", self.click_target)
            self.click_at_map(self.click_target)

    def search_for_boss(self, repeat=0, idx=0):
        logger.info("搜索Boss(%d)", repeat)

        if not self.current_fleet:
            self.recheck_full_map()
            self.search_for_boss(repeat+1, idx)
            return

        if not isinstance(self.boss, str):
            if idx is not None:
                target = self.data['ViewPort'][idx]
                logger.info("检查区域%s", target)
                self.move_map_to(*self.locate_target(target)[1])
            if repeat >= len(self.data['ViewPort']):
                self.critical("Boss搜索失败")

            anchor_name, anchor_pos = self.get_best_anchor()

            pos = self.find_on_map(anchor_name, anchor_pos, 'Boss')
            if not pos and "Boss2" in self.resources:
                pos = self.find_on_map(anchor_name, anchor_pos, 'Boss2')
            if not pos and "Boss3" in self.resources:
                pos = self.find_on_map(anchor_name, anchor_pos, 'Boss3')
            if not pos:
                self.search_for_boss(repeat, idx+1)
                return
            boss = list(pos)[0]
            if boss in self.boss:
                self.boss = boss
            else:
                logger.warning("False Boss %s not in %s", boss, self.boss)
                self.search_for_boss(repeat, idx+1)
                return
        logger.info("找到Boss %s", self.boss)
        self.click_at_map(self.boss)
        return
