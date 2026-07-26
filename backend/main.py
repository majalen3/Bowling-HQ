from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from routes import (
    commander_router,
    arsenal_router,
    patterns_router,
    sessions_router,
    ghost_bowler_router,
)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered bowling intelligence platform API",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = "/api/v1"

app.include_router(commander_router, prefix=API_PREFIX)
app.include_router(arsenal_router,   prefix=API_PREFIX)
app.include_router(patterns_router,  prefix=API_PREFIX)
app.include_router(sessions_router,  prefix=API_PREFIX)
app.include_router(ghost_bowler_router, prefix=API_PREFIX)


@app.get("/", tags=["Health"])
def root():
    return {"app": settings.app_name, "version": settings.app_version, "status": "running"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}
