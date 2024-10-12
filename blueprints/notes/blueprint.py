import json
import uuid

from flask import (
    Blueprint,
    render_template,
    flash,
    redirect,
    url_for,
    request,
    send_file,
)
from datetime import datetime

from utils import setup_logger
from .models import Note

logger = setup_logger(__name__)

notes_blueprint = Blueprint("notes", __name__)


@notes_blueprint.route("/")
def index():
    notes = Note.all()
    return render_template("notes/list.html", notes=notes)


@notes_blueprint.route("/<uuid:note_id>", methods=["GET"])
def detail(note_id):
    note = Note.get(note_id)
    if note:
        return render_template("detail.html", note=note)
    else:
        flash("Note not found!")
        return redirect(url_for("ui.notes.index"))

@notes_blueprint.route("/<uuid:note_id>/update", methods=["POST"])
def update_note(note_id):
    title = request.form["title"]
    content = request.form["content"]

    note = Note.get(note_id)

    if note:
        note.title = title
        note.content = content
        note.updated_at = datetime.now()
        note.save()
        flash("Note updated successfully!")
    else:
        flash("Note not found!")

    return redirect(url_for("ui.notes.detail", note_id=note.id))


@notes_blueprint.route("/create", methods=["POST"])
def create_note():
    title = request.form["title"]
    content = request.form["content"]

    if title and content:
        new_note = Note(
            title=title,
            content=content,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        new_note.save()
        flash(f"Note '{new_note.title}' created successfully!")
    else:
        flash("Please provide both title and content!")

    return redirect(url_for("ui.notes.index"))


@notes_blueprint.route("/<uuid:note_id>/delete", methods=["GET"])
def delete_note(note_id: uuid.UUID):
    note = Note.get(note_id)
    if note:
        note.delete()
        flash("Note deleted successfully!")
    return redirect(url_for("ui.notes.index"))


@notes_blueprint.route("/backup-restore", methods=["GET", "POST"])
def backup_restore_notes():
    if request.method == "POST":
        if "backup" in request.form:
            notes = Note.all()

            deserialized_notes = [note.json() for note in notes]
            backup_file_name = "notes.json"
            with open(backup_file_name, "w") as json_file:
                deserialized_notes = [json.loads(_note) for _note in deserialized_notes]
                json.dump(deserialized_notes, json_file)

            return send_file(backup_file_name, as_attachment=True)

        elif "restore" in request.form:
            file = request.files["file"]
            logger.debug("Restoring file %s.", file)
            if file and file.filename.endswith(".json"):
                logger.debug("Passed .json file check.")
                notes_to_restore = json.load(file)
                logger.debug("Serialized %s.", notes_to_restore)
                for note in notes_to_restore:
                    new_note = Note(**note)
                    new_note.id = None
                    new_note.save()
                return redirect(url_for("ui.notes.backup_restore_notes"))

    notes = Note.all()
    return render_template("notes/backup_restore.html", notes=notes)
