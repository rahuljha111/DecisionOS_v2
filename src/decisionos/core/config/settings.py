from functools import lru_cache

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    app_name: str
    app_env: str
    debug: bool
    log_level: str

    # Database
    database_host: str
    database_port: int
    database_name: str
    database_user: str
    database_password: str

    @computed_field
    @property
    def database_url(self) -> str:
        return (
            "postgresql+asyncpg://"
            f"{self.database_user}:{self.database_password}"
            f"@{self.database_host}:{self.database_port}"
            f"/{self.database_name}"
        )

    @computed_field
    @property
    def database_url_sync(self) -> str:
        return (
            "postgresql+psycopg://"
            f"{self.database_user}:{self.database_password}"
            f"@{self.database_host}:{self.database_port}"
            f"/{self.database_name}"
        )

@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()