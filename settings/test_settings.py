import os

from settings.utils import EnvMeta, Value


def test_fallback_to_default_value_if_env_key_missing(monkeypatch):
    if os.getenv("DATABASE_URL"):
        monkeypatch.delenv("DATABASE_URL")

    class Common(metaclass=EnvMeta):
        DATABASE_URL = Value(
            "postgres://postgres:postgres@postgres:5432/journal-default"
        )

    assert (
        Common.DATABASE_URL
        == "postgres://postgres:postgres@postgres:5432/journal-default"
    )


def test_given_env_key_load_env_value(monkeypatch):
    monkeypatch.setenv(
        "DATABASE_URL", "postgres://postgres:postgres@postgres:5432/journal-from-env"
    )

    class Common(metaclass=EnvMeta):
        DATABASE_URL = Value(
            "postgres://postgres:postgres@postgres:5432/journal-default"
        )

    assert (
        Common.DATABASE_URL
        == "postgres://postgres:postgres@postgres:5432/journal-from-env"
    )
