# GaoGao Office Skill

`gaogao-office` is a Codex skill for creating, migrating, and maintaining a lightweight `Agent Office/` inside long-running agent-assisted projects.

It treats the current chat as the founding project manager/controller, renames that chat to its job title when Codex Desktop allows it, proposes an organization, and invites employees only after formal takeover. In multi-employee mode, the user can keep talking to that one project-manager chat while it dispatches work to employee threads according to local capacity and reports back.

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
    Old Project Memory/
```

Root `AGENTS.md` is not written until the user approves a current reply option that authorizes formal takeover or AGENTS application. Old knowledge is absorbed before being archived under `Agent Office/Archive/Old Project Memory/`.

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
Use $gaogao-office to inspect this project read-only, tell me what you think it is, and propose an Agent Office organization. Wait for my A/B/C/D choice before creating files. A is recommended-team takeover, B is single-window takeover, C is custom team, and D pauses without writing. After takeover, ask whether I want direction-advisor mode.
```

Existing project migration:

```text
Use $gaogao-office to take over this old project. Scan filenames, inspect likely old-knowledge docs, propose an organization, and let the current chat act as project manager. Do not invite employees until formal takeover is complete.
```

Upgrade an existing office after updating the skill:

```text
Use $gaogao-office to inspect the existing Agent Office in this project. Do not delete or rebuild blindly. Tell me what will be kept, what stale entrances will be archived, and what needs to be upgraded. Wait for my current reply option before updating it to the current GaoGao Office workflow.
```

In Codex Desktop, approved employees can be created automatically. After onboarding, the project manager dispatches work according to local capacity, reads employee replies, and synthesizes the result for the user. If thread tools are unavailable, the skill falls back to copyable onboarding prompts and manual dispatch messages.

## Helper Scripts

- `scripts/scaffold_office.py`: creates `Agent Office/` and employee folders.
- `scripts/inspect_office.py`: read-only filename map and migration report.
- `scripts/archive_legacy.py`: archives approved old-knowledge files; moves originals only with separate move approval.
- `scripts/inspect_capacity.py`: read-only local capacity check for employee dispatch concurrency.
- `scripts/validate_office.py`: checks structure, role folders, budgets, and migration safety.

## Publishing

Recommended repository name: `gaogao-office-skill`.

Do not publish a new release just because the local skill changed. Test the local install in real projects first, then decide whether to tag, zip, and publish.

License: Apache-2.0.
