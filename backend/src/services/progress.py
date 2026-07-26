from src.models.progress import MvpItem, ProgressSnapshot


def get_progress_snapshot() -> ProgressSnapshot:
    board = [
        MvpItem(
            id="MVP-001",
            title="Define finished target and done criteria",
            status="done",
            done_criteria=[
                "MVP must-have scope is explicitly listed",
                "Every MVP feature has pass/fail done criteria",
            ],
        ),
        MvpItem(
            id="MVP-002",
            title="Single visible board for all work",
            status="in_progress",
            done_criteria=[
                "Backlog, In Progress, and Done states are visible in app",
                "Every code change is mapped to one board item",
            ],
        ),
        MvpItem(
            id="MVP-003",
            title="Dedicated in-app progress view",
            status="in_progress",
            done_criteria=[
                "Frontend loads progress from backend endpoint",
                "Users can open the app and see completion status immediately",
            ],
        ),
        MvpItem(
            id="MVP-004",
            title="Complete vertical slices",
            status="backlog",
            done_criteria=[
                "Each slice ships DB, API, UI, and tests together",
                "Slice is marked done only after validation succeeds",
            ],
        ),
        MvpItem(
            id="MVP-005",
            title="Enforce completion gates",
            status="backlog",
            done_criteria=[
                "Lint, tests, and build pass for each completed slice",
                "Blockers are fixed before new feature work starts",
            ],
        ),
        MvpItem(
            id="MVP-006",
            title="Final burn-down and release readiness",
            status="backlog",
            done_criteria=[
                "Remaining MVP items reach Done",
                "Scope freeze and release checklist complete before ship",
            ],
        ),
    ]

    return ProgressSnapshot(
        finished_target=(
            "Ship Bowling-HQ MVP with visible tracked progress and "
            "release-ready quality gates."
        ),
        scope_lock=[
            "Progress board visibility",
            "Backend progress status endpoint",
            "Frontend progress dashboard",
            "Validation gates (lint, test, build)",
        ],
        release_gate=[
            "No in-progress items remaining for MVP scope",
            "make lint passes",
            "make test passes",
            "make build passes",
        ],
        board=board,
    )
