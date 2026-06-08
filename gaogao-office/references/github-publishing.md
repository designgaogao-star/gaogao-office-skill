# GitHub Publishing

Use this reference when preparing GaoGao Office for public release.

## Repository Layout

```text
gaogao-office-skill/
  gaogao-office/
    SKILL.md
    agents/openai.yaml
    references/
    scripts/
  README.md
  README.zh-CN.md
  LICENSE
  examples/
  docs/
```

## Local Install

Copy `gaogao-office/` into the Codex skills directory:

```powershell
$dest = "$env:USERPROFILE\.codex\skills\gaogao-office"
Copy-Item -Recurse .\gaogao-office $dest
```

Restart Codex after installing or updating.

If `agent-office-os` is still installed, back it up or remove it so both skills do not trigger for the same project-office request.

## Release Checklist

1. Validate the skill with `skill-creator` quick validation.
2. Run Python compile for all scripts.
3. Run the package gate and zip gate.
4. Check that generated paths use `Agent Office/` and do not use the old v0.1 nested office path.
5. Check that root `AGENTS.md` is proposal-first unless the current reply option explicitly authorized formal takeover.
6. Stage only intended files:
   ```bash
   git add README.md README.zh-CN.md LICENSE .gitignore docs examples gaogao-office
   ```
7. Commit and tag:
   ```bash
   git commit -m "Release gaogao office v0.2.3"
   git tag v0.2.3
   ```

## Suggested Release Notes

```md
# GaoGao Office v0.2.3

Practical takeover, capacity-aware dispatch, and final-answer refinement.

Highlights:
- skill renamed to `$gaogao-office` with display name GaoGao Office
- generated project folder is `Agent Office/`
- public files live directly in `Agent Office/`
- each role gets one private folder under `Agent Office/Employees/`
- root `AGENTS.md` is proposed first and applied only after the current reply option authorizes it
- first-use takeover uses plain A/B/C/D replies
- direction planning moves to post-takeover direction-advisor mode
- project managers throttle employee dispatch based on local capacity
- final-answer preflight prevents internal draft leakage
- migration starts with full filename scanning and candidate text reads
- old `vibe/` and planning files are absorbed before archive or move
- approved old knowledge archives to `Agent Office/Archive/Old Project Memory/`
```
