import datetime

from orm.orm import SimpleORM


def test_create_table():
    class Note(SimpleORM):
        __tablename__ = "notes"
        created_at: datetime.datetime
        updated_at: datetime.datetime
        title: str
        content: str

    create_table_query = Note.create_table()
    create_table_query = "".join(create_table_query.splitlines())
    create_table_query = " ".join(create_table_query.split())
    assert (
        create_table_query
        == "CREATE TABLE IF NOT EXISTS notes ( id UUID PRIMARY KEY, created_at TIMESTAMPTZ, updated_at TIMESTAMPTZ, title TEXT, content TEXT )"
    )
