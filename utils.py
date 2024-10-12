import logging

from json_log_formatter import JSONFormatter


def setup_logger(mod, log_level=logging.DEBUG) -> logging.Logger:
    formatter = JSONFormatter()

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger = logging.getLogger(mod)
    logger.addHandler(stream_handler)
    logger.setLevel(log_level)

    return logger
