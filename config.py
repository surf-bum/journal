import os

from settings.utils import EnvMeta, Value


class Common(metaclass=EnvMeta):
    DATABASE_URL = Value("postgres://postgres:postgres@postgres:5432/journal-default")


config = os.getenv("SETTINGS_PROFILE", "Common")

settings_registry = {
    "Common": Common
}

settings = settings_registry[config]
assert settings, f"Settings profile '{config}' not found."
