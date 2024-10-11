import psycopg2
from flask import Flask, render_template, request, redirect, url_for, flash

from orm import Note

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DATABASE = 'journal'
USER = 'postgres'
PASSWORD = '12dfger'
HOST = 'localhost'
PORT = '5432'


def get_db_connection():
    conn = psycopg2.connect(
        dbname=DATABASE,
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT
    )
    return conn


with get_db_connection() as conn:
    Note.create_table(conn)  # Create the table if it doesn't exist


@app.route('/')
def index():
    conn = get_db_connection()
    notes = Note.all(conn)
    conn.close()
    return render_template('list.html', notes=notes)


@app.route('/notes/<uuid:note_id>', methods=['GET'])
def detail(note_id):
    conn = get_db_connection()
    note = Note.get(conn, note_id)
    conn.close()
    if note:
        return render_template('detail.html', note=note)
    else:
        flash('Note not found!')
        return redirect(url_for('index'))


@app.route('/update_note/<uuid:note_id>', methods=['POST'])
def update_note(note_id):
    title = request.form['title']
    content = request.form['content']

    conn = get_db_connection()
    note = Note.get(conn, note_id)

    if note:
        note.title = title
        note.content = content
        note.save(conn)
        flash('Note updated successfully!')
    else:
        flash('Note not found!')

    conn.close()
    return redirect(url_for('detail', note_id=note.id))


@app.route('/add_note', methods=['POST'])
def add_note():
    title = request.form['title']
    content = request.form['content']

    if title and content:
        new_note = Note(title=title, content=content)
        with get_db_connection() as conn:
            new_note.save(conn)
        flash('Note added successfully!')
    else:
        flash('Please provide both title and content!')

    return redirect(url_for('index'))


@app.route('/delete_note/<uuid:note_id>', methods=['POST'])
def delete_note(note_id):
    with get_db_connection() as conn:
        note = Note.get(conn, note_id)
        if note:
            note.delete(conn)
            flash('Note deleted successfully!')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
