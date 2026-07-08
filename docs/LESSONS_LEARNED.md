# Lessons Learned

Document patterns worth repeating and mistakes worth avoiding.

## What Worked Well

- Keep orchestration state in dedicated docs instead of scattered chat history
- Escalate strategically when confidence is low instead of forcing a weak next step
- Track dependencies explicitly before launching parallel work

## What Did Not Work

- Relying on memory alone for multi-agent sequencing
- Treating strategic and implementation decisions as the same class of work

## How to Improve

- Refresh `ADMIN_STATUS.md` before every launch decision
- Record estimate accuracy after each merged phase
- Reuse successful prompts for agent retries and future launches

## Patterns to Replicate

- Pair strategic planning with status snapshots when the roadmap is unclear
- Launch parallel agents only when their outputs do not block each other
- Capture blockers early so the learning loop can improve future sequencing
