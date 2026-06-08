# Maintenance Playbook

Use this reference when auditing or cleaning an existing Agent Office OS.

## Default Mode

Start read-only. Produce a maintenance report before making cleanup edits unless the user explicitly requested automatic cleanup.

## Maintenance Report

Include:

- oversized files
- stale open messages
- active tasks missing DRI, reviewer, write scope, acceptance criteria, or verification
- completed tasks that should move to `tasks/done/`
- done tasks that should move to `tasks/archived/`
- missing handoffs for completed work
- thread registry entries that are idle, waiting, retired, or missing thread IDs
- role memory files that are missing, over budget, stale, or referenced by the wrong role
- ADRs that appear superseded but are not marked
- recommended cleanup actions requiring approval

## Cleanup Rules

- Close a message only when it has a clear answer or has been superseded.
- Archive a task only when it is `done` and its outcome is reflected in `status.md`, a handoff, or an ADR.
- Retire a thread only after writing or locating a retirement handoff.
- Mark an ADR `superseded` only when a newer ADR or explicit decision replaces it.
- Summarize long files before moving detail into archive.
- Treat role memory as protocol-private. For ordinary maintenance, check existence, size, owner path, and freshness; read another role's memory only when the user explicitly asks for office maintenance, audit, or recovery.
- Treat `archive/legacy-management/` as human-review and audit material. Do not read it during ordinary health checks unless the maintenance task is specifically about migration absorption, missing facts, or restore.
- Do not delete office history unless the user approves an exact deletion list.

## Suggested Maintenance States

Messages:

- `open`
- `acknowledged`
- `resolved`
- `superseded`
- `archived`

Tasks:

- `proposed`
- `assigned`
- `in-progress`
- `blocked`
- `reviewing`
- `done`
- `archived`

Threads:

- `active`
- `idle`
- `waiting`
- `retired`
- `archived`

Decisions:

- `proposed`
- `accepted`
- `rejected`
- `superseded`

## Safe Cleanup Order

1. Run `validate_office.py`.
2. Read only the files named by the findings.
3. Update `status.md` with current truth if needed.
4. Close or move stale messages.
5. Move done tasks to `tasks/done/`.
6. Move old done tasks to `tasks/archived/`.
7. Update thread registry states.
8. Report missing or oversized role memory files to the owning role, or update them only when explicitly authorized.
9. Mark superseded ADRs.
10. Produce a handoff describing cleanup and remaining risks.
