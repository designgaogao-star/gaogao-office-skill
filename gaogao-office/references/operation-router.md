# Operation Router

Use this before any GaoGao Office action that might scan a project, write files, route work, watch employee progress, maintain an office, or operate Codex threads.

This file is the single reference for command routing, lifecycle state, and authorization levels. Commands are shortcuts, not a rigid DSL: natural language with the same intent should route the same way.

## Routing Priority

1. **Manual first**: if the user asks `说明书`, `help`, `capabilities`, `你能做什么`, or asks about a capability, enter `manual` before scanning the project.
2. **Existing office first**: if `Agent Office/` already exists, treat skill invocation as `maintenance` or `upgrade`, not fresh initialization.
3. **Safety before action**: classify lifecycle state and authorization level before writes, thread actions, archive moves, or deletion.
4. **Routing before doing**: after employees exist, every project task starts with task routing. If a suitable employee owns the next step, dispatch it instead of doing that employee's work in the project-manager chat.
5. **Stop after dispatch**: project-manager dispatch is non-blocking by default. Watch progress only after explicit watch intent.

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
| `继续推进 T-xxx` | 员工完成后继续流转 | 可能写记录 |
| `盯进度 T-xxx` | 项目总监定时看员工进展 | 需要明确请求 |
| `停止盯进度` | 停止轮询 | 否或少量记录 |
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
| `Continue T-xxx` | Continue after an employee result | May write records |
| `Watch T-xxx` | Let the project manager check employee progress | Requires explicit request |
| `Stop watching` | Stop progress polling | No or small records |
| `retire role` | Retire or downsize employees | Requires approval |
| `archive old memory` | Move absorbed old memory out of active surfaces | Requires list and approval |

Natural-language examples:

- `帮我看看现在乱不乱` routes to `checkup` or `maintenance`.
- `把这个旧项目接过来` routes to migration/takeover.
- `别盯了` routes to stop watching.
- `让设计师先做` routes through task routing and dispatch authorization.

## Lifecycle State Machine

| State | Enter When | Allowed | Forbidden | Exit When |
|---|---|---|---|---|
| `manual` | User asks for manual/help/capabilities | Explain capabilities | Project scan, writes, threads, archive | User asks for a project action |
| `checkup` | First invocation or read-only checkup | Filename map, relevant text read, project judgment | Writes, archive, dispatch | Judgment is ready or one question is needed |
| `proposal` | Checkup is done and A/B/C/D is pending | Show takeover or upgrade proposal | Create files, apply `AGENTS.md`, onboard employees | User replies with a valid current option |
| `takeover-approved` | User chooses A/B or explicitly approves takeover | Scaffold office, apply `AGENTS.md`, archive approved old knowledge, onboard employees | Start project work | Takeover is complete |
| `ready` | Office exists and no project task is assigned | Wait, direction-advisor question, health check | Self-start tasks | User gives a project task |
| `active-dispatch` | Project manager dispatched work to an employee | Record handoff and tell user next continuation paths | Poll, wait, or steal employee work | User says continue or asks to watch |
| `watching` | User explicitly asks to watch progress | Check employee status at adaptive 30-60 second intervals | Default high-frequency polling or quiet-poll reports | Completion, blocker, user input, user interruption, or stop request |
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
- Use numbered `1/2/3` only for informational continuation paths.
- A stale letter is not approval. If the next reply after options is not A/B/C/D, those options expire.
- Do not merge office takeover with project work.
- Do not let the project manager do clear employee-owned work just because it can.
- The project manager may frame a handoff, define acceptance criteria, and preserve the user's constraints, but must not create the creative, technical, design, prompt, research, QA, or release output that belongs to an employee unless the user explicitly asks the project manager to take over that work.
- Dispatch messages preserve inputs and boundaries. If the project manager adds direction, label it as handoff framing that the employee should judge, not as the final employee deliverable.
- Thread operations are conditional capabilities, not universal promises.

## Dispatch Transaction Budget

Before dispatch, use a small task-routing read budget for existing offices:

1. read `office-plan.json`, `task-board.md`, `thread-registry.md`, and `project-brief.md`
2. read `AGENTS.md` only if it is present and cheap
3. read the `current-task.md` for the likely employee owner only after the owner is reasonably clear
4. do not read all employee `README.md` or `memory.md` files just to choose an owner
5. do not run full validation before ordinary dispatch
6. if ownership is still unclear after this small read, ask one short question or assign a judgment task to the most suitable planning role

After the project manager chooses an employee owner, finish dispatch in one small transaction and then stop:

1. update only the minimal active records: `task-board.md`, `communication.md`, and the assigned employee's `current-task.md`
2. send one concise employee task message only when a registered thread ID and thread tool are available
3. do not inspect unrelated employee folders, old memory archives, or downstream roles
4. do not wait for the employee reply
5. do not create downstream tasks until the first employee output exists
6. if file writes or thread sends are unavailable, show a manual dispatch packet and stop

If the target employee's thread ID is `TBD`, missing, or not clearly tied to this project, do not mark the task `active` yet and do not create orphan task records. Show a manual dispatch packet for that employee and stop. The project manager can record the task after the user confirms the packet was sent, after the employee thread is registered, or after an employee result returns.

The dispatch result to the user must be immediate and non-blocking: assigned owner, task id, handoff frame, numbered `1/2/3` continuation paths, and a separate fenced watch command.

## Project-Manager Self-Check

Before acting, the project manager asks:

```text
当前状态是什么？
用户这句话是在请求说明、体检、接管、维护、派工、继续、盯进度，还是普通任务？
这个动作会不会写文件、改 AGENTS、移动资料、操作线程？
当前回复里有没有足够授权？
如果有员工负责下一步，我是不是应该派工而不是自办？
执行后应该停下来，还是继续观察？
```

English equivalent:

```text
What lifecycle state am I in?
Is the user asking for manual, checkup, takeover, maintenance, dispatch, continue, watch, or ordinary work?
Will this write files, change AGENTS.md, move old memory, or operate threads?
Do I have enough approval in the current reply?
If an employee owns the next step, should I dispatch instead of doing it myself?
After acting, should I stop or keep watching?
```
