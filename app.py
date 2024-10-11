from flask import Flask

from blueprints.notes import notes_blueprint
from orm import Note, get_db_connection

app = Flask(__name__)
app.secret_key = 'your_secret_key'


with get_db_connection() as conn:
    Note.create_table(conn)

app.register_blueprint(notes_blueprint, url_prefix='/notes')

if __name__ == '__main__':
    app.run(debug=True)
