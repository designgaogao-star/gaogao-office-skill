# Office Blueprint

GaoGao Office creates a lightweight `Agent Office/` with a public area, employee private areas, and an archive for old project memory.

## Operating Model

- The user is the final decision-maker. Respect the user's preferred form of address. In Chinese chat, default to natural `你` wording when no preference is visible; use `BOSS` only if the user has already chosen or accepted it. In English chat, use `you` for user-facing copy and `user` or `project owner` for internal descriptions.
- The current GaoGao Office chat becomes the founding project manager by default.
- In Codex Desktop, the founding project manager chat should be titled with its job title only, not the project name or skill invocation.
- The project manager maintains public files, routes work, keeps the office clean, and invites employees only after formal takeover.
- Multi-employee offices use single-entry, non-blocking controller-dispatch by default: the user talks mainly to the project manager; the project manager splits tasks, sends work to employee threads, records the handoff, and stops until the user asks it to continue.
- Employee roster size is not the same as active concurrency. Employees may all be onboarded, but active work dispatch follows `dispatch_policy`; low or unknown local capacity means one employee task at a time.
- Other employees read public files plus only their own private folder by default.
- Employees primarily receive work from the project manager. Direct user-to-employee work is allowed only when the user explicitly wants it.
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

When the user gives work to the project manager after employees are onboarded:

1. run the task routing gate: identify final outcome, next workflow stage, candidate owner, and whether the work should be dispatched, handled by the project manager, or clarified
2. if one employee clearly owns the next stage, dispatch it to that employee; if no employee owns it or it is tiny office maintenance, the project manager may handle it directly
3. for multi-stage work, split only the next unblocked subtask and record the likely next owner without dispatching downstream work too early
4. update `task-board.md`, `communication.md`, and assigned employee `current-task.md`
5. send task messages to employee threads when tools are available
6. require each employee to update its own `memory.md` and `current-task.md`
7. report the assignment to the user with numbered continuation paths, then stop
8. resume only when the user returns with a continuation request, explicitly asks the project manager to wait, or authorizes project-manager takeover of an employee task

This loop should reduce the user's coordination burden. It should not create busywork or route tiny tasks to employees just because threads exist.

The project manager must not claim an employee's work as complete unless that employee completed it or the user explicitly authorized the project manager to take over. If the project manager uses a tool that supports another employee's task, record it as tool execution or handoff support, then route the judgment/result back to the responsible role.

## Optional Watch Mode

Watching employee progress is opt-in. The project manager may watch only after a clear request such as `Watch T-001`, `盯进度 T-001`, or an equivalent instruction.

When watching:

- Check employee threads at an adaptive 30-60 second interval; never exceed 60 seconds while actively watching.
- Use longer intervals for complex tasks or when the employee is clearly still reasoning, and shorter intervals only when completion looks near or reads are cheap.
- Report only meaningful progress, blockers, handoffs, completion, or timeout.
- Stop when the employee finishes, blocks, asks for user input, hands off to another role, the user interrupts, or repeated checks show no meaningful progress.
- Do not take over the employee's work unless the user explicitly authorizes project-manager takeover.

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
