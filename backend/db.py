"""
Database connection factories for PostgreSQL (SQLAlchemy async),
MongoDB (Motor), and Redis.
"""
from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from config import settings

# ─── PostgreSQL (SQLAlchemy async) ───────────────────────────────────────────

engine = create_async_engine(
    settings.postgres_url,
    pool_pre_ping=True,
    echo=settings.debug,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""


async def get_db() -> AsyncSession:  # type: ignore[return]
    """FastAPI dependency — yields an async SQLAlchemy session."""
    async with AsyncSessionLocal() as session:
        yield session


# ─── MongoDB (Motor) ─────────────────────────────────────────────────────────

_mongo_client: AsyncIOMotorClient | None = None


def get_mongo_client() -> AsyncIOMotorClient:
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = AsyncIOMotorClient(settings.mongodb_uri)
    return _mongo_client


def get_mongo_db() -> AsyncIOMotorDatabase:
    return get_mongo_client()[settings.mongodb_db]


# ─── Redis ───────────────────────────────────────────────────────────────────

_redis: Redis | None = None


async def get_redis() -> Redis:
    global _redis
    if _redis is None:
        _redis = Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            password=settings.redis_password or None,
            decode_responses=True,
        )
    return _redis


# ─── Lifecycle helpers (called from main.py lifespan) ────────────────────────

async def close_db_connections() -> None:
    await engine.dispose()
    if _mongo_client is not None:
        _mongo_client.close()
    if _redis is not None:
        await _redis.aclose()
