from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="Monolith FastAPI", validation_alias="APP_NAME")
    app_env: str = Field(default="local", validation_alias="APP_ENV")
    app_debug: bool = Field(default=True, validation_alias="APP_DEBUG")
    app_log_level: str = Field(default="INFO", validation_alias="APP_LOG_LEVEL")
    app_version: str = Field(default="0.1.0", validation_alias="APP_VERSION")
    api_v1_prefix: str = Field(default="/api/v1", validation_alias="APP_API_V1_PREFIX")

    db_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/monolith",
        validation_alias="DB_URL",
    )
    db_echo: bool = Field(default=False, validation_alias="DB_ECHO")
    db_pool_size: int = Field(default=10, validation_alias="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=20, validation_alias="DB_MAX_OVERFLOW")
    db_pool_timeout: int = Field(default=30, validation_alias="DB_POOL_TIMEOUT")
    db_pool_recycle: int = Field(default=1800, validation_alias="DB_POOL_RECYCLE")
    db_pool_pre_ping: bool = Field(default=True, validation_alias="DB_POOL_PRE_PING")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
