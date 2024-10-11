from orm.orm import SimpleORM


def test_create_table():
    class Note(SimpleORM):
        __tablename__ = "notes"
        title: str
        content: str

    create_table_query = Note.create_table()
    assert create_table_query == ""
