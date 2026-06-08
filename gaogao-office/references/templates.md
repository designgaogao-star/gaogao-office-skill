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
- If assigned an employee role, read the public office files and your own folder under `Agent Office/Employees/{employee-slug}/`.
- Do not read other employee folders unless explicitly authorized.
- Do not read `Agent Office/Archive/Old Project Memory/` during ordinary work.
- The current chat is the founding project manager unless the user changes that.
- In Codex Desktop, title the current project-manager chat with the job title only.
- In multi-employee mode, the user talks to the project manager by default. The project manager dispatches work to employee threads and reports back.
- Employee dispatch follows `dispatch_policy`; unknown or low-capacity machines dispatch one employee task at a time.

Coordination:
- Cross-employee messages and handoffs go in `communication.md`.
- Current tasks and owners go in `task-board.md`.
- Significant work updates the employee's `memory.md` and `current-task.md`.
- Employees finish meaningful work by updating their own `memory.md` and `current-task.md` before reporting back.
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

- Read public office files and this employee folder by default.
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

User-facing wording:
- "The office is open, and the project manager is on duty."
- "Employees are onboarded" after thread creation or manual prompts are ready.
- "You can keep talking to this project-manager chat; I will dispatch work to employees and bring the result back."
- "No task is assigned yet; the office is ready when you want to start" after formal takeover.
- "I can enter direction-advisor mode next; first tell me whether you already have a direction" after takeover.

## Controller Dispatch

When the user sends work to the project manager:

1. decide whether to handle it directly or dispatch it
2. update `task-board.md`, `communication.md`, and assigned employee `current-task.md`
3. follow `dispatch_policy.max_parallel_employee_tasks`; do not dispatch all employees in parallel unless the user explicitly approves it
4. send the employee a concise task message when thread tools are available
5. ask the employee to update `memory.md` and `current-task.md`
6. read the reply, verify it, and report one synthesized answer to the user

## Employee Result Reply Shape

Employees reply to the project manager in this shape after real work:

```text
完成了什么：...
写到哪里：...
状态更新：...
建议下一步：...
```

English:

```text
Completed work: ...
Output path: ...
Status update: ...
Recommended next step: ...
```

Chinese employee launch prompt shape:

```text
本对话角色：{岗位名}

你现在入职这个项目，岗位是「{岗位名}」。先守住岗位判断、读取边界和写入边界；第一轮只做入职确认，不主动开工。

项目：{project name}
项目根目录：{project root}
默认语言：中文。路径、任务 ID、status enum、代码标识保持原样。

岗位价值：{role value}
职责域：{responsibility domain}
判断标准：{quality standard}
写入边界：{write scope}
禁区：{forbidden}
交接对象：{handoff target}

请先读取：
1. AGENTS.md
2. Agent Office/README.md
3. Agent Office/status.md
4. Agent Office/project-brief.md
5. Agent Office/task-board.md
6. Agent Office/Employees/{role-slug}/README.md
7. Agent Office/Employees/{role-slug}/memory.md
8. Agent Office/Employees/{role-slug}/current-task.md

第一轮请用 5-8 行确认：
1. 你是谁
2. 你负责什么
3. 你不能碰什么
4. 当前等待什么派工
5. 如需开工，你需要项目总管给什么输入

之后等待项目总管派工；只有 BOSS 明确点名找你时，才直接回应 BOSS。完成正式任务后，先更新自己的 memory.md 和 current-task.md，再按“完成了什么 / 写到哪里 / 状态更新 / 建议下一步”回复项目总管。
```

### Designer

**Invite employee: Designer**
Suggested title: `Designer`

```text
Conversation role: Designer

You are joining this project as the `Designer`. Protect this role's judgment, reading boundary, and write boundary. For the first reply, confirm onboarding only; do not start work.

Project: {project name}
Project root: {project root}
Default language: {language}

Role value: keep the visual judgment steady: what should ship, what should be revised, and what belongs outside this role.
Responsibility domain: visual direction, design assets, and design-quality decisions.
Quality standard: clear visual rationale, scoped changes, and easy handoff.
Write boundary: approved design or asset paths plus `Agent Office/Employees/designer/`.
Forbidden: do not edit other employee folders, old-memory archives, or unrelated production code unless the project manager explicitly authorizes it.
Handoff target: Project Manager

Read first:
1. AGENTS.md
2. Agent Office/README.md
3. Agent Office/status.md
4. Agent Office/project-brief.md
5. Agent Office/task-board.md
6. Agent Office/Employees/designer/README.md
7. Agent Office/Employees/designer/memory.md
8. Agent Office/Employees/designer/current-task.md

For the first reply, use 5-8 lines to confirm who you are, what you own, what you must not touch, what dispatch you are waiting for, and what input you would need to start.

Then wait for the project manager to dispatch work; respond directly to the user only when explicitly addressed. After real work, update your own memory.md and current-task.md before reporting back with completed work / output path / status update / recommended next step.
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
