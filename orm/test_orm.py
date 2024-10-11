import pytest
from testcontainers.postgres import PostgresContainer

from orm.orm import SimpleORM


@pytest.fixture()
def postgres():
    with PostgresContainer("postgres:16.4") as postgres:
        yield postgres.get_connection_url()
        postgres.stop()


def test_create_table(monkeypatch, postgres):
    monkeypatch.setenv(
        "DATABASE_URL", "postgres://postgres:postgres@postgres:5432/journal"
    )

    class Note(SimpleORM):
        __tablename__ = "notes"
        title: str
        content: str

    create_table_query = Note.create_table()
    assert create_table_query == ""
