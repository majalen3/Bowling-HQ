from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import get_settings
from src.routes.arsenal import router as arsenal_router
from src.routes.commander import router as commander_router
from src.routes.ghost_bowler import router as ghost_bowler_router
from src.routes.health import router as health_router
from src.routes.patterns import router as patterns_router
from src.routes.progress import router as progress_router
from src.routes.sessions import router as sessions_router
from src.routes.tournament import router as tournament_router

settings = get_settings()
app = FastAPI(title=settings.app_name, debug=settings.debug)
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
app.include_router(arsenal_router)
app.include_router(patterns_router)
app.include_router(commander_router)
app.include_router(tournament_router)
app.include_router(ghost_bowler_router)


@app.get("/")
def read_root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "docs": "/docs",
        "health": "/health",
        "api_prefix": settings.api_prefix,
    }
