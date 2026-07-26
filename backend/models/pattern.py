from pydantic import BaseModel
from typing import Optional


class PatternBase(BaseModel):
    name: str
    pattern_type: Optional[str] = None   # 'house' | 'sport' | 'pba' | 'custom'
    oil_volume: Optional[str] = None     # 'light' | 'medium' | 'heavy' | 'very_heavy'
    oil_length_ft: Optional[int] = None
    difficulty: Optional[int] = None     # 1-4
    description: Optional[str] = None
    notes: Optional[str] = None


class PatternCreate(PatternBase):
    pass


class Pattern(PatternBase):
    id: int

    model_config = {"from_attributes": True}
