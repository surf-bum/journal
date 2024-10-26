from pathlib import Path
import sys
from app.utils import setup_logger
from flask import Blueprint, Flask

from app.assistants.blueprint import (
    api_assistants_blueprint,
    ui_assistants_blueprint,
)
from app.notes.blueprint import api_notes_blueprint, ui_notes_blueprint
from app.plugins.blueprint import api_plugins_blueprint, ui_plugins_blueprint
from app.references.blueprint import (
    api_references_blueprint,
    ui_references_blueprint,
)
from app.config import settings

logger = setup_logger(__name__)

root_folder = Path(__file__).resolve().parent
logger.debug("Adding %s to PYTHON_PATH", root_folder)
sys.path.append(str(root_folder))

flask_app = Flask(__name__)
flask_app.secret_key = settings.SECRET_KEY

api_blueprint = Blueprint("api", __name__)
api_blueprint.register_blueprint(api_assistants_blueprint, url_prefix="/assistants")
api_blueprint.register_blueprint(api_notes_blueprint, url_prefix="/notes")
api_blueprint.register_blueprint(api_plugins_blueprint, url_prefix="/plugins")
api_blueprint.register_blueprint(api_references_blueprint, url_prefix="/references")

ui_blueprint = Blueprint("ui", __name__)
ui_blueprint.register_blueprint(ui_assistants_blueprint, url_prefix="/assistants")
ui_blueprint.register_blueprint(ui_notes_blueprint, url_prefix="/notes")
ui_blueprint.register_blueprint(ui_plugins_blueprint, url_prefix="/plugins")
ui_blueprint.register_blueprint(ui_references_blueprint, url_prefix="/references")


flask_app.register_blueprint(api_blueprint, url_prefix="/api/v1")
flask_app.register_blueprint(ui_blueprint, url_prefix="/ui")
