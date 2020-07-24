"""
演习
"""

from .azurlane import AzurLaneControl
from ocr.baidu_ocr import ocr
from simulator.image_tools import get_match, cv, get_multi_match, load_map
from config_loader import logging, config

logger = logging.getLogger(__name__)


class Operation(AzurLaneControl):
    max_sl = 3
    emeny_choices = [0, 1]

    def __init__(self, map_name):
        super(Operation, self).__init__()
        self.map_name = map_name
        self.data = load_map(self.map_name, self.section)
        logger.info("Update Resources %s", self.data["Resources"].keys())
        self.resources.update(self.data["Resources"])
        logger.info("Update Scenes %s", self.data["Scenes"].keys())
        self.scenes.update(self.data["Scenes"])
        self.oper_info = {
            "left": 10,
            "cur_enemy": self.emeny_choices[0],
            "sl": self.max_sl,
        }

    def fight(self):
        text = ocr.image2text(self.crop_resource("演习次数"))
        left, _ = text.split("/")
        self.oper_info.update({"left": int(left)})
        self.click_at_resource("演习敌人列表", index=self.oper_info["cur_enemy"])
        self.wait(1)
        self.click_at_resource("开始演习", wait=True)
        self.wait(1)

    def stop_cond(self, *args, **kwargs):

        return True


if __name__ == "__main__":
    op = Operation("演习")
    op.main_loop(op.stop_cond)
