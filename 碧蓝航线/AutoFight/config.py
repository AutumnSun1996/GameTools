"""
碧蓝航线配置项
"""
import os
import sys
import json
import logging
from configparser import ConfigParser

config_file = "config-1280x720.ini"

logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format='%(asctime)s %(filename)s[%(lineno)d] - %(levelname)s: %(message)s')
logger = logging.getLogger()


class Config(ConfigParser):
    def save(self):
        with open(config_file, "w", -1, "UTF-8") as fl:
            self.write(fl)
        
config = Config()
config.read(config_file, encoding="UTF-8")
