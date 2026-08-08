from __future__ import annotations
from functools import lru_cache
from typing import Literal

from pydantic import computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

AppEnvironment = Literal["development", "production", "test"]

# Sentinel that must never be deployed in production.
_JWT_SECRET_PLACEHOLDER = "replace-with-a-64-character-random-hex-secret"


class Settings(BaseSettings):
    """Application configuration loaded from the environment.

    Values come from environment variables (prefix-less) and an optional
    ``.env`` file. Unknown variables (``extra="ignore"``) are tolerated so the
    same process tree can share unrelated environment variables.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ---- Application -----------------------------------------------------
    app_name: str = "DecisionOS"
    app_env: AppEnvironment = "development"
    debug: bool = False
    log_level: str = "INFO"
    api_version: str = "0.1.0"

    # ---- Database --------------------------------------------------------
    database_host: str
    database_port: int
    database_name: str
    database_user: str
    database_password: str

    # Production connection pooling defaults. See core/database/session.py.
    database_pool_size: int = 20
    database_max_overflow: int = 10
    database_pool_timeout: int = 30
    database_pool_recycle: int = 1800

    # ---- Security --------------------------------------------------------
    jwt_secret_key: str
    jwt_access_token_expire_minutes: int = 30

    # ---- Web -------------------------------------------------------------
    # JSON array, e.g. ["http://localhost:5173"]; empty disables CORS origins.
    cors_origins: list[str] = []
    trusted_hosts: list[str] = []

    # ---- Rate limiting (SlowAPI) -----------------------------------------
    rate_limit_enabled: bool = False
    # Expressed in the ``limits`` grammar, e.g. "100/minute".
    rate_limit: str = "100/minute"

    @model_validator(mode="after")
    def _validate_secrets(self) -> Settings:
        if self.app_env == "production" and self.jwt_secret_key == _JWT_SECRET_PLACEHOLDER:
            raise ValueError("jwt_secret_key must be overridden in production")
        return self

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def database_url(self) -> str:
        return (
            "postgresql+asyncpg://"
            f"{self.database_user}:{self.database_password}"
            f"@{self.database_host}:{self.database_port}"
            f"/{self.database_name}"
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def database_url_sync(self) -> str:
        """Synchronous URL used by Alembic migrations (psycopg3)."""
        return (
            "postgresql+psycopg://"
            f"{self.database_user}:{self.database_password}"
            f"@{self.database_host}:{self.database_port}"
            f"/{self.database_name}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


settings = get_settings()
