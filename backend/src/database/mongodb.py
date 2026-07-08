from src.config import get_settings


def get_mongodb_uri() -> str:
    return get_settings().mongodb_uri
