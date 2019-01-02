import win32api

from azurlane.map_anchor import FightMap

try:
    __builtin__ = __builtins__
except NameError:
    pass

class MannalFight(FightMap):
    def __init__(self):
        super().__init__()
        self.scenes.update({
            "进入档案确认": {
                "Name": "进入档案确认",
                "Condition": "进入档案确认",
                "Actions": [{"Type": "Click", "Target": "进入档案确认"}, {"Type": "Wait", "Time": 0.5}, ]
            }})

    def fight(self):
        if self.last_scene['Name'] in {"战斗地图", "无匹配场景"}:
            return
        self.go_top()
        win32api.MessageBeep()


if __name__ == "__main__":
    print(__builtin__)
    import datetime
    m = MannalFight()
    start_index = m.get_fight_status()["FightIndex"]
    while True:
        m.check_scene()
