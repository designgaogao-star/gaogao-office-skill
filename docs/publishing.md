# Publishing Guide

This guide shows how to publish `agent-office-os-skill` on GitHub safely.

## 1. Create the Repository

1. Open GitHub.
2. Create a new public repository named `agent-office-os-skill`.
3. Do not add a README or license in GitHub if these files already exist locally.

## 2. Validate Before Commit

From the folder that contains `README.md` and `agent-office-os/`, run a real smoke test in a disposable demo directory:

```bash
mkdir demo-project
python agent-office-os/scripts/scaffold_office.py --project-root ./demo-project --project-name Demo
python agent-office-os/scripts/inspect_office.py --project-root ./demo-project
python agent-office-os/scripts/validate_office.py --project-root ./demo-project
```

Validate the skill frontmatter:

macOS/Linux:

```bash
python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py ./agent-office-os
```

PowerShell:

```powershell
python "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" .\agent-office-os
```

Review and remove the disposable `demo-project` directory manually after checking it.

## 3. Check What Will Be Published

Run:

```bash
git status --short
git diff -- README.md README.zh-CN.md LICENSE docs examples agent-office-os .gitignore
```

Do not publish secrets, local caches, private project files, or generated smoke-test directories.

## 4. Commit Locally

```bash
git init
git add README.md README.zh-CN.md LICENSE .gitignore docs examples agent-office-os
git status --short
git diff --cached
git commit -m "Initial release of agent-office-os skill"
```

Review `git status --short` and `git diff --cached` before committing. The staged files should be only the skill package and release docs.

## 5. Connect Remote

Replace `<owner>` with your GitHub username or organization, then confirm the URL is correct before pushing.

```bash
git branch -M main
git remote add origin https://github.com/<owner>/agent-office-os-skill.git
git remote -v
git push -u origin main
```

## 6. Tag a Release

```bash
git tag v0.1.0
git push origin v0.1.0
```

In GitHub, create a release for `v0.1.0`.

Suggested release notes:

```md
# Agent Office OS v0.1.0

Initial release of an Agent Office OS skill for initializing, migrating, and maintaining a durable project office.

Includes:
- project office scaffolding
- project brief and thread-launch prompts for long-running agent roles
- communication protocol for cross-role messages and handoffs
- old project migration playbook
- role cards for PM, Architect, Builder, Reviewer, and Archivist
- task, message, handoff, and ADR templates
- safe inspection, archive-copy, and validation scripts
```

## 7. Installation Link

After publishing, users can paste this into Codex chat:

```text
$skill-installer https://github.com/<owner>/agent-office-os-skill/tree/main/agent-office-os
```

## 8. Maintenance

For future versions:

1. Update the skill.
2. Run validation and smoke tests.
3. Stage only intended files.
4. Commit changes.
5. Tag a new version such as `v0.2.0`.
6. Update the GitHub release notes.
