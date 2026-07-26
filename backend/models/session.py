from pydantic import BaseModel
from typing import Optional
from datetime import date


class SessionBase(BaseModel):
    user_id: int = 1
    center_id: Optional[int] = None
    pattern_id: Optional[int] = None
    session_type: Optional[str] = None  # 'league' | 'tournament' | 'practice' | 'open'
    session_date: date
    total_games: Optional[int] = None
    notes: Optional[str] = None


class SessionCreate(SessionBase):
    pass


class Session(SessionBase):
    id: int

    model_config = {"from_attributes": True}
