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
git commit -m "Release gaogao office v1.0.3"
```

## 3. 打 tag

```bash
git tag v1.0.3
git push origin main
git push origin v1.0.3
```

## 4. Zip 资产

发布附件使用父级工作区里的 `outputs/gaogao-office-skill.zip`。发布前重新生成，并确认完整 gate 输出 `zip content matches package`。

## 5. Release Notes

使用 `docs/release-notes-v1.0.3.md` 作为 GitHub release 正文。发布页默认展示中文，英文放在折叠的 `<details>` 里，方便切换查看。

## 6. GitHub Release

把 `outputs/gaogao-office-skill.zip` 上传为 `v1.0.3` 的发布附件。

## 7. 安装提示

发布后，用户可以让 Codex 执行：

```text
从 https://github.com/designgaogao-star/gaogao-office-skill 安装 GaoGao Office。安装完成后请重启 Codex。
```
