# Migration Playbook

Use this reference when taking over an old or long-running project.

## Table of Contents

- [Migration Principles](#migration-principles)
- [Discovery Targets](#discovery-targets)
- [Migration Report](#migration-report)
- [Archive Process](#archive-process)
- [Deletion Process](#deletion-process)
- [Conflict Handling](#conflict-handling)

## Migration Principles

- Inspect before modifying.
- Summarize durable facts, not every historical detail.
- Archive before deleting.
- Never delete old framework files without explicit user confirmation.
- Preserve active work, branches, and task context.
- Do not migrate secrets or private credentials into office docs.
- Do not follow symlinks or junctions into external project areas during inspection or validation.

## Discovery Targets

Look for:

- `AGENTS.md`, `AGENTS.override.md`
- `CLAUDE.md`, `GEMINI.md`, `.cursorrules`
- `.codex/`, `.agents/`, `.github/`
- `docs/`, `planning/`, `roadmap/`, `tasks/`, `adr/`, `decisions/`
- files containing `roadmap`, `plan`, `todo`, `status`, `architecture`, `decision`, `context`, `handoff`, `milestone`, `sprint`

Skip generated or dependency directories:

- `.git`, `node_modules`, `vendor`, `dist`, `build`, `target`, `.venv`, `__pycache__`, `.cache`

## Migration Report

Create `docs/agent-office/migration-report.md` with:

- discovered management surfaces
- likely authoritative files
- stale or conflicting files
- active tasks found
- decisions found
- recommended standing roles
- proposed archive list
- proposed deletion list, if any
- questions for the user

Use these exact second-level headings so `scripts/validate_office.py` can check the report:

- `## Candidates`
- `## Likely Authoritative Files`
- `## Stale Or Conflicting Files`
- `## Active Tasks Found`
- `## Decisions Found`
- `## Recommended Roles`
- `## Proposed Archive List`
- `## Proposed Delete List`
- `## User Questions`
- `## User Approval Record`

The approval record starts as:

```markdown
Approved archive list: NO
Approved deletion list: NO
Approved by: <pending>
Approval date: <pending>
```

## Archive Process

1. Scaffold `docs/agent-office/` if missing.
2. Create `docs/agent-office/archive/legacy-management/`.
3. Copy old framework files into dated subfolders only after user approval.
4. Prefer `scripts/archive_legacy.py` for the copy step when the approved report is clear.
5. Use durable archive copies, not symlinks or junctions to external files.
6. Leave original legacy files in place until a separate deletion approval is recorded.
7. Leave a short index file explaining where each legacy item came from.
8. Update `status.md`, `thread-registry.md`, task packets, and ADRs with durable facts.

Archive helper:

```bash
python agent-office-os/scripts/archive_legacy.py --project-root ./project --dry-run
python agent-office-os/scripts/archive_legacy.py --project-root ./project
```

The helper refuses to run unless `Approved archive list: YES` is an exact approval line in `## User Approval Record`. It never deletes or moves files.

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
