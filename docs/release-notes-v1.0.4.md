# GaoGao Office v1.0.4

文件优先通信协议修复补丁。

## 重点修复

- 修正新办公室 `office-plan.json` 中的 `employee_report_transport`，从旧的线程优先语义改为 `file-first-thread-index`。
- 修正 `project-brief.md`、`thread-registry.md` 和员工启动示例里的旧描述：完整汇报优先写入 `Agent Office/Exchange/Reports/`，线程只回传任务名、报告路径、状态和是否需要用户介入。
- 更新校验器和 gate，让旧的 `director-thread-first` 不再被当作正确结果。

## 升级说明

安装或更新后重启 Codex。已有 `Agent Office/` 的项目再次调用 `$gaogao-office` 时，会先进入维护/升级判断；如果只是缺 v1.0.4 协议，可以选择只补协议，保留员工记忆。

<details>
<summary>English release notes</summary>

# GaoGao Office v1.0.4

File-first communication protocol fix.

## Highlights

- Corrects `employee_report_transport` in new `office-plan.json` files from the old thread-first wording to `file-first-thread-index`.
- Fixes stale wording in `project-brief.md`, `thread-registry.md`, and employee launch examples: full reports should live under `Agent Office/Exchange/Reports/`, while thread messages return only task title, report path, status, and user-input need.
- Updates validation and gate checks so the old `director-thread-first` value is no longer accepted as correct.

## Upgrade Notes

Restart Codex after installing or updating. In projects that already have `Agent Office/`, calling `$gaogao-office` enters maintenance/upgrade first; if only the v1.0.4 protocol is missing, you can patch the protocol while preserving employee memory.

</details>
