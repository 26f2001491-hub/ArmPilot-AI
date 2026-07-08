from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "ArmPilot-AI"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    DATABASE_URL: str

    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = "logs"


@lru_cache
def get_settings() -> Settings:
    return Settings()
