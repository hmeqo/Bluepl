"""日志处理"""

import logging
from logging.handlers import RotatingFileHandler

from . import gconfig

logger = None


def get_logger(logfp):
    global logger
    if logger is not None:
        return logger
    log_handler = RotatingFileHandler(
        logfp, "w", maxBytes=1 * 1024 * 1024, backupCount=1, encoding="UTF-8")
    formatter = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s")
    log_handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(log_handler)
    return logger


def print_gconfig():
    print("DIR_PATH:", gconfig.Dirs.root)
    print("APP_NAME:", gconfig.App.name)
