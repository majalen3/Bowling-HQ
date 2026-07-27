from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from src.models.arsenal import (
    ArsenalFitRequest,
    ArsenalFitResponse,
    ArsenalResponse,
    BallCreate,
    BallItem,
    CreateAndAddBallRequest,
    UserArsenalBall,
)
from src.services.arsenal import (
    create_and_add_ball,
    ensure_ball_catalog,
    get_arsenal_fit_recommendations,
    get_user_arsenal,
    list_balls_catalog,
    remove_from_arsenal,
)
from src.services.session_progress import DEMO_USER_ID

router = APIRouter(prefix="/api/v1/arsenal", tags=["arsenal"])


@router.get("", response_model=ArsenalResponse)
def read_arsenal() -> ArsenalResponse:
    # TODO: replace with authenticated user
    return get_user_arsenal(DEMO_USER_ID)


@router.post("", response_model=UserArsenalBall, status_code=201)
def add_ball(payload: CreateAndAddBallRequest) -> UserArsenalBall:
    # TODO: replace with authenticated user
    ball_create = BallCreate.model_validate(
        payload.model_dump(exclude={"notes"})
    )
    return create_and_add_ball(
        DEMO_USER_ID,
        ball_create,
        payload.notes,
    )


@router.delete("/{arsenal_id}")
def delete_ball(arsenal_id: UUID) -> dict[str, bool]:
    # TODO: replace with authenticated user
    deleted = remove_from_arsenal(DEMO_USER_ID, arsenal_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Arsenal entry not found",
        )
    return {"deleted": True}


@router.get("/catalog", response_model=list[BallItem])
def read_catalog() -> list[BallItem]:
    ensure_ball_catalog()
    return list_balls_catalog()


@router.post("/fit", response_model=ArsenalFitResponse)
def score_arsenal_fit(payload: ArsenalFitRequest) -> ArsenalFitResponse:
    return get_arsenal_fit_recommendations(DEMO_USER_ID, payload)
