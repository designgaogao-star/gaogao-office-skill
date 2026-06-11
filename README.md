# GaoGao Office Skill

`gaogao-office` is a Codex skill for creating, migrating, and maintaining a lightweight `Agent Office/` inside long-running agent-assisted projects.

It treats the current chat as the founding project director, renames that chat to its job title when Codex Desktop allows it, proposes an organization, and invites employees only after formal takeover. In multi-employee mode, the user can keep talking to that one project-director chat while it judges each request, routes employee-owned work to the right thread according to local capacity, receives employee reports, waits for dependencies, and advances according to the user's A/B/C progress mode.

v1.0.0 is the first stable collaboration release: centralized project-director dispatch, fixed employee reports, task-title-first continuation, progress expectations before work starts, and A/B/C manual, semi-automatic, or automatic progress until the next user checkpoint.

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

## Common Commands

| Command | Purpose |
|---|---|
| `help` | Show the capability manual without scanning or writing |
| `checkup` | Inspect the current project read-only |
| `take over` | Start the formal takeover proposal |
| `migrate` | Absorb old project memory and propose migration |
| `health check` | Audit an existing office |
| `continue` / `ok` / `proceed` | Continue the current task from context |
| `automatic progress to checkpoint` | Let the project director continue until the next user checkpoint |
| `stop automatic progress` | Stop automatic progress or heartbeat |
| `retire role` | Downsize or retire employee routes |

## Local Install

From the repository root:

```powershell
$dest = "$env:USERPROFILE\.codex\skills\gaogao-office"
if (Test-Path $dest) {
  $backupRoot = "$env:USERPROFILE\.codex\skill-backups\gaogao-office"
  New-Item -ItemType Directory -Force $backupRoot | Out-Null
  $backup = Join-Path $backupRoot "gaogao-office-$(Get-Date -Format yyyyMMdd-HHmmss)"
  Move-Item -LiteralPath $dest -Destination $backup
  Write-Host "Backed up existing install to $backup"
}
New-Item -ItemType Directory -Force "$env:USERPROFILE\.codex\skills" | Out-Null
Copy-Item -Recurse .\gaogao-office $dest
```

Restart Codex after installing or updating.

If `agent-office-os` is still installed, move it outside `.codex\skills` or remove it so both skills do not respond to the same request.

## Usage

New project:

```text
Use $gaogao-office to inspect this project read-only and propose an Agent Office organization. Start immediately; if you cannot infer the project purpose, ask one short question. Wait for my A/B/C/D choice before creating files. A should be the recommended formal takeover mode, B the other formal takeover mode, C custom team, and D later without writing. After takeover, ask whether I want direction-advisor mode.
```

Capability manual:

```text
Use $gaogao-office help to explain what you can do. Do not scan the project or write files.
```

Existing project migration:

```text
Use $gaogao-office to take over this old project. Scan filenames, inspect likely old-knowledge docs, propose an organization, and let the current chat act as project director. Do not invite employees until formal takeover is complete.
```

Upgrade an existing office after updating the skill:

```text
Use $gaogao-office to inspect the existing Agent Office in this project. Do not delete or rebuild blindly. Tell me what will be kept, what stale entrances will be archived, and what needs to be upgraded. Wait for my current reply option before updating it to the current GaoGao Office workflow.
```

In Codex Desktop, approved employees can be created automatically. After onboarding, the project director first judges who should own each request: clear employee-owned work is dispatched, small office work is handled directly, and ambiguous direction gets one brief clarification. Before long work starts, it states expected steps, participating employees, and the next user checkpoint, then asks for A/B/C: A manual progress, B semi-automatic progress, C automatic progress until the checkpoint. C mode may create or update a heartbeat when automation tools are available. If thread or automation tools are unavailable, the skill falls back to copyable onboarding prompts and manual dispatch messages.

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
