# Maintenance Playbook

Use this when auditing or cleaning an existing `Agent Office/`.

If the user has updated the skill and runs it again in a project that already has `Agent Office/`, treat that as an office upgrade/re-takeover request, not a fresh initialization.

Before maintenance action, apply `references/operation-router.md`. Existing offices usually enter `maintenance`; if the user asks to use the latest workflow or rerun the skill, enter upgrade/re-takeover inside `maintenance`.

For user-visible maintenance, follow `references/markdown-output-guide.md`: use task lists for health checks and retirement summaries, tables for stale-entry maps, and warning blocks for deletion or move risks.

## Default Mode

Start read-only. Produce a maintenance report before cleanup edits unless the user explicitly requested safe cleanup.

Use a quick maintenance pass first. If `Agent Office/` exists, do not restart the first-use flow. Read public office files, `office-plan.json`, `thread-registry.md`, and only employee metadata needed to preserve memory. Optional validation should use:

```text
validate_office.py --project-root <project> --warn-only
```

If validation is unavailable, noisy, or slow, do not stall. Report the useful findings already collected and mark validation as skipped or inconclusive.

## Check

- public files that are too long or stale
- `office-plan.json` missing the current `office_schema_version` or `collaboration_mode`
- `task-board.md` tasks missing owner, reviewer, write scope, status, or verification
- `communication.md` messages or handoffs that are unresolved
- `thread-registry.md` entries that are missing thread IDs, stale, retired, or still waiting
- whether controller-dispatch is still true: user requests should enter through the project director by default, employees should update current task/memory before reporting, and employee reports should either return via `send_message_to_thread` to a confirmed project-director thread ID or fall back to a copyable report
- whether older offices are missing v1.0.3 collaboration fields: `employee_report_transport`, `employee_report_fallback`, `employee_report_intake`, `role_calibration_policy`, `inter_agent_communication`, project-director thread ID status, file-first report paths, manual-copy fallback wording, and report-intake records
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
- Thread creation, renaming, reading, or archival is a `thread-action`: do it only when Codex Desktop thread tools are available and the user clearly approved that thread action.
- Moving old project files is an `archive-move`: show the exact list before moving originals. Copying approved absorbed old knowledge into archive remains safer than moving originals.
- Deleting files is a `delete` action: require a separate exact deletion list and explicit delete approval.

## Team Retirement / Downsizing

Use this when the user asks to withdraw employees, remove the team, switch back to one chat, cancel a direction, or archive employee windows.

If the request is clear, this is a safe maintenance action: preserve records, archive/retire the employee routes, and stop dispatch. Ask a follow-up only when the user might mean deletion rather than retirement.

Rules:

- Do not delete employee folders or historical task results by default.
- Do not change a completed task to `cancelled`. Completed work remains `done`; future, proposed, waiting, or active tasks may become `cancelled`.
- Update `thread-registry.md` so retired employees show `archived` or `withdrawn` and have no active write scope.
- If Codex thread tools are available, archive the retired employee threads after the user clearly asked to withdraw the team.
- Update each retired employee's `current-task.md` with a withdrawal note, and append a short `memory.md` Work Log entry so a future reactivation can understand what happened.
- Update project-director `memory.md`, `status.md`, `task-board.md`, `communication.md`, and `decisions.md`.
- Add or preserve an `AGENTS.md` rule that archived/withdrawn employees must not receive new dispatches unless the user explicitly reactivates them.
- Keep useful work products in place if they are still reference material; move them to `Agent Office/Archive/Old Project Memory/` only when the user says the old direction itself is obsolete.

Good closing style:

```md
**撤岗完成**

- [x] 员工线程已归档
- [x] 未来任务已取消
- [x] 已完成任务保持 `done`
- [x] 员工资料没有删除
- [x] 当前只保留项目总监窗口待命

> 已归档员工不会再收到派工；如果以后要恢复，需要用户明确重新启用。
```

## Safe Cleanup Order

1. Run `validate_office.py --project-root <project> --warn-only` when available.
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
3. If the office mostly works but lacks the current report-return/report-intake protocol, offer a protocol-only patch before a full refresh.
4. Propose what to refresh, what to archive, and what to leave alone.
5. Ask for A/B/C/D approval before overwriting active office files.
6. Preserve or archive retired employee folders instead of deleting them.
7. Rebuild current templates only after approval, then run validation again.
8. Treat stale A/B/C/D letters as expired if the next user reply after the options was not a valid letter.

Light upgrade options:

```text
回 A / B / C / D 即可
```

- A. 只补协议：补 `employee_report_intake`、项目总监 thread ID 登记说明、汇报接收记录；不重建员工记忆。
- B. 健康检查：只读审计并给报告。
- C. 完整升级：刷新办公室模板，保留/归档旧员工记忆。
- D. 暂停。

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
