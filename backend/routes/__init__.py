from routes.commander import router as commander_router
from routes.arsenal import router as arsenal_router
from routes.patterns import router as patterns_router
from routes.sessions import router as sessions_router
from routes.ghost_bowler import router as ghost_bowler_router

__all__ = [
    "commander_router",
    "arsenal_router",
    "patterns_router",
    "sessions_router",
    "ghost_bowler_router",
]
