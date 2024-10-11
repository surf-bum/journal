from flask import Flask

from blueprints.notes import notes_blueprint
from orm import Note, get_db_connection

app = Flask(__name__)

with get_db_connection() as conn:
    Note.create_table(conn)

app.register_blueprint(notes_blueprint, url_prefix="/notes")
