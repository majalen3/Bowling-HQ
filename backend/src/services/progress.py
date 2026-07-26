import json
from pathlib import Path

from src.models.progress import ProgressSnapshot
from src.services.session_progress import get_session_progress_snapshot

SNAPSHOT_PATH = Path(__file__).with_name("progress_snapshot.json")


def get_progress_snapshot() -> ProgressSnapshot:
    with SNAPSHOT_PATH.open(encoding="utf-8") as snapshot_file:
        payload = json.load(snapshot_file)
    session_snapshot = get_session_progress_snapshot()
    board = []
    for item in payload["board"]:
        if item["id"] != "MVP-004":
            board.append(item)
            continue
        if session_snapshot.total_sessions == 0:
            status = "backlog"
        elif (
            session_snapshot.completed_sessions
            == session_snapshot.total_sessions
        ):
            status = "done"
        else:
            status = "in_progress"
        done_criteria = [
            criterion
            for criterion in item["done_criteria"]
            if not criterion.startswith("Slice 1 sessions completed:")
        ]
        done_criteria.append(
            "Slice 1 sessions completed: "
            f"{session_snapshot.completed_sessions}/"
            f"{session_snapshot.total_sessions}",
        )
        board.append(
            {
                **item,
                "status": status,
                "done_criteria": done_criteria,
            },
        )
    payload = {**payload, "board": board}
    return ProgressSnapshot.model_validate(payload)
