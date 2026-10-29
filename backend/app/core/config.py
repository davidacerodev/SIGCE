from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    database_url: str = "postgresql+psycopg://notebooklm:notebooklm@localhost:5432/notebooklm"
    cors_origins: str = "http://localhost:5173"
    secret_key: str = "change-me-in-production"
    upload_dir: str = "uploads"
    max_upload_mb: int = 25
    ai_provider: str = "mock"
    embedding_dimensions: int = 768
    access_token_minutes: int = 720

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
