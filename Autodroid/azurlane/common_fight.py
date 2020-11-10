"""
碧蓝航线战斗棋盘地图分析和定位
"""
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import logging

from simulator.win32_tools import rand_click
from simulator import parse_condition
from .map_anchor import FightMap

logger = logging.getLogger(__name__)


class CommonMap(FightMap):
    """地图操作"""

    def __init__(self, map_name=None):
        super().__init__(map_name)
        self.reset_map_data()

    def get_fight_status(self):
        status = super().get_fight_status()
        if self.data["FightCount"] > 0:
            status["FightIndexMod"] = status["FightIndex"] % self.data["FightCount"]
        else:
            status["FightIndexMod"] = status["FightIndex"]
        return status

    def parse_fight_condition(self, condition):
        status = self.get_fight_status()
        return parse_condition(condition, self, status.__getitem__)

    def reset_map_data(self):
        """进入战场，重置虚拟战斗次数，使下一次战斗正常开始
        """

        self.g = nx.Graph()
        self.boss = []
        self.other_fleet = None
        self.current_fleet = None
        self.last_map_target = None
        self.born_points = []  # used for init `current_fleet`
        self.fleet_id = 1
        self.submarine = []
        self.resource_points = []
        self.enemies = set()
        self.pos = {}
        for j, row in enumerate(self.data["Map"]):
            for i, cell_type in enumerate(row):
                name = chr(ord("A") + i) + str(j + 1)
                self.g.add_node(name, cell_type=cell_type)
                self.pos[name] = i, -j
                if cell_type == "O":  # 障碍
                    continue
                if cell_type == "B":  # Boss
                    self.boss.append(name)
                if cell_type == "?":  # 问号点
                    self.resource_points.append(name)
                if cell_type == "S":  # 潜艇
                    self.submarine.append(name)
                if cell_type == "F":  # 出生点
                    self.born_points.append(name)
                if i > 0:
                    left = chr(ord("A") + i - 1) + str(j + 1)
                    if self.g.nodes.get(left, {}).get("cell_type", "O") != "O":
                        self.g.add_edge(name, left)
                if j > 0:
                    top = chr(ord("A") + i) + str(j)
                    if self.g.nodes.get(top, {}).get("cell_type", "O") != "O":
                        self.g.add_edge(name, top)
        if len(self.submarine) == 1:
            self.submarine = self.submarine[0]
        for node in self.g:
            if self.g.nodes[node]["cell_type"] == "E":  # 可能出现敌人的地点
                self.set_enemy(node, "Possible")

    def reset_fight_index(self, target_mod=0):
        # self.virtual_fight_index = 0
        self.reset_map_data()
        status = self.get_fight_status()
        mod = status["TrueFightIndex"] % self.data["FightCount"]
        logger.warning("Current Fight Index: %d (%d)", status["FightIndex"], mod)
        if mod != target_mod:
            status["VirtualFightIndex"] = target_mod - mod
            self.save_fight_status(status)
            logger.info("Reset Fight Index From Mod %d To %d", mod, target_mod)

    def toggle_fleet(self):
        self.click_at_resource("切换舰队")
        self.current_fleet, self.other_fleet = self.other_fleet, self.current_fleet
        self.wait(2)

    def update_cur_fleet(self):
        """将上次点击位置设置为当前舰队位置

        预期在战斗准备界面被调用
        """
        if self.last_map_target is not None:
            self.current_fleet = self.last_map_target
            self.set_enemy(self.current_fleet, "Defeated")

    def enemies_on_path(self, path):
        enemies = []
        for cell in path:
            if self.g.nodes[cell].get("enemy") == "Exist":
                enemies.append(cell)
        return enemies

    def get_color(self, cell):
        info = self.g.nodes[cell]
        if info["cell_type"] == "O":
            return "#000000"
        enemy = info.get("enemy")
        if enemy is None:
            return "#00FF00"
        if enemy == "Defeated":
            return "#666666"
        if enemy == "Exist":
            return "#993333"
        if enemy == "Boss":
            return "#FF0000"
        return "#66ccff"

    def set_enemy(self, cell, status="Exist"):
        if cell is None:
            logger.warning("abort set_enemy: cell is None")
            return
        info = self.g.nodes[cell]
        if info["cell_type"] == "O":
            self.notice("%s为不可通过区域" % cell)
            return
        if info["cell_type"] == "B" and status == "Exist":
            status = "Boss"
        if status == "Boss":
            weight = 100
            self.boss = [cell]
            self.enemies.add(cell)
        elif status == "Exist":
            weight = 1000
            self.enemies.add(cell)
        elif status == "Possible":
            weight = 0.1
        elif status == "Defeated":
            weight = 0.1
            self.enemies.discard(cell)
        else:
            weight = 0.5
        info["enemy"] = status
        info["weight"] = weight
        for neighbor in self.g.neighbors(cell):
            n_weight = self.g.nodes[neighbor].get("weight", 0.5)
            self.g[cell][neighbor]["weight"] = info["weight"] + n_weight

    def draw(self):
        cf = plt.gcf()
        ax = cf.gca()
        ax.set_axis_off()
        nodes = list(self.g.nodes)
        nx.draw_networkx_nodes(
            self.g,
            pos=self.pos,
            nodelist=nodes,
            node_color=[self.get_color(key) for key in nodes],
        )
        nx.draw_networkx_edges(self.g, pos=self.pos)
        nx.draw_networkx_labels(self.g, pos=self.pos, font_color="white")

    def draw_path(self, path):
        edges = []
        for i in range(1, len(path)):
            self.g[path[i - 1]][path[i]]["InPath"] = True
            edges.append((path[i - 1], path[i]))
        nx.draw_networkx_edges(
            self.g.to_directed(), pos=self.pos, edgelist=edges, edge_color="r"
        )

    def shortest_path(self, start, target, weight="weight"):
        return nx.shortest_path(self.g, start, target, weight)

    def shortest_path_length(self, start, target, weight="weight"):
        return nx.shortest_path_length(self.g, start, target, weight)

    def common_path(self, start, targets):
        path = []
        for node in zip(*[self.shortest_path(start, target) for target in targets]):
            if len(set(node)) > 1:
                break
            path.append(node[0])
        return path

    def better_position(self, start, target=None):
        if target is None:
            target = self.boss
        if isinstance(target, (list, tuple)):
            path = self.common_path(start, target)
        else:
            path = nx.shortest_path(self.g, start, target, "weight")
        profit = 0
        choice = None
        print(path)
        for i in range(1, len(path)):
            cell = path[i]
            enemy = self.g.nodes[cell].get("enemy")
            print("Check %s: %s" % (cell, enemy))
            if enemy == "Possible":
                profit += 1
                choice = cell
                print("Gain Profit %d till %s" % (profit, cell))
            elif enemy == "Exist":
                break
            elif profit > 0:
                choice = cell
        return choice

    def next_enemy(self, source):
        if not self.scene_match_check("战斗地图", False):
            logger.warning("abort next_enemy: Not in 战斗地图.")
            return

        if not self.enemies:
            self.recheck_full_map()
            return self.next_enemy(source)
        for f in source:
            for b in self.boss + self.resource_points:
                if f == b:
                    logger.debug("Ignore current pos %s", f)
                    continue
                path = self.shortest_path(f, b)
                enemies = self.enemies_on_path(path)
                if enemies:
                    logger.info("选择挡住%s->%s所有路径的敌人(%s)", f, b, enemies)
                    return enemies[0]
        for f in source:
            for b in self.boss + self.resource_points:
                path = self.shortest_path(f, b, None)
                enemies = self.enemies_on_path(path)
                if enemies:
                    logger.info("选择挡住%s->%s最短路径的敌人(%s)", f, b, enemies)
                    return enemies[0]

        distance = []
        for enemy in self.enemies:
            distance.append(
                [self.shortest_path_length(self.current_fleet, enemy), enemy]
            )
        distance.sort()
        logger.info("选择最近的敌人: %s", distance[0][1])
        return distance[0][1]

    def search_for_boss(self, repeat=0, idx=0):
        if not self.scene_match_check("战斗地图", False):
            logger.warning("abort search_for_boss: Not in 战斗地图")
            return
        logger.info("搜索Boss(%d,%d)", repeat, idx)
        if len(self.boss) == 1:
            self.click_at_map(self.boss[0])
            return
        if repeat > 5:
            raise RuntimeError("search_for_boss:Failed after %s attempt", repeat)
        anchor_name, anchor_pos = self.get_best_anchor()
        names = self.data.get("BossMarkers", ["Boss"])
        boss = self.find_multi_on_map(anchor_name, anchor_pos, names, False)
        boss_ports = self.data.get("BossViewPoints", list(self.boss))
        if not boss:
            if idx < len(boss_ports):
                _, pos = self.locate_target(boss_ports[idx])
                self.move_map_to(*pos)
                self.search_for_boss(repeat, idx + 1)
                return
            self.search_for_boss(repeat + 1, 0)
            return
        boss = list(boss)[0]
        self.click_at_map(boss)
        self.wait(3)
        return

    def find_on_map(self, anchor_name, anchor_pos, target_name, reshot=True):
        results = FightMap.find_on_map(
            self, anchor_name, anchor_pos, target_name, reshot
        )
        return results.intersection(self.g.nodes)

    def find_multi_on_map(self, anchor_name, anchor_pos, target_names, reshot=True):
        results = set()
        for name in target_names:
            if name in self.resources:
                items = self.find_on_map(anchor_name, anchor_pos, name, reshot=reshot)
                results = results.union(items)
        return results.intersection(self.g.nodes)

    def check_map(self):
        self.make_screen_shot()
        # in case of scene changes after scene update
        if not self.scene_match_check("战斗地图", False):
            logger.warning("abort check_map: Not in 战斗地图")
            return
        anchor_name, anchor_pos = self.get_best_anchor()

        names = self.data.get("EnemyMarkers", ["Lv", "Lv1", "Lv2"])
        enemies = self.find_multi_on_map(anchor_name, anchor_pos, names, False)

        logger.info("找到敌人: %s", enemies)
        for enemy in enemies:
            self.set_enemy(enemy)

        # boss = self.find_on_map(anchor_name, anchor_pos, 'Boss', False)
        # if len(boss) != 1:
        # boss = self.find_on_map(
        # anchor_name, anchor_pos, 'Boss-Bigger', False)
        # if len(boss) == 1:
        # self.boss = list(boss)
        # logger.info("找到Boss: %s", boss)

        if self.current_fleet is None:
            names = self.data.get(
                "CurFleetMarkers", ["Pointer", "Pointer2", "Pointer3"]
            )
            cur_fleet = self.find_multi_on_map(anchor_name, anchor_pos, names, False)
            logger.info("找到当前舰队: %s", cur_fleet)
            if cur_fleet:
                self.current_fleet = list(cur_fleet)[0]

        names = self.data.get("FleetMarkers", ["Ammo", "Ammo2", "Ammo3"])
        fleets = self.find_multi_on_map(anchor_name, anchor_pos, names, False)
        logger.info("找到舰队: %s", fleets)
        if self.current_fleet in fleets:
            fleets.discard(self.current_fleet)
        if not self.submarine:
            # 无潜艇
            pass
        elif isinstance(self.submarine, list):
            # 未确定潜艇位置
            both = fleets.intersection(self.submarine)
            if both:
                self.submarine = list(both)[0]
                logger.info("找到潜艇: %s", self.submarine)
                fleets.discard(self.submarine)
        else:
            fleets.discard(self.submarine)
        if len(fleets) == 1:
            self.other_fleet = list(fleets)[0]
            logger.info("找到另一舰队: %s", self.other_fleet)

        if self.current_fleet and self.current_fleet in self.enemies:
            self.set_enemy(self.current_fleet, "Defeated")
        if self.other_fleet and self.other_fleet in self.enemies:
            self.set_enemy(self.other_fleet, "Defeated")

    def recheck_full_map(self):
        logger.warning("地图信息更新")
        for target in self.data["ViewPoints"]:
            logger.info("查看%s周围信息", target)
            self.wait(1)
            self.make_screen_shot()
            # in case of scene changes after scene update
            if not self.scene_match_check("战斗地图", False):
                logger.warning("abort recheck_full_map: Not in 战斗地图.")
                return
            _, pos = self.locate_target(target, reshot=False)
            self.move_map_to(*pos)
            self.wait(1)
            self.check_map()

    def after_bonus(self):
        """处理到达问号点之后的获得道具, 获得维修判断"""
        scene = self.update_current_scene(["获得道具", "战斗地图"])
        if scene["Name"] == "获得道具":
            self.do_actions(scene["Actions"])
            self.wait(1)
            if not self.resource_in_screen("右侧菜单"):
                self.click_at_resource("右侧菜单")
            self.update_current_scene(["战斗地图"])

    def search_for_bonus(self, repeat=0):
        if repeat >= 5:
            self.critical("问号点搜索失败")
        ret, pos = self.search_resource("问号点")
        if not ret:
            self.wait_mannual("未找到问号点")
            self.recheck_full_map()
            self.search_for_bonus(repeat + 1)
            return

        x, y = pos
        x_min, y_min, x_max, y_max = self.get_resource_rect("可移动区域")
        if x < x_min or x > x_max or y < y_min or y > y_max:
            logger.debug("目标不在中间区域")
            self.move_map_to(x, y)
            self.search_for_bonus(repeat + 1)
            return

        dx, dy = self.resources["问号点"]["Offset"]
        w, h = self.resources["问号点"]["Size"]
        logger.info("找到问号点")
        rand_click(self.hwnd, (x + dx, y + dy, x + dx + w, y + dy + h))
        self.wait(6)
        self.after_bonus()
        return

    def get_fight_index(self):
        return self.get_fight_status()["FightIndex"]

    def fight(self):
        status = self.get_fight_status()
        logger.info("战斗%s", status)
        for item in self.data["Strategy"]:
            if self.parse_fight_condition(item["Condition"]):
                logger.info("战斗策略：%s", item)
                self.do_actions(item["Actions"])
                if item.get("Break", None):
                    break

    def click_at_map(self, target):
        FightMap.click_at_map(self, target)
        self.last_map_target = target
        if self.current_fleet is None:
            # avoid wrong shortest_path search.
            self.current_fleet = self.born_points[0]
        path = self.shortest_path(self.current_fleet, target)
        wait = (len(path) - 1) * 0.7
        self.wait(wait)
        if target == self.other_fleet:
            self.other_fleet = self.current_fleet
        self.current_fleet = target
        # if target in self.enemies:
        #     self.set_enemy(target, 'Defeated')

    def normal_fight(self, repeat=0):
        if not self.scene_match_check("战斗地图", False):
            logger.warning("abort normal_fight: Not in 战斗地图")
            return
        if repeat >= 5:
            self.error("地图处理失败")
            return

        self.check_map()
        if not self.current_fleet and not self.enemies:
            self.recheck_full_map()
            self.normal_fight(repeat + 1)
            return
        if self.current_fleet is None:
            self.current_fleet = self.born_points[0]

        fleets = [self.current_fleet]
        if self.other_fleet:
            fleets.append(self.other_fleet)

        self.click_at_map(self.next_enemy(fleets))

    def goto_res_on_map(self, names, viewpoints=None, repeat=0, idx=0):
        if not self.scene_match_check("战斗地图", False):
            logger.warning("abort goto_res_on_map({}): Not in 战斗地图".format(names))
            return
        if repeat >= 5:
            self.error("地图处理失败 goto_res_on_map({})".format(names))
            return
        if isinstance(names, str):
            # 获取待检查资源名列表
            names = self.data.get(names, [names])
        if names == ["Boss"] and viewpoints is None:
            # 单独处理Boss
            viewpoints = list(self.boss)
        if viewpoints is None:
            # 获取待检查点位列表
            viewpoints = self.data["ViewPoints"]

        if idx >= len(viewpoints):
            self.goto_res_on_map(names, viewpoints, repeat + 1, 0)
            return

        logger.info("move to %s.", viewpoints[idx])
        _, pos = self.locate_target(viewpoints[idx])
        self.move_map_to(*pos)
        self.make_screen_shot()
        anchor_name, anchor_pos = self.get_best_anchor()
        targets = self.find_multi_on_map(anchor_name, anchor_pos, names, False)
        logger.info(
            "goto_res_on_map(%s, %s[%d]) attempt%d: %s",
            names,
            viewpoints,
            idx,
            repeat,
            targets,
        )
        if not targets:
            self.goto_res_on_map(names, viewpoints, repeat, idx + 1)
            return
        self.click_at_map(list(targets)[0])

    def goto_bonus(self, positions=None):
        if positions is None:
            self.goto_res_on_map([["问号点"]])
            self.after_bonus()
            return
        for loc in positions:
            self.click_at_map(loc)
            self.after_bonus()


if __name__ == "__main__":
    import datetime

    # logger.setLevel("DEBUG")
    s = CommonMap("斯图尔特的硝烟SP3")
    logger.info("FinghtIndex: %d", s.parse_fight_condition(["FightIndex"]))
    start_index = s.get_fight_index()
    while True:
        s.check_scene()
        if s.current_scene["Name"] == "外部地图":
            now = datetime.datetime.now()
            new_fight = s.get_fight_index() - start_index
            logger.info("战斗次数:%d(%d)", s.get_fight_index(), new_fight)
            if new_fight > 6 * 10:
                exit(0)
            if now.hour >= 22:
                exit(0)
