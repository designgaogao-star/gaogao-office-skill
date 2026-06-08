# Agent Office OS Skill

`agent-office-os` is an agent-readable skill for creating, migrating, and maintaining a durable project office for large agent-assisted projects.

It helps a project keep agent context small while still supporting long-running work, role-based threads, task packets, handoffs, messages, ADRs, and safe migration from older planning frameworks.

The package is optimized for Codex installation, but the core workflow is plain Markdown plus Python helper scripts. Other coding agents can use it by reading `agent-office-os/SKILL.md` and following the generated `docs/agent-office/` office.

## What It Does

- Initializes a new `docs/agent-office/` workspace.
- Writes a short `AGENTS.md` entrypoint.
- Records project type, risk level, first milestone, and role decisions in `context-packs/project-brief.md`.
- Creates role cards for PM, Architect, Builder, Reviewer, Archivist, and optional specialists.
- Creates task, message, handoff, and decision workflows.
- Creates `communication.md` so role threads know how to open, answer, close, and hand off cross-role work.
- Audits old project-management files before migration.
- Archives old frameworks before any deletion.
- Writes `context-packs/thread-launch-prompts.md` with one starter prompt per long-running agent role.
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
Use $agent-office-os to initialize this project as a new Agent Office OS workspace.
```

or:

```text
Use $agent-office-os to inspect this old project, migrate its planning docs into an Agent Office OS, and archive the old framework before any deletion.
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

After scaffolding, review `demo-project/docs/agent-office/context-packs/project-brief.md`, `demo-project/docs/agent-office/communication.md`, then open `demo-project/docs/agent-office/context-packs/thread-launch-prompts.md` and create the recommended long-running agent threads. Record each returned thread ID in `docs/agent-office/thread-registry.md`.

After a migration report is reviewed and `Approved archive list: YES` is recorded in `User Approval Record`, copy approved legacy files with:

```bash
python agent-office-os/scripts/archive_legacy.py --project-root ./old-project --dry-run
python agent-office-os/scripts/archive_legacy.py --project-root ./old-project
```

Safety defaults:

- `scaffold_office.py` never deletes files and skips existing files unless `--force` is provided.
- `scaffold_office.py` requires `--create-root` to create a missing project root and requires `--confirm-overwrite` with `--force`.
- `scaffold_office.py` refuses linked paths that would resolve outside the selected project root.
- `inspect_office.py` is read-only unless you pass `--output`, output must stay inside the project root, and linked paths are skipped without reading external content.
- `archive_legacy.py` copies only an explicitly approved archive list, refuses linked or sensitive-looking paths, and never deletes originals.
- `validate_office.py` reports structure and health issues without modifying files.

## Publishing

See [docs/publishing.md](docs/publishing.md) for step-by-step GitHub release instructions.

## License

Apache-2.0. See [LICENSE](LICENSE).
