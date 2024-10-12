import os

from settings.utils import EnvMeta, Value


class Common(metaclass=EnvMeta):
    DATABASE_URL = Value("postgres://postgres:postgres@localhost:5432/journal")
    SECRET_KEY = Value("change-me-please")


config = os.getenv("SETTINGS_PROFILE", "Common")

settings_registry = {"Common": Common}

settings = settings_registry[config]
assert settings, f"Settings profile '{config}' not found."
