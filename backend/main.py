from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from db import close_db_connections
from routers.arsenal import router as arsenal_router
from routers.patterns import centers_router, router as patterns_router
from routers.recommendations import router as recommendations_router
from routers.sessions import router as sessions_router


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    yield
    await close_db_connections()


app = FastAPI(
    title="Bowling-HQ API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ──────────────────────────────────────────────────────────────────
prefix = settings.api_prefix

app.include_router(arsenal_router, prefix=prefix)
app.include_router(patterns_router, prefix=prefix)
app.include_router(centers_router, prefix=prefix)
app.include_router(sessions_router, prefix=prefix)
app.include_router(recommendations_router, prefix=prefix)


# ─── Root endpoints ───────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}


@app.get(f"{settings.api_prefix}")
async def api_root():
    return {
        "message": "Bowling-HQ API",
        "version": "0.1.0",
        "docs": "/docs",
        "endpoints": {
            "arsenal": f"{prefix}/arsenal",
            "patterns": f"{prefix}/patterns",
            "centers": f"{prefix}/centers",
            "sessions": f"{prefix}/sessions",
            "recommendations": f"{prefix}/recommendations",
        },
    }
