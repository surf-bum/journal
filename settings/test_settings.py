from settings.utils import EnvMeta, Value


def test_fallback_to_default_value_if_env_variable_missing(monkeypatch):
    monkeypatch.delenv(
        "DATABASE_URL"
    )

    class Common(metaclass=EnvMeta):
        DATABASE_URL = Value("postgres://postgres:postgres@postgres:5432/journal-default")

    assert (
            Common.DATABASE_URL
            == "postgres://postgres:postgres@postgres:5432/journal-default"
    )


def test_load_from_env_variable(monkeypatch):
    monkeypatch.setenv(
        "DATABASE_URL", "postgres://postgres:postgres@postgres:5432/journal-from-env"
    )

    class Common(metaclass=EnvMeta):
        DATABASE_URL = Value("postgres://postgres:postgres@postgres:5432/journal-default")

    assert (
            Common.DATABASE_URL
            == "postgres://postgres:postgres@postgres:5432/journal-from-env"
    )
