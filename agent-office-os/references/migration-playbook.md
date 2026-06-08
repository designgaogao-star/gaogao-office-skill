# Migration Playbook

Use this reference when taking over an old or long-running project.

## Table of Contents

- [Migration Principles](#migration-principles)
- [Discovery Targets](#discovery-targets)
- [Migration Report](#migration-report)
- [Absorption Process](#absorption-process)
- [AGENTS Replacement Process](#agents-replacement-process)
- [Archive Process](#archive-process)
- [Move Process](#move-process)
- [Deletion Process](#deletion-process)
- [Conflict Handling](#conflict-handling)

## Migration Principles

- Inspect before modifying.
- Absorb durable facts into the new office before archiving or moving old framework files.
- Summarize durable facts, not every historical detail.
- Keep existing root `AGENTS.md` unchanged by default. Generate a proposed replacement first.
- Archive before deleting.
- Move old framework files only after a separate exact-list approval.
- Never delete old framework files without explicit user confirmation.
- Preserve active work, branches, and task context.
- Do not migrate secrets or private credentials into office docs.
- Do not follow symlinks or junctions into external project areas during inspection or validation.
- After absorption, treat legacy archives as human-review/audit material, not normal role context.

## Discovery Targets

Look for:

- `AGENTS.md`, `AGENTS.override.md`
- `CLAUDE.md`, `GEMINI.md`, `.cursorrules`
- `.codex/`, `.agents/`, `.github/`
- `docs/`, `planning/`, `roadmap/`, `tasks/`, `adr/`, `decisions/`
- files containing `roadmap`, `plan`, `todo`, `status`, `architecture`, `decision`, `context`, `handoff`, `milestone`, `sprint`
- folders or files named `vibe`, `VIBE.md`, `context`, or equivalent project-memory notes

Skip generated or dependency directories:

- `.git`, `node_modules`, `vendor`, `dist`, `build`, `target`, `.venv`, `__pycache__`, `.cache`

## Migration Report

Create `docs/agent-office/migration-report.md` with:

- discovered management surfaces
- likely authoritative files
- stale or conflicting files
- active tasks found
- decisions found
- absorption map
- proposed `AGENTS.md` replacement path and status
- recommended standing roles
- proposed archive list
- proposed move list, if any
- proposed deletion list, if any
- questions for the user

Use these exact second-level headings so `scripts/validate_office.py` can check the report:

- `## Candidates`
- `## Likely Authoritative Files`
- `## Stale Or Conflicting Files`
- `## Active Tasks Found`
- `## Decisions Found`
- `## Absorption Map`
- `## Proposed AGENTS Replacement`
- `## Recommended Roles`
- `## Proposed Archive List`
- `## Proposed Move List`
- `## Proposed Delete List`
- `## User Questions`
- `## User Approval Record`

The approval record starts as:

```markdown
Approved archive list: NO
Approved AGENTS replacement: NO
Approved legacy move list: NO
Approved deletion list: NO
Approved by: <pending>
Approval date: <pending>
```

## Absorption Process

The migration must do more than preserve old files. For each old management surface, decide what it contributes to the new office:

| Old content | New office destination |
|---|---|
| current goal, milestone, blockers | `docs/agent-office/status.md` |
| active tasks and ownership | task packets under `docs/agent-office/tasks/active/` |
| finished or historical tasks | `tasks/done/`, `handoffs/`, or archive notes |
| durable rules and safety constraints | `docs/agent-office/proposals/AGENTS.proposed.md` and role cards |
| project background, audience, product intent | `context-packs/project-brief.md` |
| accepted decisions | ADRs under `docs/agent-office/decisions/` |
| open questions for another role | `docs/agent-office/messages/open/` |
| vague vibe/context notes | concise project-brief notes, task context, or user questions |

Do not copy a legacy document wholesale into always-loaded files. Extract the durable facts, cite the source path in the migration report, and mark uncertainty as a user question.

## AGENTS Replacement Process

When root `AGENTS.md` or an equivalent rule file already exists:

1. Read only the parts needed to preserve build, test, safety, review, and office-entry rules.
2. Write the replacement draft to `docs/agent-office/proposals/AGENTS.proposed.md`.
3. Keep the draft short and index-like. It should point to `docs/agent-office/`, preserve still-valid project rules, and exclude verbose history.
4. Tell the user they can manually copy the proposal over `AGENTS.md`.
5. Apply the replacement yourself only after the user explicitly approves that exact proposal. Create a dated backup before overwriting.
6. Record the approval under `## User Approval Record` in the migration report.

## Archive Process

1. Scaffold `docs/agent-office/` if missing.
2. Create `docs/agent-office/archive/legacy-management/`.
3. Absorb durable facts into current office files before archiving.
4. Copy old framework files into dated subfolders only after user approval.
5. Prefer `scripts/archive_legacy.py` for the copy step when the approved report is clear.
6. Use durable archive copies, not symlinks or junctions to external files.
7. Leave original legacy files in place until a separate move or deletion approval is recorded.
8. Leave a short index file explaining where each legacy item came from.
9. Update `status.md`, `thread-registry.md`, task packets, and ADRs with durable facts.
10. Add an archive note that `archive/legacy-management/` is human-review/audit material and not part of normal role loading.

Archive helper:

```bash
python agent-office-os/scripts/archive_legacy.py --project-root ./project --dry-run
python agent-office-os/scripts/archive_legacy.py --project-root ./project
```

The helper refuses to run unless `Approved archive list: YES` is an exact approval line in `## User Approval Record`. It copies by default and never deletes files. It moves originals only when `--move-originals` is passed and `Approved legacy move list: YES` is also present.

## Move Process

Moving old files is optional and more disruptive than copy-archiving. Use it only when the user wants the project folder cleaned up after absorption.

Required conditions:

- the old file appears in the approved archive/move list
- its durable facts were absorbed into the new office or intentionally discarded with reason
- `Approved archive list: YES` and `Approved legacy move list: YES` appear as exact approval lines in `## User Approval Record`
- the move destination is under `docs/agent-office/archive/legacy-management/<date>/`
- an `_archive-index.md` records the original source path

When using the helper:

```bash
python agent-office-os/scripts/archive_legacy.py --project-root ./project --move-originals --dry-run
python agent-office-os/scripts/archive_legacy.py --project-root ./project --move-originals
```

After moving, normal role threads should not read the legacy archive. If a migrated fact is missing from current office docs, ask the coordinator or archivist for an audit task instead of browsing the archive ad hoc.

## Deletion Process

Deletion is never the default. It requires:

- exact file list
- reason each file is safe to remove
- confirmation that content was migrated or intentionally discarded
- durable archive copy for each file before deletion
- explicit user approval

If in doubt, keep the old file archived.

## Conflict Handling

When old instructions conflict with the new office:

- Keep `AGENTS.md` as the short entrypoint.
- Copy or summarize verbose old rules into archive or a referenced office document.
- Keep current build/test commands if still valid.
- Preserve security and deployment warnings until a domain owner rejects them.
- Mark uncertain facts as questions in `migration-report.md`, not as project truth.
