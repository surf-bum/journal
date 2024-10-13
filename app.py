from flask import Blueprint, Flask

from blueprints.notes.blueprint import api_notes_blueprint, ui_notes_blueprint
from blueprints.references.blueprint import (
    api_references_blueprint,
    ui_references_blueprint,
)
from config import settings

app = Flask(__name__)
app.secret_key = settings.SECRET_KEY

api_blueprint = Blueprint("api", __name__)
api_blueprint.register_blueprint(api_notes_blueprint, url_prefix="/notes")
api_blueprint.register_blueprint(api_references_blueprint, url_prefix="/references")

ui_blueprint = Blueprint("ui", __name__)
ui_blueprint.register_blueprint(ui_notes_blueprint, url_prefix="/notes")
ui_blueprint.register_blueprint(ui_references_blueprint, url_prefix="/references")


app.register_blueprint(api_blueprint, url_prefix="/api/v1")
app.register_blueprint(ui_blueprint, url_prefix="/ui")
