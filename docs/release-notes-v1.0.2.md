# GaoGao Office v1.0.2

稳定办公室协作版的员工汇报接收补丁。

## 重点更新

- 员工汇报仍优先通过 `send_message_to_thread` 发回已确认的项目总监线程。
- 项目总监收到员工汇报后，会先验收格式、更新 `task-board.md` / `communication.md`、等待缺失依赖，再按用户选择的 A/B/C 推进模式继续。
- `thread-registry.md` 增加项目总监 thread ID 登记修复说明：能可靠识别才写真实 ID，否则保留 `current-window`，不假装自动回传可用。
- 旧办公室升级时可以只补协议，不重建员工记忆。
- 文案瘦身：员工续任、派工、汇报接收相关说明更短，减少员工窗口重读成本。

## 不变的安全边界

- 不改变轻量化 `Agent Office/` 目录结构。
- 不会静默改 `AGENTS.md`。
- 不会静默删除旧资料。
- 自动线程回传仍然需要 Codex Desktop 线程工具和已确认的项目总监 thread ID。

## 升级建议

安装或更新后重启 Codex。已有 `Agent Office/` 的项目再次调用 `$gaogao-office` 时，会先进入维护/升级判断；如果只是缺 v1.0.2 协议，可以选择只补协议，保留员工记忆。

<details>
<summary>English release notes</summary>

# GaoGao Office v1.0.2

Focused report-intake patch for the stable office-collaboration release.

## Highlights

- Employee reports still prefer `send_message_to_thread` back to a confirmed project-director thread.
- When the project director receives an employee report, it validates the report shape, updates `task-board.md` / `communication.md`, waits for missing dependencies, and advances only under the selected A/B/C progress mode.
- `thread-registry.md` now includes project-director thread ID repair guidance: record the real ID only when it can be reliably identified; otherwise keep `current-window` and do not overpromise automatic return.
- Existing offices can receive a protocol-only upgrade without rebuilding employee memory.
- Copy slimming: employee restart, dispatch, and report-intake guidance is shorter to reduce re-read cost.

## Safety Boundaries

- No change to the lightweight `Agent Office/` structure.
- No silent `AGENTS.md` changes.
- No silent deletion of old material.
- Automatic employee-to-director return still requires Codex Desktop thread tools and a confirmed project-director thread ID.

## Upgrade Notes

Restart Codex after installing or updating. In projects that already have `Agent Office/`, calling `$gaogao-office` enters maintenance/upgrade first; if only the v1.0.2 protocol is missing, you can patch the protocol while preserving employee memory.

</details>
