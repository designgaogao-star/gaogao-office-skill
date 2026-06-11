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
git commit -m "Release gaogao office v1.0.1"
```

## 3. 打 tag

```bash
git tag v1.0.1
git push origin main
git push origin v1.0.1
```

## 4. Zip 资产

发布附件使用父级工作区里的 `outputs/gaogao-office-skill.zip`。发布前重新生成，并确认完整 gate 输出 `zip content matches package`。

## 5. Release Notes

```md
# GaoGao Office v1.0.1

稳定办公室协作版的员工汇报回传补丁。

重点：
- 员工现在有明确的上行汇报传输规则
- 员工完成正式任务后，先更新 `memory.md` 和 `current-task.md`，再汇报
- 员工汇报优先用 `send_message_to_thread` 发回已确认的项目总监 thread ID
- 如果线程工具或项目总监 thread ID 不可用，员工输出可复制汇报，不假装已经发送
- v1.0.0 办公室只会得到升级 warning，可以保留员工记忆补上新协议
- 不改变轻量化 `Agent Office/` 目录结构
```

## 6. GitHub Release

把 `outputs/gaogao-office-skill.zip` 上传为 `v1.0.1` 的发布附件。

## 7. 安装提示

发布后，用户可以让 Codex 执行：

```text
从 https://github.com/designgaogao-star/gaogao-office-skill 安装 GaoGao Office。安装完成后请重启 Codex。
```
