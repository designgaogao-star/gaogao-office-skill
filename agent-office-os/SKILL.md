---
name: agent-office-os
description: Set up, migrate, or maintain a durable Agent Office OS project office. Use when the user explicitly wants Agent Office OS, AI coding-agent project-office scaffolding, multi-thread agent employee roles, task/handoff/message/ADR workflows, migration from an old planning framework, or cleanup of a long-running project into a sustainable agent management system. Do not use for one-off AGENTS.md edits, generic task lists, or ordinary project management that does not need an Agent Office OS.
---

# Agent Office OS

Create and maintain a lightweight project office for AI coding agents: a small `AGENTS.md`, a structured `docs/agent-office/` workspace, role cards, role memory, task packets, handoffs, messages, ADRs, and thread instructions.

## Fit

Use this for long-running work anchored in a real project folder. It costs more upfront than a plain one-off chat, but should reduce repeated reorientation after context compaction, handoffs, or multi-window work.

Do not use it for lightweight standalone questions, isolated file edits, or unrelated multi-task chats that do not share one durable project folder.

## Workflow Decision

Choose exactly one workflow before writing files:

1. **Initialize a new project**: user is starting a project or wants a fresh agent management system.
2. **Migrate an existing project**: user has a long-running project, old planning docs, old agent rules, or scattered context to consolidate.
3. **Maintain an existing office**: user already has `docs/agent-office/` and wants cleanup, audit, role tuning, or context reduction.

If the user request is ambiguous, inspect the project first, then ask only the questions that materially change the office design.

## Required First Pass

Before changing files:

- Inspect the project root, existing `AGENTS.md`, `.codex/`, `.agents/`, `docs/`, planning files, and Git status when available.
- If this is a migration, run or emulate `scripts/inspect_office.py` first and present the migration findings.
- Identify whether the project is version-controlled. Prefer worktree-based recommendations for parallel implementation only when Git is available.
- Never bulk-read all project documents. Build a short context map and load only the files needed for the current workflow.

## First-Use Consultation Gate

For first-time setup requests, read `references/first-use-playbook.md` before scaffolding. The default interaction is lightweight chat, not Plan Mode.

On initial invocation:

- Introduce Agent Office OS briefly: it designs a durable agent project office, first performs a read-only project check, and will not create files until the user explicitly approves.
- Explain fit and safety briefly: best for long-running project folders, not short one-off chats; first pass is read-only; existing files are skipped by default, existing `AGENTS.md` gets a proposed replacement first, confirmed overwrites create backups, migration archives copy files before any separate move/delete approval, and the user can ask for a restore plan from those backups/archives.
- Inspect project clues read-only: directory name, README, package/config files, `docs/`, existing agent instructions, and Git status.
- During first-use consultation, do not run `inspect_office.py --output` or write a report before approval; keep findings in chat until the user approves file creation.
- Run a lightweight suitability check before continuing. If the request or folder looks like a one-off task, isolated edit, no durable project folder, or unrelated multi-task chat, say Agent Office OS may be overkill and ordinary chat is likely cheaper unless the user wants a durable project office.
- If the project purpose is inferable, confirm it: "I think this is X, likely aiming at Y. Is that right?"
- If it is not inferable, ask what the project does and what the main deliverable is.
- Ask at most 3-5 numbered questions per round. Accept numbered answers.
- Do not require Plan Mode. Mention Plan Mode only as an optional slower path when the user wants a formal spec before writing.
- Present an office configuration plan before writing files: project understanding, recommended roles, why each role exists, why deferred roles are not created now, role boundaries, write scopes, and first task.
- Create files only after an explicit approval phrase in the user's language, such as `create this office` or `apply this plan`.

## User Interview

Use `references/interview-guide.md` when project details are not obvious. Ask concise numbered questions in batches when possible. Lock these decisions before scaffolding:

- project name and project type
- new setup, migration, or maintenance
- expected project size and risk level
- first milestone or definition of initial success
- dynamic standing roles and their distinct write scopes
- whether old management docs should be absorbed into the new office, archived for human review, moved after approval, left in place, or later deleted after confirmation
- whether GitHub publishing materials are needed

Do not use a fixed role set just because a project resembles a known type. Create only the roles that are currently useful and whose responsibilities, inputs, outputs, and write scopes are meaningfully different. Archive-before-delete remains the default migration policy.

## New Project Flow

1. Read `references/first-use-playbook.md` and run the consultation gate.
2. If project details are unclear, read `references/interview-guide.md`.
3. Draft a dynamic office plan. Read `references/role-catalog.md` only if role boundaries need help.
4. Before writing, wait for an explicit approval phrase.
5. After approval, save the approved plan as `office-plan.json` and run `scripts/scaffold_office.py` with `--config office-plan.json`.
6. Read `references/office-blueprint.md` or `references/templates.md` only when manually writing or auditing generated files.
7. Create the approved office:
   - `AGENTS.md`
   - `docs/agent-office/README.md`
   - `docs/agent-office/status.md`
   - `docs/agent-office/thread-registry.md`
   - `docs/agent-office/communication.md`
   - `docs/agent-office/operating-model.md`
   - `docs/agent-office/roles/`
   - `docs/agent-office/role-memory/`
   - `docs/agent-office/tasks/active/`
   - `docs/agent-office/tasks/done/`
   - `docs/agent-office/tasks/archived/`
   - `docs/agent-office/messages/open/`
   - `docs/agent-office/messages/closed/`
   - `docs/agent-office/handoffs/`
   - `docs/agent-office/decisions/`
   - `docs/agent-office/context-packs/`
   - `docs/agent-office/context-packs/project-brief.md`
   - `docs/agent-office/context-packs/thread-launch-prompts.md`
   - `docs/agent-office/proposals/`
   - `docs/agent-office/cadences/`
   - `docs/agent-office/archive/legacy-management/`
8. In the current chat, output the approved role launch prompts so the user can copy them directly. Put "new window" and suggested title instructions outside the fenced code block; put only the message to send in the code block.
9. Run `scripts/validate_office.py` or perform the same checks manually.

Use `scripts/scaffold_office.py` for deterministic scaffolding when the target project root is clear.

## Migration Flow

1. Read `references/migration-playbook.md` and `references/templates.md`.
2. Inspect old management surfaces:
   - agent instruction files such as `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.cursorrules`
   - planning docs such as roadmap, tasks, architecture, ADRs, status notes, meeting notes
   - existing `.codex/`, `.agents/`, `.github/`, issue templates, or automation notes
3. Produce `docs/agent-office/migration-report.md` or a proposed report before changing legacy files.
4. Build an absorption map: for each old management file, say which durable facts move into `status.md`, `project-brief.md`, task packets, ADRs, role cards, messages, handoffs, or archive notes.
5. Present an exact absorb/archive/move/overwrite/delete plan and ask for approval. Do not copy, move, overwrite, archive, or delete legacy management files until the user approves the exact list.
6. Scaffold the new office if it does not exist. If `AGENTS.md` already exists, preserve it by default and write a merged proposed replacement to `docs/agent-office/proposals/AGENTS.proposed.md` instead of using `--force`.
7. Migrate durable shared facts into `status.md`, `context-packs/project-brief.md`, role cards, task packets, decisions, messages, handoffs, and archive notes. Create role memory files for approved roles, but do not copy broad legacy history into a role's private memory unless the user explicitly approves that role-specific summary.
8. Copy approved old framework files under `docs/agent-office/archive/legacy-management/`; use `scripts/archive_legacy.py` when the approved report is clear. Leave originals in place unless the user separately approves moving the exact absorbed files.
9. If the user approves moving absorbed legacy files, move only the exact list into `docs/agent-office/archive/legacy-management/<date>/` and record provenance in `_archive-index.md`.
10. Delete old framework files only after a separate explicit user confirmation and a reviewed deletion list.

Do not silently copy, delete, or overwrite old project management files.

### Existing AGENTS.md

When a project already has `AGENTS.md`, `AGENTS.override.md`, or an equivalent agent rule file:

- inspect it first and identify durable build, test, security, and review rules
- preserve those rules in the new office or proposed replacement
- keep the final `AGENTS.md` short and index-like
- write `docs/agent-office/proposals/AGENTS.proposed.md` for user review
- tell the user to manually copy it over root `AGENTS.md`, or apply it yourself only after the user explicitly approves that exact replacement
- never run `scaffold_office.py --force` during migration or maintenance without an approved overwrite list

### Legacy Archive Read Boundary

Treat `docs/agent-office/archive/legacy-management/` as human-review and audit material, not normal working context. Once old files have been absorbed into current office docs, role threads should not read the legacy archive by default. Only the coordinator, archivist, or an explicitly authorized migration/audit task may read it.

## Maintenance Flow

Read `references/office-blueprint.md` and `references/maintenance-playbook.md`, then audit:

- overgrown `AGENTS.md` or `status.md`
- active tasks without DRI, reviewer, acceptance criteria, or write scope
- stale open messages
- missing handoffs for completed tasks
- retired or idle thread registry entries
- missing, oversized, or stale role memory files
- superseded ADRs

Use `scripts/validate_office.py` for a deterministic report. Produce a read-only maintenance report first unless the user explicitly asked for cleanup edits. Ask before archiving, retiring, superseding, or deleting large legacy areas.

## Optional Codex Thread Creation

Default to manual thread creation with copyable prompts. If the user explicitly asks to automatically create Codex conversations and thread tools are available, create one conversation per approved role and record returned thread IDs in `docs/agent-office/thread-registry.md`. If thread tools are unavailable, say so and fall back to manual copy prompts. This is a Codex convenience only; the Markdown office must remain usable by other agents.

## Safety Rules

- Treat context as a budget. Do not load the entire office unless auditing it.
- Keep `AGENTS.md` short and index-like.
- Do not allow multiple writer threads to own the same file scope.
- If a role is asked to work outside its scope, it should route the request to the right role or write a message under `docs/agent-office/messages/open/` instead of doing the work silently.
- Each role may read and update only its own `docs/agent-office/role-memory/{role-slug}.md` by default. Do not read another role's memory unless the user explicitly asks for office maintenance, audit, or recovery.
- Do not read `docs/agent-office/archive/legacy-management/` during ordinary role work. It is human-review/audit material after migration absorption.
- Do not create files during first-use consultation before explicit approval.
- Treat worktree offices as isolated proposals until the owner, coordinator, or archivist integrates them.
- Do not edit `.git`, secrets, home directory files, or external configuration while scaffolding.
- Refuse project-office paths that resolve outside the project root through symlinks or junctions.
- Do not delete legacy files without explicit confirmation after showing the exact list.
- Follow the user's language by default. Keep machine identifiers such as paths, frontmatter keys, role slugs, `status: proposed`, and `T-000` stable.

## Resources

- `references/office-blueprint.md`: operating model and context-budget rules.
- `references/first-use-playbook.md`: lightweight first-use consultation, dynamic role planning, and prompt-output rules.
- `references/interview-guide.md`: questions for new projects, migrations, and maintenance.
- `references/templates.md`: ready-to-write Markdown templates.
- `references/migration-playbook.md`: old-framework audit and archive process.
- `references/maintenance-playbook.md`: office health audit and cleanup workflow.
- `references/role-catalog.md`: standing and optional agent employee roles.
- `references/github-publishing.md`: GitHub release and installation guide.
- `scripts/scaffold_office.py`: create a safe office scaffold.
- `scripts/inspect_office.py`: read-only migration discovery.
- `scripts/archive_legacy.py`: copy approved legacy files into the office archive; optionally move originals only with explicit move approval.
- `scripts/validate_office.py`: structure and health checks.
