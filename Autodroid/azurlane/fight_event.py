"""
针对带有移动步数限制、精英舰队、无空袭和伏击的活动图
"""
from .common_fight import CommonMap, FightMap, logger

class EventFight(CommonMap):
    def toggle_on_map(self, target, side):
        if self.current_fleet == target:
            self.goto(side)
        else:
            self.goto(target)

    def goto(self, target):
        path = self.shortest_path(self.current_fleet, target)
        if "FleetMoveStep" in self.data:
            logger.info("Limit Move %s[:%d]", path, self.data["FleetMoveStep"])
            path = path[:self.data["FleetMoveStep"]+1]
            target = path[-1]

        FightMap.click_at_map(self, target)
        wait = (len(path)-1) * 0.7
        self.wait(wait)
        if target == self.other_fleet:
            self.other_fleet = self.current_fleet
        self.current_fleet = target
        if target in self.enemies:
            self.set_enemy(target, 'Defeated')

    def normal_fight(self, repeat=0):
        if repeat >= 5:
            self.error("地图处理失败")
            return

        if not self.current_fleet:
            self.recheck_full_map()
            self.normal_fight(repeat+1)
            return

        fleets = [self.current_fleet]
        if self.other_fleet:
            fleets.append(self.other_fleet)

        self.goto(self.next_enemy(fleets))
        
    def search_for_boss(self, repeat=0, idx=0):
        logger.info("搜索Boss(%d)", repeat)

        if not self.current_fleet:
            self.recheck_full_map()
            self.search_for_boss(repeat+1, idx)
            return
            
        if idx is not None:
            target = self.data['ViewPort'][idx]
            logger.info("检查区域%s", target)
            self.move_map_to(*self.locate_target(target)[1])
        if repeat >= len(self.data['ViewPort']):
            self.critical("Boss搜索失败")

            
        anchor_name, anchor_pos = self.get_best_anchor()
        
        pos = self.find_on_map(anchor_name, anchor_pos, 'Boss')
        if not pos:
            pos = self.find_on_map(anchor_name, anchor_pos, 'Boss-Bigger')
        if not pos:
            self.search_for_boss(repeat, idx+1)
            return
        logger.info("找到Boss %s", pos)
        target = list(pos)[0]
        self.goto(target)
        return