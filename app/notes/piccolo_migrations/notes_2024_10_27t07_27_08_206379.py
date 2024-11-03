from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.column_types import Integer
from piccolo.columns.indexes import IndexMethod


ID = "2024-10-27T07:27:08:206379"
VERSION = "1.22.0"
DESCRIPTION = "Add position column to cell."


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="notes", description=DESCRIPTION
    )

    manager.add_column(
        table_class_name="Cell",
        tablename="cell",
        column_name="position",
        db_column_name="position",
        column_class_name="Integer",
        column_class=Integer,
        params={
            "default": 0,
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    return manager
