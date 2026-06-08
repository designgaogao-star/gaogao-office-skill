# Agent Office OS Skill

`agent-office-os` 是一个 agent-readable skill，用来给大型项目建立长期、可持续的 Agent 项目办公室。

它的目标不是制造一堆重文档，而是让 Agent 每次只读最小上下文，同时知道项目状态在哪里、谁负责、该改哪些文件、做完交给谁。

这个包针对 Codex 安装做了适配，但核心流程是普通 Markdown 加 Python 辅助脚本。其他编码 Agent 只要能读取 `agent-office-os/SKILL.md` 和生成的 `docs/agent-office/`，也可以按同一套办公室流程使用。

## 它能做什么

- 先进行轻量聊天式咨询和只读项目判断。
- 能判断项目用途时先向你确认，判断不了时用编号问题快速询问。
- 只有你明确确认方案后，才初始化新的 `docs/agent-office/` 项目办公室。
- 创建短小的 `AGENTS.md`，作为 Agent 自动加载入口。
- 把项目类型、风险等级、第一里程碑和动态角色决策写入 `context-packs/project-brief.md`。
- 按真实项目情况创建角色卡，不套固定岗位模板。
- 创建 task、message、handoff、ADR 模板。
- 创建 `communication.md`，让不同角色线程知道如何开消息、回复、关闭和交接工作。
- 审计旧项目里已有的计划、规则、任务、架构和上下文文档。
- 迁移旧框架时先归档，再确认删除，避免误删。
- 写出 `context-packs/thread-launch-prompts.md`，并在当前聊天框给出可直接复制的长期 Agent 角色启动提示词。
- 提供安全脚本用于脚手架、旧项目扫描和健康检查。

## 本机安装

推荐发布后用 `$skill-installer` 安装。手动本机安装时，请在仓库根目录运行下面命令，并且不要覆盖已有安装。

PowerShell：

```powershell
$dest = "$env:USERPROFILE\.codex\skills\agent-office-os"
if (Test-Path $dest) { throw "Skill already exists at $dest. Back it up or remove it first." }
New-Item -ItemType Directory -Force "$env:USERPROFILE\.codex\skills" | Out-Null
Copy-Item -Recurse .\agent-office-os $dest
```

macOS/Linux：

```bash
dest="$HOME/.codex/skills/agent-office-os"
test -e "$dest" && { echo "Skill already exists at $dest. Back it up or remove it first."; exit 1; }
mkdir -p "$HOME/.codex/skills"
cp -R ./agent-office-os "$dest"
```

安装或更新后重启 Codex。

然后在项目里对 Codex 说：

```text
Use $agent-office-os to inspect this project read-only, infer what it is, ask me concise numbered questions, propose dynamic agent roles, and wait for my approval before creating files.
```

或者：

```text
Use $agent-office-os to inspect this old project, migrate its planning docs into an Agent Office OS, and archive the old framework before any deletion.
```

## 从 GitHub 安装

发布到 GitHub 后，可以这样安装：

把下面这句粘贴到 Codex 对话里：

```text
$skill-installer https://github.com/<owner>/agent-office-os-skill/tree/main/agent-office-os
```

把 `<owner>` 换成你的 GitHub 用户名或组织名。

## 辅助脚本

```bash
mkdir demo-project
python agent-office-os/scripts/scaffold_office.py --project-root ./demo-project --project-name "My Project" --project-type app --risk-level medium --first-milestone "Ship the first usable workflow"
python agent-office-os/scripts/inspect_office.py --project-root ./demo-project
python agent-office-os/scripts/validate_office.py --project-root ./demo-project --warn-only
```

如果路径里有空格，请给路径加引号。

动态角色推荐由 Skill 在咨询后生成。你确认方案后，可以把批准的方案保存为 `office-plan.json`，再运行：

```bash
python agent-office-os/scripts/scaffold_office.py --project-root ./demo-project --config ./office-plan.json
```

脚手架生成后，先看 `demo-project/docs/agent-office/context-packs/project-brief.md` 和 `demo-project/docs/agent-office/communication.md`，再使用当前聊天框输出的提示词，或打开 `demo-project/docs/agent-office/context-packs/thread-launch-prompts.md`，按里面的提示创建长期 Agent 对话框。每创建一个，就把返回的 thread ID 记录到 `docs/agent-office/thread-registry.md`。

旧项目迁移报告审查完成，并且在 `User Approval Record` 里写入 `Approved archive list: YES` 后，可以这样复制已批准的旧框架文件：

```bash
python agent-office-os/scripts/archive_legacy.py --project-root ./old-project --dry-run
python agent-office-os/scripts/archive_legacy.py --project-root ./old-project
```

安全默认值：

- `scaffold_office.py` 不删除文件，默认不覆盖已有文件。
- `scaffold_office.py` 只有加 `--create-root` 才会创建不存在的项目根目录，覆盖已有文件时必须同时使用 `--force` 和 `--confirm-overwrite`。
- `scaffold_office.py` 会拒绝通过符号链接或 junction 解析到项目根目录之外的路径。
- `inspect_office.py` 默认只读扫描；如果指定 `--output`，输出路径必须在项目根目录内；链接路径会被跳过，不读取外部内容。
- `archive_legacy.py` 只复制已经明确批准的归档清单，会拒绝链接路径或疑似敏感路径，并且永远不删除原文件。
- `validate_office.py` 只报告问题，不修改文件。

## 发布到 GitHub

详细步骤见 [docs/publishing.zh-CN.md](docs/publishing.zh-CN.md)。

## 许可证

Apache-2.0，见 [LICENSE](LICENSE)。
