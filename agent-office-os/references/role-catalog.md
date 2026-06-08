# Role Catalog

Use this reference to design and write role cards. The role names below are examples and fallback building blocks, not a required default roster. Never copy the whole catalog into a new project just because the names are available.

## Contents

- [Dynamic Role Rules](#dynamic-role-rules)
- [Common Role Building Blocks](#common-role-building-blocks)
- [Optional Roles](#optional-roles)
- [Thread Prompt Template](#thread-prompt-template)
- [Thread Launch Checklist](#thread-launch-checklist)

## Dynamic Role Rules

Create roles from the actual project context.

- Use few, necessary roles.
- Do not split roles just to sound professional.
- Split only when responsibilities, inputs, outputs, write scope, or review authority are clearly different.
- Do not allow two default writer roles to own the same file scope.
- Every active role needs a current assignment, default reading material, write boundary, and handoff target.
- Every active role owns exactly one `docs/agent-office/role-memory/{role-slug}.md` file for continuity across replacement chat windows.
- Defer roles that are plausible later but not needed for the first milestone.
- Explain both why a role exists now and why likely alternatives are not created yet.
- Compress before splitting: if two roles would read the same files, write the same outputs, or hand off to the same person for the same task, merge them for now.
- Favor a role name the user would understand in this project over a generic title from this catalog.

The stable part is the office structure: `AGENTS.md`, `docs/agent-office/status.md`, role cards, role memory, task packets, messages, handoffs, ADRs, and launch prompts. The flexible part is who uses those documents.

## Common Role Building Blocks

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

Generate this prompt in the user's language. The fenced text block should contain only the message to send to the new thread.

```text
You are the {ROLE} agent employee for this project.

Read:
1. AGENTS.md
2. docs/agent-office/status.md
3. docs/agent-office/context-packs/project-brief.md
4. docs/agent-office/roles/{role}.md
5. docs/agent-office/role-memory/{role}.md
6. docs/agent-office/thread-registry.md
7. docs/agent-office/communication.md
8. the assigned task packet, if one exists

Rules:
- Load only task-relevant context.
- Current assignment: {TASK}
- Write scope: {WRITE_SCOPE}
- Handoff target: {HANDOFF_TARGET}
- Read and update only docs/agent-office/role-memory/{role}.md by default. Do not open another role's memory unless the user explicitly asks for maintenance, audit, or recovery.
- If the user asks for work outside your write scope, do not do it silently; name the role that should own it or write a message under docs/agent-office/messages/open/ to your handoff target or coordinator.
- Write cross-role messages as separate files under docs/agent-office/messages/open/.
- End significant work with a handoff under docs/agent-office/handoffs/.
- After significant work, update your own role memory with short durable continuity notes. Do not paste transcripts.
- Do not silently modify unrelated project-management files.
```

## Thread Launch Checklist

1. Create one long-running agent thread per approved role.
2. Start each thread with the role prompt, project root, current assignment, and write scope.
3. Confirm the role's own memory file exists before the thread starts.
4. Record the returned thread ID in `docs/agent-office/thread-registry.md`.
5. Set `Status` to `active`, `waiting`, or `idle` and keep exactly one DRI per active task.
6. Add a message under `docs/agent-office/messages/open/` when a thread needs another role to act.
