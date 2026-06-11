# 发布 GaoGao Office

只有本机安装版已经在真实项目里测试通过后，才发布新版本。不要因为本地文件改了就自动打 tag 或创建 GitHub release。

## 1. 验证

在工作区根目录运行完整 gate：

```bash
python work/run_gaogao_office_gate.py --workspace .
```

## 2. 提交

在 skill 包仓库里：

```bash
git status --short
git add README.md README.zh-CN.md LICENSE .gitignore docs examples gaogao-office
git commit -m "Release gaogao office v1.0.0"
```

## 3. 打 tag

```bash
git tag v1.0.0
git push origin main
git push origin v1.0.0
```

## 4. Zip 资产

发布附件使用父级工作区里的 `outputs/gaogao-office-skill.zip`。发布前重新生成，并确认完整 gate 输出 `zip content matches package`。

## 5. Release Notes

```md
# GaoGao Office v1.0.0

第一个稳定办公室协作版本，面向长期 AI Agent 项目。

重点：
- 当前窗口担任项目总监，集中调度员工对话
- 员工用固定格式向项目总监汇报
- 用户侧用任务名和短词继续推进，不再要求记内部任务编号
- 长任务开工前先说明预计步骤、参与员工和下次用户检查点
- A/B/C 推进模式支持手动、半自动或自动推进到检查点
- heartbeat 只在用户选择自动推进时启用，且不授权高风险动作
- 不改变轻量化 `Agent Office/` 目录结构
```

## 6. GitHub Release

把 `outputs/gaogao-office-skill.zip` 上传为 `v1.0.0` 的发布附件。

## 7. 安装提示

发布后，用户可以让 Codex 执行：

```text
从 https://github.com/designgaogao-star/gaogao-office-skill 安装 GaoGao Office。安装完成后请重启 Codex。
```
