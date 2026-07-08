from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="Bowling-HQ API", alias="APP_NAME")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=True, alias="DEBUG")
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    api_prefix: str = Field(default="/api/v1", alias="API_PREFIX")
    postgres_url: str = Field(
        default=(
            "postgresql://"
            "user"
            ":"
            "password"
            "@postgres:5432/bowling_hq"
        ),
        alias="POSTGRES_URL",
    )
    mongodb_uri: str = Field(
        default=(
            "mongodb://"
            "user"
            ":"
            "password"
            "@mongo:27017/bowling_hq?authSource=admin"
        ),
        alias="MONGODB_URI",
    )
    redis_url: str = Field(
        default="redis://redis:6379/0",
        alias="REDIS_URL",
    )
    secret_key: str = Field(
        default="change-me-in-production",
        alias="SECRET_KEY",
    )
    cors_origins: str = Field(
        default="http://localhost:5173",
        alias="CORS_ORIGINS",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
