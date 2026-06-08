# Office Blueprint

GaoGao Office creates a lightweight `Agent Office/` with a public area, employee private areas, and an archive for old project memory.

## Operating Model

- The user is the final decision-maker. In Chinese chat, address them as `BOSS`.
- The current GaoGao Office chat becomes the founding project manager by default.
- In Codex Desktop, the founding project manager chat should be titled with its job title only, not the project name or skill invocation.
- The project manager maintains public files, routes work, keeps the office clean, and invites employees only after formal takeover.
- Multi-employee offices use single-entry controller-dispatch by default: BOSS talks mainly to the project manager; the project manager splits tasks, sends work to employee threads, gathers results, and reports back.
- Employee roster size is not the same as active concurrency. Employees may all be onboarded, but active work dispatch follows `dispatch_policy`; low or unknown local capacity means one employee task at a time.
- Other employees read public files plus only their own private folder by default.
- Employees primarily receive work from the project manager. Direct BOSS-to-employee work is allowed only when BOSS explicitly wants it.
- Old project memory is not ordinary working context after absorption.

## Structure

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
    employee-slug/
      README.md
      memory.md
      current-task.md
  Archive/
    Old Project Memory/
```

## Public Area

Files directly under `Agent Office/` are shared context. Keep them short and current. If a file becomes long, summarize the durable facts and move detail into archive or an employee file.

## Employee Area

Each employee folder has:

- `README.md`: employee profile with job value, responsibility domain, judgment standard, write scope, forbidden areas, and handoff rules.
- `memory.md`: private continuity with `Next Action` at the top and `Work Log` below.
- `current-task.md`: current status: waiting / active / deferred / cancelled / done.

Employees update their own memory after meaningful work. The project manager may update employee files during onboarding, maintenance, or recovery.

## Archive

`Agent Office/Archive/Old Project Memory/` contains absorbed old knowledge. It is not a trash folder and not a daily context source. Ordinary employees do not read it unless the user asks for audit, recovery, or migration review.

## Reading Order

Ordinary employees load:

1. `AGENTS.md`
2. `Agent Office/README.md`
3. `Agent Office/status.md`
4. `Agent Office/project-brief.md`
5. `Agent Office/task-board.md`
6. `Agent Office/Employees/{employee-slug}/README.md`
7. `Agent Office/Employees/{employee-slug}/memory.md`
8. `Agent Office/Employees/{employee-slug}/current-task.md`

The project manager may also read `communication.md`, `decisions.md`, `thread-registry.md`, migration reports, and employee files when maintaining the office.

## Controller Dispatch Loop

When BOSS gives work to the project manager after employees are onboarded:

1. classify the request and decide whether it needs employees
2. split only the necessary subtasks
3. update `task-board.md`, `communication.md`, and assigned employee `current-task.md`
4. send task messages to employee threads when tools are available
5. require each employee to update its own `memory.md` and `current-task.md`
6. read employee replies, verify or reconcile them, update public files, and report one answer to BOSS

This loop should reduce BOSS's coordination burden. It should not create busywork or route tiny tasks to employees just because threads exist.

## Context Budgets

| File | Target | Hard Limit |
|---|---:|---:|
| `AGENTS.md` | 700 words | 1,500 words |
| public status/task/brief files | 800 words each | 1,500 words each |
| `thread-registry.md` | 1,500 words | 2,500 words |
| employee `README.md` | 900 words | 1,200 words |
| employee `memory.md` | 900 words | 1,200 words |

## Clean Office Rule

Temporary plans, old prompts, absorbed knowledge files, generated QA output, and migration intermediates should not remain active project entrances. Archive or move them out of the production surface when the user approves formal takeover.
