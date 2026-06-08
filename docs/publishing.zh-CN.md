# GitHub 发布指南

这份说明给没有发布过 GitHub 项目的人使用，重点是避免把本地无关文件或敏感文件发到公开仓库。

## 1. 创建仓库

1. 打开 GitHub。
2. 新建一个公开仓库，推荐名称：`agent-office-os-skill`。
3. 如果本地已经有 `README.md` 和 `LICENSE`，GitHub 创建页面里不要再勾选自动生成 README 或 License。

## 2. 提交前先验证

进入包含 `README.md` 和 `agent-office-os/` 的文件夹，先创建一个临时 demo 项目跑通流程：

```bash
mkdir demo-project
python agent-office-os/scripts/scaffold_office.py --project-root ./demo-project --project-name Demo
python agent-office-os/scripts/inspect_office.py --project-root ./demo-project
python agent-office-os/scripts/validate_office.py --project-root ./demo-project
```

再校验 skill frontmatter：

macOS/Linux：

```bash
python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py ./agent-office-os
```

PowerShell：

```powershell
python "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" .\agent-office-os
```

检查完以后，手动删除临时 `demo-project` 目录。

## 3. 检查即将发布的内容

运行：

```bash
git status --short
git diff -- README.md README.zh-CN.md LICENSE docs examples agent-office-os .gitignore
```

不要发布 secrets、本地缓存、私人项目文件或临时测试目录。

## 4. 本地提交

```bash
git init
git add README.md README.zh-CN.md LICENSE .gitignore docs examples agent-office-os
git status --short
git diff --cached
git commit -m "Initial release of agent-office-os skill"
```

提交前认真看 `git status --short` 和 `git diff --cached`，确认只包含 skill 包和发布文档。

## 5. 绑定 GitHub 仓库

把 `<owner>` 换成你的 GitHub 用户名或组织名，并在 push 前确认远程地址正确：

```bash
git branch -M main
git remote add origin https://github.com/<owner>/agent-office-os-skill.git
git remote -v
git push -u origin main
```

## 6. 打版本标签

```bash
git tag v0.1.0
git push origin v0.1.0
```

然后在 GitHub 页面创建 release，选择 `v0.1.0`。

建议 release notes：

```md
# Agent Office OS v0.1.0

Agent Office OS skill 初始发布，用于初始化、迁移和维护长期可持续的 Agent 项目办公室。

包含：
- 新项目办公室脚手架
- 项目简报和长期 Agent 角色线程启动提示
- 跨角色 message/handoff 通信协议
- 旧项目迁移 playbook
- PM、Architect、Builder、Reviewer、Archivist 等角色卡
- task、message、handoff、ADR 模板
- 安全的扫描、归档复制和校验脚本
```

## 7. 安装链接

发布后，别人可以把下面这句粘贴到 Codex 对话里：

```text
$skill-installer https://github.com/<owner>/agent-office-os-skill/tree/main/agent-office-os
```

## 8. 以后怎么更新

1. 修改 skill。
2. 运行校验和脚本测试。
3. 只 stage 需要发布的文件。
4. 提交 commit。
5. 打新 tag，比如 `v0.2.0`。
6. 在 GitHub 更新 release notes。
