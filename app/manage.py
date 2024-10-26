import os
import shutil
import sys

from dotenv import find_dotenv, load_dotenv

from utils import setup_logger

load_dotenv(find_dotenv())

logger = setup_logger(__name__)
command = sys.argv[1]
logger.debug("Received command %s", command)

python = shutil.which("python")
logger.debug("Using python %s", python)

if command == "gunicorn":
    gunicorn = shutil.which("gunicorn")
    logger.debug("Using gunicorn %s", gunicorn)
    os.chdir("..")
    os.execv(gunicorn, [gunicorn, "app.serve:flask_app"])
elif command == "runserver":
    flask = shutil.which("flask")
    logger.debug("Using flask %s", flask)
    os.execv(flask, [flask, "--app", "serve:flask_app", "run", "--debug"])
elif command == "makemigrations":
    os.execv(python, [python, "-m", "orm.makemigrations"])
elif command == "migrate":
    os.execv(python, [python, "-m", "orm.migrate"])

logger.debug("Launching journal.")
