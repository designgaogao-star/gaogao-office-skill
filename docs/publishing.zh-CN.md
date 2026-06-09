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
git commit -m "Release gaogao office v0.2.8"
```

## 3. 打 tag

```bash
git tag v0.2.8
git push origin main
git push origin v0.2.8
```

## 4. Zip 资产

Release asset 使用父级工作区里的 `outputs/gaogao-office-skill.zip`。发布前重新生成，并确认完整 gate 输出 `zip content matches package`。

## 5. Release Notes

```md
# GaoGao Office v0.2.8

Release-readiness safety update for project scanning, path handling, and office writes.

Highlights:
- office writes now refuse symlink or junction targets
- project inspection prunes skipped directories before traversal
- relative report paths resolve inside the selected project root
- inspect, archive, and validate scripts reject unsafe project roots
- Chinese and English budget checks now use mixed budget units
- no change to the lightweight `Agent Office/` structure
```

## 6. GitHub Release

把 `outputs/gaogao-office-skill.zip` 上传为 `v0.2.8` 的 release asset。

## 7. 安装提示

发布后，用户可以让 Codex 执行：

```text
Install the skill from https://github.com/designgaogao-star/gaogao-office-skill and restart Codex after installation.
```
