# Templates

Use these document-shape templates when writing `Agent Office/` manually. Replace placeholders with the approved dynamic roles for the actual project.

## AGENTS.proposed.md

```md
# AGENTS.md

## GAOGAO Office Protocol

This repository uses `Agent Office/` as the long-running agent project office.

Before project work:
- Read `Agent Office/README.md`, `Agent Office/status.md`, `Agent Office/project-brief.md`, and `Agent Office/task-board.md`.
- If assigned a role, read only your own employee folder under `Agent Office/Employees/{role-slug}/`.
- Do not read other employee folders unless the user explicitly asks for office maintenance, audit, or recovery.
- Do not read `Agent Office/Archive/Legacy Management/` during ordinary work.

Coordination:
- Cross-role requests, answers, and handoffs go in `Agent Office/communication.md`.
- Current tasks and owners go in `Agent Office/task-board.md`.
- Durable decisions go in `Agent Office/decisions.md`.
- End every task with what changed, what was verified, what remains, and who should pick it up next.
```

## README.md

```md
# Agent Office

This is the project office for `{project_name}`.

Public files in this folder are shared context. Employee folders under `Employees/` are private-by-protocol. `Archive/Legacy Management/` is human-review/audit material after migration absorption.
```

## status.md

```md
# Project Status

Project: {project_name}
Last updated: {date}
Project type: {project_type}
Risk level: {risk_level}

## Current Goal

{project_goal}

## Current Phase

First milestone: {first_milestone}

## Current Risks

- None recorded yet.

## Next Step

Confirm the first task in `task-board.md`.
```

## project-brief.md

```md
# Project Brief

Project: {project_name}
Generated: {date}

## Goal

{project_goal}

## Role Decisions

{role_decisions}

## Current Roles

- {Role} (`{role_slug}`): {mission}. Write scope: {write_scope}

## Deferred Roles

- {deferred_role_or_none}
```

## project-map.md

```md
# Project Map

Status: pending scan

## File Map

Record filename-level findings here.

## Absorbed Legacy Material

| Source | Absorbed Into | Notes |
|---|---|---|
| `{source}` | `{destination}` | {summary} |
```

## task-board.md

```md
# Task Board

| Task | Owner | Status | Reviewer | Write Scope | Notes |
|---|---|---|---|---|---|
| T-000 | {owner} | proposed | {reviewer} | {write_scope} | {first_milestone} |
```

## communication.md

```md
# Communication And Handoffs

## Open Messages

None.

## Handoffs

None.
```

## decisions.md

```md
# Decisions

| ID | Status | Owner | Decision | Notes |
|---|---|---|---|---|
| D-000 | proposed | Project owner | No durable decisions yet | Record when needed |
```

## thread-registry.md

````md
# Thread Registry

| Role | Thread Title | Thread ID | Mode | Current Assignment | Write Scope | Status |
|---|---|---|---|---|---|---|
| {Role} | {project_name} / {Role} | TBD | local | {task} | {write_scope} | active |

## Role Launch Prompts

**Create a new window: {Role}**
Suggested title: `{project_name} / {Role}`

```text
You are the {Role} agent employee for this project.

Read first:
1. AGENTS.md
2. Agent Office/README.md
3. Agent Office/status.md
4. Agent Office/project-brief.md
5. Agent Office/task-board.md
6. Agent Office/Employees/{role_slug}/README.md
7. Agent Office/Employees/{role_slug}/memory.md
8. Agent Office/Employees/{role_slug}/current-task.md

Rules:
- Read only your own employee folder by default.
- Do not read Agent Office/Archive/Legacy Management/ during ordinary work.
- Route out-of-scope work through Agent Office/communication.md.
```
````

## Employee Folder

```text
Agent Office/Employees/{role_slug}/
  README.md
  memory.md
  current-task.md
```

## migration-report.md

```md
# GAOGAO Office Migration Report

## Project Map

| Path | Kind | Read Policy | Size |
|---|---|---|---:|
| `{path}` | text | candidate-text | 123 |

## Absorption Map

| Source | Durable Facts To Absorb | New Office Destination | Status |
|---|---|---|---|
| `{source}` | {facts} | `Agent Office/project-brief.md` | proposed |

## Proposed AGENTS Replacement

Draft path: `Agent Office/Proposals/AGENTS.proposed.md`

## Proposed Archive List

| Source | Proposed Archive Destination | Reason |
|---|---|---|
| `{source}` | `Agent Office/Archive/Legacy Management/{date}/{source}` | content absorbed |

## Proposed Move List

No files are proposed for moving yet.

## Proposed Delete List

No files are proposed for deletion yet.

## User Approval Record

Approved archive list: NO
Approved AGENTS replacement: NO
Approved legacy move list: NO
Approved deletion list: NO
Approved by: <pending>
Approval date: <pending>
```
