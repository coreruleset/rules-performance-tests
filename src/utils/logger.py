"""
Custom logger for logging
"""

import logging


class Formatter(logging.Formatter):
    """
    Custom formatter for logging 
    """
    __grey = "\x1b[38;20m"
    __yellow = "\x1b[33;20m"
    __red = "\x1b[31;20m"
    __bold_red = "\x1b[31;1m"
    __reset = "\x1b[0m"
    __format = "[%(levelname)s] %(message)s"

    __FORMATS = {
        logging.DEBUG: __grey + __format + __reset,
        logging.INFO: __format,
        logging.WARNING: __yellow + __format + __reset,
        logging.ERROR: __red + __format + __reset,
        logging.CRITICAL: __bold_red + __format + __reset
    }

    def format(self, record):
        log_fmt = self.__FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

logger = logging.getLogger()
handler = logging.StreamHandler()
handler.setFormatter(Formatter())
logger.setLevel(logging.INFO)
logger.addHandler(handler)
