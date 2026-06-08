# Migration Playbook

Use this when an existing project has old agent rules, scattered planning docs, old memory folders, or cleanup needs.

For user-visible migration summaries, follow `references/markdown-output-guide.md`: use a short summary, a migration table, and one clear warning block when files may move.

## Goal

Turn old project knowledge into a clean `Agent Office/` without letting old frameworks keep competing for agent attention.

Use office language in chat. Say "项目体检" for the read-only scan, "旧资料入库" for archiving absorbed knowledge, and "办公室挂牌" for the approved takeover. Keep BOSS in control: present what will happen, then wait for the A/B/C/D reply.

Formal takeover means:

1. old knowledge has been read selectively and absorbed
2. `Agent Office/` exists
3. root `AGENTS.md` points to the office, with backup
4. absorbed old knowledge is archived under `Agent Office/Archive/Old Project Memory/`
5. the current chat is recorded as founding project manager
6. the current chat is renamed to the project-manager job title when Codex Desktop title tools are available
7. employees are invited only after the previous steps are complete

## What To Inspect

Filename-map the full project while skipping `.git`, dependencies, build output, caches, virtualenvs, temporary output folders, linked paths, and existing `Agent Office/`.

Read only likely old-knowledge text candidates:

- agent rules: `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.cursorrules`
- memory folders: `vibe/`, `context/`, old handoff or notes folders
- project management: tasks, todos, roadmap, planning, milestones, status, decisions, ADRs
- domain context: copy docs, architecture notes, workflows, QA checklists, changelogs, content strategy, release notes

Do not content-read images, video, audio, fonts, binaries, secrets, credentials, dependencies, build artifacts, or generated QA output. For ordinary structured data such as `.json`, `.yaml`, `.csv`, or `.tsv`, read the filename and metadata first; content-read it only when the path/name looks like rules, plans, tasks, context, decisions, copy, or handoff material.

## Absorption Map

For every old-knowledge candidate, say:

- what durable facts were absorbed
- where those facts now live in `Agent Office/`
- whether the original should be archived, left alone, or ignored

Typical destinations:

| Old knowledge | New destination |
|---|---|
| agent rules and safety boundaries | `Agent Office/Proposals/AGENTS.proposed.md` |
| current state and next work | `Agent Office/status.md`, `Agent Office/task-board.md` |
| file map and code ownership | `Agent Office/project-map.md` |
| durable decisions | `Agent Office/decisions.md` |
| employee-specific continuity | `Agent Office/Employees/{role-slug}/memory.md` |
| old source material after absorption | `Agent Office/Archive/Old Project Memory/` |

For BOSS-facing migration reports, use this table shape:

```md
| 旧资料 | 吸收位置 | 归档动作 |
|---|---|---|
| `vibe/notes.md` | `Agent Office/project-brief.md`、`Agent Office/task-board.md` | 已吸收后入库 |
```

## User Choice

After the migration proposal, use plain A/B/C/D reply options. Do not use tables or card-like choice layouts. Put the "reply one letter" instruction in a fenced `text` block. For most old projects:

```text
回一个字母即可：A / B / C / D
```

A. 正式接管：办公室挂牌、应用 AGENTS、旧资料入库，再邀请员工入职
B. 先挂牌办公室和 AGENTS，旧资料暂时不动
C. 我想自己指定员工数量或岗位
D. 先暂停，我只看方案

Make clear that A includes creating `Agent Office/`, applying `AGENTS.md` with backup, archiving absorbed old knowledge, and only then onboarding employees.
If A invites employees, also make clear that BOSS can keep using the current project-manager chat as the single entry point; the manager will dispatch work to employee threads.

Use a blockquote or warning callout for the risk boundary:

```md
> [!WARNING]
> `A` 会改动项目入口：创建 `Agent Office/`、备份并应用根 `AGENTS.md`、归档已吸收旧资料。
> 在你回复前，我不会移动或覆盖旧资料。
```

## AGENTS Replacement

When root `AGENTS.md` already exists:

1. summarize the current content
2. write the replacement draft to `Agent Office/Proposals/AGENTS.proposed.md`
3. show the important content in chat
4. apply it only when the selected option authorizes AGENTS application
5. create a dated backup before overwriting

Root `AGENTS.md` should be short and index-like. It must tell ordinary employees not to read `Agent Office/Archive/Old Project Memory/`.

## Archive And Move

Absorbed old knowledge should leave the active project surface when the user selects formal takeover. Archive under:

```text
Agent Office/Archive/Old Project Memory/<date>/
```

Default action is archive/move according to the approved migration plan. Do not delete old files. If unsure, copy into the archive and leave a clear pending decision.

Use `scripts/archive_legacy.py` for deterministic archive/move operations. It requires archive approval and an Absorption Map status that says each source was absorbed into `Agent Office/`. `needs absorption note`, `proposed`, or pending wording must be resolved before archiving.

When `--move-originals` is used, only files listed in `## Proposed Move List` may move. The broader archive list is for copy-only historical preservation.

If root `AGENTS.md` was replaced during formal takeover, archive the pre-apply backup (`AGENTS.md.gaogao-office-*.bak`) as the old `AGENTS.md` material. Do not archive the newly applied root `AGENTS.md` as old knowledge.

## Employee Onboarding

Do not invite employees before formal takeover. After takeover:

- current chat is the project manager
- project manager is BOSS's default single entry point and dispatches work to employee threads
- rename the current project-manager chat to its job title only; if this cannot be done automatically, tell the user the exact manual title
- each other employee gets a human job title
- employee profiles are written before launch prompts
- Codex Desktop threads are created automatically when authorized and tools are available
- fallback prompts start with `本对话角色：职位名` or `Conversation role: Job Title`

Good Chinese report style after migration:

```text
旧资料已经入库，活跃项目面现在干净了。
我把可用信息吸收到 `project-brief.md`、`task-board.md` 和员工档案里；原始材料放进 `Agent Office/Archive/Old Project Memory/`，日常员工不会再翻那里。
接下来可以开始让员工按岗位工作。
```
