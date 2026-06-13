# Operation Router

Use this before any GaoGao Office action that might scan a project, write files, route work, continue from employee reports, maintain an office, or operate Codex threads.

This file is the single reference for command routing, lifecycle state, and authorization levels. Commands are shortcuts, not a rigid DSL: natural language with the same intent should route the same way.

## Routing Priority

1. **Manual first**: if the user asks `说明书`, `help`, `capabilities`, `你能做什么`, or asks about a capability, enter `manual` before scanning the project.
2. **Existing office first**: if `Agent Office/` already exists, treat skill invocation as `maintenance` or `upgrade`, not fresh initialization.
3. **Safety before action**: classify lifecycle state and authorization level before writes, thread actions, archive moves, or deletion.
4. **Routing before doing**: after employees exist, every project task starts with task routing. If a suitable employee owns the next step, dispatch it instead of doing that employee's work in the project-director chat.
5. **First-assignment calibration**: employee startup is not role training. Before the first real task for an employee, ask the user for light, standard, deep, or skipped calibration; the employee writes project-specific role judgment into its own memory.
6. **File-first transport**: full dispatch packets and employee reports should live in office files when practical. Thread messages carry task title, file path, status, and whether user input is needed.
7. **Director receives reports**: employees do not default-dispatch to each other. They close out local state, return report indexes to the project director when transport is available, and otherwise produce copyable reports for manual return.

## One-Pass Checkup Budget

First-use and read-only checkup must be quick enough to answer in the current turn. Do one focused pass:

1. filename map, excluding dependency/build/cache/temp folders and `.git`
2. existing `Agent Office/` or root rule files such as `AGENTS.md`
3. README and top-level docs that clearly describe the project
4. likely old-memory text files, by filename first and content only when clearly relevant
5. Git status only when it is cheap and available

Stop inspecting as soon as the project purpose and office state are reasonably clear. If the quick pass is enough, produce a judgment and proposal. If it is not enough, ask one light question. If an optional check is slow, unclear, or noisy, skip it and reply with visible uncertainty instead of stalling.

## Command Menu

Chinese:

| 口令 | 作用 | 是否写文件 |
|---|---|---|
| `说明书` | 查看能力说明 | 否 |
| `只读体检` | 只读判断项目状态 | 否 |
| `接管项目` | 进入接管方案流程 | 需要确认 |
| `迁移旧项目` | 旧资料吸收、归档、接管 | 需要确认 |
| `升级办公室` | 旧版 `Agent Office/` 升级 | 需要确认 |
| `健康检查` | 检查办公室状态 | 默认只读 |
| `跟进` / `继续` / `OK` | 按当前任务语境继续推进 | 可能写记录 |
| `自动推进到检查点` | 让项目总监持续推进到下一次用户检查点 | 需要明确选择 |
| `停止自动推进` | 停止自动推进或 heartbeat | 否或少量记录 |
| `撤岗` | 停用员工或缩编 | 需要确认 |
| `归档旧资料` | 移走已吸收旧资料 | 需要清单和确认 |

English:

| Command | Purpose | Writes Files? |
|---|---|---|
| `help` | Show the capability manual | No |
| `checkup` | Inspect project state read-only | No |
| `take over` | Start the takeover proposal flow | Requires approval |
| `migrate` | Absorb, archive, and take over old project memory | Requires approval |
| `upgrade office` | Upgrade an existing `Agent Office/` | Requires approval |
| `health check` | Audit the office state | Read-only by default |
| `continue` / `ok` / `proceed` | Continue the current task from context | May write records |
| `automatic progress to checkpoint` | Let the project director continue until the next user checkpoint | Requires explicit choice |
| `stop automatic progress` | Stop automatic progress or heartbeat | No or small records |
| `retire role` | Retire or downsize employees | Requires approval |
| `archive old memory` | Move absorbed old memory out of active surfaces | Requires list and approval |

Natural-language examples:

- `帮我看看现在乱不乱` routes to `checkup` or `maintenance`.
- `把这个旧项目接过来` routes to migration/takeover.
- `先自动推进到下个检查点` routes to automatic progress if the office and tools can support it.
- `让设计师先做` routes through task routing and dispatch authorization.

## Lifecycle State Machine

| State | Enter When | Allowed | Forbidden | Exit When |
|---|---|---|---|---|
| `manual` | User asks for manual/help/capabilities | Explain capabilities | Project scan, writes, threads, archive | User asks for a project action |
| `checkup` | First invocation or read-only checkup | Filename map, relevant text read, project judgment | Writes, archive, dispatch | Judgment is ready or one question is needed |
| `proposal` | Checkup is done and A/B/C/D is pending | Show takeover or upgrade proposal | Create files, apply `AGENTS.md`, onboard employees | User replies with a valid current option |
| `takeover-approved` | User chooses A/B or explicitly approves takeover | Scaffold office, apply `AGENTS.md`, archive approved old knowledge, onboard employees | Start project work | Takeover is complete |
| `ready` | Office exists and no project task is assigned | Wait, direction-advisor question, health check | Self-start tasks | User gives a project task |
| `active-dispatch` | Project director dispatched work to an employee | Record handoff, wait for employee report, and follow chosen progress mode | Poll without opt-in, advance without dependencies, or steal employee work | User continues, employee report arrives, or automatic progress is active |
| `automatic-progress` | User chooses C or explicitly asks to continue automatically until a checkpoint | Continue from employee reports, set/update heartbeat if tools exist, stop at checkpoint/blocker/risk | Risky actions, deletion, archive moves, publishing, or `AGENTS.md` changes | Checkpoint, completion, blocker, user input, interruption, or stop request |
| `maintenance` | Health check, upgrade, cleanup, retire role | Audit, propose, then maintain after approval | Silent deletion or memory destruction | Maintenance completes or pauses |
| `blocked` | Missing approval, tool unavailable, risk unclear | Explain blocker and next step | Guessing execution | User supplies approval/context or chooses to stop |

## Authorization Matrix

| Level | Examples | Authorization |
|---|---|---|
| `read-only` | Manual, filename scan, relevant text read, health report | No extra approval |
| `proposal-only` | Takeover proposal, migration report, `AGENTS.md` proposal | No project-root writes |
| `approved-write` | Create `Agent Office/`, update office files, apply `AGENTS.md` | Current A/B option or explicit approval |
| `thread-action` | Create, rename, send to, read, archive, or retire employee threads | Codex Desktop thread tools plus explicit approval |
| `archive-move` | Move absorbed old knowledge into `Old Project Memory` | Reviewed list plus approval |
| `delete` | Delete old files or old frameworks | Separate exact delete list plus explicit delete approval |

Hard rules:

- Use `A/B/C/D` only for current action choices that authorize different actions.
- Use `A/B/C` for progress-mode choices before long work: A manual, B semi-automatic, C automatic until the next user checkpoint.
- Use numbered lists only for informational guidance or task-title disambiguation.
- A stale letter is not approval. If the next reply after options is not A/B/C/D, those options expire.
- Do not merge office takeover with project work.
- Do not let the project director do clear employee-owned work just because it can.
- The project director may frame a handoff, define acceptance criteria, and preserve the user's constraints, but must not create the creative, technical, design, prompt, research, QA, or release output that belongs to an employee unless the user explicitly asks the project director to take over that work.
- Employees report back to the project director using the fixed employee-report shape. The report has a transport layer: when possible, write the full report to `Agent Office/Exchange/Reports/` and use `send_message_to_thread` only for a short index; otherwise output a copyable report and say it needs to be copied back to the project-director chat. The project director records partial results and waits when downstream work depends on several employees.
- Dispatch messages preserve inputs and boundaries. If the project director adds direction, label it as handoff framing that the employee should judge, not as the final employee deliverable.
- Thread operations are conditional capabilities, not universal promises.

## Dispatch Transaction Budget

Before dispatch, use a small task-routing read budget for existing offices:

1. read `office-plan.json`, `task-board.md`, `thread-registry.md`, and `project-brief.md`
2. read `AGENTS.md` only if it is present and cheap
3. read the `current-task.md` for the likely employee owner only after the owner is reasonably clear
4. do not read all employee `README.md` or `memory.md` files just to choose an owner
5. do not run full validation before ordinary dispatch
6. if ownership is still unclear after this small read, ask one short question or assign a judgment task to the most suitable planning role

After the project director chooses an employee owner, finish dispatch in one small transaction and then follow the user's progress mode:

1. update only the minimal active records: `task-board.md`, `communication.md`, and the assigned employee's `current-task.md`
2. before that employee's first real task, ask the user for calibration level: A light, B standard, C deep, D skip
3. when practical, write the full dispatch packet to `Agent Office/Exchange/Dispatch/`; otherwise keep the handoff short in `communication.md`
4. send one concise employee task message only when a registered employee thread ID and thread tool are available; the message should carry task title, file path, status, and return requirement
5. do not inspect unrelated employee folders, old memory archives, or downstream roles
6. do not create downstream tasks until the required employee output exists
7. if downstream work depends on several employees, record partial reports and wait for all required inputs
8. if file writes or employee-thread sends are unavailable, show a manual dispatch packet and stop
9. every dispatch includes the return target: project-director title, project-director thread ID status, automatic return condition, and manual-copy fallback

If the target employee's thread ID is `TBD`, missing, or not clearly tied to this project, do not mark the task `active` yet and do not create orphan task records. Show a manual dispatch packet for that employee and stop. The project director can record the task after the user confirms the packet was sent, after the employee thread is registered, or after an employee result returns.

The dispatch result to the user uses readable task titles, not internal IDs. If there is exactly one active or waiting task, short replies such as `跟进`, `继续`, `OK`, `好的`, `可以`, `continue`, `ok`, or `proceed` mean continue that task. If several tasks are candidates, list task titles and ask the user to choose by number or task name.

## Progress Modes

Before longer or multi-employee work starts, the project director gives a short progress expectation and asks the user to choose:

```text
回 A / B / C 即可
```

- A. 手动推进 / Manual progress: dispatch the current step, then wait for the user to return with a short continue phrase.
- B. 半自动推进 / Semi-automatic progress: continue from employee reports, but stop at key checkpoints, dependency gaps, risky actions, or user-judgment moments.
- C. 自动推进到检查点 / Automatic progress until checkpoint: keep advancing until the next user checkpoint when thread tools and, if needed, heartbeat automation are available.

C mode may create or update a heartbeat for the current thread only when automation tools exist. Discover and use the Codex automation tool when the environment exposes one; if no automation tool is available, explain the downgrade instead of writing raw automation instructions. Heartbeat reminders should wake the project director to check whether unfinished work remains, continue only if safe, and stop immediately if work is done, blocked, risky, or needs the user. Automatic progress never authorizes deletion, publishing, archive moves, or `AGENTS.md` changes.

## Role Calibration

Role calibration happens before an employee's first real assignment, not during startup. Show the user the cost/benefit choices and use only the chosen level:

```text
回 A / B / C / D 即可
```

- A. 轻量校准 / Light: lowest token cost; write 3-5 project-specific success criteria and one confirmation trigger.
- B. 标准校准 / Standard: recommended for core employees; write success criteria, quality red lines, common mistakes, confirmation triggers, and the first-task judgment.
- C. 深度校准 / Deep: highest cost; use only after explicit approval for broader file reads, web research, or user-provided references.
- D. 跳过 / Skip: no calibration now; fastest, but the role may be less stable.

Employees write calibration into their own `memory.md` `Role Calibration` section. If a role needs live platform rules, market facts, professional standards, or external references, it must say what evidence is missing instead of pretending to know it.

## Employee Report Shape

Employees must report back to the project director, not default-dispatch to each other:

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

## Employee Report Transport

The employee completion chain is fixed:

```text
complete first-task role calibration when required
update memory.md
update current-task.md
write full Employee Report to office file when practical
return a short report index to the project director
```

Automatic return is allowed only when all are true:

- Codex Desktop exposes `send_message_to_thread`.
- `Agent Office/thread-registry.md` contains a real project-director thread ID.
- The ID is not `current-window`, `TBD`, blank, stale, or ambiguous.
- The employee is returning a report index to the project director, not sending work to another employee.

If any condition is false, the employee outputs a copyable report in its own chat and states that it must be copied back to the project-director chat. Do not claim the report was sent. If the full report was written to a file, return the file path instead of pasting the full content into thread chat.

## Employee Report Intake

When the project director receives `【员工汇报】` / `[Employee Report]`, do not treat it as a fresh user request.

1. Verify reporter, task title, status, output location, summary, suggested next step, and whether user input is needed.
2. If the shape is incomplete or the task does not match the office records, ask for the missing piece and do not advance.
3. If valid, update the matching task in `task-board.md`, append a short report-intake record in `communication.md`, and update dependency status.
4. If downstream work depends on other employees, wait for the missing reports.
5. If dependencies are complete, continue only according to the chosen A/B/C progress mode.

## Project-Director Self-Check

Before acting, the project director asks:

```text
当前状态是什么？
用户这句话是在请求说明、体检、接管、维护、派工、员工汇报、自然语言继续、自动推进，还是普通任务？
这个动作会不会写文件、改 AGENTS、移动资料、操作线程？
当前回复里有没有足够授权？
如果有员工负责下一步，我是不是应该派工而不是自办？
依赖是否齐全？
执行后应该停下来，还是按 A/B/C 继续？
```

English equivalent:

```text
What lifecycle state am I in?
Is the user asking for manual, checkup, takeover, maintenance, dispatch, employee report intake, natural-language continue, automatic progress, or ordinary work?
Will this write files, change AGENTS.md, move old memory, or operate threads?
Do I have enough approval in the current reply?
If an employee owns the next step, should I dispatch instead of doing it myself?
Are dependencies complete?
After acting, should I stop or continue under A/B/C?
```
