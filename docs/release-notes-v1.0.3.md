# GaoGao Office v1.0.3

岗位校准与文件优先通信补丁。

## 重点更新

- 员工第一次正式任务前，项目总监会让用户选择岗位校准档位：轻量、标准、深度或跳过。
- 校准结果写入员工自己的 `memory.md`，用于形成本项目里的岗位判断标准，而不是把长身份提示塞进聊天。
- 深度校准、联网、广泛读取项目资料或外部参考都需要单独授权。
- 派工和汇报改为文件优先：完整派工包和完整员工汇报可写入 `Agent Office/Exchange/`，线程里只传路径、状态和是否需要用户介入。
- 员工启动逻辑保持不变；本版只影响首次正式派工和后续汇报链路。

## 升级说明

安装或更新后重启 Codex。已有 `Agent Office/` 的项目再次调用 `$gaogao-office` 时，会先进入维护/升级判断；如果只是缺 v1.0.3 协议，可以选择只补协议，保留员工记忆。

<details>
<summary>English release notes</summary>

# GaoGao Office v1.0.3

Role-calibration and file-first communication patch.

## Highlights

- Before an employee's first real task, the project director asks the user to choose a calibration level: light, standard, deep, or skip.
- Calibration is written into the employee's own `memory.md`, so the role develops project-specific judgment without bloating chat prompts.
- Deep calibration, web access, broad project reading, or external references require separate authorization.
- Dispatch and reporting are now file-first: full dispatch packets and full employee reports may live under `Agent Office/Exchange/`, while thread messages carry paths, status, and user-input needs.
- Employee startup behavior is unchanged; this release affects first real dispatch and later report transport.

## Upgrade Notes

Restart Codex after installing or updating. In projects that already have `Agent Office/`, calling `$gaogao-office` enters maintenance/upgrade first; if only the v1.0.3 protocol is missing, you can patch the protocol while preserving employee memory.

</details>
