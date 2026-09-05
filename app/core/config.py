from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "fastapisample"
    environment: str = "local"
    debug: bool = False
    database_url: str = "sqlite+aiosqlite:///./app.db"
    api_v1_prefix: str = "/api/v1"
    log_level: str = "INFO"
    # Comma-separated: managed-Postgres/PaaS env vars are plain strings, not JSON.
    cors_origins: str = "http://localhost:3000"

    @field_validator("database_url", mode="after")
    @classmethod
    def _normalize_database_url(cls, value: str) -> str:
        # Managed Postgres providers (Railway, Neon, Supabase, ...) hand out
        # plain postgres(ql):// URLs, but SQLAlchemy's async engine needs the
        # asyncpg driver named explicitly or it picks a sync driver and breaks
        # every await in the app.
        if value.startswith("postgres://"):
            return "postgresql+asyncpg://" + value.removeprefix("postgres://")
        if value.startswith("postgresql://"):
            return "postgresql+asyncpg://" + value.removeprefix("postgresql://")
        return value

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
