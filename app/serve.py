from flask import Blueprint, Flask

from app.blueprints.assistants.blueprint import (
    api_assistants_blueprint,
    ui_assistants_blueprint,
)
from app.blueprints.notes.blueprint import api_notes_blueprint, ui_notes_blueprint
from app.blueprints.references.blueprint import (
    api_references_blueprint,
    ui_references_blueprint,
)
from app.config import settings

flask_app = Flask(__name__)
flask_app.secret_key = settings.SECRET_KEY

api_blueprint = Blueprint("api", __name__)
api_blueprint.register_blueprint(api_assistants_blueprint, url_prefix="/assistants")
api_blueprint.register_blueprint(api_notes_blueprint, url_prefix="/notes")
api_blueprint.register_blueprint(api_references_blueprint, url_prefix="/references")

ui_blueprint = Blueprint("ui", __name__)
ui_blueprint.register_blueprint(ui_assistants_blueprint, url_prefix="/assistants")
ui_blueprint.register_blueprint(ui_notes_blueprint, url_prefix="/notes")
ui_blueprint.register_blueprint(ui_references_blueprint, url_prefix="/references")


flask_app.register_blueprint(api_blueprint, url_prefix="/api/v1")
flask_app.register_blueprint(ui_blueprint, url_prefix="/ui")
