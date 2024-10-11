from flask import Flask

from blueprints.notes import notes_blueprint
from config import settings
from orm import Note, get_db_connection

app = Flask(__name__)
app.secret_key = settings.SECRET_KEY

with get_db_connection() as conn:
    Note.create_table(conn)

app.register_blueprint(notes_blueprint, url_prefix="/notes")
