# Interview Guide

Use this guide to ask only questions that change the office design. Prefer answering discoverable facts by inspecting the repo first. Use ordinary chat by default; Plan Mode is optional, not required.

## New Project Questions

Ask these when the project is new, empty, or unclear. Use at most 3-5 numbered questions per round and accept numbered answers.

1. What is this project trying to produce?
2. Who is the primary user, audience, or customer?
3. What should the first milestone accomplish?
4. What work is coming next: design, writing, coding, data, review, migration, release, research, or something else?
5. Are there file areas that should be protected from casual edits?

When project clues are visible, start by confirming the inference instead of asking from zero:

```text
I think this is a {project kind} for {likely goal}. Is that right?
If yes, answer these:
1. Who is the intended audience or primary user?
2. What is the first milestone?
3. Which work matters most next?
```

Do not ask the user to pick from a fixed role list. The model should infer the smallest useful role roster from the project and explain it.

## Existing Project Questions

Ask after inspecting the project:

1. Which existing docs are authoritative and which are stale?
2. Should old management files be archived inside the new office before deletion?
3. Which old framework names should be preserved for compatibility?
4. Are there current active tasks or branches that must not be disturbed?
5. Are any docs sensitive and unsuitable for migration summaries?
6. Who should be the first long-running agent roles after migration?

Recommended default: copy old framework files under `docs/agent-office/archive/legacy-management/` and delete originals only after explicit confirmation.

## Maintenance Questions

Ask only if not obvious:

1. Should the audit be read-only or should the agent clean up stale office docs?
2. What age makes a message stale: 7, 14, or 30 days?
3. Should retired threads remain in the registry or move to archive?
4. Should completed tasks be summarized into status before archiving?

Recommended default: read-only report first, then small cleanup after user approval.

## Office Plan Response

Before scaffolding, produce a plan with:

- project understanding
- recommended roles and why each exists now
- roles deliberately deferred and why
- responsibilities, default inputs, outputs, write scope, and handoff target for each role
- first task, DRI, reviewer, and verification expectation
- whether worktree mode is useful

Then ask for explicit approval before writing files.

## Role Design Heuristic

- Start with fewer roles than seem impressive.
- Keep a role only if it has a distinct job, distinct inputs/outputs, and a distinct write scope.
- Do not give two writer roles default ownership over the same files.
- Merge coordination and archiving when the project is small.
- Split review from building when there is meaningful implementation risk.
- Add specialist roles only when the first milestone needs them now.
- Defer plausible later roles and name the trigger for adding them.
