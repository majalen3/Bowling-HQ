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
    add_lineup_ball,
    create_lineup,
    delete_lineup,
    get_lineup,
    list_lineups,
    recommend_lineup,
    remove_lineup_ball,
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


@router.delete("/lineups/{lineup_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lineup_route(lineup_id: UUID) -> None:
    if not delete_lineup(lineup_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lineup not found",
        )


@router.post(
    "/lineups/{lineup_id}/recommend",
    response_model=list[LineupRecommendation],
)
def recommend_lineup_route(lineup_id: UUID) -> list[LineupRecommendation]:
    result = recommend_lineup(lineup_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lineup not found",
        )
    return result


@router.post(
    "/lineups/{lineup_id}/balls",
    response_model=LineupBall,
    status_code=status.HTTP_201_CREATED,
)
def add_lineup_ball_route(
    lineup_id: UUID,
    payload: LineupBallAddRequest,
) -> LineupBall:
    result = add_lineup_ball(lineup_id, payload)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lineup or ball not found",
        )
    return result


@router.delete(
    "/lineups/{lineup_id}/balls/{lineup_ball_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_lineup_ball_route(lineup_id: UUID, lineup_ball_id: UUID) -> None:
    if not remove_lineup_ball(lineup_id, lineup_ball_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lineup ball not found",
        )
