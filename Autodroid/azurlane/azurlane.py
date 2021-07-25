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

    def wait_for_confirm(self, timeout=3, interval=0.5):
        """等待资源出现在画面内"""
        due = time.time() + timeout
        while time.time() < due:
            self.make_screen_shot()
            name = "一键退役"
            if self.resource_in_screen(name):
                logger.info("found %s, wait and retry", name)
                time.sleep(interval)
                continue
            for name in ["退役-确定", "获得道具"]:
                if self.resource_in_screen(name):
                    logger.info("found %s, return", name)
                    return name

        logger.info("等待退役确认超时！")
        return None

    def retire(self):
        """执行退役操作"""
        self.make_screen_shot()
        click_remap = {"获得道具": "退役-右下角"}
        suc = 0

        self.click_at_resource("一键退役")
        self.wait(1)
        self.make_screen_shot()
        # 未跳转到确认场景
        if not self.wait_for_confirm(1):
            logger.info("未跳转到确认场景, 结束退役操作")
        else:
            suc += 1
            while True:
                res = self.wait_for_confirm(2)
                if res:
                    # 稍作等待，保证判断不再变化
                    self.wait(1)
                    res = self.wait_for_confirm(2)

                if res:
                    target = click_remap.get(res, res)
                    logger.info("找到%r, 点击%r", res, target)
                    self.click_at_resource(target)
                    self.wait(1)
                else:
                    self.wait(1)
                    break

        logger.info("完成退役%d", suc)
        self.wait(1)
        logger.debug("返回之前界面")
        self.click_at_resource("退役-取消", True)
        if not suc:
            self.critical("自动退役失败")
        self.wait(3)


if __name__ == "__main__":
    logger.setLevel("DEBUG")
    controler = AzurLaneControl("M")
    # print(controler.retire())
