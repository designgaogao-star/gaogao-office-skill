# Publishing GAOGAO Office

## 1. Validate

Run the gate from the workspace root:

```bash
python work/run_gaogao_office_gate.py --workspace .
```

## 2. Commit

From the package repository:

```bash
git status --short
git add README.md README.zh-CN.md LICENSE .gitignore docs examples gaogao-office
git commit -m "Release gaogao office v0.2.0"
```

## 3. Tag

```bash
git tag v0.2.0
git push origin main
git push origin v0.2.0
```

## 4. Release Notes

```md
# GAOGAO Office v0.2.0

Lightweight public/private Agent Office redesign.

Highlights:
- skill renamed to `$gaogao-office` with display name GAOGAO Office
- generated project folder is `Agent Office/`
- public files live directly in `Agent Office/`
- each role gets one private folder under `Agent Office/Employees/`
- root `AGENTS.md` is proposed first and applied only after `确认应用 AGENTS.md`
- migration starts with full filename scanning and candidate text reads
- old `vibe/` and planning files are absorbed before archive or move
- approved legacy files archive to `Agent Office/Archive/Legacy Management/`
```

## 5. Install Prompt

After publishing, users can ask Codex:

```text
Install the skill from https://github.com/<owner>/gaogao-office-skill and restart Codex after installation.
```
