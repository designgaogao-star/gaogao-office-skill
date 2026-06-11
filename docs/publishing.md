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
git commit -m "Release gaogao office v1.0.1"
```

## 3. Tag

```bash
git tag v1.0.1
git push origin main
git push origin v1.0.1
```

## 4. Zip Asset

The release asset should be `outputs/gaogao-office-skill.zip` from the parent workspace. Rebuild it before release and verify the full gate says `zip content matches package`.

## 5. Release Notes

```md
# GaoGao Office v1.0.1

Focused employee-report return patch for the stable office-collaboration release.

Highlights:
- employees now have an explicit upward report transport
- after real work, employees update `memory.md` and `current-task.md` before reporting
- employee reports prefer `send_message_to_thread` to a confirmed project-director thread ID
- if thread tools or the director thread ID are unavailable, employees output a copyable report instead of pretending it was sent
- v1.0.0 offices validate with a warning and can be upgraded without rebuilding employee memory
- no change to the lightweight `Agent Office/` structure
```

## 6. GitHub Release

Upload `outputs/gaogao-office-skill.zip` as the release asset for `v1.0.1`.

## 7. Install Prompt

After publishing, users can ask Codex:

```text
Install the skill from https://github.com/designgaogao-star/gaogao-office-skill and restart Codex after installation.
```
