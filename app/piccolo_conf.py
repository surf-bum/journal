from piccolo.conf.apps import AppRegistry
from piccolo.engine.postgres import PostgresEngine


from config import settings

DB = PostgresEngine(config={"dsn": settings.DATABASE_URL})


# A list of paths to piccolo apps
# e.g. ['blog.piccolo_app']
APP_REGISTRY = AppRegistry(apps=["notes.piccolo_app"])
