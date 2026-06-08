# Role Catalog

Use this only when role boundaries need help. Do not treat it as a required roster.

## Role Rules

- Create few, necessary roles.
- Split only when responsibilities, inputs, outputs, write scope, or review authority are meaningfully different.
- Each role gets `Agent Office/Employees/{role-slug}/README.md`, `memory.md`, and `current-task.md`.
- A role reads only its own employee folder by default.
- A role asked to do out-of-scope work should route it through `Agent Office/communication.md` or the coordinator.

## Common Role Patterns

- **Coordinator**: owns public office truth, task ownership, scope, and handoffs.
- **Builder**: implements assigned work inside a task write scope.
- **Reviewer**: reviews diffs, outputs, regressions, missing tests, and scope fit.
- **Archivist**: absorbs old project memory, keeps public files short, and manages archive material.
- **Architect**: owns architecture boundaries and durable decisions.
- **QA**: owns acceptance scenarios and verification.
- **Security**: owns secrets, permissions, dependency risk, and unsafe automation checks.
- **UX / Content / Research**: create only when the current project needs those distinct long-running responsibilities.

## Compression Check

Before proposing roles, ask:

- Could one role handle the first milestone without confusion?
- Do any proposed roles share the same write scope?
- Is this role useful now, or merely plausible later?
- Would the user understand why this role deserves a separate window?

Merge or defer roles that fail this check.
