"""
碧蓝航线通用功能

By AutumnSun
"""
import time
import json
from collections import defaultdict

from config_loader import logger, config
from simulator import SimulatorControl
from simulator.win32_tools import rand_click
from simulator.image_tools import cv_save
from ocr.baidu_ocr import ocr, contact_images


class AzurLaneControl(SimulatorControl):
    """碧蓝航线通用控制"""

    no_quiet = False
    section = "AzurLane"
    scene_check_max_repeat = 10
    status_path = "%s/data/fightStatus.json" % section
    retire_choices = {
        # 驱逐-普通
        "卡辛",
        "唐斯",
        "克雷文",
        "麦考尔",
        "奥利克",
        "富特",
        "斯彭斯",
        "小猎兔犬",
        "大斗犬",
        "彗星",
        "新月",
        "小天鹅",
        "狐提",
        "蒲",
        "松",
        "樟",
        "楙",
        "杌",
        "檧",
        "Z20",
        # 驱逐-稀有
        "格里德利",
        "弗莱彻",
        "撒切尔",
        "本森",
        "西姆斯",
        "哈曼",
        "拉德福特",
        "杰金斯",
        "布什",
        "黑泽伍德",
        "霍比",
        "科尔克",
        "女将",
        "热心",
        "命运女神",
        "天后",
        "枫",
        "梓",
        "柏",
        "梿",
        "棭",
        "蓉",
        "藮",
        "榊",
        "棡",
        "枨",
        "萩",
        "槆",
        "柉",
        "樇",
        "栭",
        "栘",
        "樋",
        "Z18",
        "Z19",
        "福尔班",
        "勒马尔",
        "回声",
        "艾尔温",
        # 驱逐-精锐
        "萤火虫",
        "标枪",
        "Z23",
        "拉菲",
        "柚",
        "查尔斯·奥斯本",
        # 轻巡-普通
        "奥马哈",
        "罗利",
        "里士满",
        "利安得",
        "貊",
        "貃",
        "柯尼斯堡",
        "卡尔斯鲁厄",
        "科隆",
        # 轻巡-稀有
        "布鲁克林",
        "菲尼克斯",
        "亚特兰大",
        "朱诺",
        "孟菲斯",
        "康克德",
        "阿基里斯",
        "--阿贾克斯",
        "阿瑞托莎",
        "加拉蒂亚",
        "斐济",
        "纽卡斯尔",
        "--牙买加",
        "貉",
        "--豻",
        # 轻巡-精锐
        "海伦娜",
        "克利夫兰",
        "欧若拉",
        "逸仙",
        "宁海",
        "貎",
        # 轻巡-超稀有
        "圣地亚哥",
        "贝尔法斯特",
        # 重巡-普通
        "彭萨科拉",
        "盐湖城",
        "狼",
        "狌",
        "犹",
        "猅",
        # 重巡-稀有
        "北安普敦",
        "芝加哥",
        "波特兰",
        "什罗普郡",
        "肯特",
        "萨福克",
        "诺福克",
        "獌",
        "狏",
        "苏塞克斯",
        # 重巡-精锐
        "休斯敦",
        "印第安纳波利斯",
        "伦敦",
        "埃克塞特",
        "约克",
        # 战
        "内华达",
        "俄克拉荷马",
        "反击",
        "宾夕法尼亚",
        "田纳西",
        "加利福尼亚",
        "鲼",
        "声望",
        "伊丽莎白女王",
        "罗德尼",
        "胡德",
        "华盛顿",
        # 航
        "博格",
        "兰利",
        "突击者",
        "竞技神",
        "长岛",
        "鹞",
        "独角兽",
        "枭",
        "皇家方舟",
        "龙",
        "企业",
        "光辉",
        "埃塞克斯",
        # 其他
        "女灶神",
        "黑暗界",
        "茗",
        "恐怖",
    }

    def get_fight_status(self):
        """战斗次数计数"""
        try:
            with open(self.status_path, "r") as fl:
                status = json.load(fl)
            status["FightIndex"] = (
                status["VirtualFightIndex"] + status["TrueFightIndex"]
            )
        except FileNotFoundError:
            status = {"VirtualFightIndex": 0, "TrueFightIndex": 0, "FightIndex": 0}
        return status

    def inc_fight_index(self, inc=1):
        """增加战斗次数"""
        status = self.get_fight_status()
        logger.debug(
            "增加Fight Index: %d -> %d",
            status["TrueFightIndex"],
            status["TrueFightIndex"] + inc,
        )
        status["TrueFightIndex"] += inc
        self.save_fight_status(status)

    def save_fight_status(self, status):
        """设置战斗次数"""
        with open(self.status_path, "w") as fl:
            json.dump(status, fl, ensure_ascii=False)

    def fight(self):
        """处理战斗内容. 随每个地图变化"""
        pass

    def mood_detect(self):
        """舰娘心情检测"""
        if self.current_scene["Name"] == "舰队选择":
            colors = [
                ("黄", self.error),
            ]
            action = "进入地图"
        elif self.current_scene["Name"] == "战斗准备":
            colors = [
                ("红", self.critical),
                ("黄", self.notice),
                ("绿", self.notice),
            ]
            action = "继续战斗"
        for color in colors:
            name = "{0}-{1[0]}脸".format(self.current_scene["Name"], color)
            if self.resource_in_screen(name):
                color[1]("舰娘心情值低(%s)" % (name), "舰娘心情值", action)
                # 检测顺序为红黄绿, 因此无需多次检测
                return

    def select_ships(self):
        """选择退役舰娘"""
        self.make_screen_shot()
        images = []
        clicks = []
        retire = self.resources["退役选择"]
        dx, dy = retire.get("ClickOffset", (0, 0))
        dw, dh = retire.get("ClickSize", retire["Size"])

        for x, y in retire["Positions"]:
            images.append(self.crop_resource("退役选择", offset=(x, y)))
            clicks.append((x + dx, y + dy, x + dx + dw, y + dy + dh))

        names = ocr.images2text(*images)

        results = []
        for idx in range(len(names)):
            if names[idx] in self.retire_choices:
                logger.info("select_ship: Choose %s", names[idx])
                results.append(clicks[idx])
            else:
                logger.info("select_ship: Skip %s", names[idx])
        return results[:10]

    def wait_for_confirm(self, timeout=3):
        """等待资源出现在画面内"""
        interval = 0.5
        due = time.time() + timeout
        while time.time() < due:
            self.make_screen_shot()
            name = "一键退役"
            if self.resource_in_screen(name):
                time.sleep(interval)
                continue
            for name in ["退役-确定", "获得道具"]:
                if self.resource_in_screen(name):
                    return name

        self.error("等待退役确认超时！")
        return None

    def retire(self):
        """执行退役操作"""
        self.make_screen_shot()
        suc = 0
        while True:
            self.click_at_resource("一键退役")
            time.sleep(1)
            self.make_screen_shot()
            # 未跳转到确认场景
            if not self.wait_for_confirm():
                break
            suc += 1
            while True:
                res = self.wait_for_confirm()
                if res:
                    logger.info("Click %s", res)
                    self.click_at_resource(res)
                else:
                    break

        if not suc:
            self.critical("自动退役失败")
        self.wait(1)
        logger.debug("返回之前界面")
        self.click_at_resource("退役-取消", True)
        self.wait(3)


if __name__ == "__main__":
    logger.setLevel("DEBUG")
    controler = AzurLaneControl()
    print(controler.select_ships())
    # print(controler.retire())
