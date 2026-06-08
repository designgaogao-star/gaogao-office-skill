# GAOGAO Office Skill

`gaogao-office` is a Codex skill for creating, migrating, and maintaining a lightweight `Agent Office/` inside long-running agent-assisted projects.

It keeps shared project truth in a public office area and gives each long-running role its own private-by-protocol employee folder.

## When To Use It

Use it for real project folders that will continue over time: software projects, portfolio sites, brand planning, research projects, product launches, or cleanup of old agent/planning frameworks.

Do not use it for short one-off questions or unrelated multi-task chats.

## What It Creates

```text
Agent Office/
  README.md
  status.md
  project-brief.md
  project-map.md
  task-board.md
  communication.md
  decisions.md
  thread-registry.md
  office-plan.json
  Proposals/
    AGENTS.proposed.md
  Employees/
    role-slug/
      README.md
      memory.md
      current-task.md
  Archive/
    Legacy Management/
```

Root `AGENTS.md` is not written by default. The skill writes `Agent Office/Proposals/AGENTS.proposed.md` first. Codex applies it only after the user says `确认应用 AGENTS.md`.

## Local Install

From the repository root:

```powershell
$dest = "$env:USERPROFILE\.codex\skills\gaogao-office"
if (Test-Path $dest) { throw "Skill already exists at $dest. Back it up or remove it first." }
New-Item -ItemType Directory -Force "$env:USERPROFILE\.codex\skills" | Out-Null
Copy-Item -Recurse .\gaogao-office $dest
```

Restart Codex after installing or updating.

If `agent-office-os` is still installed, back it up or remove it so both skills do not respond to the same request.

## Usage

New project:

```text
Use $gaogao-office to inspect this project read-only and propose a lightweight Agent Office. Do not create files until I approve the plan.
```

Existing project migration:

```text
Use $gaogao-office to inspect this old project, scan filenames, absorb old planning/vibe docs into Agent Office, propose AGENTS.md, and archive absorbed legacy files only after approval.
```

Apply root `AGENTS.md` after reviewing the proposal:

```text
确认应用 AGENTS.md
```

## Helper Scripts

- `scripts/scaffold_office.py`: creates `Agent Office/` and employee folders.
- `scripts/inspect_office.py`: read-only filename map and migration report.
- `scripts/archive_legacy.py`: copies approved legacy files; moves originals only with separate move approval.
- `scripts/validate_office.py`: checks structure, role folders, budgets, and migration safety.

## Publishing

Recommended repository name: `gaogao-office-skill`.

License: Apache-2.0.
