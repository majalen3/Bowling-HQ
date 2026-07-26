from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class SessionCreateRequest(BaseModel):
    session_type: str = Field(min_length=1, max_length=50)
    location_name: Optional[str] = Field(default=None, max_length=255)


class SessionProgressItem(BaseModel):
    id: UUID
    session_type: str
    location_name: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime]


class SessionProgressSnapshot(BaseModel):
    total_sessions: int
    completed_sessions: int
    active_sessions: int
    sessions: list[SessionProgressItem]
