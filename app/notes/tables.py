from piccolo.table import Table
from piccolo.columns import ForeignKey, JSONB, Timestamp, Varchar, UUID
from piccolo.utils.pydantic import create_pydantic_model


class BaseTable(Table):
    id = UUID(primary_key=True)
    created_at = Timestamp()
    updated_at = Timestamp()
    title = Varchar(length=255)


class Note(BaseTable):
    pass


class Cell(BaseTable):
    note = ForeignKey(references=Note)
    title = Varchar(length=255)
    plugin = Varchar(length=255)
    content = JSONB()


NoteSerializer = create_pydantic_model(Note)
CellSerializer = create_pydantic_model(Cell)
