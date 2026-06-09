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
git commit -m "Release gaogao office v0.2.9"
```

## 3. Tag

```bash
git tag v0.2.9
git push origin main
git push origin v0.2.9
```

## 4. Zip Asset

The release asset should be `outputs/gaogao-office-skill.zip` from the parent workspace. Rebuild it before release and verify the full gate says `zip content matches package`.

## 5. Release Notes

```md
# GaoGao Office v0.2.9

Small experience cleanup for Chinese office wording, runtime metadata, and generated state values.

Highlights:
- Chinese offices now use `项目总监` for the founding project-manager role
- current-window employees record `status: current-window` instead of a job title
- `agents/openai.yaml` default prompt is shorter and less repetitive
- runtime skill references no longer include publishing-only notes
- project inspection skips `Agent Office/` case-insensitively
- no change to the lightweight `Agent Office/` structure
```

## 6. GitHub Release

Upload `outputs/gaogao-office-skill.zip` as the release asset for `v0.2.9`.

## 7. Install Prompt

After publishing, users can ask Codex:

```text
Install the skill from https://github.com/designgaogao-star/gaogao-office-skill and restart Codex after installation.
```
