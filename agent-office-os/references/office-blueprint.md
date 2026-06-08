# Agent Office OS Blueprint

Use this reference when creating or maintaining the project office.

## Table of Contents

- Core Model
- Default Directory
- Context Budgets
- Loading Order
- Object States
- Parallel Work Rules
- Completion Gate

## Core Model

Agent Office OS is a thin-kernel project management system for large agent projects:

- `AGENTS.md` is the automatic entrypoint and must stay short.
- `docs/agent-office/` is the canonical project office.
- Long-running agent threads act as role-based employees.
- Subagents are temporary investigators, not permanent employees.
- Worktrees isolate parallel implementation but are not realtime shared offices.
- Skills contain reusable workflows; project docs contain project truth.

The office must help an agent answer these questions quickly:

1. What is the project doing now?
2. Who owns the current work?
3. Where is the relevant task packet?
4. What files may be changed?
5. Who receives the handoff?
6. Where should another role leave an answer, blocker, or follow-up?

## Default Directory

```text
AGENTS.md
docs/agent-office/
  README.md
  status.md
  thread-registry.md
  communication.md
  operating-model.md
  roles/
  tasks/
    active/
    done/
    archived/
  messages/
    open/
    closed/
  handoffs/
  decisions/
  context-packs/
    project-brief.md
    thread-launch-prompts.md
  cadences/
  archive/
    legacy-management/
```

## Context Budgets

Use these targets to keep the office sustainable:

| File type | Target | Hard limit |
|---|---:|---:|
| `AGENTS.md` | 900 words | 1,500 words |
| `status.md` | 800 words | 1,200 words |
| `communication.md` | 500 words | 900 words |
| role card | 400 words | 600 words |
| task packet | 700 words | 1,000 words |
| handoff | 500 words | 700 words |
| message | 250 words | 400 words |
| ADR | 900 words | 1,200 words |

If a file exceeds its hard limit, archive detail and replace it with a summary.

## Loading Order

Tell agent workers to load:

1. `AGENTS.md`
2. `docs/agent-office/status.md`
3. `docs/agent-office/communication.md` when writing messages or handoffs
4. matching role card
5. current task packet
6. files named by the task packet

Do not read the whole office unless doing an audit.

## Object States

Use these state machines:

- Thread: `active`, `idle`, `waiting`, `retired`, `archived`
- Task: `proposed`, `assigned`, `in-progress`, `blocked`, `reviewing`, `done`, `archived`
- Message: `open`, `acknowledged`, `resolved`, `superseded`, `archived`
- Decision: `proposed`, `accepted`, `rejected`, `superseded`

## Parallel Work Rules

Read-heavy work can run in parallel. Write-heavy work needs:

- one DRI
- one reviewer
- one write scope
- one local checkout or worktree owner
- one handoff

Do not let two writer roles own the same files at the same time.

Scaffolding and maintenance tools should refuse project-office paths that resolve outside the project root through symlinks or junctions.

## Completion Gate

Before a task is done, verify:

- acceptance criteria were satisfied
- write scope was respected
- requested checks were run or explicitly skipped with reason
- risks are documented
- handoff exists
- ADR exists when a durable decision was made
- `status.md` is updated when PM/Archivist owns the update
