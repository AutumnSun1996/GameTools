import os
import sys

import logging
from config import hocon
logger = logging.getLogger(__name__)



if __name__ == "__main__":
    # help(conflictsparse.conflictsparse)
    config_file = sys.argv[1]
    info = hocon.load(config_file)
    print(hocon.to_hocon(info))
