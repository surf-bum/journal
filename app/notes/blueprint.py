import json
import tempfile
import uuid

from pydantic import ValidationError

from app.notes.manager import NoteManager
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

from app.notes.serializers import CreateNote, PatchNote
from app.utils import setup_logger
from .tables import CellSerializer, NoteSerializer


logger = setup_logger(__name__)

api_notes_blueprint = Blueprint("notes_api", __name__)
ui_notes_blueprint = Blueprint("notes_ui", __name__)


@ui_notes_blueprint.route("/")
async def index():
    notes = await NoteManager.get_notes()
    return render_template("notes/list.html", notes=notes)


@ui_notes_blueprint.route("/<uuid:note_id>", methods=["GET"])
async def get_note(note_id):
    note = await NoteManager.get_note(note_id)
    cells = await NoteManager.get_cells(note_id)
    if note:
        return render_template("notes/detail.html", cells=cells, note=note)
    else:
        flash("Note not found!")
        return redirect(url_for("ui.notes_ui.index"))


@ui_notes_blueprint.route(
    "/notes/<uuid:note_id>/cells", methods=["POST"]
)
async def create_cell(note_id):
    title = request.form["title"]
    content = request.form["content"]

    note = await NoteManager.get_note(note_id)

    cell = CellSerializer(
        id=uuid.uuid4(),
        content=content,
        created_at=datetime.now(),
        note=note.id,
        plugin="markdown",
        position=0,
        title = title,
        updated_at=datetime.now(),
    )
    cell = await NoteManager.create_cell(cell)

    return redirect(url_for("ui.notes_ui.get_note", note_id=note_id))


@ui_notes_blueprint.route(
    "/notes/<uuid:note_id>/cells/<uuid:cell_id>/update", methods=["POST"]
)
async def update_cell(cell_id, note_id):
    title = request.form["title"]
    content = request.form["content"]

    cell = await NoteManager.get_cell(cell_id)
    cell.title = title
    cell.content = content
    await NoteManager.update_cell(cell)

    return redirect(url_for("ui.notes_ui.get_note", note_id=note_id))

@ui_notes_blueprint.route("/create", methods=["POST"])
async def create_note():
    title = request.form["title"]

    try:
        serialized_note = CreateNote.model_validate({"title": title})
    except ValidationError as e:
        logger.error(e)
        return {"error": {"message": str(e)}}, 400

    if note := await NoteManager.create_note(serialized_note):
        flash(f"Note '{note.title}' created successfully!")
    else:
        flash("Please provide title!")

    return redirect(url_for("ui.notes_ui.get_note", note_id=note.id))


@ui_notes_blueprint.route(
    "/<uuid:note_id>/cells/<uuid:cell_id>/delete", methods=["GET"]
)
async def delete_cell(cell_id: uuid.UUID, note_id: uuid.UUID):
    note = await NoteManager.get_cell(cell_id)
    if note:
        await NoteManager.delete_cell(cell_id)
        flash("Cell deleted successfully!")
    return redirect(url_for("ui.notes_ui.get_note", note_id=note_id))


@ui_notes_blueprint.route("/<uuid:note_id>/delete", methods=["GET"])
async def delete_note(note_id: uuid.UUID):
    note = await NoteManager.get_note(note_id)
    if note:
        await NoteManager.delete_note(note_id)
        flash("Note deleted successfully!")
    return redirect(url_for("ui.notes_ui.index"))


@ui_notes_blueprint.route("/backup-restore", methods=["GET", "POST"])
async def backup_restore_notes():
    if request.method == "POST":
        if "backup" in request.form:
            notes = await NoteManager.get_notes()

            deserialized_notes = [note.model_dump_json() for note in notes]
            with tempfile.NamedTemporaryFile(mode="w", delete=False) as json_file:
                deserialized_notes = [json.loads(_note) for _note in deserialized_notes]
                json.dump(deserialized_notes, json_file)

            return send_file(
                json_file.name, as_attachment=True, download_name="notes.json"
            )

        elif "restore" in request.form:
            file = request.files["file"]
            logger.debug("Restoring file %s.", file)
            if file and file.filename.endswith(".json"):
                logger.debug("Passed .json file check.")
                notes_to_restore = json.load(file)
                logger.debug("Serialized %s.", notes_to_restore)

                for note in notes_to_restore:
                    content = note.get("content")
                    title = note.get("title")

                    new_note = NoteSerializer(
                        id=uuid.uuid4(),
                        created_at=datetime.now(),
                        title=title,
                        updated_at=datetime.now(),
                    )
                    new_cell = CellSerializer(
                        id=uuid.uuid4(),
                        content=json.dumps({"body": content}),
                        created_at=datetime.now(),
                        note=new_note.id,
                        title=title,
                        updated_at=datetime.now(),
                        plugin="markdown",
                    )
                    new_note = await NoteManager.create_note(new_note, [new_cell])

                return redirect(url_for("ui.notes_ui.backup_restore_notes"))

    notes = await NoteManager.get_notes()
    return render_template("notes/backup_restore.html", notes=notes)

@ui_notes_blueprint.route("/partials/<uuid:note_id>/editor/cells/<uuid:cell_id>")
async def partial_cell_editor(cell_id, note_id):
    cell = await NoteManager.get_cell(cell_id)
    note = await NoteManager.get_note(note_id)

    return render_template("notes/partials/cells/editor.html", cell=cell, note=note)

@ui_notes_blueprint.route(
    "/partials/<uuid:note_id>/cells/<uuid:cell_id>/position", methods=["POST"]
)
async def partial_cell_position(cell_id, note_id):
    position = int(request.form["position"])

    cell = await NoteManager.get_cell(cell_id)
    cell.position += position
    await NoteManager.update_cell(cell)

    cells = await NoteManager.get_cells(note_id)
    note = await NoteManager.get_note(note_id)

    return render_template("notes/partials/cells/cells.html", cells=cells, note=note)

@ui_notes_blueprint.route("/partials/<uuid:note_id>/viewer/cells/<uuid:cell_id>")
async def partial_cell_viewer(cell_id, note_id):
    cell = await NoteManager.get_cell(cell_id)
    note = await NoteManager.get_note(note_id)

    return render_template("notes/partials/cells/viewer.html", cell=cell, note=note)


@ui_notes_blueprint.route("/partials/<uuid:note_id>/editor")
async def partial_note_editor(note_id):
    note = await NoteManager.get_note(note_id)

    return render_template("notes/partials/notes/editor.html", note=note)


@ui_notes_blueprint.route("/partials/<uuid:note_id>/viewer")
async def partial_note_viewer(note_id):
    note = await NoteManager.get_note(note_id)

    return render_template("notes/partials/notes/viewer.html", note=note)


@ui_notes_blueprint.route("/partials/<uuid:note_id>/update", methods=["POST"])
async def partial_note_update(note_id):
    title = request.form["title"]

    note = await NoteManager.get_note(note_id)
    note.title = title

    await NoteManager.update_note(note)

    return redirect(url_for("ui.notes_ui.partial_note_viewer", note_id=note.id))

@api_notes_blueprint.route(
    "/<uuid:note_id>", methods=["DELETE"]
)
async def delete_api_note(note_id):
    if _ := await NoteManager.get_note(note_id):
        await NoteManager.delete_note(note_id)
    else:
        "", 404

    return "", 204

@api_notes_blueprint.route(
    "/<uuid:note_id>", methods=["GET"]
)
async def get_api_note(note_id):
    if _ := await NoteManager.get_note(note_id):
        return {}
    else:
        return {"error": {"message": "Object not found"}}, 404
    
@api_notes_blueprint.route(
    "/<uuid:note_id>", methods=["PATCH"]
)
async def patch_note(note_id):
    try:
        serialized_note = PatchNote.model_validate(request.json)
    except ValidationError as e:
        logger.error(e)
        return {"error": {"message": str(e)}}, 400
    
    if _ := await NoteManager.get_note(note_id):
        NoteManager.update_note(serialized_note)
        return serialized_note.model_dump()
    else:
        return {"error": {"message": "Object not found"}}, 404

@api_notes_blueprint.route(
    "/", methods=["POST"]
)
async def post_note():
    try:
        serialized_note = CreateNote.model_validate(request.json)
    except ValidationError as e:
        logger.error(e)
        return {"error": {"message": str(e)}}, 400

    note = await NoteManager.create_note(serialized_note)

    return note.model_dump(), 201


@api_notes_blueprint.route(
    "/<uuid:note_id>/cells/<uuid:cell_id>/content", methods=["GET"]
)
async def cell_content(cell_id, note_id):
    cell = await NoteManager.get_cell(cell_id)
    if not cell:
        return {"error": {"message": "Detail not found."}}

    return {"content": cell.content}
