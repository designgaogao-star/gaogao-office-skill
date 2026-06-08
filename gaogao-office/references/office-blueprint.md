# GAOGAO Office Blueprint

Use this reference when creating or maintaining the lightweight `Agent Office/` project office.

## Core Model

- GAOGAO Office is the skill and brand.
- `Agent Office/` is the project-local office folder.
- `AGENTS.md` is the automatic root entrypoint, but it is proposed first and applied only after user approval.
- Public files live directly in `Agent Office/`.
- Private role continuity lives under `Agent Office/Employees/{role-slug}/`.
- Legacy material lives under `Agent Office/Archive/Legacy Management/` after absorption and is not ordinary working context.

## Default Directory

```text
AGENTS.md
Agent Office/
  README.md
  status.md
  project-brief.md
  project-map.md
  task-board.md
  communication.md
  decisions.md
  thread-registry.md
  office-plan.json
  Proposals/
    AGENTS.proposed.md
  Employees/
    role-slug/
      README.md
      memory.md
      current-task.md
  Archive/
    Legacy Management/
```

## Loading Order

Ordinary role workers load:

1. `AGENTS.md`
2. `Agent Office/README.md`
3. `Agent Office/status.md`
4. `Agent Office/project-brief.md`
5. `Agent Office/task-board.md`
6. `Agent Office/Employees/{role-slug}/README.md`
7. `Agent Office/Employees/{role-slug}/memory.md`
8. `Agent Office/Employees/{role-slug}/current-task.md`

Read `Agent Office/communication.md` when messages or handoffs are needed. Read `Agent Office/decisions.md` when durable decisions matter. Do not read other employee folders or `Archive/Legacy Management/` unless the user explicitly asks for maintenance, audit, recovery, or migration.

## Context Budgets

| File type | Target | Hard limit |
|---|---:|---:|
| `AGENTS.md` | 700 words | 1,500 words |
| public office file | 700 words | 1,500 words |
| `project-map.md` | 1,200 words | 2,000 words |
| `thread-registry.md` | 1,500 words | 2,500 words |
| employee `README.md` | 400 words | 700 words |
| employee `memory.md` | 500 words | 900 words |
| employee `current-task.md` | 450 words | 800 words |

When a file exceeds its hard limit, summarize it and move detail into archive or a focused note.

## Completion Gate

Before a role marks work done:

- acceptance criteria are satisfied or explicitly deferred
- write scope was respected
- checks were run or skipped with reason
- public truth is updated when needed
- the role's own `memory.md` or `current-task.md` is updated when continuity changed
- handoff is recorded in `communication.md` when another role must continue
