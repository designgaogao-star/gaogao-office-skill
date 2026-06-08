# GAOGAO Office Skill

`gaogao-office` 是一个 Codex skill，用来在长期项目里创建、迁移和维护轻量化的 `Agent Office/`。

它的核心结构是“公共区 + 员工私有区”：公共文件放在 `Agent Office/` 根部，每个长期角色在 `Agent Office/Employees/{role-slug}/` 里有自己的记忆和当前任务。

## 什么时候适合用

适合有固定项目文件夹、会持续推进很久的工作：软件项目、作品集、品牌长期策划、研究项目、产品从 0 到 1、旧项目接管整理等。

不适合一次性小问题、互不相关的多任务聊天、没有共同项目文件夹的临时工作。

## 会创建什么

```text
Agent Office/
  README.md
  status.md
  project-brief.md
  project-map.md
  task-board.md
  communication.md
  decisions.md
  thread-registry.md
  office-plan.json
  Proposals/
    AGENTS.proposed.md
  Employees/
    role-slug/
      README.md
      memory.md
      current-task.md
  Archive/
    Legacy Management/
```

默认不会直接写根目录 `AGENTS.md`。skill 会先写 `Agent Office/Proposals/AGENTS.proposed.md`，你看完后回复固定确认词：

```text
确认应用 AGENTS.md
```

Codex 才能把它应用到根目录；如果原本已有 `AGENTS.md`，会先备份。

## 本机安装

在仓库根目录运行：

```powershell
$dest = "$env:USERPROFILE\.codex\skills\gaogao-office"
if (Test-Path $dest) { throw "Skill already exists at $dest. Back it up or remove it first." }
New-Item -ItemType Directory -Force "$env:USERPROFILE\.codex\skills" | Out-Null
Copy-Item -Recurse .\gaogao-office $dest
```

安装或更新后重启 Codex。

如果旧的 `agent-office-os` 还装着，建议先备份或移除，避免两个 skill 同时响应同一个项目办公室请求。

## 使用示例

新项目：

```text
Use $gaogao-office to inspect this project read-only and propose a lightweight Agent Office. Do not create files until I approve the plan.
```

旧项目接管：

```text
Use $gaogao-office to inspect this old project, scan filenames, absorb old planning/vibe docs into Agent Office, propose AGENTS.md, and archive absorbed legacy files only after approval.
```

## 辅助脚本

- `scripts/scaffold_office.py`：创建 `Agent Office/` 和员工文件夹。
- `scripts/inspect_office.py`：只读扫描文件名并生成迁移报告。
- `scripts/archive_legacy.py`：复制已批准旧文件；只有单独批准时才移动原文件。
- `scripts/validate_office.py`：检查结构、员工文件夹、上下文预算和迁移安全。

## 发布

建议 GitHub 仓库名：`gaogao-office-skill`。

许可证：Apache-2.0。
