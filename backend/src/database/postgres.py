from src.config import get_settings


def get_postgres_url() -> str:
    return get_settings().postgres_url
