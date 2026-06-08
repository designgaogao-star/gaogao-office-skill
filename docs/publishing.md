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
git commit -m "Release gaogao office v0.2.3"
```

## 3. Tag

```bash
git tag v0.2.3
git push origin main
git push origin v0.2.3
```

## 4. Release Notes

```md
# GaoGao Office v0.2.3

Practical takeover, capacity-aware dispatch, and final-answer refinement.

Highlights:
- current chat becomes the founding project manager
- users choose first-use takeover style with plain A/B/C/D replies
- direction planning moves to post-takeover direction-advisor mode
- employees use human job titles and onboarding language
- Codex Desktop can create employee threads automatically after approval
- project managers throttle employee dispatch based on local capacity
- final-answer preflight prevents internal draft leakage
- absorbed old knowledge archives to `Agent Office/Archive/Old Project Memory/`
```

## 5. Install Prompt

After publishing, users can ask Codex:

```text
Install the skill from https://github.com/<owner>/gaogao-office-skill and restart Codex after installation.
```
