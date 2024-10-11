import uuid

from flask import Blueprint, render_template, flash, redirect, url_for, request

from models import Note
from orm import get_db_connection

notes_blueprint = Blueprint("notes", __name__)


@notes_blueprint.route("/")
def index():
    conn = get_db_connection()
    notes = Note.all(conn)
    conn.close()
    return render_template("list.html", notes=notes)


@notes_blueprint.route("/<uuid:note_id>", methods=["GET"])
def detail(note_id):
    conn = get_db_connection()
    note = Note.get(conn, note_id)
    conn.close()
    if note:
        return render_template("detail.html", note=note)
    else:
        flash("Note not found!")
        return redirect(url_for("notes.index"))  # Update to point to notes blueprint


@notes_blueprint.route("/<uuid:note_id>/update", methods=["POST"])
def update_note(note_id):
    title = request.form["title"]
    content = request.form["content"]

    conn = get_db_connection()
    note = Note.get(conn, note_id)

    if note:
        note.title = title
        note.content = content
        note.save(conn)
        flash("Note updated successfully!")
    else:
        flash("Note not found!")

    conn.close()
    return redirect(
        url_for("notes.detail", note_id=note.id)
    )  # Update to point to notes blueprint


@notes_blueprint.route("/add", methods=["POST"])
def add_note():
    title = request.form["title"]
    content = request.form["content"]

    if title and content:
        new_note = Note(title=title, content=content)
        with get_db_connection() as conn:
            new_note.save(conn)
        flash("Note created successfully!")
    else:
        flash("Please provide both title and content!")

    return redirect(url_for("notes.index"))


@notes_blueprint.route("/<uuid:note_id>/delete", methods=["GET"])
def delete_note(note_id: uuid.UUID):
    with get_db_connection() as conn:
        note = Note.get(conn, note_id)
        if note:
            note.delete(conn)
            flash("Note deleted successfully!")
    return redirect(url_for("notes.index"))
