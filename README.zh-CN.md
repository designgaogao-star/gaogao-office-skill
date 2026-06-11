# GaoGao Office Skill

`gaogao-office` 是一个 Codex skill，用来在长期项目里创建、迁移和维护轻量化的 `Agent Office/`。

它会让当前窗口先接任第一任项目总监，提出组织方案，等你用 A/B/C/D 拍板后再正式接管。多员工模式下，你也可以继续只和项目总监窗口说话，由它先判断每个需求该谁负责，再按本机容量派给员工窗口、接收员工汇报，并根据依赖关系和你选择的 A/B/C 推进模式继续流转。

v1.0.0 是第一个稳定版：项目总监集中调度、员工固定格式汇报、任务名优先、开工前给进度预期，并用 A/B/C 选择手动、半自动或自动推进到下一个用户检查点。

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
    Old Project Memory/
```

默认不会直接写根目录 `AGENTS.md`。只有你在当前回复选项里授权正式接管或应用 AGENTS 时，它才会备份旧版并应用新入口。已吸收的旧知识会进入 `Agent Office/Archive/Old Project Memory/`。

## 常用口令

| 口令 | 作用 |
|---|---|
| `说明书` | 查看功能说明，不扫描、不写文件 |
| `只读体检` | 只读检查当前项目状态 |
| `接管项目` | 进入正式接管方案 |
| `迁移旧项目` | 吸收旧项目记忆并提出迁移方案 |
| `健康检查` | 审计已有办公室 |
| `跟进` / `继续` / `OK` | 按当前任务语境继续推进 |
| `自动推进到检查点` | 让项目总监自动推进到下次需要你查看的位置 |
| `停止自动推进` | 停止自动推进或 heartbeat |
| `撤岗` | 缩编或停用员工路线 |

## 本机安装或更新

在仓库根目录运行：

```powershell
$dest = "$env:USERPROFILE\.codex\skills\gaogao-office"
if (Test-Path $dest) {
  $backupRoot = "$env:USERPROFILE\.codex\skill-backups\gaogao-office"
  New-Item -ItemType Directory -Force $backupRoot | Out-Null
  $backup = Join-Path $backupRoot "gaogao-office-$(Get-Date -Format yyyyMMdd-HHmmss)"
  Move-Item -LiteralPath $dest -Destination $backup
  Write-Host "已备份旧安装到 $backup"
}
New-Item -ItemType Directory -Force "$env:USERPROFILE\.codex\skills" | Out-Null
Copy-Item -Recurse .\gaogao-office $dest
```

安装或更新后重启 Codex。

如果旧的 `agent-office-os` 还装着，建议移到 `.codex\skills` 之外的备份目录，或直接移除，避免两个 skill 同时响应同一个项目办公室请求。

## 使用示例

新项目：

```text
使用 $gaogao-office 只读体检这个项目，并给我一份 Agent Office 组织建议。直接开始；如果你判断不出项目用途，只问我一个简短问题。等我回复 A/B/C/D 后再创建文件。A 是你推荐的正式接管方式，B 是另一种正式接管方式，C 是自定义团队，D 是以后再说且不写文件。接管完成后，再问我要不要进入方向顾问模式。
```

先看说明书：

```text
使用 $gaogao-office 说明书，告诉我你能做什么。不要扫描项目，也不要写文件。
```

旧项目接管：

```text
使用 $gaogao-office 接管这个旧项目。先扫描文件名，读取明显像旧知识、规则、计划、上下文或交接记录的文本文件，给出组织方案，并让当前窗口接任项目总监。正式接管完成前，不要邀请员工或移动旧资料。
```

更新 skill 后升级已有办公室：

```text
使用 $gaogao-office 检查这个项目里已有的 Agent Office。不要直接删除或重建；先告诉我旧办公室哪些内容会保留、哪些旧入口会归档、哪些文件需要升级。等我回复当前选项后，再把它升级成当前 GaoGao Office 流程。
```

在 Codex 桌面环境中，授权后会先尝试把当前项目总监对话改成职位名标题，再自动创建员工对话并设置职位名标题。员工入职后，项目总监会先判断每个需求的归属：员工职责明确的就派给员工，办公室小事自己处理，方向不清时只补问一句。长任务开工前，项目总监会先说明预计几步、哪些员工参与、下次需要你查看的位置，然后让你选 A/B/C：A 手动推进，B 半自动推进，C 自动推进到检查点。只有选择 C 或明确要求自动推进时，才会在工具可用时创建或更新 heartbeat；没有线程或自动化工具时，会回退成可复制的入职提示词和手动派工消息。

## 辅助脚本

- `scripts/scaffold_office.py`：创建 `Agent Office/` 和员工文件夹。
- `scripts/inspect_capacity.py`：只读检测本机容量，给员工并发派工数建议。
- `scripts/inspect_office.py`：只读扫描文件名并生成迁移报告。
- `scripts/archive_legacy.py`：归档已批准旧知识文件；只有单独批准时才移动原文件。
- `scripts/validate_office.py`：检查结构、员工文件夹、上下文预算和迁移安全。

## 发布

建议 GitHub 仓库名：`gaogao-office-skill`。

不要因为本地 skill 改了就默认发布。先更新本机安装版，在真实项目里测试，确认体验稳定后再决定是否打 tag、打包和发 release。

许可证：Apache-2.0。
