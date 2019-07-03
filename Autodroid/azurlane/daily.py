"""
每日任务
"""

from .azurlane import AzurLaneControl

import numpy as np
import cv2 as cv
from simulator.image_tools import get_match, cv_crop, load_map
from config_loader import logging, config

logger = logging.getLogger(__name__)
filter_kernel = np.array([[-4, -2, -4], [-2, 24, -2], [-4, -2, -4]])


class Daily(AzurLaneControl):
    def __init__(self, map_name):
        super(Daily, self).__init__()
        self.map_name = map_name
        self.data = load_map(self.map_name, self.section)
        logger.info("Update Resources %s", self.data['Resources'].keys())
        self.resources.update(self.data['Resources'])
        logger.info("Update Scenes %s", self.data['Scenes'].keys())
        self.scenes.update(self.data['Scenes'])

    def check_one(self, part):
        part = cv.resize(part, (200, 300))
        filtered = cv.filter2D(part, 0, filter_kernel)
        if not self.resource_in_image("Total3", filtered):
            return False
        if self.resource_in_image("Num0", filtered):
            return False
        if self.resource_in_image("今日未开放", part):
            return False
        return True

    def choose_daily_task(self):
        """选择将要进行的任务"""
        for i in range(5):
            name = "Crop%d" % i
            part = self.crop_resource(name)
            if self.check_one(part):
                self.click_at_resource(name)
                return
        self.close()
