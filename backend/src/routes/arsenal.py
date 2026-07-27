from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from src.models.arsenal import ArsenalAddRequest, ArsenalItem, BowlingBall
from src.services.arsenal import (
    add_to_arsenal,
    get_catalog_ball,
    list_catalog,
    list_user_arsenal,
    remove_from_arsenal,
)

router = APIRouter(prefix="/api/v1/arsenal", tags=["arsenal"])


@router.get("/catalog", response_model=list[BowlingBall])
def read_catalog(
    oil_condition: str | None = Query(default=None),
    coverstock_type: str | None = Query(default=None),
) -> list[BowlingBall]:
    return list_catalog(
        oil_condition=oil_condition,
        coverstock_type=coverstock_type,
    )


@router.get("/catalog/{ball_id}", response_model=BowlingBall)
def read_catalog_ball(ball_id: UUID) -> BowlingBall:
    ball = get_catalog_ball(ball_id)
    if ball is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ball not found",
        )
    return ball


@router.get("", response_model=list[ArsenalItem])
def read_user_arsenal() -> list[ArsenalItem]:
    return list_user_arsenal()


@router.post(
    "", response_model=ArsenalItem, status_code=status.HTTP_201_CREATED
)
def create_arsenal_item(payload: ArsenalAddRequest) -> ArsenalItem:
    try:
        return add_to_arsenal(payload)
    except KeyError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ball not found",
        ) from error


@router.delete("/{user_arsenal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_arsenal_item(user_arsenal_id: UUID) -> None:
    try:
        remove_from_arsenal(user_arsenal_id)
    except KeyError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Arsenal item not found",
        ) from error
