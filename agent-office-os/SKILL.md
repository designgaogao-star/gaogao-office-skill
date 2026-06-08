---
name: agent-office-os
description: Set up, migrate, or maintain a durable Agent Office OS project office. Use when the user explicitly wants Agent Office OS, AI coding-agent project-office scaffolding, multi-thread agent employee roles, task/handoff/message/ADR workflows, migration from an old planning framework, or cleanup of a long-running project into a sustainable agent management system. Do not use for one-off AGENTS.md edits, generic task lists, or ordinary project management that does not need an Agent Office OS.
---

# Agent Office OS

Create and maintain a lightweight project office for AI coding agents: a small `AGENTS.md`, a structured `docs/agent-office/` workspace, role cards, task packets, handoffs, messages, ADRs, and thread instructions.

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
- Inspect project clues read-only: directory name, README, package/config files, `docs/`, existing agent instructions, and Git status.
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
- whether old management docs should be archived, left in place, or later deleted after confirmation
- whether GitHub publishing materials are needed

Do not use a fixed role set just because a project resembles a known type. Create only the roles that are currently useful and whose responsibilities, inputs, outputs, and write scopes are meaningfully different. Archive-before-delete remains the default migration policy.

## New Project Flow

1. Read `references/first-use-playbook.md`, `references/office-blueprint.md`, `references/role-catalog.md`, and `references/templates.md`.
2. Run the first-use consultation gate and interview the user for missing project facts.
3. Propose a dynamic office plan. If using the scaffold script, save the approved plan as `office-plan.json` and run `scripts/scaffold_office.py` with `--config office-plan.json`.
4. Create the approved office:
   - `AGENTS.md`
   - `docs/agent-office/README.md`
   - `docs/agent-office/status.md`
   - `docs/agent-office/thread-registry.md`
   - `docs/agent-office/communication.md`
   - `docs/agent-office/operating-model.md`
   - `docs/agent-office/roles/`
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
   - `docs/agent-office/cadences/`
   - `docs/agent-office/archive/legacy-management/`
5. In the current chat, output the approved role launch prompts so the user can copy them directly. Put "new window" and suggested title instructions outside the fenced code block; put only the message to send in the code block.
6. Run `scripts/validate_office.py` or perform the same checks manually.

Use `scripts/scaffold_office.py` for deterministic scaffolding when the target project root is clear.

## Migration Flow

1. Read `references/migration-playbook.md` and `references/templates.md`.
2. Inspect old management surfaces:
   - agent instruction files such as `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.cursorrules`
   - planning docs such as roadmap, tasks, architecture, ADRs, status notes, meeting notes
   - existing `.codex/`, `.agents/`, `.github/`, issue templates, or automation notes
3. Produce `docs/agent-office/migration-report.md` or a proposed report before changing legacy files.
4. Present an exact archive/overwrite/delete plan and ask for approval. Do not copy, overwrite, archive, or delete legacy management files until the user approves the exact list.
5. Scaffold the new office if it does not exist. If `AGENTS.md` already exists, preserve it by default and propose a merged replacement instead of using `--force`.
6. Migrate durable facts into `status.md`, role cards, task packets, decisions, and archive notes.
7. Copy approved old framework files under `docs/agent-office/archive/legacy-management/`; use `scripts/archive_legacy.py` when the approved report is clear. Leave originals in place until separate deletion approval.
8. Delete old framework files only after a separate explicit user confirmation and a reviewed deletion list.

Do not silently copy, delete, or overwrite old project management files.

### Existing AGENTS.md

When a project already has `AGENTS.md`, `AGENTS.override.md`, or an equivalent agent rule file:

- inspect it first and identify durable build, test, security, and review rules
- preserve those rules in the new office or proposed replacement
- keep the final `AGENTS.md` short and index-like
- write a proposed replacement or patch for user review
- never run `scaffold_office.py --force` during migration or maintenance without an approved overwrite list

## Maintenance Flow

Read `references/office-blueprint.md` and `references/maintenance-playbook.md`, then audit:

- overgrown `AGENTS.md` or `status.md`
- active tasks without DRI, reviewer, acceptance criteria, or write scope
- stale open messages
- missing handoffs for completed tasks
- retired or idle thread registry entries
- superseded ADRs

Use `scripts/validate_office.py` for a deterministic report. Produce a read-only maintenance report first unless the user explicitly asked for cleanup edits. Ask before archiving, retiring, superseding, or deleting large legacy areas.

## Optional Codex Thread Creation

Default to manual thread creation with copyable prompts. If the user explicitly asks to automatically create Codex conversations and thread tools are available, create one conversation per approved role and record returned thread IDs in `docs/agent-office/thread-registry.md`. If thread tools are unavailable, say so and fall back to manual copy prompts. This is a Codex convenience only; the Markdown office must remain usable by other agents.

## Safety Rules

- Treat context as a budget. Do not load the entire office unless auditing it.
- Keep `AGENTS.md` short and index-like.
- Do not allow multiple writer threads to own the same file scope.
- Do not create files during first-use consultation before explicit approval.
- Treat worktree offices as isolated proposals until PM/Archivist integrates them.
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
- `scripts/archive_legacy.py`: copy approved legacy files into the office archive without deleting originals.
- `scripts/validate_office.py`: structure and health checks.
