# Templates

Use these shapes when writing `Agent Office/` manually. Keep them concise and adapt them to the approved organization.

## User-Visible Chat Output

Follow `references/markdown-output-guide.md` when presenting these templates in chat.

- Human instructions such as where to paste a prompt stay outside fenced blocks.
- The actual message to send to an employee thread goes only inside a fenced `text` block.
- Do not put "new window", "suggested title", or other external instructions inside the employee prompt.
- Use tables for role rosters and migration maps.
- Use task lists for takeover, health-check, and retirement results.
- Before final answers, remove internal drafting traces such as `Wait`, `Need final`, `analysis`, tentative link syntax, and implementation chatter.

## AGENTS.proposed.md

```md
# AGENTS.md

## GaoGao Office Protocol

This project uses `Agent Office/` as the long-running agent office.

Before work:
- Read `Agent Office/README.md`, `status.md`, `project-brief.md`, `project-map.md`, and `task-board.md`.
- If assigned an employee role, read only `Agent Office/Employees/{employee-slug}/`.
- Do not read `Agent Office/Archive/Old Project Memory/` during ordinary work.
- The current chat is the founding project manager unless the user changes that.
- In Codex Desktop, title the current project-manager chat with the job title only.
- In multi-employee mode, BOSS talks to the project manager by default. The project manager dispatches work to employee threads and reports back.
- Employee dispatch follows `dispatch_policy`; unknown or low-capacity machines dispatch one employee task at a time.

Coordination:
- Cross-employee messages and handoffs go in `communication.md`.
- Current tasks and owners go in `task-board.md`.
- Significant work updates the employee's `memory.md` and `current-task.md`.
```

## Employee Profile

```md
# {Job Title}

## Role Value

{why this employee exists}

## Responsibility Domain

{process or functional domain, such as visual assets, frontend code, publishing checks}

## Judgment Standard

{how this employee decides what good work looks like}

## Inputs

{what the employee reads or receives}

## Outputs

{what the employee produces}

## Write Scope

{allowed files or areas}

## Forbidden

{files, actions, APIs, or decisions this employee must not touch}

## Handoff Target

{project manager or another employee}

## Rules

- Read only this employee folder by default.
- Do not read other employee folders.
- Do not read `Archive/Old Project Memory/` during ordinary work.
- Route out-of-scope work to the project manager.
- Update memory after meaningful work.
```

## Employee Memory

```md
# {Job Title} Memory

Owner role: `{employee-slug}`
Privacy: protocol-private.
Last updated: {date}

## Next Action

status: waiting
next: {next action or waiting state}
reason: {why this is next}

## Work Log

### {date}

- Completed: {what was done}
- Result: {done / waiting / deferred / cancelled}
- Validation: {checks or none}
- New next action: {next action}

## Durable Notes

- {facts this employee needs next time}

## Memory Rules

- Append a Work Log entry after meaningful work.
- Mark postponed work as `deferred`.
- Mark user-cancelled work as `cancelled by user`.
- Put shared project truth in the public area.
```

## Current Task

```md
# Current Task

status: waiting
current: {assignment}
owner: {Job Title}

## Required Reading

- `AGENTS.md`
- `Agent Office/README.md`
- `Agent Office/status.md`
- `Agent Office/project-brief.md`
- `Agent Office/task-board.md`
- this folder's `README.md`
- this folder's `memory.md`

## Write Scope

{write scope}

## On Completion

- Update status: waiting / active / deferred / cancelled / done.
- Update `memory.md` Next Action and Work Log.
- Write a handoff if another employee should continue.
```

## Thread Registry

````md
# Thread Registry

Current project-manager window title: `Project Manager`

| Role | Thread Title | Thread ID | Mode | Current Assignment | Write Scope | Status |
|---|---|---|---|---|---|---|
| Project Manager | Project Manager | current-window | local | maintain the office | Agent Office public files | founding-steward |
| Designer | Designer | TBD | local | waiting | approved design/assets scope | waiting |

## Employee Rejoin / Restart Prompts

These prompts are for employee onboarding, employee restart, or role recovery after formal takeover. Do not send them before the office is created, AGENTS.md is applied, and absorbed old knowledge is archived.

The project manager should title this current chat first, then invite employees.
Use automatic Codex Desktop thread creation when available. Manual prompts are fallback only.

BOSS-facing wording:
- "The office is open, and the project manager is on duty."
- "Employees are onboarded" after thread creation or manual prompts are ready.
- "You can keep talking to this project-manager chat; I will dispatch work to employees and bring the result back."
- "No task is assigned yet; the office is ready when BOSS wants to start" after formal takeover.
- "I can enter direction-advisor mode next; first tell me whether BOSS already has a direction" after takeover.

## Controller Dispatch

When BOSS sends work to the project manager:

1. decide whether to handle it directly or dispatch it
2. update `task-board.md`, `communication.md`, and assigned employee `current-task.md`
3. follow `dispatch_policy.max_parallel_employee_tasks`; do not dispatch all employees in parallel unless BOSS explicitly approves it
4. send the employee a concise task message when thread tools are available
5. ask the employee to update `memory.md` and `current-task.md`
6. read the reply, verify it, and report one synthesized answer to BOSS

## Employee Result Reply Shape

Employees reply to the project manager in this shape after real work:

```text
完成了什么：...
写到哪里：...
状态更新：...
建议下一步：...
```

### Designer

**Invite employee: Designer**
Suggested title: `Designer`

```text
Conversation role: Designer

You are joining this project as the `Designer`.
Project: {project name}
Project root: {project root}
Default language: {language}

You are the project's Designer. Your value is to keep the visual judgment steady: what should ship, what should be revised, and what belongs outside this role.

First read AGENTS.md, the Agent Office public files, and your own employee folder. Do not edit files during your first reply. Introduce what you own, what you must not touch, and what you are waiting for. Then wait for the project manager's task.
```
````

## Migration Report Sections

```md
## Absorption Map

| Source | Durable Facts To Absorb | New Office Destination | Status |
|---|---|---|---|
| `old/context.md` | project goals and constraints | `Agent Office/project-brief.md` | absorbed |

## Proposed Archive List

| Source | Proposed Archive Destination | Reason |
|---|---|---|
| `old/context.md` | `Agent Office/Archive/Old Project Memory/{date}/old/context.md` | content absorbed |

## User Approval Record

Approved archive list: NO
Approved AGENTS replacement: NO
Approved legacy move list: NO
Approved deletion list: NO
```
