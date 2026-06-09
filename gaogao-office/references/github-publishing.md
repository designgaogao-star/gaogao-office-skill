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
   git commit -m "Release gaogao office v0.2.6"
   git tag v0.2.6
   ```
8. Push and create the GitHub release with `outputs/gaogao-office-skill.zip` as the release asset.

## Suggested Release Notes

```md
# GaoGao Office v0.2.6

Adds a stateful operation router so project managers classify lifecycle state, authorization level, and task ownership before writing, dispatching, watching progress, or maintaining an office.

Highlights:
- generated project folder is `Agent Office/`
- new `operation-router.md` reference covers command routing, lifecycle states, authorization levels, and project-manager self-checks
- A/B/C/D takeover choices are dynamic: A is the recommended mode, B is the other formal mode
- A/B/C/D are reserved for authorization choices; 1/2/3 are reserved for informational continuation paths
- Chinese output respects the user's preferred address and does not force `BOSS`
- single `$gaogao-office` invocation starts the read-only checkup directly
- first-use Mermaid roadmap is shorter and easier to scan
- root `AGENTS.md` is proposal-first and applied only after the current reply option authorizes it
- direction planning moves to post-takeover direction-advisor mode
- project-manager dispatch is non-blocking by default and watch mode remains opt-in
- migration starts with full filename scanning and candidate text reads
- legacy archive rejects active office, dependency, build, cache, and project-root paths
- approved old knowledge archives to `Agent Office/Archive/Old Project Memory/`
```
