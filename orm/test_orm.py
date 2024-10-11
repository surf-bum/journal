import pytest
from testcontainers.postgres import PostgresContainer

from orm.orm import SimpleORM


def test_create_table(monkeypatch, postgres):
    class Note(SimpleORM):
        __tablename__ = "notes"
        title: str
        content: str

    create_table_query = Note.create_table()
    assert create_table_query == ""
