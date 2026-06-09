# Migration Playbook

Use this when an existing project has old agent rules, planning docs, scattered project memory, stale prompts, or cleanup needs.

Before migration action, apply `references/operation-router.md`. Migration begins as `checkup` or `maintenance`, produces a `proposal-only` report, and becomes `takeover-approved` only after the current A/B option or another explicit approval authorizes formal takeover.

## Migration Rules

- Start read-only: filename map first, then candidate text files.
- Do not read binary, media, secrets, dependencies, build output, caches, `.git`, symlinks, or linked external paths.
- Absorb durable facts into active office files before archiving the source material.
- Default archive action is copy. Moving originals requires a separate exact move list and explicit move approval.
- Never silently delete old files.
- Ordinary employees must not read `Agent Office/Archive/Old Project Memory/` after migration; it is historical material, not active project truth.

## What To Inspect

Likely old-knowledge candidates include:

- `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.cursorrules`
- `README.md`, `docs/`, planning, task, roadmap, architecture, ADR, status, handoff, workflow, changelog, checklist, and copy files
- memory folders such as `vibe/`, `context/`, `notes/`, or old handoff folders

Images, videos, archives, and structured data are metadata-only unless the user explicitly asks for content analysis.

## Absorption Targets

| Old Material | Absorb Into |
|---|---|
| project purpose, audience, constraints | `Agent Office/project-brief.md` |
| active state, blockers, next steps | `Agent Office/status.md` |
| tasks, owners, acceptance criteria | `Agent Office/task-board.md` |
| decisions, rules, architecture notes | `Agent Office/decisions.md` |
| agent rules and safety boundaries | `Agent Office/Proposals/AGENTS.proposed.md` |
| cross-role notes and handoffs | `Agent Office/communication.md` |
| employee-specific continuity | `Agent Office/Employees/{role-slug}/memory.md` |

## Migration Report Shape

Use tables for scan and migration results:

```md
## Project Map

| Path | Kind | Read Policy | Why |
|---|---|---|---|
| `vibe/notes.md` | project-memory | content-read | old working context |
| `assets/hero.png` | media | metadata-only | visual asset |

## Absorption Map

| Source | Absorbed Into | Status |
|---|---|---|
| `vibe/notes.md` | `Agent Office/project-brief.md`, `Agent Office/task-board.md` | absorbed into active office files |

## Proposed Archive List

| Source | Archive Destination | Reason |
|---|---|---|
| `vibe/notes.md` | `Agent Office/Archive/Old Project Memory/{stamp}/vibe/notes.md` | content absorbed into active office |

## Proposed Move List

No files are proposed for moving yet.

## Proposed Delete List

No files are proposed for deletion.

## User Approval Record

Approved archive list: NO
Approved AGENTS replacement: NO
Approved legacy move list: NO
Approved deletion list: NO
```

## User Choice

After the migration proposal, use the same dynamic A/B/C/D reply options as first-use. The options choose the office organization, not whether the takeover is half-applied.

If single-employee is recommended:

```text
回一个字母即可：A / B / C / D
```

A. 单员工（推荐）
创建 `Agent Office/`、应用 `AGENTS.md`、归档已吸收旧资料；当前项目总管窗口正式接管，不邀请额外员工。

B. 多员工
创建 `Agent Office/`、应用 `AGENTS.md`、归档已吸收旧资料；邀请合适员工入职，由项目总管统一调度。

C. 自定义
用户指定员工数量或岗位；项目总管重新分配职责、边界和入职方案。

D. 以后再说
不创建文件，不修改项目。

If multi-employee is recommended, swap A and B:

```text
A. 多员工（推荐）
B. 单员工
```

A and B both include creating `Agent Office/`, applying `AGENTS.md` with backup, archiving absorbed old knowledge, and only then onboarding employees if that organization mode uses employees.

If the next user reply after A/B/C/D is not a valid letter, the options expire. Ask again before treating a later letter as approval.

Use a warning block for the risk boundary:

```md
> [!WARNING]
> `A` 或 `B` 会改动项目入口：创建 `Agent Office/`、备份并应用根 `AGENTS.md`、归档已吸收旧资料。
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
Agent Office/Archive/Old Project Memory/
```

Default action is to copy absorbed old knowledge into the archive. Move originals only with all of these:

- `--move-originals`
- exact `## Proposed Move List`
- `Approved archive list: YES`
- `Approved legacy move list: YES`

If unsure, copy into the archive and leave a clear pending decision.

Use `scripts/archive_legacy.py` for deterministic archive or move operations. It requires archive approval and an Absorption Map status that says each source was absorbed into `Agent Office/`. `needs absorption note`, `proposed`, or pending wording must be resolved before archiving.

If root `AGENTS.md` was replaced during formal takeover, archive the pre-apply backup (`AGENTS.md.gaogao-office-*.bak`) as the old `AGENTS.md` material. Do not archive the newly applied root `AGENTS.md` as old knowledge.

## Employee Onboarding

Do not invite employees before formal takeover. After takeover:

- current chat is the project manager
- project manager is the user's default single entry point and dispatches work to employee threads
- rename the current project-manager chat to its job title only; if this cannot be done automatically, tell the user the exact manual title
- each other employee gets a human job title
- employee profiles are written before launch prompts
- Codex Desktop threads are created automatically when authorized and tools are available
- fallback prompts start with `本对话角色：职位名` or `Conversation role: Job Title`
