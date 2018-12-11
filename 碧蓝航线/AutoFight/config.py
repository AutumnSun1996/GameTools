"""
碧蓝航线配置项
"""
import os
import sys
import json
import logging
import socket
from configparser import ConfigParser

config_file = "config-Company.ini"

logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format='%(asctime)s %(filename)s[%(lineno)d] - %(levelname)s: %(message)s')
logger = logging.getLogger()


class Config(ConfigParser):
    def save(self):
        with open(config_file, "w", -1, "UTF-8") as fl:
            self.write(fl)

    def init_device(self, hostname):
        pass


config = Config()
config.read(config_file, encoding="UTF-8")

hostname = "Device_"+socket.gethostname()
if not config.has_section(hostname):
    config.init_device(hostname)
