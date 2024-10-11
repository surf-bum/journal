from flask import Flask

from blueprints.notes.blueprint import notes_blueprint
from config import settings

app = Flask(__name__)
app.secret_key = settings.SECRET_KEY

app.register_blueprint(notes_blueprint, url_prefix="/notes")
