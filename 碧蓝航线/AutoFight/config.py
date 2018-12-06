import sys
import logging

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[%(lineno)d] - %(levelname)s: %(message)s')
logger = logging.getLogger()

class options:
    ORIGIN_WINDOW_SIZE = (1284, 752)