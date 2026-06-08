# Maintenance Playbook

Use this when auditing or cleaning an existing `Agent Office/`.

## Default Mode

Start read-only. Produce a maintenance report before cleanup edits unless the user explicitly requested safe cleanup.

## Check

- public files that are too long or stale
- `task-board.md` tasks missing owner, reviewer, write scope, status, or verification
- `communication.md` messages or handoffs that are unresolved
- `thread-registry.md` entries that are missing thread IDs, stale, retired, or still waiting
- employee folders missing `README.md`, `memory.md`, or `current-task.md`
- employee `memory.md` files that are too long, stale, or contain shared facts that belong in public files
- `decisions.md` entries that are superseded or unresolved
- old v0.1 nested office layout

## Cleanup Rules

- Do not read employee folders during ordinary health checks except for existence, size, and freshness.
- Read employee memory contents only when the user explicitly asks for maintenance, audit, or recovery.
- Do not read `Archive/Legacy Management/` unless the task is migration absorption, missing-fact audit, or restore.
- Move detail out of public files when they exceed budget; keep public files short.
- Do not delete office history unless the user approves an exact deletion list.

## Safe Cleanup Order

1. Run `validate_office.py`.
2. Read only files named by findings.
3. Update `status.md` and `task-board.md` with current truth if needed.
4. Resolve stale entries in `communication.md`.
5. Update `thread-registry.md`.
6. Ask owning roles to update their own `memory.md`, or edit only with explicit authorization.
7. Record cleanup summary in `communication.md`.
