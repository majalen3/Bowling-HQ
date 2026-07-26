from typing import Literal

from pydantic import BaseModel


BoardStatus = Literal["backlog", "in_progress", "done"]


class MvpItem(BaseModel):
    id: str
    title: str
    status: BoardStatus
    done_criteria: list[str]


class ProgressSnapshot(BaseModel):
    finished_target: str
    scope_lock: list[str]
    release_gate: list[str]
    board: list[MvpItem]
