from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from src.models.patterns import LanePattern, LanePatternDetail
from src.services.patterns import get_pattern, list_patterns

router = APIRouter(prefix="/api/v1/patterns", tags=["patterns"])


@router.get("", response_model=list[LanePattern])
def read_patterns(
    difficulty: int | None = Query(default=None),
    pattern_type: str | None = Query(default=None),
) -> list[LanePattern]:
    return list_patterns(difficulty=difficulty, pattern_type=pattern_type)


@router.get("/{pattern_id}", response_model=LanePatternDetail)
def read_pattern(pattern_id: UUID) -> LanePatternDetail:
    pattern = get_pattern(pattern_id)
    if pattern is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pattern not found",
        )
    return pattern
