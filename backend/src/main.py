from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import get_settings
from src.routes.analytics import router as analytics_router
from src.routes.arsenal import router as arsenal_router
from src.routes.auth import router as auth_router
from src.routes.games import router as games_router
from src.routes.health import router as health_router
from src.routes.progress import router as progress_router
from src.routes.recommendations import router as recommendations_router
from src.routes.sessions import router as sessions_router
from src.services.arsenal import ensure_ball_catalog

settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    try:
        ensure_ball_catalog()
    except Exception:
        # Catalog seeding is best-effort; the database may be
        # unavailable in some environments (e.g. tests).
        pass
    yield


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health_router)
app.include_router(progress_router)
app.include_router(sessions_router)
app.include_router(games_router)
app.include_router(arsenal_router)
app.include_router(recommendations_router)
app.include_router(analytics_router)
app.include_router(auth_router)


@app.get("/")
def read_root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "docs": "/docs",
        "health": "/health",
        "api_prefix": settings.api_prefix,
    }
