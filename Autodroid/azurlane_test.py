import win32api

from azurlane.common_fight import CommonMap

try:
    __builtin__ = __builtins__
except NameError:
    pass

class MannalFight(CommonMap):
    def __init__(self):
        CommonMap.__init__(self, "通用地图")
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
