import json
from pathlib import Path

from src.models.progress import ProgressSnapshot

SNAPSHOT_PATH = Path(__file__).with_name("progress_snapshot.json")


def get_progress_snapshot() -> ProgressSnapshot:
    with SNAPSHOT_PATH.open(encoding="utf-8") as snapshot_file:
        payload = json.load(snapshot_file)
    return ProgressSnapshot.model_validate(payload)
