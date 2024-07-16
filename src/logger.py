import logging
import sys
from functools import wraps
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


def BroadErrorHandler(logger):
    def decorator(func):
        @wraps(func)
        def innerFunction(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                logger.error(f"An error occurred at {func.__name__}")
                logger.error(str(e))
                # raise ValueError("Debug") from e

        return innerFunction
    return decorator
