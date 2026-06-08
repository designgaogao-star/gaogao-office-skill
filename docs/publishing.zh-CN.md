# 发布 GaoGao Office

只有本机安装版在真实项目里测试通过后，才考虑发布。不要因为本地 skill 改了就自动打 tag、打包或发 GitHub release。

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
git commit -m "Release gaogao office v0.2.3"
```

## 3. 打标签

```bash
git tag v0.2.3
git push origin main
git push origin v0.2.3
```

## 4. Release Notes

```md
# GaoGao Office v0.2.3

实战接管、容量派工和最终回复体验改进。

Highlights:
- 当前窗口默认接任第一任项目总管
- 用户通过 A/B/C/D 回复选择首次接管方式
- 方案咨询从接管选项中移除，改为接管完成后的方向顾问模式
- 员工使用人类岗位名和入职式提示
- Codex 桌面可在授权后自动创建员工对话
- 项目总管根据本机容量控制员工并发派工
- 最终回复增加公开输出自检，避免内部草稿泄露
- 已吸收旧知识归档到 `Agent Office/Archive/Old Project Memory/`
```

## 5. 安装提示

发布后，别人可以让 Codex 安装：

```text
Install the skill from https://github.com/<owner>/gaogao-office-skill and restart Codex after installation.
```
