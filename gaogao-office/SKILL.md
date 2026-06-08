---
name: gaogao-office
description: Set up, migrate, or maintain GAOGAO Office, a lightweight Agent Office project workspace for long-running AI coding-agent projects. Use when the user explicitly wants GAOGAO Office, Agent Office, multi-window agent employee roles, per-role memory, project cleanup, old planning/vibe framework migration, AGENTS.md approval workflows, or durable project-office management. Do not use for one-off AGENTS.md edits, generic task lists, or ordinary short chats that do not need a durable project folder.
---

# GAOGAO Office

Create and maintain a lightweight project office for AI agents. The skill is named GAOGAO Office; the project folder it creates is always `Agent Office/`.

## Fit

Use this for long-running work anchored in a real project folder. It costs more upfront than a plain one-off chat, but should reduce repeated reorientation after context compaction, handoffs, or multi-window role work.

Do not use it for lightweight standalone questions, isolated file edits, or unrelated multi-task chats that do not share one durable project folder.

## Workflow Decision

Choose exactly one workflow before writing files:

1. **Initialize a new project**: user is starting a project or wants a fresh agent office.
2. **Migrate an existing project**: user has old planning docs, `vibe/` context, old agent rules, scattered memory, or wants cleanup.
3. **Maintain an existing office**: user already has `Agent Office/` and wants audit, role tuning, archival, or context reduction.

If the request is ambiguous, inspect the project first, then ask only the questions that materially change the office design.

## Required First Pass

Before changing files:

- Introduce GAOGAO Office briefly: it designs a durable `Agent Office/`, first performs a read-only project check, and will not create files until the user approves.
- Inspect project clues read-only: directory name, full filename map excluding skip directories, README, config files, existing `AGENTS.md`, `vibe/`, top-level docs, and Git status when available.
- Do not bulk-read every file. Full-scan filenames; read only relevant text candidates such as README, agent rules, planning, tasks, context/vibe, copy docs, ADRs, and status notes.
- Do not content-read images, media, binary files, sensitive-looking files, dependencies, build output, caches, virtualenvs, `.git`, or linked external paths.
- If this is migration, run or emulate `scripts/inspect_office.py` and present migration findings before changing legacy files.

## First-Use Consultation Gate

For first-time setup requests, read `references/first-use-playbook.md` before scaffolding. Default to lightweight chat, not Plan Mode.

On initial invocation:

- Explain fit and safety briefly: best for long-running project folders; first pass is read-only; root `AGENTS.md` gets a proposal first; confirmed overwrites create backups; legacy files are absorbed before archive/move/delete.
- If the project purpose is inferable, confirm it. If not, ask what the project does and what the main deliverable is.
- Ask at most 3-5 numbered questions per round. Accept numbered answers.
- Present an office configuration plan before writing files: project understanding, recommended dynamic roles, why each role exists, deferred roles, public/private boundaries, write scopes, first task, and whether old materials should be absorbed or archived.
- Create office files only after an explicit approval phrase in the user's language, such as `create this office` or `apply this plan`.

## New Project Flow

1. Read `references/first-use-playbook.md` and run the consultation gate.
2. If project details are unclear, read `references/interview-guide.md`.
3. Draft a dynamic office plan. Read `references/role-catalog.md` only if role boundaries need help.
4. After approval, save the approved plan as JSON and run `scripts/scaffold_office.py --config <plan>`.
5. Create the approved office:
   - `Agent Office/README.md`
   - `Agent Office/status.md`
   - `Agent Office/project-brief.md`
   - `Agent Office/project-map.md`
   - `Agent Office/task-board.md`
   - `Agent Office/communication.md`
   - `Agent Office/decisions.md`
   - `Agent Office/thread-registry.md`
   - `Agent Office/office-plan.json`
   - `Agent Office/Proposals/AGENTS.proposed.md`
   - `Agent Office/Employees/{role-slug}/README.md`
   - `Agent Office/Employees/{role-slug}/memory.md`
   - `Agent Office/Employees/{role-slug}/current-task.md`
   - `Agent Office/Archive/Legacy Management/`
6. Do not write root `AGENTS.md` during initial scaffold. Show `Agent Office/Proposals/AGENTS.proposed.md` in chat and ask the user for the exact AGENTS apply phrase defined in `references/first-use-playbook.md`.
7. After the exact AGENTS apply phrase, run `scripts/scaffold_office.py --apply-agents --confirm-apply-agents` or manually apply the same proposal with a dated backup if root `AGENTS.md` exists.
8. In the current chat, output the approved role launch prompts from `Agent Office/thread-registry.md`. Put new-window/title instructions outside fenced code blocks.
9. Run `scripts/validate_office.py` or equivalent checks.

## Migration Flow

1. Read `references/migration-playbook.md` and `references/templates.md`.
2. Inspect old management surfaces:
   - `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.cursorrules`
   - `vibe/`, context docs, roadmap, tasks, architecture, ADRs, status notes, meeting notes
   - existing `.codex/`, `.agents/`, `.github/`, issue templates, and automation notes
3. Produce `Agent Office/migration-report.md` or a proposed report before changing legacy files.
4. Build an absorption map: for each old management file, say which durable facts move into `status.md`, `project-brief.md`, `project-map.md`, `task-board.md`, `decisions.md`, `communication.md`, employee files, or archive notes.
5. Scaffold `Agent Office/` if missing, preserving root `AGENTS.md` by default.
6. Write `Agent Office/Proposals/AGENTS.proposed.md` for review. Apply it only after the user says the exact AGENTS apply phrase from `references/first-use-playbook.md`.
7. Copy approved absorbed legacy files under `Agent Office/Archive/Legacy Management/`; move originals only after a separate exact move approval.
8. Delete legacy files only after separate explicit confirmation and a reviewed deletion list.

Do not silently copy, move, delete, or overwrite old project management files.

## Office Model

Public area:

- Files directly inside `Agent Office/` are shared context all roles may read.
- Keep public files short. If a public file grows too large, summarize and move detail into archive or a focused note.

Private area:

- Each role has one private-by-protocol folder under `Agent Office/Employees/{role-slug}/`.
- A role reads and updates only its own employee folder by default.
- Other roles may read an employee folder only when the user explicitly asks for maintenance, audit, recovery, or handoff review.

Archive:

- `Agent Office/Archive/Legacy Management/` is human-review/audit material after migration absorption.
- Ordinary role work must not read the legacy archive.

## Optional Codex Thread Creation

Default to manual thread creation with copyable prompts. If the user explicitly asks to automatically create Codex conversations and thread tools are available, create one conversation per approved role and record returned thread IDs in `Agent Office/thread-registry.md`. If thread tools are unavailable, fall back to manual copy prompts. The Markdown office must remain usable by other agents.

## Safety Rules

- Treat context as a budget. Full-scan filenames; do not full-read the whole project.
- Keep `AGENTS.md` short and index-like.
- Do not apply root `AGENTS.md` unless the user explicitly says the exact AGENTS apply phrase from `references/first-use-playbook.md`.
- Do not let multiple writer roles own the same file scope.
- If a role is asked to work outside scope, route the request to the right role or record it in `Agent Office/communication.md`.
- Do not edit `.git`, secrets, home directory files, external configuration, or linked external paths while scaffolding.
- Refuse project-office paths that resolve outside the project root through symlinks or junctions.
- Follow the user's language by default. Keep machine identifiers such as paths, role slugs, `status: proposed`, and `T-000` stable.

## Resources

- `references/office-blueprint.md`: operating model and context-budget rules.
- `references/first-use-playbook.md`: consultation, dynamic role planning, and prompt-output rules.
- `references/interview-guide.md`: questions for new projects, migrations, and maintenance.
- `references/templates.md`: Markdown templates for the lightweight office.
- `references/migration-playbook.md`: old-framework audit, absorption, archive, and move process.
- `references/maintenance-playbook.md`: office health audit and cleanup workflow.
- `references/role-catalog.md`: standing and optional employee role strategies.
- `references/github-publishing.md`: GitHub release and installation guide.
- `scripts/scaffold_office.py`: create a safe lightweight office scaffold.
- `scripts/inspect_office.py`: read-only filename map and migration discovery.
- `scripts/archive_legacy.py`: copy approved legacy files; optionally move originals only with explicit move approval.
- `scripts/validate_office.py`: structure and health checks.
