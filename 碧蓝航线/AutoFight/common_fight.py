"""
碧蓝航线战斗棋盘地图分析和定位
"""
import networkx as nx
import matplotlib.pyplot as plt

from win32_tools import rand_click
from config import logger
from map_anchor import FightMap


class CommonMap(FightMap):
    """地图操作"""
    map_name = None

    def __init__(self, map_name=None):
        super().__init__(map_name)
        self.g = nx.Graph()
        self.boss = []
        self.resource_points = []
        self.enemies = set()
        self.pos = {}
        self.virtual_fight_index = 6
        for j, row in enumerate(self.data['Map']):
            for i, cell_type in enumerate(row):
                name = chr(ord('A')+i) + str(j+1)
                self.g.add_node(name, cell_type=cell_type)
                self.pos[name] = i, -j
                if cell_type == "O":
                    continue
                if cell_type == 'B':
                    self.boss.append(name)
                if cell_type == '?':
                    self.resource_points.append(name)
                if i > 0:
                    left = chr(ord('A')+i-1) + str(j+1)
                    if self.g.nodes.get(left, {}).get('cell_type', 'O') != 'O':
                        self.g.add_edge(name, left)
                if j > 0:
                    top = chr(ord('A')+i) + str(j)
                    if self.g.nodes.get(top, {}).get('cell_type', 'O') != 'O':
                        self.g.add_edge(name, top)
        for node in self.g:
            if self.g.nodes[node]['cell_type'] == 'E':
                self.set_enemy(node, 'Possible')
    
    def parse_fight_condition(self, condition):
        if isinstance(condition, list):
            if condition[0] == 'FightIndex':
                fidx = self.get_fight_index() + self.virtual_fight_index
                mod = fidx % 6
                logger.debug("FightIndex %d(%d)", fidx, mod)
                return mod
            if condition[0] == 'not':
                return not self.parse_fight_condition(condition[1])
            if condition[0] == '==':
                return self.parse_fight_condition(condition[1]) == self.parse_fight_condition(condition[2])
            if condition[0] == 'in':
                return self.parse_fight_condition(condition[1]) in self.parse_fight_condition(condition[2])
            if condition[0] == '>=':
                return self.parse_fight_condition(condition[1]) >= self.parse_fight_condition(condition[2])
            if condition[0] == '<=':
                return self.parse_fight_condition(condition[1]) <= self.parse_fight_condition(condition[2])
            if condition[0] == '!=':
                return self.parse_fight_condition(condition[1]) != self.parse_fight_condition(condition[2])
        return condition

    def reset_fight_index(self):
        """进入战场，重置虚拟战斗次数，使下一次战斗正常开始
        """
        # self.virtual_fight_index = 0
        fight_idx = self.get_fight_index() + self.virtual_fight_index
        mod = fight_idx % 6
        logger.warning("Current Fight Index: %d (%d)", fight_idx, mod)
        if mod != 0:
            self.virtual_fight_index += 6-mod
            logger.info("Reset Fight Index From %d To %d", fight_idx, fight_idx+6-mod)


    def enemies_on_path(self, path):
        enemies = []
        for cell in path:
            if self.g.nodes[cell].get('enemy') == 'Exist':
                enemies.append(cell)
        return enemies

    def get_color(self, cell):
        info = self.g.nodes[cell]
        if info['cell_type'] == 'O':
            return '#000000'
        enemy = info.get('enemy')
        if enemy is None:
            return '#00FF00'
        if enemy == 'Defeated':
            return '#666666'
        if enemy == 'Exist':
            return '#993333'
        if enemy == 'Boss':
            return '#FF0000'
        return '#66ccff'

    def set_enemy(self, cell, status="Exist"):
        info = self.g.nodes[cell]
        if info['cell_type'] == 'O':
            raise ValueError("%s为不可通过区域" % cell)
        if info['cell_type'] == 'B' and status == 'Exist':
            status = 'Boss'
        if status == 'Boss':
            weight = 100
            self.boss = [cell]
            self.enemies.add(cell)
        elif status == 'Exist':
            weight = 1000
            self.enemies.add(cell)
        elif status == 'Possible':
            weight = 0.1
        elif status == 'Defeated':
            weight = 0.1
            self.enemies.discard(cell)
        else:
            weight = 0.5
        info['enemy'] = status
        info['weight'] = weight
        for neighbor in self.g.neighbors(cell):
            n_weight = self.g.nodes[neighbor].get('weight', 0.5)
            self.g[cell][neighbor]['weight'] = info['weight'] + n_weight

    def draw(self):
        cf = plt.gcf()
        ax = cf.gca()
        ax.set_axis_off()
        nodes = list(self.g.nodes)
        nx.draw_networkx_nodes(self.g, pos=self.pos, nodelist=nodes, node_color=[self.get_color(key) for key in nodes])
        nx.draw_networkx_edges(self.g, pos=self.pos)
        nx.draw_networkx_labels(self.g, pos=self.pos, font_color='white')

    def draw_path(self, path):
        edges = []
        for i in range(1, len(path)):
            self.g[path[i-1]][path[i]]['InPath'] = True
            edges.append((path[i-1], path[i]))
        nx.draw_networkx_edges(self.g.to_directed(), pos=self.pos, edgelist=edges, edge_color='r')

    def shortest_path(self, start, target):
        return nx.shortest_path(self.g, start, target, 'weight')

    def shortest_path_length(self, start, target):
        return nx.shortest_path_length(self.g, start, target, 'weight')

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
            path = nx.shortest_path(self.g, start, target, 'weight')
        profit = 0
        choice = None
        print(path)
        for i in range(1, len(path)):
            cell = path[i]
            enemy = self.g.nodes[cell].get('enemy')
            print("Check %s: %s" % (cell, enemy))
            if enemy == 'Possible':
                profit += 1
                choice = cell
                print("Gain Profit %d till %s" % (profit, cell))
            elif enemy == 'Exist':
                break
            elif profit > 0:
                choice = cell
        return choice

    def next_enemy(self, source):
        for f in source:
            for b in self.boss + self.resource_points:
                path = self.shortest_path(f, b)
                enemies = self.enemies_on_path(path)
                if enemies:
                    logger.info("选择挡路的敌人(%s)", enemies)
                    return enemies[0]
        cur = source[0]
        distance = []
        for enemy in self.enemies:
            distance.append([self.shortest_path_length(cur, enemy), enemy])
        distance.sort()
        logger.info("选择最近的敌人: %s", distance[0][1])
        return distance[0][1]

    def search_for_boss(self, repeat=0):
        if repeat >= 5:
            self.critical("Boss搜索失败")

        ret, pos = self.resource_in_screen('Boss')
        if ret:
            x, y = pos
            x_min, y_min, x_max, y_max = self.get_resource_rect("可移动区域")
            if x < x_min or x > x_max or y < y_min or y > y_max:
                logger.debug("目标不在中间区域")
                self.move_map_to(x, y)
                self.search_for_boss(repeat+1)
                return
            dx, dy = self.resources['Boss']['Offset']
            w, h = self.resources['Boss']['Size']
            logger.info("找到Boss")
            rand_click(self.hwnd, (x+dx, y+dy, x+dx+w, y+dy+h))
            self.wait(6)
            return
        self.wait_mannual("未找到Boss")

    def recheck_full_map(self):
        # TODO: 地图信息更新
        pass

    def after_bonus(self):
        # TODO: 前往问号点后判断获得道具, 获得维修
        pass

    def search_for_bonus(self,  repeat=0):
        if repeat >= 5:
            self.critical("问号点搜索失败")
        ret, pos = self.resource_in_screen('问号点')
        if not ret:
            self.wait_mannual("未找到问号点")
            self.recheck_full_map()
            self.search_for_bonus(repeat+1)
            return
        
        x, y = pos
        x_min, y_min, x_max, y_max = self.get_resource_rect("可移动区域")
        if x < x_min or x > x_max or y < y_min or y > y_max:
            logger.debug("目标不在中间区域")
            self.move_map_to(x, y)
            self.search_for_bonus(repeat+1)
            return
        
        dx, dy = self.resources['问号点']['Offset']
        w, h = self.resources['问号点']['Size']
        logger.info("找到问号点")
        rand_click(self.hwnd, (x+dx, y+dy, x+dx+w, y+dy+h))
        self.wait(6)
        self.after_bonus()
        return

    def fight(self):
        fight_idx = self.get_fight_index() + self.virtual_fight_index
        mod = fight_idx % 6
        logger.info("战斗轮次%d(%d)", fight_idx, mod)
        for item in self.data['Strategy']:
            if self.parse_fight_condition(item['Condition']):
                logger.info("战斗策略：%s", item)
                for action in item['Actions']:
                    if action == "NormalFight":
                        self.normal_fight()
                    elif action == "问号点":
                        self.search_for_bonus()
                    elif action == "Boss":
                        self.search_for_boss()
                    elif action == "ToggleFleet":
                        self.click_at_resource("切换舰队")
                    else:
                        self.error("Unkown Action %s", action)

    def normal_fight(self):
        anchor_name, anchor_pos = self.get_best_anchor()
        # boss = self.find_on_map(anchor_name, anchor_pos, 'Boss')
        # if boss:
        #     self.try_for_boss(boss)
        #     return
        self.make_screen_shot()
        if not self.parse_condition(self.scenes['战斗地图']['Condition']):
            self.notice("Not in 战斗地图")
            return
        for enemy in self.find_on_map(anchor_name, anchor_pos, 'Lv', False):
            self.set_enemy(enemy)
        fleets = self.find_on_map(anchor_name, anchor_pos, 'Ammo', False)
        for fleet in fleets:
            if fleet in list(self.enemies):
                self.set_enemy(fleet, 'Defeated')
        logger.info("找到敌人 %s", self.enemies)

        current_fleet = self.find_on_map(anchor_name, anchor_pos, 'Pointer', False)
        if current_fleet:
            current_fleet = list(current_fleet)[0]
        else:
            current_fleet = list(fleets)[0]

        fleets.discard(current_fleet)
        if fleets:
            other_fleet = list(fleets)[0]
            logger.info("当前舰队: %s, 另一舰队: %s", current_fleet, other_fleet)
            self.click_at_map(self.next_enemy([current_fleet, other_fleet]))
        else:
            logger.info("当前舰队: %s", current_fleet)
            self.click_at_map(self.next_enemy([current_fleet]))
        self.wait(2)


if __name__ == "__main__":
    logger.setLevel("DEBUG")
    s = CommonMap("围剿斯佩伯爵SP3")
    start_index = s.get_fight_index()
    # s.reset_fight_index()
    while True:
        s.check_scene()
        if s.current_scene["Name"] == "活动地图":
            new_fight = s.get_fight_index() - start_index
            logger.info("战斗次数:%d(%d)", s.get_fight_index(), new_fight)
            if new_fight > 0:
                exit(0)
