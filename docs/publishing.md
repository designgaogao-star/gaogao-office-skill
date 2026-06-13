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
git commit -m "Release gaogao office v1.0.4"
```

## 3. Tag

```bash
git tag v1.0.4
git push origin main
git push origin v1.0.4
```

## 4. Zip Asset

The release asset should be `outputs/gaogao-office-skill.zip` from the parent workspace. Rebuild it before release and verify the full gate says `zip content matches package`.

## 5. Release Notes

Use `docs/release-notes-v1.0.4.md` as the GitHub release body. The release page should show Chinese by default and keep English in a collapsed `<details>` section.

## 6. GitHub Release

Upload `outputs/gaogao-office-skill.zip` as the release asset for `v1.0.4`.

## 7. Install Prompt

After publishing, users can ask Codex:

```text
Install the skill from https://github.com/designgaogao-star/gaogao-office-skill and restart Codex after installation.
```
