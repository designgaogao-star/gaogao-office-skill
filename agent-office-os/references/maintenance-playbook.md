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
- ADRs that appear superseded but are not marked
- recommended cleanup actions requiring approval

## Cleanup Rules

- Close a message only when it has a clear answer or has been superseded.
- Archive a task only when it is `done` and its outcome is reflected in `status.md`, a handoff, or an ADR.
- Retire a thread only after writing or locating a retirement handoff.
- Mark an ADR `superseded` only when a newer ADR or explicit decision replaces it.
- Summarize long files before moving detail into archive.
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
8. Mark superseded ADRs.
9. Produce a handoff describing cleanup and remaining risks.
