"""
通用配置项
"""
import os
import hashlib
import yaml
import logging
import logging.config
from configparser import ConfigParser
import concurrent_log_handler

with open("config/logging.yaml") as f:
    conf = yaml.load(f)
logging.config.dictConfig(conf)
logger = logging.getLogger(__name__)
logger.info("Loggin Inited...")

config = ConfigParser()
config.read("config/common.conf", encoding="UTF-8")

text = '\n'.join([os.popen(cmd).read().splitlines()[2] for cmd in [
    "wmic BaseBoard get Manufacturer,Product,SerialNumber",
    "wmic CPU get Caption,Manufacturer,Name,ProcessorId,SerialNumber,SystemName",
]])
device_id = hashlib.md5(text.encode()).hexdigest()
logger.info("Load Device %s:\n%s", device_id, text)

name = "config/%s.conf" % device_id
if not os.path.exists(name):
    raise FileNotFoundError("No Config File For This Device!")

config.read(name, encoding="UTF-8")
