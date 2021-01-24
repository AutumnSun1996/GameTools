import os
import logging

from config import hocon

logger = logging.getLogger(__name__)


def load_map(map_name):
    config_file = os.path.join("azurlane", "maps", map_name + ".conf")
    info = hocon.load(config_file)
    if "MapClass" in info:
        import importlib

        module_path, cls_name = info["MapClass"]
        m = importlib.import_module(module_path)
        map_cls = getattr(m, cls_name)
    else:
        from azurlane.azurlane import AzurLaneControl as map_cls
    logger.warning("Use class %r", map_cls)
    az = map_cls(map_name)
    return az
