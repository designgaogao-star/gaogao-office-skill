# GitHub Publishing Guide

Use this reference when preparing the skill for public release.

## Table of Contents

- Repository Layout
- Local Install
- Install From GitHub
- Release Checklist
- Suggested Release Notes

## Repository Layout

Recommended repository name: `agent-office-os-skill`

```text
agent-office-os-skill/
  agent-office-os/
    SKILL.md
    agents/openai.yaml
    references/
    scripts/
  examples/
  docs/
  README.md
  README.zh-CN.md
  LICENSE
  .gitignore
```

## Local Install

Prefer `$skill-installer` after publishing. For manual install, stop if the destination already exists.

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

## Install From GitHub

After publishing, paste this into Codex chat:

```text
$skill-installer https://github.com/<owner>/agent-office-os-skill/tree/main/agent-office-os
```

## Release Checklist

1. Validate the skill:
   ```bash
   python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py ./agent-office-os
   ```
2. Run a real smoke test:
   ```bash
   mkdir demo-project
   python agent-office-os/scripts/scaffold_office.py --project-root ./demo-project --project-name Demo
   python agent-office-os/scripts/inspect_office.py --project-root ./demo-project
   python agent-office-os/scripts/validate_office.py --project-root ./demo-project
   ```
3. Review and remove `demo-project` manually.
4. Check for unsafe deletion commands and local secrets.
5. Stage only the intended files:
   ```bash
   git add README.md README.zh-CN.md LICENSE .gitignore docs examples agent-office-os
   git status --short
   git diff --cached
   ```
6. Commit:
   ```bash
   git commit -m "Release agent-office-os skill"
   ```
7. Push and tag:
   ```bash
   git push origin main
   git tag v0.1.2
   git push origin v0.1.2
   ```
8. Create a GitHub release with:
   - what the skill does
   - install instructions
   - safety note: archive-before-delete migration
   - known limitations

## Suggested Release Notes

```md
# Agent Office OS v0.1.2

First-use experience update for Agent Office OS.

Highlights:
- lightweight chat consultation before scaffolding
- read-only project inference before asking questions
- explicit approval gate before file creation
- dynamic role generation from project context
- Chinese document and role prompt generation
- new project office scaffolding
- project brief and thread-launch prompts for long-running agent roles
- communication protocol for cross-role messages and handoffs
- old project migration playbook
- task, message, handoff, and ADR templates
- safe audit, archive-copy, and validation scripts
```
