# Capability Manual

Use this when the user asks what GaoGao Office can do, asks for a manual, says `说明书`, `使用说明`, `功能介绍`, `你能做什么`, `help`, `capabilities`, or asks whether a specific office-management ability exists.

Do not scan the project, write files, create threads, archive files, or change `AGENTS.md` when answering in manual mode. Explain capabilities only. Follow the user's language; output only Chinese or only English unless the user asks for both.

Keep the manual compact, but do not omit core capabilities: project checkup, new project takeover, existing project migration, employee onboarding, first-assignment role calibration, task routing, file-first dispatch/reporting, A/B/C progress modes, employee reports, role memory, retire/replace roles, office cleanup, old-memory archive, and Codex thread/heartbeat enhancement.

## Chinese Manual Shape

````md
我是 GaoGao Office。你可以把我当成一个长期项目的项目总监：先帮你看清项目，再决定要不要建立 `Agent Office/`、接管旧资料、邀请员工入职，以及后续怎么把任务派给合适的人。

> 说明书模式只介绍功能，不扫描项目、不写文件、不改 `AGENTS.md`、不创建或归档线程。

**我能做什么**

| 能力 | 适合什么时候用 | 会不会写文件 | 授权要求 |
|---|---|---|---|
| 项目体检 | 不确定项目是什么、乱在哪里、有没有旧规则 | 否 | 不需要 |
| 新项目接管 | 刚开项目，想建立长期工作秩序 | 是 | 需要你选 A/B |
| 旧项目迁移 | 有旧 planning、vibe、规则、任务或上下文散落 | 是 | 先给迁移方案，再等确认 |
| 员工入职 | 想把长期项目拆给多个专业对话窗口 | 是 | 正式接管后再授权 |
| 岗位校准 | 员工第一次正式开工前，让岗位形成本项目专属判断标准 | 是 | 由你选择轻量/标准/深度/跳过 |
| 任务路由 | 你只跟项目总监说需求，由它判断谁来做 | 可能 | 派工前会记录任务 |
| 文件优先交接 | 减少员工窗口里反复粘贴长背景和长汇报 | 可能 | 派工或汇报较长时使用 |
| A/B/C 推进 | 长任务开工前选择手动、半自动或自动推进到检查点 | 可能 | 每条长任务开工前由你选择 |
| 员工汇报 | 员工完成后更新记忆、回传项目总监，并由总监验收记账 | 可能 | 员工完成正式任务后使用 |
| 角色记忆 | 让每个岗位保留自己的长期记忆 | 是 | 员工完成正式任务后更新 |
| 撤岗/换岗 | 减少员工、停掉方向、换新窗口接任 | 是 | 先给保留和归档方案 |
| 办公室清理 | 把旧提示词、临时计划、重复入口移出工作区 | 是 | 先列清单，再确认 |
| 旧资料归档 | 吸收旧知识后，把旧文件放进历史档案区 | 是 | 默认只归档，不静默删除 |
| Codex 线程增强 | 自动创建、命名、登记、员工回传、归档或停用员工对话 | 可能 | 只有有线程工具且你明确授权时 |

**常用口令**

| 口令 | 适合什么时候发 |
|---|---|
| `只读体检` | 只想先看看项目现状，不想写文件 |
| `接管项目` | 想正式建立或刷新 `Agent Office/` |
| `迁移旧项目` | 有旧 planning、vibe、规则、任务或上下文要吸收 |
| `健康检查` | 已经有办公室，想看看有没有过期、混乱或缺记录 |
| `跟进` / `继续` / `OK` | 按当前唯一等待任务继续推进 |
| `自动推进到检查点` | 让项目总监继续到下次需要你查看的位置 |
| `停止自动推进` | 停止自动推进或 heartbeat |
| `撤岗` | 停用员工、缩编或把某个方向收起来 |

**我不会默认做什么**

- 不会默认写文件。
- 不会默认改 `AGENTS.md`。
- 不会默认创建、读取、归档或停用线程。
- 不会默认删除旧资料。
- 不会默认自动推进或反复轮询员工窗口。
- 不会在办公室接管完成后自动开始项目任务。

**最常用的三种开始方式**

```text
使用 $gaogao-office 只读体检当前项目
```

```text
说明书
```

```text
使用 $gaogao-office 接管这个旧项目，先给迁移方案，不要直接改文件
```

<details>
<summary>高级能力怎么理解</summary>

- 多员工不是默认越多越好。GaoGao Office 会根据项目判断该单窗口还是多员工。
- 项目总监默认是当前窗口。你可以只和它说话，它负责派工、接收员工汇报、更新任务记录并等待依赖齐全。
- 长任务开工前会先给你预计步骤、参与员工和下次检查点，再让你选 A/B/C 推进方式。
- 员工窗口有自己的岗位档案、当前任务和记忆文件；默认不读别人的私有区。
- 员工第一次正式任务前可以做岗位校准：轻量最省 token，标准适合核心岗位，深度需要额外授权，跳过最快但稳定性较弱。
- 派工包和完整汇报可以写进 `Agent Office/Exchange/`，线程里只发路径和状态，减少窗口上下文消耗。
- 已吸收的旧资料会进入 `Agent Office/Archive/Old Project Memory/`，日常员工不会读它。
- 线程相关能力依赖 Codex Desktop 当前是否提供线程工具；员工回传还需要项目总监 thread ID 已登记。工具或 ID 不可用时，会退回手动复制汇报。

典型工作流：

1. 新项目：只读体检 → 组织方案 → A/B/C/D → 正式接管 → 是否进入方向顾问。
2. 旧项目：扫描旧知识 → 吸收地图 → 接管方案 → 归档已吸收旧资料 → 员工入职。
3. 单窗口：当前项目总监负责全部长期记忆和任务记录。
4. 多员工：用户主要找项目总监，项目总监按职责派工、等待员工汇报，并按 A/B/C 推进。
5. 换岗/撤岗：保留已完成工作和记忆，取消未来任务，必要时归档线程。

</details>

**不适合用我的情况**

- 一次性小问题。
- 没有固定项目文件夹的闲聊。
- 互不相关的多任务对话。
- 只想临时改一个文件，不需要长期记忆或项目秩序。
````

## English Manual Shape

````md
I am GaoGao Office. Think of me as a project director for long-running AI-assisted projects: I inspect the project, propose whether to create `Agent Office/`, absorb old project memory, onboard employee chats, and route later work to the right role.

> Manual mode only explains capabilities. I will not scan the project, write files, change `AGENTS.md`, create threads, or archive anything.

**What I Can Do**

| Capability | When To Use It | Writes Files? | Authorization |
|---|---|---|---|
| Project checkup | You are not sure what the project contains or how messy it is | No | Not needed |
| New project takeover | You want durable order in a new long-running project | Yes | Requires A/B approval |
| Existing project migration | Old planning, vibe, rules, tasks, or context are scattered | Yes | Migration plan first, then approval |
| Employee onboarding | You want specialist chats for long-running roles | Yes | After formal takeover |
| Role calibration | Before an employee's first real task, turn project context into role-specific judgment | Yes | You choose light / standard / deep / skip |
| Task routing | You talk to the project director; it decides who should do the next step | Maybe | Task is recorded before dispatch |
| File-first handoff | Reduce long repeated chat between employee windows | Maybe | Used when dispatches or reports are long |
| A/B/C progress | Choose manual, semi-automatic, or automatic progress until the next checkpoint | Maybe | You choose before each long workstream |
| Employee reports | Employees update memory, return a report, and the project director records intake | Maybe | Used after meaningful employee work |
| Role memory | Each role keeps durable private continuity | Yes | Employees update after real work |
| Retire or replace roles | Downsize, stop a direction, or move a role into a fresh chat | Yes | Proposal before changes |
| Office cleanup | Move old prompts, temporary plans, and duplicate entrances out of the active surface | Yes | Reviewed list first |
| Old-memory archive | Absorb old knowledge and move sources to historical storage | Yes | Archive by approval; no silent deletion |
| Codex thread enhancement | Create, title, register, employee-return, archive, or retire employee chats | Maybe | Only when thread tools exist and you approve |

**Common Commands**

| Command | When To Use It |
|---|---|
| `checkup` | Inspect project state without writing files |
| `take over` | Create or refresh `Agent Office/` |
| `migrate` | Absorb old planning, vibe, rules, tasks, or context |
| `health check` | Audit an existing office for stale or missing records |
| `continue` / `ok` / `proceed` | Continue the current waiting task from context |
| `automatic progress to checkpoint` | Continue until the next user checkpoint |
| `stop automatic progress` | Stop automatic progress or heartbeat |
| `retire role` | Retire employees, downsize, or close a direction |

**What I Will Not Do By Default**

- I will not write files by default.
- I will not change `AGENTS.md` by default.
- I will not create, read, archive, or retire threads by default.
- I will not delete old material by default.
- I will not automatically progress or repeatedly poll employee chats by default.
- I will not start project work automatically after office takeover.

**Common Starting Points**

```text
Use $gaogao-office to inspect this project read-only
```

```text
help
```

```text
Use $gaogao-office to take over this old project. Give me the migration plan first; do not change files yet.
```

<details>
<summary>How the advanced parts work</summary>

- More employees is not automatically better. GaoGao Office recommends one chat or multiple employees based on the project.
- The current chat is the project director by default. You can keep talking to it while it dispatches work, receives reports, records intake, and waits for dependencies.
- Before long work starts, it gives expected steps, participating employees, and the next user checkpoint, then asks you to choose A/B/C progress mode.
- Employee chats keep their own profile, current task, and memory; they do not read other private folders by default.
- Before an employee's first real task, role calibration can be light, standard, deep, or skipped. Deep calibration needs separate approval for broader reading, web research, or external references.
- Full dispatch packets and reports can live under `Agent Office/Exchange/`; thread messages carry paths and status to reduce chat context.
- Absorbed old material goes to `Agent Office/Archive/Old Project Memory/`; ordinary employees do not use it as daily context.
- Thread operations depend on Codex Desktop thread tools. Employee return also needs a registered project-director thread ID. If tools or the ID are unavailable, GaoGao Office falls back to manual prompts or copyable employee reports.

Typical workflows:

1. New project: checkup -> proposal -> A/B/C/D -> formal takeover -> optional direction advisor.
2. Existing project: old-memory scan -> absorption map -> takeover proposal -> archive absorbed sources -> employee onboarding.
3. One-person office: the current project director keeps all durable memory and task records.
4. Multi-employee office: the user mainly talks to the project director; it dispatches by responsibility, waits for employee reports, and follows A/B/C progress.
5. Role retirement or replacement: preserve completed work and memory, cancel future tasks, and archive threads when approved.

</details>

**When Not To Use It**

- One-off questions.
- Casual chats without a real project folder.
- Unrelated multi-task conversations.
- A tiny file edit that does not need durable memory or project organization.
````
