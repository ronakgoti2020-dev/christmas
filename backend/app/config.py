from functools import lru_cache
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _sqlalchemy_url(url: str) -> str:
    if url.startswith("postgres://"):
        return "postgresql+psycopg2://" + url[len("postgres://") :]
    if url.startswith("postgresql://") and "+psycopg2" not in url:
        return "postgresql+psycopg2://" + url[len("postgresql://") :]
    return url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "SecretSanta"
    app_env: Literal["development", "test", "production"] = "development"
    secret_key: str = "change-me-in-production-use-a-long-random-string"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7
    refresh_token_expire_minutes: int = 60 * 24 * 30

    database_url: str = "postgresql+psycopg2://secretsanta:secretsanta@localhost:5432/secretsanta"

    @field_validator("database_url")
    @classmethod
    def postgres_scheme(cls, value: str) -> str:
        return _sqlalchemy_url(value)
    redis_url: str = "redis://localhost:6379/0"

    frontend_url: str = "http://localhost:3000"
    api_public_url: str = "http://localhost:8000"
    cors_origins: str = "*"

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from: str = "SecretSanta <noreply@secretsanta.app>"

    google_client_id: str = ""
    aws_s3_bucket: str = ""
    aws_region: str = "us-east-1"
    upload_dir: str = "uploads"

    rate_limit: str = "60/minute"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
