from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Bowling-HQ"
    app_version: str = "0.1.0"
    debug: bool = True
    # Required via DATABASE_URL environment variable (see .env.example)
    database_url: str
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    class Config:
        env_file = ".env"


settings = Settings()
