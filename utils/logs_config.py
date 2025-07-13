import os
import logging

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)


def logger_setup(name, filename):
    handler = logging.FileHandler(os.path.join(LOG_DIR, filename), mode='a')
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.propagate = False
    return logger

comms_logger = logger_setup("comms", "comms.log")
net_logger = logger_setup("net", "net.log")
error_logger = logger_setup("errors", "errors.log")