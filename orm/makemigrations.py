import importlib

from orm.orm import SimpleORM


class Migration(SimpleORM):
    __tablename__ = "migrations"
    title: str
    version: int


if __name__ == "__main__":
    mod = importlib.import_module("blueprints.notes.migrations.0001_initial")
    print(mod)
