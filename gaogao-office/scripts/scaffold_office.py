#!/usr/bin/env python3
"""Scaffold a lightweight GAOGAO Office project office.

The script writes only inside the selected project root. It creates the
project office at `Agent Office/` and writes a proposed root `AGENTS.md` under
`Agent Office/Proposals/` by default. It writes or overwrites root `AGENTS.md`
only when explicitly requested with --apply-agents and --confirm-apply-agents.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path
from typing import Any


OFFICE_DIR = "Agent Office"
EMPLOYEES_DIR = "Employees"
PROPOSALS_DIR = "Proposals"
ARCHIVE_DIR = "Archive"
LEGACY_ARCHIVE_DIR = "Legacy Management"


ROLE_DEFINITIONS = {
    "pm": {
        "title": "Coordinator",
        "mission": "Maintain shared project truth, task ownership, scope, and handoffs.",
        "authority": "May update public office files and coordinate employee work.",
    },
    "builder": {
        "title": "Builder",
        "mission": "Implement assigned work inside the approved write scope and verify it.",
        "authority": "May change only files named by the current task.",
    },
    "reviewer": {
        "title": "Reviewer",
        "mission": "Review work for correctness, regressions, scope, quality, and missing checks.",
        "authority": "Read-heavy by default; may update review notes and handoffs.",
    },
    "archivist": {
        "title": "Archivist",
        "mission": "Keep the office clean, absorb old project memory, and archive stale material.",
        "authority": "May update public office files and archive records; does not change product code.",
    },
    "architect": {
        "title": "Architect",
        "mission": "Maintain architecture boundaries and durable technical decisions.",
        "authority": "May update decisions and architecture notes; code changes require task assignment.",
    },
    "qa": {
        "title": "QA",
        "mission": "Own acceptance scenarios, regression checks, and release confidence.",
        "authority": "May update QA notes, task acceptance, and verification records.",
    },
    "security": {
        "title": "Security",
        "mission": "Review secrets, permissions, dependency risk, and unsafe automation.",
        "authority": "May update security decisions and blocker notes.",
    },
    "ux": {
        "title": "UX",
        "mission": "Review user flows, accessibility, interaction states, and user-facing clarity.",
        "authority": "May update UX notes and acceptance criteria.",
    },
}

ROLE_WRITE_SCOPES = {
    "pm": "Agent Office public files",
    "builder": "current task scope only",
    "reviewer": "review notes and task-board updates",
    "archivist": "Agent Office public files and archive records",
    "architect": "decisions and architecture notes",
    "qa": "verification notes and acceptance criteria",
    "security": "security notes and blocker decisions",
    "ux": "UX notes and acceptance criteria",
}


@dataclass
class RoleSpec:
    slug: str
    title: str
    mission: str
    authority: str
    write_scope: str
    current_assignment: str
    thread_mode: str = "local"
    handoff_to: str = ""


@dataclass
class OfficeSpec:
    project_name: str
    project_goal: str
    profile: str
    project_type: str
    risk_level: str
    first_milestone: str
    language: str
    roles: list[RoleSpec]
    role_decisions: str = ""
    deferred_roles: list[str] = field(default_factory=list)


def normalize_language(raw: str | None) -> str:
    if not raw:
        return "en"
    lowered = raw.strip().lower()
    if lowered in {"zh", "zh-cn", "zh_cn", "chinese", "cn"}:
        return "zh-CN"
    return "en"


def is_zh(language: str) -> bool:
    return language == "zh-CN"


def slugify(raw: str, fallback: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", raw.lower()).strip("-")
    return (slug[:40].strip("-") or fallback)


def validate_slug(slug: str) -> None:
    if not re.fullmatch(r"[a-z][a-z0-9-]{0,39}", slug):
        raise SystemExit(f"Invalid role slug `{slug}`. Use lowercase letters, digits, and hyphens.")


def coalesce(*values: Any, default: str = "") -> str:
    for value in values:
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return default


def as_string_list(raw: Any) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, list):
        return [str(item).strip() for item in raw if str(item).strip()]
    text = str(raw).strip()
    return [text] if text else []


def normalize_thread_mode(raw: Any) -> str:
    value = str(raw or "local").strip().lower()
    return "worktree" if value in {"worktree", "branch"} else "local"


def role_from_legacy_key(role: str) -> RoleSpec:
    definition = ROLE_DEFINITIONS[role]
    return RoleSpec(
        slug=role,
        title=definition["title"],
        mission=definition["mission"],
        authority=definition["authority"],
        write_scope=ROLE_WRITE_SCOPES.get(role, "current task scope only"),
        current_assignment="T-000" if role == "pm" else "waiting",
        thread_mode="worktree" if role == "builder" else "local",
        handoff_to="Coordinator" if role != "pm" else "Project owner",
    )


def parse_roles(raw: str, profile: str) -> list[RoleSpec]:
    if raw:
        role_keys = [part.strip().lower() for part in raw.split(",") if part.strip()]
    elif profile == "minimal":
        role_keys = ["pm"]
    elif profile == "expanded":
        role_keys = ["pm", "builder", "reviewer", "archivist", "architect", "qa"]
    else:
        role_keys = ["pm", "builder", "reviewer"]
    unknown = [role for role in role_keys if role not in ROLE_DEFINITIONS]
    if unknown:
        raise SystemExit(f"Unknown role(s): {', '.join(unknown)}")
    duplicates = sorted({role for role in role_keys if role_keys.count(role) > 1})
    if duplicates:
        raise SystemExit(f"Duplicate role(s): {', '.join(duplicates)}")
    return [role_from_legacy_key(role) for role in role_keys]


def role_from_config(raw: dict[str, Any], index: int, default_handoff: str) -> RoleSpec:
    title = coalesce(raw.get("title"), raw.get("name"), default=f"Role {index + 1}")
    slug = slugify(coalesce(raw.get("slug"), default=title), f"role-{index + 1}")
    validate_slug(slug)
    return RoleSpec(
        slug=slug,
        title=title,
        mission=coalesce(raw.get("mission"), raw.get("purpose"), default="Own a distinct part of the approved workflow."),
        authority=coalesce(
            raw.get("authority"),
            raw.get("boundaries"),
            default="May update only the approved write scope and this employee's private folder.",
        ),
        write_scope=coalesce(raw.get("write_scope"), raw.get("writeScope"), default="current task scope only"),
        current_assignment=coalesce(raw.get("current_assignment"), raw.get("assignment"), raw.get("currentAssignment"), default="waiting"),
        thread_mode=normalize_thread_mode(raw.get("thread_mode", raw.get("threadMode"))),
        handoff_to=coalesce(raw.get("handoff_to"), raw.get("handoffTo"), default=default_handoff),
    )


def infer_default_handoff(roles: list[RoleSpec], language: str) -> str:
    for role in roles:
        haystack = f"{role.slug} {role.title}".lower()
        if any(token in haystack for token in ["coordinator", "owner", "lead", "manager", "producer"]):
            return role.title
        if any(token in role.title for token in ["协调", "负责人", "主理", "策展", "主编"]):
            return role.title
    if roles:
        return roles[0].title
    return "项目负责人" if is_zh(language) else "Project owner"


def fill_missing_handoffs(roles: list[RoleSpec], default_handoff: str, language: str) -> None:
    fallback_owner = "项目负责人" if is_zh(language) else "Project owner"
    inferred = default_handoff or infer_default_handoff(roles, language)
    for role in roles:
        if not role.handoff_to:
            role.handoff_to = fallback_owner if role.title == inferred else inferred


def validate_roles(roles: list[RoleSpec]) -> None:
    if not roles:
        raise SystemExit("At least one role is required.")
    slugs = [role.slug for role in roles]
    duplicates = sorted({slug for slug in slugs if slugs.count(slug) > 1})
    if duplicates:
        raise SystemExit(f"Duplicate role slug(s): {', '.join(duplicates)}")
    for role in roles:
        validate_slug(role.slug)


def load_config_spec(config_path: Path, args: argparse.Namespace, root: Path) -> OfficeSpec:
    try:
        raw = json.loads(config_path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON config: {config_path}: {exc}") from exc
    if not isinstance(raw, dict):
        raise SystemExit("Office config must be a JSON object.")
    role_items = raw.get("roles")
    if not isinstance(role_items, list) or not role_items:
        raise SystemExit("Office config must contain a non-empty `roles` list.")
    language = normalize_language(coalesce(raw.get("language"), args.language, default="en"))
    default_handoff = coalesce(raw.get("default_handoff_to"), raw.get("handoff_to"), default="")
    roles = [role_from_config(item, index, default_handoff) for index, item in enumerate(role_items) if isinstance(item, dict)]
    if len(roles) != len(role_items):
        raise SystemExit("Each role in config must be a JSON object.")
    fill_missing_handoffs(roles, default_handoff, language)
    validate_roles(roles)
    return OfficeSpec(
        project_name=coalesce(raw.get("project_name"), raw.get("name"), args.project_name, root.name, default="Project"),
        project_goal=coalesce(raw.get("project_goal"), raw.get("goal"), args.project_goal, default="Define the first milestone."),
        profile=coalesce(raw.get("profile"), args.profile, default="dynamic"),
        project_type=coalesce(raw.get("project_type"), raw.get("type"), args.project_type, default="unspecified"),
        risk_level=coalesce(raw.get("risk_level"), args.risk_level, default="unspecified"),
        first_milestone=coalesce(raw.get("first_milestone"), raw.get("milestone"), args.first_milestone, default="Define the first milestone."),
        language=language,
        roles=roles,
        role_decisions=coalesce(raw.get("role_decisions"), raw.get("role_strategy"), default=""),
        deferred_roles=as_string_list(raw.get("deferred_roles")),
    )


def load_office_spec(args: argparse.Namespace, root: Path) -> OfficeSpec:
    if args.config:
        return load_config_spec(Path(args.config).resolve(), args, root)
    roles = parse_roles(args.roles, args.profile)
    return OfficeSpec(
        project_name=args.project_name or root.name or "Project",
        project_goal=args.project_goal,
        profile=args.profile,
        project_type=args.project_type,
        risk_level=args.risk_level,
        first_milestone=args.first_milestone,
        language=normalize_language(args.language),
        roles=roles,
    )


def first_role_title(spec: OfficeSpec) -> str:
    return spec.roles[0].title if spec.roles else "Project owner"


def reviewer_title(spec: OfficeSpec) -> str:
    for role in spec.roles:
        haystack = f"{role.slug} {role.title}".lower()
        if "review" in haystack or "qa" in haystack:
            return role.title
    return spec.roles[1].title if len(spec.roles) > 1 else first_role_title(spec)


def role_titles(roles: list[RoleSpec]) -> str:
    return ", ".join(role.title for role in roles)


def render_agents_proposal(language: str) -> str:
    if is_zh(language):
        return """# AGENTS.md

## GAOGAO Office Protocol

本仓库使用 `Agent Office/` 作为长期 Agent 项目办公室。

开始项目工作前：
- 先读 `Agent Office/README.md`、`Agent Office/status.md`、`Agent Office/project-brief.md` 和 `Agent Office/task-board.md`。
- 如果你被分配了角色，只读 `Agent Office/Employees/{role-slug}/` 里属于自己的员工文件夹。
- 不要读取其他员工文件夹，除非用户明确要求维护、审计或恢复办公室。
- 日常工作不要读取 `Agent Office/Archive/Legacy Management/`；那里是旧框架吸收后的人工查看/审计材料。

协作规则：
- `Agent Office/thread-registry.md` 是长期 Agent 员工目录和启动提示记录。
- 跨角色请求、答复和交接写入 `Agent Office/communication.md`。
- 当前任务和责任人写入 `Agent Office/task-board.md`。
- 只有协调角色、归档角色、项目 owner 或被明确授权的角色才更新公共状态。
- 结束任务时说明改了什么、验证了什么、还剩什么、下一个负责人是谁。
"""
    return """# AGENTS.md

## GAOGAO Office Protocol

This repository uses `Agent Office/` as the long-running agent project office.

Before project work:
- Read `Agent Office/README.md`, `Agent Office/status.md`, `Agent Office/project-brief.md`, and `Agent Office/task-board.md`.
- If assigned a role, read only your own employee folder under `Agent Office/Employees/{role-slug}/`.
- Do not read other employee folders unless the user explicitly asks for office maintenance, audit, or recovery.
- Do not read `Agent Office/Archive/Legacy Management/` during ordinary work; it is human-review/audit material after migration absorption.

Coordination:
- `Agent Office/thread-registry.md` is the directory and launch prompt record for long-running agent employees.
- Cross-role requests, answers, and handoffs go in `Agent Office/communication.md`.
- Current tasks and owners go in `Agent Office/task-board.md`.
- Only the coordinator, archivist, project owner, or explicitly assigned role updates public status.
- End every task with what changed, what was verified, what remains, and who should pick it up next.
"""


def render_readme(spec: OfficeSpec) -> str:
    if is_zh(spec.language):
        return f"""# Agent Office

这是 `{spec.project_name}` 的项目办公室。

## 公共区

所有员工都可以读取本文件夹根目录里的公共文件：

- `status.md`：当前项目状态
- `project-brief.md`：项目目标、受众、范围和角色决策
- `project-map.md`：项目文件地图和旧项目接管线索
- `task-board.md`：当前任务、负责人、审查人和写入范围
- `communication.md`：跨角色消息、交接和升级
- `decisions.md`：长期决策
- `thread-registry.md`：长期对话框和角色启动提示

## 私有区

`Employees/` 下每个角色一个文件夹。角色默认只读自己的文件夹，不读其他员工文件夹。

## 归档区

`Archive/Legacy Management/` 是旧框架吸收后的人工查看和审计材料。普通工作不要读取它。
"""
    return f"""# Agent Office

This is the project office for `{spec.project_name}`.

## Public Area

All employee roles may read the public files in this folder:

- `status.md`: current project status
- `project-brief.md`: project goal, audience, scope, and role decisions
- `project-map.md`: project file map and migration clues
- `task-board.md`: current tasks, owners, reviewers, and write scopes
- `communication.md`: cross-role messages, handoffs, and escalations
- `decisions.md`: durable decisions
- `thread-registry.md`: long-running windows and role launch prompts

## Private Area

Each role has one folder under `Employees/`. A role reads only its own folder by default.

## Archive

`Archive/Legacy Management/` is human-review/audit material after old frameworks are absorbed. Ordinary role work should not read it.
"""


def render_status(spec: OfficeSpec) -> str:
    today = date.today().isoformat()
    if is_zh(spec.language):
        return f"""# 项目状态

项目：{spec.project_name}
最后更新：{today}
办公室配置：{spec.profile}
项目类型：{spec.project_type}
风险等级：{spec.risk_level}

## 当前目标

{spec.project_goal}

## 当前阶段

第一里程碑：{spec.first_milestone}

## 当前风险

- 风险等级：{spec.risk_level}
- 暂无更具体的风险记录。

## 下一步

确认 `task-board.md` 中的第一项任务是否仍然准确。
"""
    return f"""# Project Status

Project: {spec.project_name}
Last updated: {today}
Office profile: {spec.profile}
Project type: {spec.project_type}
Risk level: {spec.risk_level}

## Current Goal

{spec.project_goal}

## Current Phase

First milestone: {spec.first_milestone}

## Current Risks

- Risk level: {spec.risk_level}
- No specific risks recorded yet.

## Next Step

Confirm whether the first task in `task-board.md` is still accurate.
"""


def render_project_brief(spec: OfficeSpec) -> str:
    today = date.today().isoformat()
    deferred = "\n".join(f"- {item}" for item in spec.deferred_roles)
    if not deferred:
        deferred = "- None recorded yet." if not is_zh(spec.language) else "- 暂无。"
    if is_zh(spec.language):
        role_lines = "\n".join(f"- {role.title} (`{role.slug}`)：{role.mission} 写入范围：{role.write_scope}" for role in spec.roles)
        notes = spec.role_decisions or "角色按当前里程碑动态生成，后续可扩编。"
        return f"""# 项目简报

项目：{spec.project_name}
生成日期：{today}

## 目标

{spec.project_goal}

## 第一里程碑

{spec.first_milestone}

## 访谈决策

- 项目类型：{spec.project_type}
- 办公室配置：{spec.profile}
- 风险等级：{spec.risk_level}
- 当前角色：{role_titles(spec.roles)}

## 角色决策

{notes}

{role_lines}

## 暂不创建的角色

{deferred}
"""
    role_lines = "\n".join(f"- {role.title} (`{role.slug}`): {role.mission} Write scope: {role.write_scope}" for role in spec.roles)
    notes = spec.role_decisions or "Roles were generated dynamically for the current milestone and can be expanded later."
    return f"""# Project Brief

Project: {spec.project_name}
Generated: {today}

## Goal

{spec.project_goal}

## First Milestone

{spec.first_milestone}

## Interview Decisions

- Project type: {spec.project_type}
- Office profile: {spec.profile}
- Risk level: {spec.risk_level}
- Current roles: {role_titles(spec.roles)}

## Role Decisions

{notes}

{role_lines}

## Deferred Roles

{deferred}
"""


def render_project_map(spec: OfficeSpec) -> str:
    if is_zh(spec.language):
        return """# 项目地图

状态：待扫描

## 文件地图

尚未记录。旧项目接管时先完整扫描文件名，再把明显相关的文本候选文件摘要到这里。

## 已吸收的旧资料

暂无。

## 不读取内容的材料

图片、视频、二进制文件、疑似敏感文件和依赖/构建目录只记录文件名或跳过内容读取。
"""
    return """# Project Map

Status: pending scan

## File Map

No scan recorded yet. During takeover, scan filenames first, then summarize clearly relevant text candidates here.

## Absorbed Legacy Material

None recorded yet.

## Content Not Read

Images, videos, binary files, sensitive-looking files, dependencies, and build output should be listed by filename or skipped without content reads.
"""


def render_task_board(spec: OfficeSpec) -> str:
    today = date.today().isoformat()
    owner = first_role_title(spec)
    reviewer = reviewer_title(spec)
    if is_zh(spec.language):
        return f"""# 任务板

最后更新：{today}

| Task | Owner | Status | Reviewer | Write Scope | Notes |
|---|---|---|---|---|---|
| T-000 | {owner} | proposed | {reviewer} | Agent Office public files | {spec.first_milestone} |

## 任务规则

- 每项任务必须有 owner、reviewer、写入范围和验收方式。
- 如果任务变复杂，再拆出单独任务文件或归档记录。
"""
    return f"""# Task Board

Last updated: {today}

| Task | Owner | Status | Reviewer | Write Scope | Notes |
|---|---|---|---|---|---|
| T-000 | {owner} | proposed | {reviewer} | Agent Office public files | {spec.first_milestone} |

## Task Rules

- Every task needs an owner, reviewer, write scope, and verification approach.
- If a task grows too large, split it into a separate task note or archive record.
"""


def render_decisions(language: str) -> str:
    if is_zh(language):
        return """# 决策记录

| ID | Status | Owner | Decision | Notes |
|---|---|---|---|---|
| D-000 | proposed | Project owner | 暂无长期决策 | 需要时再记录 |
"""
    return """# Decisions

| ID | Status | Owner | Decision | Notes |
|---|---|---|---|---|
| D-000 | proposed | Project owner | No durable decisions yet | Record when needed |
"""


def render_communication(language: str) -> str:
    if is_zh(language):
        return """# 沟通与交接

## 消息规则

- 职责外请求不要直接执行；先说明应该由哪个角色负责。
- 需要跨角色处理时，在本文件追加一条消息记录，写清楚 from、to、task、requested response、next owner。
- 任务完成、阻塞、换 owner 或进入 review 时，在本文件追加交接记录。

## Open Messages

暂无。

## Handoffs

暂无。
"""
    return """# Communication And Handoffs

## Message Rules

- Do not perform out-of-scope requests directly; name the role that should own the work.
- When cross-role coordination is needed, append a message here with from, to, task, requested response, and next owner.
- When work is done, blocked, changes owner, or enters review, append a handoff here.

## Open Messages

None.

## Handoffs

None.
"""


def render_employee_readme(spec: OfficeSpec, role: RoleSpec) -> str:
    if is_zh(spec.language):
        return f"""# {role.title}

## 使命

{role.mission}

## 权限

{role.authority}

## 写入范围

{role.write_scope}

## 当前任务

{role.current_assignment}

## 交接对象

{role.handoff_to}

## 边界

- 默认只读取本员工文件夹。
- 不读取其他员工文件夹，除非用户明确要求维护、审计或恢复办公室。
- 职责外请求先路由给合适角色或协调角色。
"""
    return f"""# {role.title}

## Mission

{role.mission}

## Authority

{role.authority}

## Write Scope

{role.write_scope}

## Current Assignment

{role.current_assignment}

## Handoff Target

{role.handoff_to}

## Boundaries

- Read this employee folder by default.
- Do not read other employee folders unless the user explicitly asks for office maintenance, audit, or recovery.
- Route out-of-scope requests to the right role or coordinator.
"""


def render_employee_memory(spec: OfficeSpec, role: RoleSpec) -> str:
    today = date.today().isoformat()
    if is_zh(spec.language):
        return f"""# {role.title} Memory

Owner role: `{role.slug}`
Privacy: protocol-private. 默认只有 `{role.title}` 读取和更新。
Last updated: {today}

## 长期要点

- 初始使命：{role.mission}
- 写入范围：{role.write_scope}
- 交接对象：{role.handoff_to}

## 用户偏好

- 暂无。

## 接续记录

- 保持简短，只记录这个角色下次接续真正需要的事实。
- 共享项目事实写到公共区，不要塞进这里。
"""
    return f"""# {role.title} Memory

Owner role: `{role.slug}`
Privacy: protocol-private. By default only `{role.title}` reads and updates this file.
Last updated: {today}

## Durable Notes

- Initial mission: {role.mission}
- Write scope: {role.write_scope}
- Handoff target: {role.handoff_to}

## User Preferences

- None recorded yet.

## Continuity Notes

- Keep this short and record only facts this role needs next time.
- Put shared project truth in the public area, not here.
"""


def render_employee_task(spec: OfficeSpec, role: RoleSpec) -> str:
    if is_zh(spec.language):
        return f"""# Current Task

当前任务：{role.current_assignment}

## 必读

- `Agent Office/README.md`
- `Agent Office/status.md`
- `Agent Office/project-brief.md`
- `Agent Office/task-board.md`
- 本文件夹的 `README.md`
- 本文件夹的 `memory.md`

## 写入范围

{role.write_scope}

## 完成时

- 更新本文件或 `memory.md` 中的接续信息。
- 如有跨角色交接，更新 `Agent Office/communication.md`。
"""
    return f"""# Current Task

Current assignment: {role.current_assignment}

## Required Reading

- `Agent Office/README.md`
- `Agent Office/status.md`
- `Agent Office/project-brief.md`
- `Agent Office/task-board.md`
- this folder's `README.md`
- this folder's `memory.md`

## Write Scope

{role.write_scope}

## On Completion

- Update continuity notes in this file or `memory.md`.
- If another role needs context, update `Agent Office/communication.md`.
"""


def render_prompt_body(spec: OfficeSpec, role: RoleSpec) -> str:
    if is_zh(spec.language):
        return f"""你是本项目的 {role.title} Agent 员工。

项目：{spec.project_name}
当前任务：{role.current_assignment}
写入范围：{role.write_scope}
交接对象：{role.handoff_to}

请先读取：
1. AGENTS.md
2. Agent Office/README.md
3. Agent Office/status.md
4. Agent Office/project-brief.md
5. Agent Office/task-board.md
6. Agent Office/Employees/{role.slug}/README.md
7. Agent Office/Employees/{role.slug}/memory.md
8. Agent Office/Employees/{role.slug}/current-task.md

工作规则：
- 只加载和当前任务相关的上下文。
- 默认只读取自己的员工文件夹，不读取其他员工文件夹。
- 日常工作不要读取 Agent Office/Archive/Legacy Management/。
- 不要超出写入范围。
- 如果用户要求你处理职责外的事情，先说明应由哪个角色负责，或在 Agent Office/communication.md 里留下消息。
- 重要工作结束后更新自己的 memory.md 或 current-task.md，并在需要时写交接。
"""
    return f"""You are the {role.title} agent employee for this project.

Project: {spec.project_name}
Current assignment: {role.current_assignment}
Write scope: {role.write_scope}
Handoff target: {role.handoff_to}

Read first:
1. AGENTS.md
2. Agent Office/README.md
3. Agent Office/status.md
4. Agent Office/project-brief.md
5. Agent Office/task-board.md
6. Agent Office/Employees/{role.slug}/README.md
7. Agent Office/Employees/{role.slug}/memory.md
8. Agent Office/Employees/{role.slug}/current-task.md

Rules:
- Load only task-relevant context.
- Read only your own employee folder by default; do not read other employee folders.
- Do not read Agent Office/Archive/Legacy Management/ during ordinary work.
- Do not exceed the approved write scope.
- If the user asks for out-of-scope work, name the role that should own it or leave a message in Agent Office/communication.md.
- After significant work, update your own memory.md or current-task.md and write a handoff when needed.
"""


def render_thread_registry(spec: OfficeSpec) -> str:
    today = date.today().isoformat()
    rows = []
    for index, role in enumerate(spec.roles):
        status = "active" if index == 0 else "waiting"
        rows.append(
            f"| {role.title} | {spec.project_name} / {role.title} | TBD | {role.thread_mode} | {role.current_assignment} | {role.write_scope} | {status} |"
        )
    if is_zh(spec.language):
        sections = [
            "# 线程登记表",
            "",
            f"最后更新：{today}",
            "",
            "| Role | Thread Title | Thread ID | Mode | Current Assignment | Write Scope | Status |",
            "|---|---|---|---|---|---|---|",
            *rows,
            "",
            "## 角色启动提示词",
            "",
            "默认手动创建长期对话框。下面每个 `text` 代码框只放要发给新窗口的第一条消息。",
            "",
        ]
        for role in spec.roles:
            sections.extend(
                [
                    f"### {role.title}",
                    "",
                    f"**新建一个窗口：{role.title}**",
                    f"建议标题：`{spec.project_name} / {role.title}`",
                    "",
                    "```text",
                    render_prompt_body(spec, role).rstrip(),
                    "```",
                    "",
                ]
            )
        return "\n".join(sections)
    sections = [
        "# Thread Registry",
        "",
        f"Last updated: {today}",
        "",
        "| Role | Thread Title | Thread ID | Mode | Current Assignment | Write Scope | Status |",
        "|---|---|---|---|---|---|---|",
        *rows,
        "",
        "## Role Launch Prompts",
        "",
        "Create one long-running window for each approved role. Each `text` block contains only the first message to send.",
        "",
    ]
    for role in spec.roles:
        sections.extend(
            [
                f"### {role.title}",
                "",
                f"**Create a new window: {role.title}**",
                f"Suggested title: `{spec.project_name} / {role.title}`",
                "",
                "```text",
                render_prompt_body(spec, role).rstrip(),
                "```",
                "",
            ]
        )
    return "\n".join(sections)


def spec_to_json(spec: OfficeSpec) -> str:
    payload = asdict(spec)
    payload["office_directory"] = OFFICE_DIR
    payload["agents_apply_phrase"] = "确认应用 AGENTS.md"
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def backup_path(path: Path) -> Path:
    stamp = date.today().isoformat()
    candidate = path.with_name(f"{path.name}.gaogao-office-{stamp}.bak")
    if not candidate.exists() and not candidate.is_symlink():
        return candidate
    for index in range(2, 1000):
        candidate = path.with_name(f"{path.name}.gaogao-office-{stamp}.{index}.bak")
        if not candidate.exists() and not candidate.is_symlink():
            return candidate
    raise SystemExit(f"Could not create a unique backup path for: {path}")


def is_link(path: Path) -> bool:
    is_junction = getattr(path, "is_junction", lambda: False)
    return path.is_symlink() or is_junction()


def has_link_in_path(root: Path, path: Path) -> bool:
    try:
        relative = path.relative_to(root)
    except ValueError:
        return True
    current = root
    for part in relative.parts:
        current = current / part
        if current.exists() and is_link(current):
            return True
    return False


def assert_safe_target(root: Path, path: Path) -> None:
    resolved_root = root.resolve()
    resolved_target = path.resolve(strict=False)
    try:
        resolved_target.relative_to(resolved_root)
    except ValueError:
        raise SystemExit(f"Refusing to write outside project root via symlink or resolved path: {path}")
    if has_link_in_path(root, path.parent if path.parent.exists() else path):
        raise SystemExit(f"Refusing to write through symlink or junction: {path}")


def is_unsafe_root(root: Path) -> bool:
    home = Path.home().resolve()
    if root.parent == root or root == home:
        return True
    return any(part.lower() == ".git" for part in root.parts)


def safe_write(
    path: Path,
    content: str,
    *,
    root: Path,
    force: bool,
    confirm_overwrite: bool,
    dry_run: bool,
    actions: list[dict[str, Any]],
) -> None:
    assert_safe_target(root, path)
    action = "write"
    backup = None
    if path.exists():
        if not force:
            action = "skip-existing"
        elif not confirm_overwrite:
            action = "refuse-overwrite"
        else:
            action = "overwrite"
            backup = str(backup_path(path))
    actions.append({"action": action, "path": str(path), **({"backup": backup} if backup else {})})
    if dry_run or action == "skip-existing":
        return
    if action == "refuse-overwrite":
        raise SystemExit(f"Refusing to overwrite existing file without confirmation: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    if action == "overwrite" and backup:
        shutil.copy2(path, backup)
    path.write_text(content, encoding="utf-8", newline="\n")


def planned_scaffold_files(root: Path, roles: list[RoleSpec], *, apply_agents: bool) -> list[Path]:
    office = root / OFFICE_DIR
    files = [
        office / "README.md",
        office / "status.md",
        office / "project-brief.md",
        office / "project-map.md",
        office / "task-board.md",
        office / "communication.md",
        office / "decisions.md",
        office / "thread-registry.md",
        office / "office-plan.json",
        office / PROPOSALS_DIR / "AGENTS.proposed.md",
        office / ARCHIVE_DIR / LEGACY_ARCHIVE_DIR / ".gitkeep",
    ]
    if apply_agents:
        files.append(root / "AGENTS.md")
    for role in roles:
        base = office / EMPLOYEES_DIR / role.slug
        files.extend([base / "README.md", base / "memory.md", base / "current-task.md"])
    return files


def write_scaffold(root: Path, spec: OfficeSpec, args: argparse.Namespace) -> list[dict[str, Any]]:
    office = root / OFFICE_DIR
    actions: list[dict[str, Any]] = []
    planned = planned_scaffold_files(root, spec.roles, apply_agents=args.apply_agents)
    for target in planned:
        assert_safe_target(root, target)
    if args.apply_agents and not args.confirm_apply_agents:
        raise SystemExit("Refusing to apply AGENTS.md without --confirm-apply-agents. Use it only after the user says `确认应用 AGENTS.md`.")
    if args.force and not args.confirm_overwrite and not args.dry_run:
        existing = [path for path in planned if path.exists() and path.name != "AGENTS.md"]
        if existing:
            preview = ", ".join(str(path) for path in existing[:5])
            suffix = " ..." if len(existing) > 5 else ""
            raise SystemExit(f"Refusing --force without --confirm-overwrite because existing office files were found: {preview}{suffix}")
    if not args.dry_run:
        root.mkdir(parents=True, exist_ok=True)
    write_kwargs = {
        "root": root,
        "force": args.force,
        "confirm_overwrite": args.confirm_overwrite,
        "dry_run": args.dry_run,
        "actions": actions,
    }
    safe_write(office / "README.md", render_readme(spec), **write_kwargs)
    safe_write(office / "status.md", render_status(spec), **write_kwargs)
    safe_write(office / "project-brief.md", render_project_brief(spec), **write_kwargs)
    safe_write(office / "project-map.md", render_project_map(spec), **write_kwargs)
    safe_write(office / "task-board.md", render_task_board(spec), **write_kwargs)
    safe_write(office / "communication.md", render_communication(spec.language), **write_kwargs)
    safe_write(office / "decisions.md", render_decisions(spec.language), **write_kwargs)
    safe_write(office / "thread-registry.md", render_thread_registry(spec), **write_kwargs)
    safe_write(office / "office-plan.json", spec_to_json(spec), **write_kwargs)
    safe_write(office / PROPOSALS_DIR / "AGENTS.proposed.md", render_agents_proposal(spec.language), **write_kwargs)
    for role in spec.roles:
        employee = office / EMPLOYEES_DIR / role.slug
        safe_write(employee / "README.md", render_employee_readme(spec, role), **write_kwargs)
        safe_write(employee / "memory.md", render_employee_memory(spec, role), **write_kwargs)
        safe_write(employee / "current-task.md", render_employee_task(spec, role), **write_kwargs)
    safe_write(office / ARCHIVE_DIR / LEGACY_ARCHIVE_DIR / ".gitkeep", "", **write_kwargs)
    if args.apply_agents:
        safe_write(
            root / "AGENTS.md",
            render_agents_proposal(spec.language),
            root=root,
            force=True,
            confirm_overwrite=args.confirm_apply_agents,
            dry_run=args.dry_run,
            actions=actions,
        )
    return actions


def main() -> int:
    parser = argparse.ArgumentParser(description="Scaffold a lightweight GAOGAO Office project office.")
    parser.add_argument("--project-root", default=".", help="Project root to scaffold")
    parser.add_argument("--config", default=None, help="Path to office-plan.json with dynamic role definitions")
    parser.add_argument("--project-name", default=None, help="Project display name")
    parser.add_argument("--project-goal", default="Define the first milestone.", help="Initial project goal")
    parser.add_argument("--project-type", default="unspecified", help="Project type from the user interview")
    parser.add_argument(
        "--risk-level",
        choices=["unspecified", "low", "medium", "high", "critical"],
        default="unspecified",
        help="Risk level from the user interview",
    )
    parser.add_argument("--first-milestone", default="Define the first milestone.", help="First milestone from the user interview")
    parser.add_argument("--profile", choices=["minimal", "standard", "expanded", "dynamic"], default="standard")
    parser.add_argument("--roles", default="", help="Comma-separated legacy role keys, e.g. pm,builder,reviewer")
    parser.add_argument("--language", choices=["en", "zh-CN"], default=None, help="Language for generated user-facing docs")
    parser.add_argument("--apply-agents", action="store_true", help="Apply the proposed AGENTS.md to the project root")
    parser.add_argument("--confirm-apply-agents", action="store_true", help="Required with --apply-agents after user approval")
    parser.add_argument("--force", action="store_true", help="Overwrite existing office files, excluding AGENTS.md")
    parser.add_argument("--confirm-overwrite", action="store_true", help="Required with --force to overwrite existing office files")
    parser.add_argument("--create-root", action="store_true", help="Create --project-root if it does not already exist")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without writing files")
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    if is_unsafe_root(root):
        raise SystemExit(f"Refusing to scaffold into unsafe root: {root}")
    if not root.exists() and not args.create_root and not args.dry_run:
        raise SystemExit(f"Project root does not exist. Create it first or pass --create-root: {root}")
    spec = load_office_spec(args, root)
    validate_roles(spec.roles)
    actions = write_scaffold(root, spec, args)
    result = {
        "project_root": str(root),
        "office_dir": OFFICE_DIR,
        "project_name": spec.project_name,
        "project_type": spec.project_type,
        "risk_level": spec.risk_level,
        "first_milestone": spec.first_milestone,
        "profile": spec.profile,
        "language": spec.language,
        "roles": [role.slug for role in spec.roles],
        "role_details": [asdict(role) for role in spec.roles],
        "apply_agents": args.apply_agents,
        "dry_run": args.dry_run,
        "actions": actions,
    }
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        for item in actions:
            print(f"{item['action']}: {item['path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
