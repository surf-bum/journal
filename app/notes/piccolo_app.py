import os

from notes.tables import Cell, Note
from piccolo.conf.apps import AppConfig


CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))


APP_CONFIG = AppConfig(
    app_name="notes",
    migrations_folder_path=os.path.join(CURRENT_DIRECTORY, "piccolo_migrations"),
    table_classes=[Cell, Note],
    migration_dependencies=[],
    commands=[],
)
