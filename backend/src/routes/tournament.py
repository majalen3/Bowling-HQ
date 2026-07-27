from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from src.models.tournament import (
    LineupBall,
    LineupBallAddRequest,
    LineupCreateRequest,
    LineupRecommendation,
    TournamentLineup,
    TournamentLineupDetail,
)
from src.services.tournament import (
    add_ball_to_lineup,
    create_lineup,
    get_lineup,
    list_lineups,
    recommend_lineup,
    remove_ball_from_lineup,
)

router = APIRouter(prefix="/api/v1/tournament", tags=["tournament"])


@router.get("/lineups", response_model=list[TournamentLineup])
def read_lineups() -> list[TournamentLineup]:
    return list_lineups()


@router.post(
    "/lineups",
    response_model=TournamentLineup,
    status_code=status.HTTP_201_CREATED,
)
def create_lineup_route(payload: LineupCreateRequest) -> TournamentLineup:
    return create_lineup(payload)


@router.get("/lineups/{lineup_id}", response_model=TournamentLineupDetail)
def read_lineup(lineup_id: UUID) -> TournamentLineupDetail:
    lineup = get_lineup(lineup_id)
    if lineup is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lineup not found",
        )
    return lineup


@router.post(
    "/lineups/{lineup_id}/recommend",
    response_model=list[LineupRecommendation],
)
def recommend_lineup_route(lineup_id: UUID) -> list[LineupRecommendation]:
    try:
        return recommend_lineup(lineup_id)
    except KeyError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lineup not found",
        ) from error


@router.post(
    "/lineups/{lineup_id}/balls",
    response_model=LineupBall,
    status_code=status.HTTP_201_CREATED,
)
def add_lineup_ball_route(
    lineup_id: UUID,
    payload: LineupBallAddRequest,
) -> LineupBall:
    try:
        return add_ball_to_lineup(lineup_id, payload)
    except KeyError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lineup not found",
        ) from error
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.delete(
    "/lineups/{lineup_id}/balls/{lineup_ball_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_lineup_ball_route(lineup_id: UUID, lineup_ball_id: UUID) -> None:
    try:
        remove_ball_from_lineup(lineup_id, lineup_ball_id)
    except KeyError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lineup ball not found",
        ) from error
