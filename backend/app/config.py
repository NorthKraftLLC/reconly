"""Application configuration using pydantic-settings."""

from pathlib import Path

from pydantic_settings import BaseSettings

# Find .env file (check current dir, then project root)
_env_path = Path(".env")
if not _env_path.exists():
    _project_root = Path(__file__).resolve().parent.parent.parent
    _env_path = _project_root / ".env"


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    REDIS_URL: str = "redis://redis:6379/0"
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    FRONTEND_URL: str = "http://localhost:5173"
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    DEBUG: bool = False

    model_config = {"env_file": str(_env_path), "env_file_encoding": "utf-8"}


settings = Settings()
