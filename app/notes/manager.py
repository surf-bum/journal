from app.notes.tables import Cell, Note, NoteSerializer
from app.utils import setup_logger
from piccolo.query.functions.aggregate import Count

logger = setup_logger(__name__)


class NoteManager:
    @classmethod
    async def count_notes(cls) -> list:
        return await Note.select(Count())

    @classmethod
    async def create_note(cls, note, cells):
        note = await Note.insert(
            Note(**note.dict()),
        ).returning(Note.title)
        note = note[0]

        await Cell.insert(*[Cell(**cell.dict()) for cell in cells])

        return NoteSerializer(**note)

    @classmethod
    async def delete_cell(cls, cell_id) -> None:
        await Cell.delete().where(Cell.id == cell_id)

    @classmethod
    async def delete_note(cls, note_id) -> None:
        await Note.delete().where(Note.id == note_id)

    @classmethod
    async def get_cell(cls, cell_id) -> Cell:
        return await Cell.objects().get(Cell.id == cell_id).output(load_json=True)

    @classmethod
    async def get_note(cls, note_id) -> Note:
        return await Note.objects().get(Note.id == note_id)

    @classmethod
    async def get_cells(cls, note_id) -> list:
        return await Cell.objects().where(Cell.note == note_id)

    @classmethod
    async def get_notes(cls) -> list:
        return await Note.select()

    @classmethod
    async def update_cell(cls, partial_cell) -> list:
        return await Cell.update(
            title=partial_cell.title, content=partial_cell.content
        ).where(Cell.id == partial_cell.id)

    @classmethod
    async def update_note(cls, partial_note) -> list:
        return await Note.update(title=partial_note.title).where(
            Note.id == partial_note.id
        )
