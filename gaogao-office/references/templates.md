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
- The current chat is the founding project director unless the user changes that.
- In Codex Desktop, title the current project-director chat with the job title only.
- In multi-employee mode, the user talks to the project director by default. The project director dispatches work to employee threads, receives employee reports, waits for required dependencies, and advances according to the user's A/B/C progress mode.
- Employee dispatch follows `dispatch_policy`; unknown or low-capacity machines dispatch one employee task at a time.

Coordination:
- Cross-employee messages and handoffs go in `communication.md`.
- Current tasks and owners go in `task-board.md`.
- Significant work updates the employee's `memory.md` and `current-task.md`.
- Employees finish meaningful work by updating their own `memory.md` and `current-task.md` before reporting back.
- The project director runs a task routing judgment before doing work: if a current employee clearly owns the next stage, dispatch it; if no employee owns it or it is tiny office maintenance, handle it directly and record the result.
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

{project director}

## Rules

- Read public office files and this employee folder by default.
- Do not read other employee folders.
- Do not read `Archive/Old Project Memory/` during ordinary work.
- Route out-of-scope work to the project director.
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

Current project-director window title: `Project Director`

| Role | Thread Title | Thread ID | Mode | Current Assignment | Write Scope | Status |
|---|---|---|---|---|---|---|
| Project Director | Project Director | current-window | local | maintain the office | Agent Office public files | current-window |
| Designer | Designer | TBD | local | waiting | approved design/assets scope | waiting |

## Employee Rejoin / Restart Prompts

These prompts are for employee onboarding, employee restart, or role recovery after formal takeover. Do not send them before the office is created, AGENTS.md is applied, and absorbed old knowledge is archived.

The project director should title this current chat first, then invite employees.
Use automatic Codex Desktop thread creation when available. Manual prompts are fallback only.

User-facing wording:
- "The office is open, and the project director is on duty."
- "Employees are onboarded" after thread creation or manual prompts are ready.
- "You can keep talking to this project-director chat; I will dispatch work to employees and collect their reports."
- "No task is assigned yet; the office is ready when you want to start" after formal takeover.
- "I can enter direction-advisor mode next; first tell me whether you already have a direction" after takeover.

## Controller Dispatch

When the user sends work to the project director:

1. before long or multi-employee work starts, state expected steps, participating employees, and the next user checkpoint, then ask for A/B/C progress mode
2. run a task routing judgment: final outcome, next workflow stage, candidate owner, and whether to dispatch, handle directly, or ask one clarification
3. if one employee clearly owns the next stage, dispatch to that employee; if no employee owns it or it is small office maintenance, the project director may handle it
4. update `task-board.md`, `communication.md`, and assigned employee `current-task.md`
5. follow `dispatch_policy.max_parallel_employee_tasks`; do not dispatch all employees in parallel unless the user explicitly approves it
6. send the employee a concise task message when thread tools and a registered employee thread ID are available
7. include the project-director return target in that message: title, thread ID status, automatic return condition, and manual-copy fallback
8. ask the employee to update `memory.md` and `current-task.md`, then return the fixed employee-report shape to the project director
9. record partial employee reports, wait for required dependencies, and continue only according to A/B/C mode
10. in automatic progress mode, create or update heartbeat only when automation tools are available and stop at completion, blocker, risk, or the next user checkpoint

The project director may write handoff framing, inputs, constraints, and acceptance criteria. It must not write the employee-owned final output unless the user explicitly asks the project director to take over that employee's work.

Task-routing read budget: read `office-plan.json`, `task-board.md`, `thread-registry.md`, `project-brief.md`, optional root `AGENTS.md`, and only the likely owner's `current-task.md`. Do not read every employee file or run full validation before ordinary dispatch.

Dispatch transaction budget: update only `task-board.md`, `communication.md`, and the assigned employee's `current-task.md`; send at most one employee-thread message; then report to the user and stop. If writes or thread sends are unavailable, show a manual dispatch packet and stop.

If the employee thread ID is `TBD`, missing, or not clearly tied to this project, do not mark the task `active`. Show the manual dispatch packet and stop; record the task after the user confirms it was sent or after the employee result returns.

## Employee Report Shape

Employees reply to the project director in this shape after real work. If `send_message_to_thread` is available and `thread-registry.md` has a confirmed project-director thread ID, send this report to that thread; otherwise output the report as a copyable block and say it needs to be copied back to the project-director chat.

```text
【员工汇报】
汇报人：{员工职位}
任务：{任务名}
状态：已完成 / 阻塞 / 需要确认
产出位置：{路径或线程摘要}
结论摘要：{短摘要}
建议下一步：{建议交给谁或停在哪里}
需要用户介入：是/否
```

English:

```text
[Employee Report]
Reporter: {employee job title}
Task: {task title}
Status: done / blocked / needs-confirmation
Output location: {path or thread summary}
Summary: {short summary}
Suggested next step: {next owner or stop point}
User input needed: yes/no
```

## Dispatch Reply Shape

Use task titles in user-facing text. Internal `task_id` may be recorded in office files, but do not ask the user to remember it. Reserve A/B/C/D for choices that authorize different progress modes or actions.

Chinese:

````md
已派工给：`{员工职位}`
任务：`{任务名}`
路由判断：{为什么这件事归这个员工；若有下一棒，写下一棒是谁}
交接框架：{目标、约束、输入材料、验收标准；不要替员工写最终产物}
当前状态：等待 `{员工职位}` 完成。

我会按你选择的推进方式处理：
- A：等你回来发 `跟进` / `继续` / `OK` 后再推进。
- B：员工汇报回来后，我会继续流转，但关键检查点会停下来给你看。
- C：我会自动推进到下一个用户检查点；如可用，会设置 heartbeat 防止中断。

如果还有多个可继续任务，我会列任务名让你选。
````

Manual dispatch packet fallback:

````md
员工线程还没有登记，所以我先不给办公室写孤儿任务。请把下面这段发给 `{员工职位}` 窗口：

```text
本次派工：{任务名}
路由判断：{为什么这件事归这个员工}
交接框架：{目标、约束、输入材料、验收标准；不要替员工写最终产物}
回传目标：项目总监窗口 `{项目总监标题}`；若 thread-registry.md 有真实项目总监 thread ID，优先用 send_message_to_thread 发回。
完成后请更新你的 memory.md 和 current-task.md，然后用 `【员工汇报】` 格式回复给项目总监。
如果无法自动发回项目总监线程，请在本窗口输出完整 `【员工汇报】`，并写明需要复制回项目总监窗口。
```
````

English:

````md
Assigned to: `{employee job title}`
Task: `{task title}`
Routing decision: {why this belongs to this employee; name the likely next owner if any}
Handoff frame: {goal, constraints, inputs, acceptance criteria only; do not write the employee-owned output}
Current status: waiting for `{employee job title}`.

I will follow the progress mode you chose:
- A: I wait until you return with `continue`, `ok`, or a similar short reply.
- B: I continue from employee reports, but stop at key checkpoints.
- C: I continue automatically until the next user checkpoint; if available, I set a heartbeat to avoid interruption.

If several tasks can continue, I will list task titles and ask you to choose.
````

Manual dispatch packet fallback:

````md
The employee thread is not registered yet, so I will not create an orphan active task. Send this to the `{employee job title}` chat:

```text
Dispatch task: {task title}
Routing decision: {why this belongs to this employee}
Handoff frame: {goal, constraints, inputs, acceptance criteria only; do not write the employee-owned output}
Return target: project-director chat `{project-director title}`; if thread-registry.md contains a real project-director thread ID, prefer send_message_to_thread.
After completion, update your memory.md and current-task.md, then prepare the `[Employee Report]` shape.
If you cannot send it back to the project-director thread automatically, output the full report here and state that it needs to be copied back to the project-director chat.
```
````

## Report Intake Reply Shape

Use this when the project director receives an employee report. Keep it short.

Chinese:

````md
**收到员工汇报**

- 任务：`{任务名}`
- 汇报人：`{员工职位}`
- 状态：`{已完成 / 阻塞 / 需要确认}`
- 记录：已更新 `task-board.md` 和 `communication.md`
- 下一步：{等待缺失汇报 / 按 A/B/C 继续 / 需要用户判断}
````

English:

````md
**Employee Report Received**

- Task: `{task title}`
- Reporter: `{employee job title}`
- Status: `{done / blocked / needs-confirmation}`
- Records: updated `task-board.md` and `communication.md`
- Next: {wait for missing reports / continue under A/B/C / need user judgment}
````

Chinese employee launch prompt shape:

```text
本对话角色：{岗位名}

你现在入职这个项目，岗位是「{岗位名}」。先守住岗位判断、读取边界和写入边界；第一轮只做入职确认，不主动开工。

项目：{project name}
项目根目录：{project root}
默认语言：中文。路径、内部任务 ID、status enum、代码标识保持原样。

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
5. 如需开工，你需要项目总监给什么输入

之后等待项目总监派工；只有用户明确点名找你时，才直接回应用户。完成正式任务后，先更新自己的 memory.md 和 current-task.md，再生成 `【员工汇报】`。

回传规则：读取 `Agent Office/thread-registry.md` 确认项目总监窗口标题和 thread ID。如果 Codex Desktop 提供 `send_message_to_thread`，且项目总监 thread ID 已登记并能确认属于本项目，就主动把完整 `【员工汇报】` 发回项目总监线程；如果 thread ID 是 `current-window`、`TBD`、缺失或不确定，或线程工具不可用，就在本窗口输出可复制的 `【员工汇报】`，并写明“需要复制回项目总监窗口”。不要把汇报发给其他员工。
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
Forbidden: do not edit other employee folders, old-memory archives, or unrelated production code unless the project director explicitly authorizes it.
Handoff target: Project Director

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

Then wait for the project director to dispatch work; respond directly to the user only when explicitly addressed. After real work, update your own memory.md and current-task.md before preparing the `[Employee Report]` shape.

Return rule: read `Agent Office/thread-registry.md` for the project-director chat title and thread ID. If Codex Desktop exposes `send_message_to_thread` and the project-director thread ID is registered and clearly tied to this project, send the full `[Employee Report]` back to that thread. If the ID is `current-window`, `TBD`, missing, uncertain, or thread tools are unavailable, output a copyable `[Employee Report]` in this chat and state that it needs to be copied back to the project-director chat. Do not send reports to other employees.
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
