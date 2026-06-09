# Maintenance Playbook

Use this when auditing or cleaning an existing `Agent Office/`.

If the user has updated the skill and runs it again in a project that already has `Agent Office/`, treat that as an office upgrade/re-takeover request, not a fresh initialization.

For user-visible maintenance, follow `references/markdown-output-guide.md`: use task lists for health checks and retirement summaries, tables for stale-entry maps, and warning blocks for deletion or move risks.

## Default Mode

Start read-only. Produce a maintenance report before cleanup edits unless the user explicitly requested safe cleanup.

## Check

- public files that are too long or stale
- `office-plan.json` missing the current `office_schema_version` or `collaboration_mode`
- `task-board.md` tasks missing owner, reviewer, write scope, status, or verification
- `communication.md` messages or handoffs that are unresolved
- `thread-registry.md` entries that are missing thread IDs, stale, retired, or still waiting
- whether controller-dispatch is still true: user requests should enter through the project manager by default, and employee threads should have current task/memory updates
- employee folders missing `README.md`, `memory.md`, or `current-task.md`
- employee `memory.md` files that are too long, stale, or contain shared facts that belong in public files
- `decisions.md` entries that are superseded or unresolved
- old v0.1 nested office layout

## Cleanup Rules

- Do not read employee folders during ordinary health checks except for existence, size, and freshness.
- Read employee memory contents only when the user explicitly asks for maintenance, audit, or recovery.
- Do not read `Archive/Old Project Memory/` unless the task is migration absorption, missing-fact audit, or restore.
- Move detail out of public files when they exceed budget; keep public files short.
- Do not delete office history unless the user approves an exact deletion list.

## Team Retirement / Downsizing

Use this when the user asks to withdraw employees, remove the team, switch back to one chat, cancel a direction, or archive employee windows.

If the request is clear, this is a safe maintenance action: preserve records, archive/retire the employee routes, and stop dispatch. Ask a follow-up only when the user might mean deletion rather than retirement.

Rules:

- Do not delete employee folders or historical task results by default.
- Do not change a completed task to `cancelled`. Completed work remains `done`; future, proposed, waiting, or active tasks may become `cancelled`.
- Update `thread-registry.md` so retired employees show `archived` or `withdrawn` and have no active write scope.
- If Codex thread tools are available, archive the retired employee threads after the user clearly asked to withdraw the team.
- Update each retired employee's `current-task.md` with a withdrawal note, and append a short `memory.md` Work Log entry so a future reactivation can understand what happened.
- Update project-manager `memory.md`, `status.md`, `task-board.md`, `communication.md`, and `decisions.md`.
- Add or preserve an `AGENTS.md` rule that archived/withdrawn employees must not receive new dispatches unless the user explicitly reactivates them.
- Keep useful work products in place if they are still reference material; move them to `Agent Office/Archive/Old Project Memory/` only when the user says the old direction itself is obsolete.

Good closing style:

```md
**撤岗完成**

- [x] 员工线程已归档
- [x] 未来任务已取消
- [x] 已完成任务保持 `done`
- [x] 员工资料没有删除
- [x] 当前只保留项目总管窗口待命

> 已归档员工不会再收到派工；如果以后要恢复，需要用户明确重新启用。
```

## Safe Cleanup Order

1. Run `validate_office.py`.
2. Read only files named by findings.
3. Update `status.md` and `task-board.md` with current truth if needed.
4. Resolve stale entries in `communication.md`.
5. Update `thread-registry.md`.
6. Ask owning roles to update their own `memory.md`, or edit only with explicit authorization.
7. Record cleanup summary in `communication.md`.

## Upgrade / Re-Takeover

When upgrading an existing office:

1. Start read-only and tell the user the old office will not be deleted automatically.
2. Summarize current public truth and employee memories that must survive.
3. Propose what to refresh, what to archive, and what to leave alone.
4. Ask for A/B/C/D approval before overwriting active office files.
5. Preserve or archive retired employee folders instead of deleting them.
6. Rebuild current templates only after approval, then run validation again.

Use this wording when helpful:

```text
这里已经有一个 Agent Office。
我不会直接删掉重来；我会先把旧办公室里有用的记忆吸收进新版结构，再把过期入口归档。
你拍板后，我再更新 active office。
```

Use a warning block before any deletion or original-file move:

```md
> [!WARNING]
> 这一步会移动或删除文件。执行前必须列出精确清单；没有用户明确批准时，只能归档，不能删除。
```
