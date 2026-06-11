# Publishing GaoGao Office

Publish only after the local install has passed real project testing. Do not tag, zip, or create a GitHub release just because the local skill changed.

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
git commit -m "Release gaogao office v1.0.0"
```

## 3. Tag

```bash
git tag v1.0.0
git push origin main
git push origin v1.0.0
```

## 4. Zip Asset

The release asset should be `outputs/gaogao-office-skill.zip` from the parent workspace. Rebuild it before release and verify the full gate says `zip content matches package`.

## 5. Release Notes

```md
# GaoGao Office v1.0.0

First stable office-collaboration release for long-running AI agent projects.

Highlights:
- the current chat acts as project director for centralized dispatch
- employees report back with a fixed employee-report shape
- user-facing task continuation uses task titles and short natural replies instead of internal IDs
- long work starts with expected steps, participating employees, and the next user checkpoint
- A/B/C progress modes support manual, semi-automatic, or automatic progress until checkpoint
- automatic heartbeat is opt-in and never authorizes risky actions
- no change to the lightweight `Agent Office/` structure
```

## 6. GitHub Release

Upload `outputs/gaogao-office-skill.zip` as the release asset for `v1.0.0`.

## 7. Install Prompt

After publishing, users can ask Codex:

```text
Install the skill from https://github.com/designgaogao-star/gaogao-office-skill and restart Codex after installation.
```
