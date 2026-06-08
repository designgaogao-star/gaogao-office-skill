# Migration Playbook

Use this when taking over an old or long-running project.

## Principles

- Full-scan filenames first; do not full-read the whole project.
- Read only relevant text candidates.
- Do not content-read images, media, binary files, sensitive-looking files, dependencies, build output, caches, virtualenvs, `.git`, or linked external paths.
- Absorb durable facts into current `Agent Office/` files before archive, move, or delete actions.
- Keep root `AGENTS.md` unchanged by default. Generate `Agent Office/Proposals/AGENTS.proposed.md` first.
- Move old files only after separate exact-list approval.
- Delete old files only after separate exact-list deletion approval.

## Discovery Targets

Look for:

- `AGENTS.md`, `AGENTS.override.md`, `CLAUDE.md`, `GEMINI.md`, `.cursorrules`
- `vibe/`, `VIBE.md`, context notes, project memory folders
- README, roadmap, planning, task, copy, architecture, ADR, status, meeting, handoff files
- `.codex/`, `.agents/`, `.github/`, issue templates, automation notes

Skip generated or dependency directories:

- `.git`, `node_modules`, `vendor`, `dist`, `build`, `target`, `.venv`, `venv`, `__pycache__`, `.cache`

## Migration Report

Create `Agent Office/migration-report.md` with these second-level headings:

- `## Project Map`
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

## Absorption Map

Map old content to new destinations:

| Old content | New destination |
|---|---|
| current goal, phase, blockers | `Agent Office/status.md` |
| active tasks, owners, reviewers | `Agent Office/task-board.md` |
| old project vibe and background | `Agent Office/project-brief.md` and `Agent Office/project-map.md` |
| file inventory and material map | `Agent Office/project-map.md` |
| accepted decisions | `Agent Office/decisions.md` |
| open questions and handoffs | `Agent Office/communication.md` |
| role-specific continuity | `Agent Office/Employees/{role-slug}/memory.md` only when explicitly role-specific |
| durable agent rules | `Agent Office/Proposals/AGENTS.proposed.md` |

Do not copy old documents wholesale into public files. Extract durable facts, cite source paths, and mark uncertainty as user questions.

## AGENTS Replacement

When root `AGENTS.md` already exists:

1. Preserve still-valid build, test, safety, review, and office-entry rules.
2. Write the replacement draft to `Agent Office/Proposals/AGENTS.proposed.md`.
3. Keep the draft short and index-like.
4. Tell the user they can manually copy it over `AGENTS.md`.
5. Apply it yourself only after the user says `确认应用 AGENTS.md`.
6. Create a dated backup before overwriting.

## Archive And Move

Default archive flow:

```bash
python gaogao-office/scripts/archive_legacy.py --project-root ./project --dry-run
python gaogao-office/scripts/archive_legacy.py --project-root ./project
```

The helper requires `Approved archive list: YES` and copies files to `Agent Office/Archive/Legacy Management/<date>/`.

Optional move flow:

```bash
python gaogao-office/scripts/archive_legacy.py --project-root ./project --move-originals --dry-run
python gaogao-office/scripts/archive_legacy.py --project-root ./project --move-originals
```

Move requires both `Approved archive list: YES` and `Approved legacy move list: YES`. The archive is human-review/audit material; ordinary employees should not read it.

## Conflict Handling

- Keep current build/test/security warnings until a domain owner rejects them.
- Mark uncertain facts as questions in the migration report.
- If old files conflict, ask the user which source is authoritative before treating either as truth.
