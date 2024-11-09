import os


class EnvMeta(type):
    def __new__(cls, name, bases, attrs):
        for attr_name, attr_value in attrs.items():
            if isinstance(attr_value, Value):
                attrs[attr_name] = attr_value.get(attr_name)
        return super().__new__(cls, name, bases, attrs)


class Value:
    def __init__(self, default, prefix=None):
        self.default = default

    def get(self, attr_name):
        env_key = attr_name
        return os.getenv(env_key, self.default)


class Common(metaclass=EnvMeta):
    DATABASE_URL = Value("postgres://postgres:postgres@localhost:5432/journal")
    OLLAMA_HOST = Value("127.0.0.1")
    OIDC_CLIENT_ID = Value("")
    OIDC_CLIENT_SECRET = Value("")
    OIDC_DISCOVERY_URI = Value("")
    OIDC_REDIRECT_URIS = Value("")
    S3_BUCKET = Value("journal")
    SECRET_KEY = Value("change-me-please")


config = os.getenv("SETTINGS_PROFILE", "Common")

settings_registry = {"Common": Common}

settings = settings_registry[config]
assert settings, f"Settings profile '{config}' not found."
