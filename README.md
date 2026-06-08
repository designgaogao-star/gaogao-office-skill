# Agent Office OS Skill

`agent-office-os` is an agent-readable skill for creating, migrating, and maintaining a durable project office for large agent-assisted projects.

It helps a project keep agent context small while still supporting long-running work, role-based threads, per-role memory, task packets, handoffs, messages, ADRs, and safe migration from older planning frameworks.

The package is optimized for Codex installation, but the core workflow is plain Markdown plus Python helper scripts. Other coding agents can use it by reading `agent-office-os/SKILL.md` and following the generated `docs/agent-office/` office.

## When To Use It

Use Agent Office OS for long-running work anchored in one durable project folder: product planning, brand strategy, software builds, research-heavy projects, or old projects that need cleanup and continuity.

Do not use it for a quick standalone question or unrelated one-off tasks in separate chats. The setup has an upfront token cost; the payoff is lower repeated reorientation when a project runs for weeks or months, spans multiple role windows, or survives context compaction.

## What It Does

- Starts with a lightweight chat consultation and read-only project inspection.
- Confirms the project purpose or asks concise numbered questions before writing files.
- Initializes a new `docs/agent-office/` workspace only after explicit approval.
- Writes a short `AGENTS.md` entrypoint for new projects; for migrations with an existing `AGENTS.md`, writes `docs/agent-office/proposals/AGENTS.proposed.md` first.
- Records project type, risk level, first milestone, and dynamic role decisions in `context-packs/project-brief.md`.
- Creates role cards based on the actual project rather than a fixed template.
- Creates one protocol-private `role-memory/{role}.md` file per approved role so replacement chat windows can continue the same role.
- Creates task, message, handoff, and decision workflows.
- Creates `communication.md` so role threads know how to open, answer, close, and hand off cross-role work.
- Audits and absorbs old project-management files before migration, including `vibe/`-style project memory folders.
- Archives old frameworks for human review before any optional move or deletion.
- Writes `context-packs/thread-launch-prompts.md` with one copyable starter prompt per approved long-running agent role.
- Provides safe helper scripts for scaffolding, inspection, and validation.

## Install Locally

Recommended for Codex: install from GitHub with `$skill-installer` after publishing. For manual local install, run these commands from the repository root and do not overwrite an existing installed copy.

PowerShell:

```powershell
$dest = "$env:USERPROFILE\.codex\skills\agent-office-os"
if (Test-Path $dest) { throw "Skill already exists at $dest. Back it up or remove it first." }
New-Item -ItemType Directory -Force "$env:USERPROFILE\.codex\skills" | Out-Null
Copy-Item -Recurse .\agent-office-os $dest
```

macOS/Linux:

```bash
dest="$HOME/.codex/skills/agent-office-os"
test -e "$dest" && { echo "Skill already exists at $dest. Back it up or remove it first."; exit 1; }
mkdir -p "$HOME/.codex/skills"
cp -R ./agent-office-os "$dest"
```

Restart Codex after installing or updating the skill.

Then ask Codex:

```text
Use $agent-office-os to inspect this project read-only, infer what it is, ask me concise numbered questions, propose dynamic agent roles, and wait for my approval before creating files.
```

or:

```text
Use $agent-office-os to inspect this old project, absorb its old planning/vibe docs into Agent Office OS, propose a merged AGENTS.md replacement, and archive absorbed legacy files before any optional move or deletion.
```

## Install From GitHub

After this repository is published, install it with:

Paste this into Codex chat:

```text
$skill-installer https://github.com/<owner>/agent-office-os-skill/tree/main/agent-office-os
```

Replace `<owner>` with your GitHub username or organization.

## Helper Scripts

Run scripts from the repository root or from any project root by passing `--project-root`.

```bash
mkdir demo-project
python agent-office-os/scripts/scaffold_office.py --project-root ./demo-project --project-name "My Project" --project-type app --risk-level medium --first-milestone "Ship the first usable workflow"
python agent-office-os/scripts/inspect_office.py --project-root ./demo-project
python agent-office-os/scripts/validate_office.py --project-root ./demo-project --warn-only
```

Quote paths that contain spaces.

For dynamic roles, save an approved `office-plan.json` and run:

```bash
python agent-office-os/scripts/scaffold_office.py --project-root ./demo-project --config ./office-plan.json
```

After scaffolding, review `demo-project/docs/agent-office/context-packs/project-brief.md`, `demo-project/docs/agent-office/communication.md`, then use the prompts printed in chat or saved in `demo-project/docs/agent-office/context-packs/thread-launch-prompts.md` to create the approved long-running agent threads. Each role prompt reads only its own `docs/agent-office/role-memory/{role}.md`; record each returned thread ID in `docs/agent-office/thread-registry.md`.

After a migration report is reviewed and `Approved archive list: YES` is recorded in `User Approval Record`, copy approved legacy files with:

```bash
python agent-office-os/scripts/archive_legacy.py --project-root ./old-project --dry-run
python agent-office-os/scripts/archive_legacy.py --project-root ./old-project
```

If the durable facts were absorbed and the user explicitly records `Approved legacy move list: YES`, originals can be moved into the same archive instead:

```bash
python agent-office-os/scripts/archive_legacy.py --project-root ./old-project --move-originals --dry-run
python agent-office-os/scripts/archive_legacy.py --project-root ./old-project --move-originals
```

Safety defaults:

- `scaffold_office.py` never deletes files and skips existing files unless `--force` is provided.
- `scaffold_office.py` requires `--create-root` to create a missing project root and requires `--confirm-overwrite` with `--force`; confirmed overwrites create `.bak` backups.
- `scaffold_office.py` refuses linked paths that would resolve outside the selected project root.
- `inspect_office.py` is read-only unless you pass `--output`, output must stay inside the project root, and linked paths are skipped without reading external content.
- `archive_legacy.py` copies only an explicitly approved archive list by default, refuses linked or sensitive-looking paths, never deletes originals, and moves originals only with a separate explicit move approval plus `--move-originals`.
- `validate_office.py` reports structure and health issues without modifying files.

## Publishing

See [docs/publishing.md](docs/publishing.md) for step-by-step GitHub release instructions.

## License

Apache-2.0. See [LICENSE](LICENSE).
