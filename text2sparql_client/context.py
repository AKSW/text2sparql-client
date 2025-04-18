"""Context object for the CLI"""

import sys

from loguru import logger


class ApplicationContext:
    """Context object for the CLI"""

    def __init__(self, debug: bool):
        self.debug = debug
        logger.remove()
        if self.debug:
            logger.add(sys.stderr, level="DEBUG")
        else:
            logger.add(sys.stderr, level="INFO")
