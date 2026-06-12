# Office Blueprint

GaoGao Office creates a lightweight `Agent Office/` with a public area, employee private areas, and an archive for old project memory.

## Operating Model

- The user is the final decision-maker. Respect the user's preferred form of address. In Chinese chat, default to natural `你` wording when no preference is visible; use `BOSS` only if the user has already chosen or accepted it. In English chat, use `you` for user-facing copy and `user` or `project owner` for internal descriptions.
- The current GaoGao Office chat becomes the founding project director by default.
- In Codex Desktop, the founding project director chat should be titled with its job title only, not the project name or skill invocation.
- The project director maintains public files, routes work, keeps the office clean, and invites employees only after formal takeover.
- Multi-employee offices use single-entry controller-dispatch by default: the user talks mainly to the project director; the project director splits tasks, sends work to employee threads, receives employee reports, waits for required dependencies, and advances according to the user's A/B/C progress choice.
- Employee roster size is not the same as active concurrency. Employees may all be onboarded, but active work dispatch follows `dispatch_policy`; low or unknown local capacity means one employee task at a time.
- Other employees read public files plus only their own private folder by default.
- Employees primarily receive work from the project director and report back to the project director. Direct user-to-employee work is allowed only when the user explicitly wants it.
- Employee report transport is explicit: after local memory/task updates, employees use `send_message_to_thread` to the registered project-director thread only when that thread ID is confirmed. Otherwise they produce a copyable report for manual return.
- Report intake is explicit too: the project director verifies the report shape, updates `task-board.md` and `communication.md`, waits for missing dependencies, then advances only under A/B/C mode.
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

Employees update their own memory after meaningful work. The project director may update employee files during onboarding, maintenance, or recovery.

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

The project director may also read `communication.md`, `decisions.md`, `thread-registry.md`, migration reports, and employee files when maintaining the office.

## Controller Dispatch Loop

When the user gives work to the project director after employees are onboarded:

1. before long or multi-employee work starts, state expected steps, participating employees, and the next user checkpoint, then ask for A/B/C progress mode
2. run the task routing gate: identify final outcome, next workflow stage, candidate owner, and whether the work should be dispatched, handled by the project director, or clarified
3. if one employee clearly owns the next stage, dispatch it to that employee; if no employee owns it or it is tiny office maintenance, the project director may handle it directly
4. for multi-stage work, split only the next unblocked subtask and record the likely next owner without dispatching downstream work too early
5. update `task-board.md`, `communication.md`, and assigned employee `current-task.md`
6. send task messages to employee threads when tools are available
7. require each employee to update its own `memory.md` and `current-task.md`, then return the fixed employee-report shape to the project director
8. when a report returns, verify reporter/task/status/output, update `task-board.md` and `communication.md`, wait for required dependencies, and advance only according to A/B/C mode

This loop should reduce the user's coordination burden. It should not create busywork or route tiny tasks to employees just because threads exist.

Task routing must stay small. Read `office-plan.json`, `task-board.md`, `thread-registry.md`, `project-brief.md`, optional root `AGENTS.md`, and only the likely owner's `current-task.md`; do not read every employee file or run full validation before ordinary dispatch.

Dispatch must stay small: update the active task board, one communication handoff, and the assigned employee's current task; send one employee-thread message when possible; then report and stop. Each dispatch includes the project-director return target and the manual-copy fallback. If writes or employee-thread sends are unavailable, provide a manual dispatch packet instead of expanding the turn.

Do not create orphan active tasks. If the target employee thread ID is `TBD`, missing, or not tied to this project, show the manual dispatch packet and stop; record the task after the user confirms it was sent, the employee thread is registered, or a result returns.

The project director must not claim an employee's work as complete unless that employee completed it or the user explicitly authorized the project director to take over. If the project director uses a tool that supports another employee's task, record it as tool execution or handoff support, then route the judgment/result back to the responsible role.

Handoff support is not employee output. The project director may preserve the user's goal, constraints, source materials, and acceptance criteria, but it must not finish the creative, prompt, design, code, research, QA, or release deliverable that belongs to an employee unless takeover is explicitly authorized.

## Progress Modes And Heartbeat

A/B/C progress is chosen before long or multi-employee work:

- A manual progress: dispatch the current step and wait for a short user reply such as `跟进`, `继续`, `OK`, `continue`, or `ok`.
- B semi-automatic progress: continue from employee reports, but stop at key checkpoints, dependency gaps, risky actions, or user judgment.
- C automatic progress until checkpoint: continue safely until the next user checkpoint. If automation tools are available, the project director may create or update a current-thread heartbeat.

Heartbeat reminders are not extra authority. When awakened, the project director checks whether unfinished work remains, continues only if safe, and stops immediately if the work is done, blocked, risky, or needs the user. Automatic progress never authorizes deletion, archive moves, publishing, or `AGENTS.md` changes.

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
