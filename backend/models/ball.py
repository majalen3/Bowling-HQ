from pydantic import BaseModel
from typing import Optional


class BallBase(BaseModel):
    name: str
    brand: str
    weight_lbs: int
    coverstock_type: Optional[str] = None
    core_type: Optional[str] = None
    rg: Optional[float] = None
    differential: Optional[float] = None
    finish: Optional[str] = None
    layout: Optional[str] = None
    purpose: Optional[str] = None
    hook_potential: Optional[int] = None
    length_rating: Optional[int] = None
    backend_rating: Optional[int] = None
    is_spare_ball: bool = False
    active: bool = True
    notes: Optional[str] = None


class BallCreate(BallBase):
    pass


class Ball(BallBase):
    id: int

    model_config = {"from_attributes": True}
