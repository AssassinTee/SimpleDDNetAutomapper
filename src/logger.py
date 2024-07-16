import logging
import sys
from logging.handlers import RotatingFileHandler

handlers = [RotatingFileHandler(filename="simple_ddnet_mapper.log",
                                mode='w',
                                maxBytes=512000,
                                backupCount=4),
            logging.StreamHandler(sys.stdout)
            ]
logging.basicConfig(handlers=handlers,
                    level=logging.DEBUG,
                    format='%(levelname)s %(asctime)s %(message)s',
                    datefmt='%m/%d/%Y%I:%M:%S %p')


def BroadErrorHandler(func):
    def innerFunction(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            logger.error(f"An error occurred at {func.__name__}")
            logger.error(str(e))

    return innerFunction
