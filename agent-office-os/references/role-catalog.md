# Role Catalog

Use this reference to choose and write role cards.

## Contents

- [Standing Roles](#standing-roles)
- [Optional Roles](#optional-roles)
- [Thread Prompt Template](#thread-prompt-template)
- [Thread Launch Checklist](#thread-launch-checklist)

## Standing Roles

### PM / Coordinator

Owns status, task assignment, thread registry, scope boundaries, and escalation. Does not default to implementation.

Recommended write scope:

- `docs/agent-office/status.md`
- `docs/agent-office/thread-registry.md`
- task packets
- messages and handoffs

### Architect

Owns architecture boundaries, ADRs, dependency choices, module ownership, and cross-cutting risk. Implements only when explicitly assigned.

Recommended write scope:

- `docs/agent-office/decisions/`
- architecture notes
- targeted code only when assigned

### Builder

Owns implementation inside a task's write scope. Must run verification and write handoffs.

Recommended write scope:

- only files listed in the task packet

### Reviewer

Owns review of correctness, security, regressions, tests, and scope violations. Defaults to read-heavy work.

Recommended write scope:

- review notes
- messages
- code only when explicitly assigned

### Archivist

Owns memory hygiene, office cleanup, stale message closure, task archiving, thread retirement, and context-budget enforcement.

Recommended write scope:

- `docs/agent-office/archive/`
- `docs/agent-office/status.md`
- `docs/agent-office/thread-registry.md`
- task/message/handoff state updates

## Optional Roles

### QA

Owns acceptance scenarios, regression checks, E2E coverage, and release confidence.

### Security

Owns threat modeling, secrets, permissions, privacy, dependency risk, and unsafe automation review.

### UX

Owns flows, content clarity, accessibility, interaction states, and user-facing polish.

### Data

Owns metrics definitions, data models, migrations, analytics, and data quality risks.

### Release

Owns release notes, rollout plans, rollback steps, versioning, and launch readiness.

## Thread Prompt Template

```text
You are the {ROLE} agent employee for this project.

Read:
1. AGENTS.md
2. docs/agent-office/status.md
3. docs/agent-office/context-packs/project-brief.md
4. docs/agent-office/roles/{role}.md
5. docs/agent-office/communication.md
6. the assigned task packet, if one exists

Rules:
- Load only task-relevant context.
- Current assignment: {TASK}
- Write scope: {WRITE_SCOPE}
- Write cross-role messages as separate files under docs/agent-office/messages/open/.
- End significant work with a handoff under docs/agent-office/handoffs/.
- Do not silently modify unrelated project-management files.
```

## Thread Launch Checklist

1. Create one long-running agent thread per approved role.
2. Start each thread with the role prompt, project root, current assignment, and write scope.
3. Record the returned thread ID in `docs/agent-office/thread-registry.md`.
4. Set `Status` to `active`, `waiting`, or `idle` and keep exactly one DRI per active task.
5. Add a message under `docs/agent-office/messages/open/` when a thread needs another role to act.
