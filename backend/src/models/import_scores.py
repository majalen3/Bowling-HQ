from uuid import UUID

from pydantic import BaseModel


class ScoreImportResult(BaseModel):
    session_id: UUID
    games_imported: int
    scores: list[int]
    errors: list[str]
