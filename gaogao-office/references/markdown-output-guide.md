# Markdown Output Guide

Use this when GaoGao Office writes user-visible chat output for onboarding, proposals, migration reports, maintenance reports, retirement summaries, or employee launch prompts.

The goal is readability, not decoration. Use the smallest Markdown structure that helps BOSS scan, decide, copy, or verify.

## Default Rules

- Write normal prose first. Add boxes only when they improve readability, emphasis, copying, comparison, or status tracking.
- Use at most 2-4 formatting types in one ordinary reply. Avoid turning every paragraph into a callout.
- Keep headings short and practical: `项目体检`, `我的判断`, `接管方案`, `下一步`.
- Keep takeover choice options as plain A/B/C/D text lists, not tables or card-like layouts.
- Put exact user replies, employee prompts, commands, and reusable messages in fenced `text` blocks.

## Format Selection

| Format | Use For | Avoid For |
|---|---|---|
| Normal prose | Brief context and transitions | Long dense status dumps |
| `inline code` | Paths, files, commands, task IDs, status values | Ordinary emphasis |
| Blockquote `>` | Safety promises, key reminders, current state | Multi-section reports |
| Alert quote | Risks, destructive actions, must-not-miss notes | Routine information |
| Fenced `text` | Copyable replies, prompts, plain instructions | Explanatory paragraphs |
| Language code block | JSON, config, commands, code | Non-code narrative |
| Table | Role plans, task status, migration maps | Long prose or choice options |
| Task list | Checkups, takeover completion, cleanup status | Role descriptions |
| `<details>` | Optional long logs or extra evidence | Required decisions |
| Mermaid | First-use roadmap or complex workflows | Ordinary status updates |

## Standard Blocks

Use plain blockquotes for stable rendering:

```md
> 现在只读，不写文件。等你回复选项后，我再执行对应动作。
```

Use alert-style quotes only when the message is important even if the client renders it as a normal quote:

```md
> [!WARNING]
> 这个选项会移动旧资料。执行前我会列出清单，不会静默删除。
```

Use `text` blocks for copyable replies. When an example contains a fenced code block, wrap the outer example in four backticks so nested fences do not break:

````md
```text
进入方向顾问模式
```
````

## First-Use Reply Shape

Use this structure for a first invocation:

````md
BOSS，我先给这个项目做一次项目体检。现在只看，不写文件。

> 现在只读，不写文件。等你回复 A/B/C/D 后，我再执行对应动作。

```mermaid
flowchart LR
  A["只读体检"] --> B["组织方案"]
  B --> C["BOSS 选 A/B/C/D"]
  C --> D["正式接管"]
  D --> E["员工入职"]
  E --> F["询问是否进入方向顾问模式"]
```

**项目体检**
- 路径：`...`
- 线索：...

**我的判断**
我判断这是 ...

**下一步**
如果这个判断不对，直接纠正我；如果判断对，我会给你接管方案。
````

Use this first-use roadmap only during onboarding, migration takeover, or upgrade takeover. Do not add Mermaid to ordinary progress updates.

If the project purpose is unknown, ask one light question in a `text` block:

````md
```text
BOSS，这个项目主要想做什么？随便说一句就行，我会先按你的描述判断该怎么组建属于您的团队。
```
````

## Organization Proposal Shape

Use a short explanation plus a table:

````md
**接管方案**

| 员工 | 为什么需要 | 职责边界 | 是否入职 |
|---|---|---|---|
| 项目总管 | 统一接收 BOSS 需求 | 公共区、任务路由、验收 | 当前窗口 |
| 设计师 | 稳定视觉判断 | 设计相关文件和自己的员工区 | 建议 |

```text
回一个字母即可：A / B / C / D
```

A. 按推荐团队正式接管
创建 Agent Office、应用 AGENTS.md、邀请员工入职。
````

## Completion Shapes

For A-style formal takeover, use a task list:

```md
**接管完成**

- [x] 创建 `Agent Office/`
- [x] 应用 `AGENTS.md`
- [x] 邀请员工入职
- [x] 派工策略已记录
- [ ] 安排项目任务

> 当前还没有安排任务。你可以继续只和项目总管窗口说话。
```

After takeover, ask whether BOSS wants direction-advisor mode:

````md
> 办公室已经就位，但我还没有安排项目任务。

```text
BOSS，你现在对这个项目有没有明确方向？有的话直接说你的想法；没有的话我来帮你判断 2-3 个方向。
```
````

## Final Answer Preflight

Before replying to BOSS, remove private drafting traces. The final answer must not contain:

- internal thinking such as `Wait`, `Need final`, `analysis`, `draft`, `TODO`, `abs?`, or `no need?`
- implementation chatter such as temporary config names, internal IDs, or "I need to figure out the link syntax"
- raw multi-thread logs unless BOSS asks for them
- uncertain Markdown link experiments

If a local link format is uncertain, write the plain absolute path. Keep the final answer to user outcomes: what changed, where it is, what is waiting, and what BOSS can do next.

## Migration And Maintenance Shapes

Use tables for migration maps:

```md
| 旧资料 | 吸收位置 | 处理方式 |
|---|---|---|
| `vibe/notes.md` | `project-brief.md` | 入库后归档 |
```

Use task lists for cleanup or retirement:

```md
**撤岗完成**

- [x] 员工线程已归档
- [x] 未来任务已取消
- [x] 已完成任务保持 `done`
- [x] 资料未删除
```
