# Templates

Use these templates when scaffolding the office. Keep generated files concise and project-specific.

## Table of Contents

- `AGENTS.md`
- `status.md`
- `thread-registry.md`
- `communication.md`
- `context-packs/project-brief.md`
- `context-packs/thread-launch-prompts.md`
- role card
- task packet
- message
- handoff
- ADR

## AGENTS.md

```md
# AGENTS.md

## Agent Office Protocol

This repository uses `docs/agent-office/` as the project office.

Before project work:
- Read `docs/agent-office/status.md`.
- If assigned a role, read only the matching file in `docs/agent-office/roles/`.
- If assigned a task, read the task packet in `docs/agent-office/tasks/active/`.
- Do not bulk-read the whole office unless explicitly asked to audit it.

Coordination:
- Treat `docs/agent-office/thread-registry.md` as the directory of long-running agent employees.
- For message and handoff format, read `docs/agent-office/communication.md`.
- Write cross-role messages as separate files under `docs/agent-office/messages/open/`.
- Write task handoffs under `docs/agent-office/handoffs/`.
- Update `status.md` only when you are PM, Archivist, or explicitly assigned to do so.

Parallel work:
- Do not let two writers modify the same files in parallel.
- Worktree changes are isolated proposals until integrated by the owner or PM.
- End every task with what changed, what was verified, what remains, and who should pick it up next.
```

## status.md

```md
# Project Status

Project: {project_name}
Last updated: {date}
Office profile: {profile}

## Current Goal

{project_goal}

## Active Tasks

| Task | Owner | Status | Reviewer | Notes |
|---|---|---|---|---|
| T-000 | PM | proposed | Reviewer | Define first milestone |

## Current Risks

- No major risks recorded yet.

## Decisions

- No durable decisions recorded yet.

## Next Step

Create the first task packet and assign a DRI.
```

## thread-registry.md

```md
# Thread Registry

Last updated: {date}

| Role | Thread Title | Thread ID | Mode | Authority | Current Assignment | Write Scope | Status |
|---|---|---|---|---|---|---|---|
| PM / Coordinator | {project_name} / PM / Coordinator | TBD | local | status, task assignment | T-000 | office docs | active |
| Builder | {project_name} / Builder | TBD | worktree | implementation | TBD | task scope only | waiting |
| Reviewer | {project_name} / Reviewer | TBD | local | review | TBD | read-heavy | waiting |
```

## communication.md

```md
# Communication Protocol

Use this file when agent employee threads need to ask, answer, escalate, close, or hand off work.

## Message Rules

- Create one file per cross-role request in `messages/open/`.
- Use a clear recipient, task id, requested response, and urgency.
- The receiving role may answer in the same file or create a response message.
- Move resolved or superseded messages to `messages/closed/` after the outcome is recorded.
- PM or Archivist closes old messages when the owner is unclear.

## Message States

- `status: open` means the message needs a response.
- `status: acknowledged` means the receiver saw it but has not resolved it.
- `status: resolved` means the answer or action is recorded.
- `status: superseded` means another task, message, ADR, or status update replaced it.

## Handoff Rules

- Write a handoff when work changes owner, reaches review, is blocked, or finishes.
- Include what changed, what was checked, known risks, and the next owner.
- Put handoffs in `handoffs/` and include the task id in the filename when possible.
- Do not mark a task done until the next owner can continue without reading unrelated history.
```

## context-packs/project-brief.md

```md
# Project Brief

Project: {project_name}
Generated: {date}

## Interview Decisions

- Project type: {project_type}
- Office profile: {profile}
- Risk level: {risk_level}
- Standing roles: {roles}

## Goal

{project_goal}

## First Milestone

{first_milestone}
```

## context-packs/thread-launch-prompts.md

````md
# Thread Launch Prompts

Project: {project_name}
Generated: {date}

Create one long-running agent thread for each approved role below. After each thread is created, record its thread ID in `docs/agent-office/thread-registry.md`.

## {Role}

Suggested title: `{project_name} / {Role}`

```text
You are the {Role} agent employee for this project.

Read:
1. AGENTS.md
2. docs/agent-office/status.md
3. docs/agent-office/context-packs/project-brief.md
4. docs/agent-office/roles/{role}.md
5. docs/agent-office/communication.md
6. the assigned task packet, if one exists

Rules:
- Load only task-relevant context.
- Current assignment: {task}
- Write scope: {write_scope}
- Write cross-role messages as separate files under docs/agent-office/messages/open/.
- End significant work with a handoff under docs/agent-office/handoffs/.
- Do not silently modify unrelated project-management files.
```
````

## role card

```md
# {Role}

## Mission

{mission}

## Authority

{authority}

## Default Inputs

- `AGENTS.md`
- `docs/agent-office/status.md`
- `docs/agent-office/context-packs/project-brief.md`
- `docs/agent-office/communication.md`
- assigned task packet

## Default Outputs

- task updates
- messages
- handoffs
- decisions, when authorized

## Boundaries

- Do not exceed assigned write scope.
- Ask PM before changing ownership or acceptance criteria.
- End significant work with a handoff.
```

## task packet

```md
---
id: T-000
status: proposed
dri: PM
reviewer: Reviewer
created: {date}
---

# T-000: Define First Milestone

## Goal

Plan the first implementation milestone and assign a DRI.

Milestone: {first_milestone}

## Required Context

- `AGENTS.md`
- `docs/agent-office/status.md`
- `docs/agent-office/context-packs/project-brief.md`
- `docs/agent-office/communication.md`

## Write Scope

Allowed:
- `docs/agent-office/tasks/active/T-000-define-first-milestone.md`
- `docs/agent-office/status.md`

Forbidden unless approved:
- application code

## Acceptance Criteria

- First milestone has a goal.
- DRI and reviewer are assigned.
- Verification approach is named.
- Role ownership and write scope are clear.

## Verification

- PM review.

## Handoff

Write a handoff if another role picks up implementation.
```

## message

```md
---
id: MSG-{date}-001
task: T-000
from: PM
to: Architect
status: open
urgency: normal
---

# Question

What decision is needed?

## Context

Why this matters now.

## Requested Response

What the receiving role should answer.
```

## handoff

```md
---
task: T-000
from: Builder
to: Reviewer
status: ready-for-review
date: {date}
---

# Handoff

## Summary

What changed.

## Files Changed

- None yet.

## Verification

- Not run yet.

## Known Risks

- None recorded.

## Next Owner

Reviewer
```

## ADR

```md
# ADR-000: Decision Title

Status: proposed
Date: {date}
Owner: Architect

## Decision

State the decision.

## Context

Why the decision exists.

## Alternatives

- Option A
- Option B

## Consequences

- Expected tradeoff.
```
