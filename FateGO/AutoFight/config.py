"""
FGO配置项
"""
import logging
import logging.config
import socket
from configparser import ConfigParser

logging.config.fileConfig("logging.conf")
logger = logging.getLogger()

config_file = "config-Company.ini"

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
