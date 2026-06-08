# 发布 GAOGAO Office

## 1. 校验

在工作区根目录运行：

```bash
python work/run_gaogao_office_gate.py --workspace .
```

## 2. 提交

进入发布包仓库后：

```bash
git status --short
git add README.md README.zh-CN.md LICENSE .gitignore docs examples gaogao-office
git commit -m "Release gaogao office v0.2.0"
```

## 3. 打标签

```bash
git tag v0.2.0
git push origin main
git push origin v0.2.0
```

## 4. Release Notes

```md
# GAOGAO Office v0.2.0

轻量化公共区/员工私有区重构。

Highlights:
- skill 改名为 `$gaogao-office`，显示名为 GAOGAO Office
- 项目内生成目录为 `Agent Office/`
- 公共文件直接放在 `Agent Office/`
- 每个角色在 `Agent Office/Employees/` 下有自己的私有文件夹
- 根 `AGENTS.md` 先生成提案，只有回复 `确认应用 AGENTS.md` 后才应用
- 迁移先完整扫描文件名，再读取候选文本
- 旧 `vibe/` 和计划文件先吸收到新 office，再归档或移动
- 已批准旧文件归档到 `Agent Office/Archive/Legacy Management/`
```

## 5. 安装提示

发布后，别人可以让 Codex 安装：

```text
Install the skill from https://github.com/<owner>/gaogao-office-skill and restart Codex after installation.
```
