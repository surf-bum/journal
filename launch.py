import os
import shutil

from dotenv import find_dotenv, load_dotenv

from utils import setup_logger

load_dotenv(find_dotenv())

logger = setup_logger(__name__)
logger.debug("Launching journal.")

flask = shutil.which("flask")
logger.debug("Using flask %s", flask)

python = shutil.which("python")
logger.debug("Using python %s", python)

os.execv(flask, [flask, "run", "--debug"])