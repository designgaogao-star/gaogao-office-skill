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
git commit -m "Release gaogao office v0.2.9"
```

## 3. 打 tag

```bash
git tag v0.2.9
git push origin main
git push origin v0.2.9
```

## 4. Zip 资产

发布附件使用父级工作区里的 `outputs/gaogao-office-skill.zip`。发布前重新生成，并确认完整 gate 输出 `zip content matches package`。

## 5. Release Notes

```md
# GaoGao Office v0.2.9

这版主要清理中文办公室措辞、运行时 metadata 和生成状态值。

重点：
- 中文办公室默认使用 `项目总监` 作为当前窗口的管理岗位名
- 当前窗口员工记录 `status: current-window`，不再把岗位名写成状态
- `agents/openai.yaml` 默认提示更短、更少重复
- 运行时参考文档不再包含发布专用说明
- 项目扫描会大小写不敏感地跳过 `Agent Office/`
- 不改变轻量化 `Agent Office/` 目录结构
```

## 6. GitHub Release

把 `outputs/gaogao-office-skill.zip` 上传为 `v0.2.9` 的发布附件。

## 7. 安装提示

发布后，用户可以让 Codex 执行：

```text
从 https://github.com/designgaogao-star/gaogao-office-skill 安装 GaoGao Office。安装完成后请重启 Codex。
```
