import logging

import chromadb
from chromadb import Collection
from json_log_formatter import JSONFormatter


def setup_logger(mod, log_level=logging.DEBUG) -> logging.Logger:
    formatter = JSONFormatter()

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger = logging.getLogger(mod)
    logger.addHandler(stream_handler)
    logger.setLevel(log_level)

    return logger


chromadb_collection = None


def get_chromadb_collection() -> Collection:
    if chromadb_collection:
        return chromadb_collection

    client = chromadb.PersistentClient(path="chromadb-data")
    return client.get_or_create_collection(name="docs")
