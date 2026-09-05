from app.core.config import Settings


def test_normalizes_bare_postgres_url() -> None:
    settings = Settings(database_url="postgres://user:pass@host:5432/db")

    assert settings.database_url == "postgresql+asyncpg://user:pass@host:5432/db"


def test_normalizes_postgresql_url_without_driver() -> None:
    settings = Settings(database_url="postgresql://user:pass@host:5432/db")

    assert settings.database_url == "postgresql+asyncpg://user:pass@host:5432/db"


def test_leaves_sqlite_url_untouched() -> None:
    settings = Settings(database_url="sqlite+aiosqlite:///./app.db")

    assert settings.database_url == "sqlite+aiosqlite:///./app.db"


def test_cors_origins_list_splits_and_strips() -> None:
    settings = Settings(cors_origins=" http://localhost:3000 , https://admin.example.com ")

    assert settings.cors_origins_list == [
        "http://localhost:3000",
        "https://admin.example.com",
    ]
