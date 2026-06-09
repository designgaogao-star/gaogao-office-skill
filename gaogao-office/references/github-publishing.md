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
if (Test-Path $dest) {
  $backup = "$dest.backup-$(Get-Date -Format yyyyMMdd-HHmmss)"
  Move-Item -LiteralPath $dest -Destination $backup
  Write-Host "Backed up existing install to $backup"
}
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
   git commit -m "Release gaogao office v0.2.8"
   git tag v0.2.8
   ```
8. Push and create the GitHub release with `outputs/gaogao-office-skill.zip` as the release asset.

## Suggested Release Notes

```md
# GaoGao Office v0.2.8

Release-readiness safety update for project scanning, path handling, and office writes.

Highlights:
- office writes now refuse symlink or junction targets
- project inspection prunes skipped directories before traversal
- relative report paths resolve inside the selected project root
- inspect, archive, and validate scripts reject unsafe project roots
- Chinese and English budget checks now use mixed budget units
- no change to the lightweight `Agent Office/` structure
```
