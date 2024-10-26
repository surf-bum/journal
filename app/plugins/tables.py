from piccolo.table import Table
from piccolo.columns import Timestamp, Varchar, UUID
from piccolo.utils.pydantic import create_pydantic_model


class BaseTable(Table):
    id = UUID(primary_key=True)
    created_at = Timestamp()
    name = Varchar(length=255)
    updated_at = Timestamp()


class Plugin(BaseTable):
    path = Varchar()
    provider = Varchar()


PluginSerializer = create_pydantic_model(Plugin)
