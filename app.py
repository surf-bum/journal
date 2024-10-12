from flask import Blueprint, Flask

from blueprints.notes.blueprint import notes_blueprint
from config import settings

app = Flask(__name__)
app.secret_key = settings.SECRET_KEY

ui_blueprint = Blueprint("ui", __name__)
ui_blueprint.register_blueprint(notes_blueprint, url_prefix="/notes")

app.register_blueprint(ui_blueprint, url_prefix="/ui")
