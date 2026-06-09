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
git commit -m "Release gaogao office v0.2.6"
```

## 3. Tag

```bash
git tag v0.2.6
git push origin main
git push origin v0.2.6
```

## 4. Zip Asset

The release asset should be `outputs/gaogao-office-skill.zip` from the parent workspace. Rebuild it before release and verify the full gate says `zip content matches package`.

## 5. Release Notes

```md
# GaoGao Office v0.2.6

Polished takeover choices, neutral user addressing, and safer legacy archiving.

Highlights:
- current chat becomes the founding project manager
- users choose dynamic A/B/C/D takeover style: A is recommended, B is the other formal mode
- Chinese output respects the user's preferred address and no longer forces `BOSS`
- first-use roadmap is shorter and easier to scan
- legacy archive paths reject active office, dependency, build, cache, and root paths
- publishing and install docs now match the current workflow
- direction planning moves to post-takeover direction-advisor mode
- employees use human job titles and onboarding language
- Codex Desktop can create employee threads automatically after approval
- project managers throttle employee dispatch based on local capacity
- absorbed old knowledge archives to `Agent Office/Archive/Old Project Memory/`
```

## 6. GitHub Release

Upload `outputs/gaogao-office-skill.zip` as the release asset for `v0.2.6`.

## 7. Install Prompt

After publishing, users can ask Codex:

```text
Install the skill from https://github.com/designgaogao-star/gaogao-office-skill and restart Codex after installation.
```
