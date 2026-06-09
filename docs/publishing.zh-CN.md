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
git commit -m "Release gaogao office v0.2.4"
```

## 3. 打 tag

```bash
git tag v0.2.4
git push origin main
git push origin v0.2.4
```

## 4. Zip 资产

Release asset 使用父级工作区里的 `outputs/gaogao-office-skill.zip`。发布前重新生成，并确认完整 gate 输出 `zip content matches package`。

## 5. Release Notes

```md
# GaoGao Office v0.2.4

Polished takeover choices, neutral user addressing, and safer legacy archiving.

Highlights:
- A/B/C/D 变成动态接管选项：A 是推荐方式，B 是另一种正式接管方式
- 中文输出尊重用户已有称呼，不再强制使用 `BOSS`
- 单独调用 `$gaogao-office` 会直接进入只读体检
- 首次调用流程图更短、更容易扫读
- 旧资料归档会拒绝活动办公室、依赖、构建、缓存和项目根路径
- 发布和安装文档已对齐当前流程
- Codex Desktop 授权后仍可自动创建员工对话
- 已吸收旧知识归档到 `Agent Office/Archive/Old Project Memory/`
```

## 6. GitHub Release

把 `outputs/gaogao-office-skill.zip` 上传为 `v0.2.4` 的 release asset。

## 7. 安装提示

发布后，用户可以让 Codex 执行：

```text
Install the skill from https://github.com/designgaogao-star/gaogao-office-skill and restart Codex after installation.
```
