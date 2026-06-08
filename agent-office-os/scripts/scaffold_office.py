#!/usr/bin/env python3
"""Scaffold an Agent Office OS project office.

The script only writes inside the selected project root. It never deletes files
and skips existing files unless --force is provided.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any


ROLE_DEFINITIONS = {
    "pm": {
        "title": "PM / Coordinator",
        "mission": "Maintain project status, assign tasks, manage scope, and coordinate agent employee threads.",
        "authority": "May update status, thread registry, task packets, messages, and handoffs.",
    },
    "architect": {
        "title": "Architect",
        "mission": "Maintain architecture boundaries, ADRs, dependencies, and cross-module decisions.",
        "authority": "May update decisions and architecture notes; code changes require explicit task assignment.",
    },
    "builder": {
        "title": "Builder",
        "mission": "Implement assigned tasks inside the approved write scope and provide verification.",
        "authority": "May change only files listed in the active task packet.",
    },
    "reviewer": {
        "title": "Reviewer",
        "mission": "Review diffs for correctness, regressions, security, scope, and missing tests.",
        "authority": "Read-heavy by default; writes review notes, messages, and handoffs unless assigned code changes.",
    },
    "archivist": {
        "title": "Archivist",
        "mission": "Keep the office clean, archive stale records, reduce context load, and retire old threads.",
        "authority": "May update office docs and archive records; does not change product code.",
    },
    "qa": {
        "title": "QA",
        "mission": "Own acceptance scenarios, regression checks, and release confidence.",
        "authority": "May update QA notes, test plans, messages, and handoffs.",
    },
    "security": {
        "title": "Security",
        "mission": "Review threat models, sensitive data, permissions, dependencies, and unsafe automation.",
        "authority": "May update security notes, decisions, and blocker messages.",
    },
    "ux": {
        "title": "UX",
        "mission": "Review user flows, accessibility, interaction states, and user-facing clarity.",
        "authority": "May update UX notes, acceptance criteria, messages, and handoffs.",
    },
    "data": {
        "title": "Data",
        "mission": "Review data models, metrics definitions, migrations, analytics, and data quality risks.",
        "authority": "May update data notes, decisions, messages, and handoffs.",
    },
    "release": {
        "title": "Release",
        "mission": "Review release notes, rollout plans, rollback steps, versioning, and launch readiness.",
        "authority": "May update release notes, cadences, messages, and handoffs.",
    },
}

ROLE_WRITE_SCOPES = {
    "pm": "office docs",
    "architect": "decisions and architecture notes",
    "builder": "task scope only",
    "reviewer": "read-heavy by default",
    "archivist": "office archive and status",
    "qa": "test plans and acceptance notes",
    "security": "security notes and blockers",
    "ux": "UX notes and acceptance criteria",
    "data": "data notes and decisions",
    "release": "release notes and rollout plans",
}

ROLE_ASSIGNMENTS = {
    "pm": "T-000",
    "architect": "TBD",
    "builder": "TBD",
    "reviewer": "T-000 review",
    "archivist": "office hygiene",
    "qa": "TBD",
    "security": "TBD",
    "ux": "TBD",
    "data": "TBD",
    "release": "TBD",
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
    if not slug:
        slug = fallback
    return slug[:40].strip("-") or fallback


def validate_slug(slug: str) -> None:
    if not re.fullmatch(r"[a-z][a-z0-9-]{0,39}", slug):
        raise SystemExit(f"Invalid role slug `{slug}`. Use lowercase letters, digits, and hyphens.")


def normalize_thread_mode(raw: Any) -> str:
    value = str(raw or "local").strip().lower()
    if value in {"worktree", "branch"}:
        return "worktree"
    return "local"


def role_from_legacy_key(role: str) -> RoleSpec:
    definition = ROLE_DEFINITIONS[role]
    return RoleSpec(
        slug=role,
        title=definition["title"],
        mission=definition["mission"],
        authority=definition["authority"],
        write_scope=ROLE_WRITE_SCOPES.get(role, "task scope only"),
        current_assignment=ROLE_ASSIGNMENTS.get(role, "TBD"),
        thread_mode="worktree" if role == "builder" else "local",
        handoff_to="PM / Coordinator" if role != "pm" else "Project owner",
    )


def parse_roles(raw: str, profile: str) -> list[RoleSpec]:
    if raw:
        role_keys = [part.strip().lower() for part in raw.split(",") if part.strip()]
    elif profile == "minimal":
        role_keys = ["pm", "builder", "reviewer"]
    elif profile == "expanded":
        role_keys = ["pm", "architect", "builder", "reviewer", "archivist", "qa", "security"]
    else:
        role_keys = ["pm", "architect", "builder", "reviewer", "archivist"]
    unknown = [role for role in role_keys if role not in ROLE_DEFINITIONS]
    if unknown:
        raise SystemExit(f"Unknown role(s): {', '.join(unknown)}")
    duplicates = sorted({role for role in role_keys if role_keys.count(role) > 1})
    if duplicates:
        raise SystemExit(f"Duplicate role(s): {', '.join(duplicates)}")
    return [role_from_legacy_key(role) for role in role_keys]


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


def role_from_config(raw: dict[str, Any], index: int, default_handoff: str) -> RoleSpec:
    title = coalesce(raw.get("title"), raw.get("name"), default=f"Role {index + 1}")
    slug = coalesce(raw.get("slug"), default=slugify(title, f"role-{index + 1}")).lower()
    slug = slugify(slug, f"role-{index + 1}")
    validate_slug(slug)
    return RoleSpec(
        slug=slug,
        title=title,
        mission=coalesce(
            raw.get("mission"),
            raw.get("purpose"),
            default="Own a distinct part of the approved project workflow.",
        ),
        authority=coalesce(
            raw.get("authority"),
            raw.get("boundaries"),
            default="May update only the approved write scope and office records for assigned work.",
        ),
        write_scope=coalesce(raw.get("write_scope"), raw.get("writeScope"), default="task scope only"),
        current_assignment=coalesce(
            raw.get("current_assignment"),
            raw.get("assignment"),
            raw.get("currentAssignment"),
            default="TBD",
        ),
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
        if role.handoff_to:
            continue
        role.handoff_to = fallback_owner if role.title == inferred else inferred


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
    roles = []
    for index, item in enumerate(role_items):
        if not isinstance(item, dict):
            raise SystemExit("Each role in config must be a JSON object.")
        roles.append(role_from_config(item, index, default_handoff))
    fill_missing_handoffs(roles, default_handoff, language)
    validate_roles(roles)
    return OfficeSpec(
        project_name=coalesce(raw.get("project_name"), raw.get("name"), args.project_name, root.name, default="Project"),
        project_goal=coalesce(raw.get("project_goal"), raw.get("goal"), args.project_goal, default="Define the first milestone."),
        profile=coalesce(raw.get("profile"), args.profile, default="dynamic"),
        project_type=coalesce(raw.get("project_type"), raw.get("type"), args.project_type, default="unspecified"),
        risk_level=coalesce(raw.get("risk_level"), args.risk_level, default="unspecified"),
        first_milestone=coalesce(
            raw.get("first_milestone"),
            raw.get("milestone"),
            args.first_milestone,
            default="Define the first milestone.",
        ),
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


def validate_roles(roles: list[RoleSpec]) -> None:
    if not roles:
        raise SystemExit("At least one role is required.")
    slugs = [role.slug for role in roles]
    duplicates = sorted({slug for slug in slugs if slugs.count(slug) > 1})
    if duplicates:
        raise SystemExit(f"Duplicate role slug(s): {', '.join(duplicates)}")
    for role in roles:
        validate_slug(role.slug)


def role_titles(roles: list[RoleSpec]) -> str:
    return ", ".join(role.title for role in roles)


def first_role_title(spec: OfficeSpec) -> str:
    return spec.roles[0].title if spec.roles else "Project owner"


def reviewer_title(spec: OfficeSpec) -> str:
    for role in spec.roles:
        haystack = f"{role.slug} {role.title}".lower()
        if "review" in haystack or "qa" in haystack:
            return role.title
    return spec.roles[1].title if len(spec.roles) > 1 else first_role_title(spec)


def render_agents(language: str) -> str:
    if is_zh(language):
        return """# AGENTS.md

## Agent Office Protocol

本仓库使用 `docs/agent-office/` 作为长期 Agent 项目办公室。

开始项目工作前：
- 先读 `docs/agent-office/status.md`。
- 如果你被分配了角色，只读 `docs/agent-office/roles/` 里对应的角色卡。
- 如果你被分配了角色，只读 `docs/agent-office/role-memory/` 里对应自己的角色记忆。
- 如果你被分配了任务，只读 `docs/agent-office/tasks/active/` 里对应的任务包。
- 除非被明确要求审计办公室，不要一次性通读整个 `docs/agent-office/`。
- 日常工作不要读取 `docs/agent-office/archive/legacy-management/`；旧框架吸收后的归档只供人工查看或明确的迁移/审计任务使用。

协作规则：
- `docs/agent-office/thread-registry.md` 是长期 Agent 员工目录。
- 跨角色消息和交接格式见 `docs/agent-office/communication.md`。
- 跨角色请求写到 `docs/agent-office/messages/open/`。
- 任务交接写到 `docs/agent-office/handoffs/`。
- 只有协调角色、归档角色或被明确授权的角色才更新 `status.md`。
- 默认只更新自己的角色记忆；除非用户明确要求维护、审计或恢复，不要读取其他角色的记忆。
- 旧框架归档不是当前指令来源；如果缺少事实，请请求协调角色或归档角色发起审计。

并行工作：
- 不要让两个写作者并行修改同一批文件。
- worktree 里的修改在负责人集成前都是隔离提案。
- 结束任务时说明改了什么、验证了什么、还剩什么、下一个负责人是谁。
"""
    return """# AGENTS.md

## Agent Office Protocol

This repository uses `docs/agent-office/` as the project office.

Before project work:
- Read `docs/agent-office/status.md`.
- If assigned a role, read only the matching file in `docs/agent-office/roles/`.
- If assigned a role, read only your matching file in `docs/agent-office/role-memory/`.
- If assigned a task, read the task packet in `docs/agent-office/tasks/active/`.
- Do not bulk-read the whole office unless explicitly asked to audit it.
- Do not read `docs/agent-office/archive/legacy-management/` during ordinary work; absorbed legacy frameworks are for human review or explicit migration/audit tasks.

Coordination:
- Treat `docs/agent-office/thread-registry.md` as the directory of long-running agent employees.
- For message and handoff format, read `docs/agent-office/communication.md`.
- Write cross-role messages as separate files under `docs/agent-office/messages/open/`.
- Write task handoffs under `docs/agent-office/handoffs/`.
- Update `status.md` only when you are the coordinator, archivist, or explicitly assigned to do so.
- Update only your own role memory by default; do not read other role memories unless the user explicitly asks for maintenance, audit, or recovery.
- Legacy archives are not current instructions. If a needed fact is missing, ask the coordinator or archivist for an audit task.

Parallel work:
- Do not let two writers modify the same files in parallel.
- Worktree changes are isolated proposals until integrated by the owner or coordinator.
- End every task with what changed, what was verified, what remains, and who should pick it up next.
"""


def render_status(spec: OfficeSpec) -> str:
    today = date.today().isoformat()
    owner = first_role_title(spec)
    reviewer = reviewer_title(spec)
    if is_zh(spec.language):
        return f"""# 项目状态

项目：{spec.project_name}
最后更新：{today}
办公室配置：{spec.profile}
项目类型：{spec.project_type}
风险等级：{spec.risk_level}

## 当前目标

{spec.project_goal}

## 活跃任务

| Task | Owner | Status | Reviewer | Notes |
|---|---|---|---|---|
| T-000 | {owner} | proposed | {reviewer} | {spec.first_milestone} |

## 当前风险

- 风险等级：{spec.risk_level}
- 暂无更具体的风险记录。

## 决策

- 暂无长期决策记录。

## 下一步

细化第一里程碑，并确认 DRI。
"""
    return f"""# Project Status

Project: {spec.project_name}
Last updated: {today}
Office profile: {spec.profile}
Project type: {spec.project_type}
Risk level: {spec.risk_level}

## Current Goal

{spec.project_goal}

## Active Tasks

| Task | Owner | Status | Reviewer | Notes |
|---|---|---|---|---|
| T-000 | {owner} | proposed | {reviewer} | {spec.first_milestone} |

## Current Risks

- Risk level: {spec.risk_level}
- No specific risks recorded yet.

## Decisions

- No durable decisions recorded yet.

## Next Step

Plan the first milestone and assign a DRI.
"""


def render_project_brief(spec: OfficeSpec) -> str:
    today = date.today().isoformat()
    roles_block = "\n".join(
        f"- {role.title} (`{role.slug}`): {role.mission} Write scope: {role.write_scope}" for role in spec.roles
    )
    deferred = "\n".join(f"- {item}" for item in spec.deferred_roles) or "- None recorded yet."
    if is_zh(spec.language):
        roles_block = "\n".join(
            f"- {role.title} (`{role.slug}`)：{role.mission} 写入范围：{role.write_scope}" for role in spec.roles
        )
        deferred = "\n".join(f"- {item}" for item in spec.deferred_roles) or "- 暂无。"
        notes = spec.role_decisions or "角色按当前里程碑动态生成，后续可扩编。"
        return f"""# 项目简报

项目：{spec.project_name}
生成日期：{today}

## 访谈决策

- 项目类型：{spec.project_type}
- 办公室配置：{spec.profile}
- 风险等级：{spec.risk_level}
- 长期角色：{role_titles(spec.roles)}

## 目标

{spec.project_goal}

## 第一里程碑

{spec.first_milestone}

## 角色决策

{notes}

{roles_block}

## 暂不创建的角色

{deferred}

## 运行备注

- 保持常驻上下文短小。
- 项目细节放到任务包、ADR 和交接记录里。
- 只有项目形态变化时才更新这份简报。
"""
    notes = spec.role_decisions or "Roles were generated dynamically for the current milestone and can be expanded later."
    return f"""# Project Brief

Project: {spec.project_name}
Generated: {today}

## Interview Decisions

- Project type: {spec.project_type}
- Office profile: {spec.profile}
- Risk level: {spec.risk_level}
- Standing roles: {role_titles(spec.roles)}

## Goal

{spec.project_goal}

## First Milestone

{spec.first_milestone}

## Role Decisions

{notes}

{roles_block}

## Deferred Roles

{deferred}

## Operating Notes

- Keep always-loaded context short.
- Put project-specific detail in task packets, ADRs, and handoffs.
- Update this brief only when the project shape changes.
"""


def render_thread_registry(spec: OfficeSpec) -> str:
    today = date.today().isoformat()
    rows = []
    for index, role in enumerate(spec.roles):
        status = "active" if index == 0 else "waiting"
        rows.append(
            f"| {role.title} | {spec.project_name} / {role.title} | TBD | {role.thread_mode} | "
            f"{role.authority} | {role.current_assignment} | {role.write_scope} | {status} |"
        )
    title = "Thread Registry" if not is_zh(spec.language) else "线程登记表"
    return f"""# {title}

Last updated: {today}

| Role | Thread Title | Thread ID | Mode | Authority | Current Assignment | Write Scope | Status |
|---|---|---|---|---|---|---|---|
{chr(10).join(rows)}
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
2. docs/agent-office/status.md
3. docs/agent-office/context-packs/project-brief.md
4. docs/agent-office/roles/{role.slug}.md
5. docs/agent-office/role-memory/{role.slug}.md
6. docs/agent-office/thread-registry.md
7. docs/agent-office/communication.md
8. 如果已有分配任务，再读取对应的任务包

工作规则：
- 只加载和当前任务相关的上下文。
- 只读取和更新自己的角色记忆：docs/agent-office/role-memory/{role.slug}.md。除非用户明确要求维护、审计或恢复办公室，不要读取其他角色记忆。
- 日常工作不要读取 docs/agent-office/archive/legacy-management/；旧框架归档只供人工查看或明确的迁移/审计任务使用。
- 不要超出写入范围。
- 如果用户要求你处理超出写入范围的事情，不要直接执行；告诉用户应由哪个角色负责，或在 docs/agent-office/messages/open/ 写给交接对象/协调角色的消息。
- 跨角色请求写成单独文件，放到 docs/agent-office/messages/open/。
- 重要工作结束后，在 docs/agent-office/handoffs/ 写交接。
- 重要工作结束后，用简短要点更新自己的角色记忆，记录下次接续需要的事实；不要粘贴完整聊天记录。
- 不要静默修改无关的项目管理文件。
"""
    return f"""You are the {role.title} agent employee for this project.

Project: {spec.project_name}
Current assignment: {role.current_assignment}
Write scope: {role.write_scope}
Handoff target: {role.handoff_to}

Read:
1. AGENTS.md
2. docs/agent-office/status.md
3. docs/agent-office/context-packs/project-brief.md
4. docs/agent-office/roles/{role.slug}.md
5. docs/agent-office/role-memory/{role.slug}.md
6. docs/agent-office/thread-registry.md
7. docs/agent-office/communication.md
8. the assigned task packet, if one exists

Rules:
- Load only task-relevant context.
- Read and update only your own role memory: docs/agent-office/role-memory/{role.slug}.md. Do not read other role memories unless the user explicitly asks for maintenance, audit, or recovery.
- Do not read docs/agent-office/archive/legacy-management/ during ordinary work; legacy archives are for human review or explicit migration/audit tasks.
- Do not exceed the approved write scope.
- If the user asks for work outside your write scope, do not do it silently; name the role that should own it or write a message under docs/agent-office/messages/open/ to your handoff target or coordinator.
- Write cross-role messages as separate files under docs/agent-office/messages/open/.
- End significant work with a handoff under docs/agent-office/handoffs/.
- After significant work, update your own role memory with short durable continuity notes. Do not paste full chat transcripts.
- Do not silently modify unrelated project-management files.
"""


def render_thread_launch_prompts(spec: OfficeSpec) -> str:
    today = date.today().isoformat()
    if is_zh(spec.language):
        sections = [
            "# 角色启动提示词",
            "",
            f"项目：{spec.project_name}",
            f"生成日期：{today}",
            "",
            "默认手动创建长期对话框。下面的说明留在当前窗口；每个 `text` 代码框里只放要发送到新窗口的第一条消息。",
            "",
        ]
        for role in spec.roles:
            sections.extend(
                [
                    f"## {role.title}",
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
        "# Thread Launch Prompts",
        "",
        f"Project: {spec.project_name}",
        f"Generated: {today}",
        "",
        "Create one long-running agent thread for each approved role below. After each thread is created, record its thread ID in `docs/agent-office/thread-registry.md`.",
        "",
    ]
    for role in spec.roles:
        sections.extend(
            [
                f"## {role.title}",
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


def render_role(role: RoleSpec, language: str) -> str:
    if is_zh(language):
        return f"""# {role.title}

## 使命

{role.mission}

## 权限

{role.authority}

## 默认输入

- `AGENTS.md`
- `docs/agent-office/status.md`
- `docs/agent-office/role-memory/{role.slug}.md`
- `docs/agent-office/communication.md`
- 分配给自己的任务包

## 默认输出

- 任务更新
- messages
- handoffs
- 自己的角色记忆
- 被授权时写 decisions

## 写入范围

{role.write_scope}

## 当前任务

{role.current_assignment}

## 交接对象

{role.handoff_to}

## 边界

- 不要超出分配的写入范围。
- 默认只读取和更新自己的角色记忆；除非用户明确要求维护、审计或恢复，不要读取其他角色记忆。
- 如果被要求处理职责外工作，先说明应由哪个角色负责，或写一条 message 给交接对象/协调角色。
- 改变负责人、验收标准或文件归属前先询问协调角色。
- 重要工作结束后写交接。
"""
    return f"""# {role.title}

## Mission

{role.mission}

## Authority

{role.authority}

## Default Inputs

- `AGENTS.md`
- `docs/agent-office/status.md`
- `docs/agent-office/role-memory/{role.slug}.md`
- `docs/agent-office/communication.md`
- assigned task packet

## Default Outputs

- task updates
- messages
- handoffs
- own role memory
- decisions, when authorized

## Write Scope

{role.write_scope}

## Current Assignment

{role.current_assignment}

## Handoff Target

{role.handoff_to}

## Boundaries

- Do not exceed assigned write scope.
- Read and update only your own role memory by default; do not read other role memories unless the user explicitly asks for maintenance, audit, or recovery.
- If asked to do out-of-scope work, name the role that should own it or write a message to the handoff target/coordinator.
- Ask the coordinator before changing ownership or acceptance criteria.
- End significant work with a handoff.
"""


def render_role_memory(role: RoleSpec, language: str) -> str:
    today = date.today().isoformat()
    if is_zh(language):
        return f"""# {role.title} Role Memory

Owner role: `{role.slug}`
Privacy: protocol-private. 默认只有 `{role.title}` 读取和更新；除非用户明确要求维护、审计或恢复办公室，其他角色不要读取。
Last updated: {today}

## 长期要点

- 初始使命：{role.mission}
- 当前任务：{role.current_assignment}
- 写入范围：{role.write_scope}
- 交接对象：{role.handoff_to}

## 用户偏好

- 暂无。

## 接续记录

- 保持简短，只记录这个角色下次接续真正需要的事实。
- 共享项目事实写到 `status.md`、任务包、messages、handoffs 或 ADR，不要塞进这里。
- 不要粘贴完整聊天记录、密钥、隐私信息或大段材料。
"""
    return f"""# {role.title} Role Memory

Owner role: `{role.slug}`
Privacy: protocol-private. By default only the `{role.title}` role reads and updates this file; other roles should not read it unless the user explicitly asks for maintenance, audit, or recovery.
Last updated: {today}

## Durable Notes

- Initial mission: {role.mission}
- Current assignment: {role.current_assignment}
- Write scope: {role.write_scope}
- Handoff target: {role.handoff_to}

## User Preferences

- None recorded yet.

## Continuity Notes

- Keep this file short and record only facts this role needs next time.
- Put shared project truth in `status.md`, task packets, messages, handoffs, or ADRs instead.
- Do not paste full chat transcripts, secrets, private data, or large source excerpts here.
"""


def render_task(spec: OfficeSpec) -> str:
    today = date.today().isoformat()
    owner = first_role_title(spec)
    reviewer = reviewer_title(spec)
    if is_zh(spec.language):
        return f"""---
id: T-000
status: proposed
dri: {owner}
reviewer: {reviewer}
created: {today}
---

# T-000: 定义第一里程碑

## 目标

细化第一里程碑，并确认 DRI。

里程碑：{spec.first_milestone}

## 必读上下文

- `AGENTS.md`
- `docs/agent-office/status.md`
- `docs/agent-office/context-packs/project-brief.md`
- `docs/agent-office/communication.md`

## 写入范围

允许：
- `docs/agent-office/tasks/active/T-000-define-first-milestone.md`
- `docs/agent-office/status.md`

未经批准禁止：
- application code

## 验收标准

- 第一里程碑有明确目标。
- DRI 和 reviewer 已确认。
- 验证方式已命名。
- 角色归属和写入范围清晰。

## 验证

- 协调角色 review。

## 交接

如果后续由其他角色接手实现，写一份 handoff。
"""
    return f"""---
id: T-000
status: proposed
dri: {owner}
reviewer: {reviewer}
created: {today}
---

# T-000: Define First Milestone

## Goal

Plan the first implementation milestone and assign a DRI.

Milestone: {spec.first_milestone}

## Required Context

- `AGENTS.md`
- `docs/agent-office/status.md`
- `docs/agent-office/context-packs/project-brief.md`
- `docs/agent-office/communication.md`

## Write Scope

Allowed:
- `docs/agent-office/tasks/active/T-000-define-first-milestone.md`
- `docs/agent-office/status.md`

Forbidden unless approved:
- application code

## Acceptance Criteria

- First milestone has a goal.
- DRI and reviewer are assigned.
- Verification approach is named.
- Role ownership and write scope are clear.

## Verification

- Coordinator review.

## Handoff

Write a handoff if another role picks up implementation.
"""


def render_operating_model(language: str) -> str:
    if is_zh(language):
        return """# Agent Office Operating Model

## 上下文预算

- 保持 `AGENTS.md` 短小，像目录一样工作。
- `status.md` 只放当前事实。
- 任务细节放进任务包。
- 角色接续事实放进自己的 `role-memory/{role}.md`，不要放进共享状态。
- 过期细节归档，不要塞进常驻文件。

## 并行工作

- 读多写少的工作可以并行。
- 写入型任务需要一个 DRI、一个 reviewer、一个写入范围。
- worktree 修改在负责人或项目 owner 集成前都是隔离提案。

## 完成门槛

任务完成前，确认验收标准、写入范围、检查结果、风险、交接和决策记录。
"""
    return """# Agent Office Operating Model

## Context Budget

- Keep `AGENTS.md` short and index-like.
- Keep `status.md` focused on current facts.
- Put task-specific details into task packets.
- Put role continuity facts into that role's own `role-memory/{role}.md`, not shared status.
- Archive stale detail instead of extending always-loaded files.

## Parallel Work

- Read-heavy work can run in parallel.
- Write-heavy work needs one DRI, one reviewer, and one write scope.
- Worktree changes are isolated proposals until integrated by the coordinator or the owner.

## Completion Gate

Before a task is done, verify acceptance criteria, write scope, checks, risks, handoff, and decision records.
"""


def render_communication(language: str) -> str:
    if is_zh(language):
        return """# Communication Protocol

当多个 Agent 员工线程需要提问、回答、升级、关闭或交接工作时，使用这个文件。

## 消息规则

- 每个跨角色请求创建一个独立文件，放到 `messages/open/`。
- 写清楚接收者、task id、期望回复、紧急程度和下一负责人。
- 职责外请求不要直接执行；写给交接对象或协调角色，让对应角色接手。
- 接收者可以在同一文件中回答，也可以创建回复消息。
- 结论记录后，把已解决或已被取代的消息移动到 `messages/closed/`。
- owner 不清楚时，由协调角色或归档角色关闭旧消息。

## 消息状态

- `status: open` 表示需要回应。
- `status: acknowledged` 表示接收者已看到但还没解决。
- `status: resolved` 表示答案或行动已记录。
- `status: superseded` 表示已被其他任务、消息、ADR 或状态更新取代。

## 交接规则

- 工作换 owner、进入 review、被阻塞或完成时，写 handoff。
- 交接必须包含改了什么、检查了什么、已知风险和 next owner。
- handoff 放到 `handoffs/`，文件名尽量包含 task id。
- 不要把任务标记为完成，除非下一个负责人不用读无关历史也能继续。

## 升级

- security、data、legal、release 或破坏性文件风险应升级为 blocker message。
- 影响架构或产品行为的跨角色分歧应变成 ADR proposal。
- 两个写作者的范围冲突先交给协调角色处理。
"""
    return """# Communication Protocol

Use this file when agent employee threads need to ask, answer, escalate, close, or hand off work.

## Message Rules

- Create one file per cross-role request in `messages/open/`.
- Use a clear recipient, task id, requested response, urgency, and next owner.
- Do not perform out-of-scope requests directly; address them to the handoff target or coordinator so the right role can take over.
- The receiving role may answer in the same file or create a response message.
- Move resolved or superseded messages to `messages/closed/` after the outcome is recorded.
- The coordinator or archivist closes old messages when the owner is unclear.

## Message States

- `status: open` means the message needs a response.
- `status: acknowledged` means the receiver saw it but has not resolved it.
- `status: resolved` means the answer or action is recorded.
- `status: superseded` means another task, message, ADR, or status update replaced it.

## Handoff Rules

- Write a handoff when work changes owner, reaches review, is blocked, or finishes.
- Include what changed, what was checked, known risks, and the next owner.
- Put handoffs in `handoffs/` and include the task id in the filename when possible.
- Do not mark a task done until the next owner can continue without reading unrelated history.

## Escalation

- Security, data, legal, release, or destructive-file risks should become blocker messages.
- Cross-role disagreement that affects architecture or product behavior should become an ADR proposal.
- Scope conflict between two writer roles should go to the coordinator before either thread edits files.
"""


def render_readme(spec: OfficeSpec) -> str:
    if is_zh(spec.language):
        return f"""# Agent Office

这是 `{spec.project_name}` 的项目办公室。

建议读取顺序：

1. `status.md`
2. `context-packs/project-brief.md`，了解项目形态和访谈决策
3. `communication.md`，了解消息和交接规则
4. `roles/` 里和你匹配的角色卡
5. `role-memory/` 里属于你这个角色的记忆文件
6. `tasks/active/` 里分配给你的任务包

除非正在审计、维护或迁移办公室，不要一次性通读整个目录，也不要读取其他角色的记忆。日常工作不要读取 `archive/legacy-management/`，那里是旧框架吸收后的人工查看/审计材料。
"""
    return f"""# Agent Office

This is the project office for `{spec.project_name}`.

Start with:

1. `status.md`
2. `context-packs/project-brief.md` for project shape and interview decisions
3. `communication.md` for messages and handoffs
4. the relevant role card in `roles/`
5. the matching role memory in `role-memory/`
6. the assigned task packet in `tasks/active/`

Do not bulk-read the entire office unless auditing, maintaining, or migrating it. Do not read another role's memory by default. Do not read `archive/legacy-management/` during ordinary role work; it is human-review/audit material after migration absorption.
"""


def backup_path(path: Path) -> Path:
    stamp = date.today().isoformat()
    candidate = path.with_name(f"{path.name}.agent-office-{stamp}.bak")
    if not candidate.exists() and not candidate.is_symlink():
        return candidate
    for index in range(2, 1000):
        candidate = path.with_name(f"{path.name}.agent-office-{stamp}.{index}.bak")
        if not candidate.exists() and not candidate.is_symlink():
            return candidate
    raise SystemExit(f"Could not create a unique backup path for: {path}")


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
        raise SystemExit(f"Refusing to overwrite existing file without --confirm-overwrite: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    if action == "overwrite" and backup:
        shutil.copy2(path, backup)
    path.write_text(content, encoding="utf-8", newline="\n")


def assert_safe_target(root: Path, path: Path) -> None:
    resolved_root = root.resolve()
    resolved_target = path.resolve(strict=False)
    try:
        resolved_target.relative_to(resolved_root)
    except ValueError:
        raise SystemExit(f"Refusing to write outside project root via symlink or resolved path: {path}")


def planned_scaffold_files(root: Path, roles: list[RoleSpec]) -> list[Path]:
    office = root / "docs" / "agent-office"
    files = [
        root / "AGENTS.md",
        office / "README.md",
        office / "status.md",
        office / "thread-registry.md",
        office / "communication.md",
        office / "context-packs" / "project-brief.md",
        office / "context-packs" / "thread-launch-prompts.md",
        office / "operating-model.md",
        office / "tasks" / "active" / "T-000-define-first-milestone.md",
    ]
    files.extend(office / "roles" / f"{role.slug}.md" for role in roles)
    files.extend(office / "role-memory" / f"{role.slug}.md" for role in roles)
    files.extend(
        directory / ".gitkeep"
        for directory in [
            office / "tasks" / "done",
            office / "tasks" / "archived",
            office / "messages" / "open",
            office / "messages" / "closed",
            office / "handoffs",
            office / "decisions",
            office / "context-packs",
            office / "proposals",
            office / "cadences",
            office / "archive" / "legacy-management",
        ]
    )
    return files


def write_scaffold(root: Path, spec: OfficeSpec, args: argparse.Namespace) -> list[dict[str, Any]]:
    office = root / "docs" / "agent-office"
    actions: list[dict[str, Any]] = []
    for target in planned_scaffold_files(root, spec.roles):
        assert_safe_target(root, target)
    if args.force and not args.confirm_overwrite and not args.dry_run:
        existing = [path for path in planned_scaffold_files(root, spec.roles) if path.exists()]
        if existing:
            preview = ", ".join(str(path) for path in existing[:5])
            suffix = " ..." if len(existing) > 5 else ""
            raise SystemExit(
                "Refusing to run --force without --confirm-overwrite because existing scaffold files were found: "
                f"{preview}{suffix}"
            )
    if not args.dry_run:
        root.mkdir(parents=True, exist_ok=True)
    write_kwargs = {
        "root": root,
        "force": args.force,
        "confirm_overwrite": args.confirm_overwrite,
        "dry_run": args.dry_run,
        "actions": actions,
    }
    safe_write(root / "AGENTS.md", render_agents(spec.language), **write_kwargs)
    safe_write(office / "README.md", render_readme(spec), **write_kwargs)
    safe_write(office / "status.md", render_status(spec), **write_kwargs)
    safe_write(office / "thread-registry.md", render_thread_registry(spec), **write_kwargs)
    safe_write(office / "communication.md", render_communication(spec.language), **write_kwargs)
    safe_write(office / "context-packs" / "project-brief.md", render_project_brief(spec), **write_kwargs)
    safe_write(office / "context-packs" / "thread-launch-prompts.md", render_thread_launch_prompts(spec), **write_kwargs)
    safe_write(office / "operating-model.md", render_operating_model(spec.language), **write_kwargs)
    safe_write(office / "tasks" / "active" / "T-000-define-first-milestone.md", render_task(spec), **write_kwargs)
    for role in spec.roles:
        safe_write(office / "roles" / f"{role.slug}.md", render_role(role, spec.language), **write_kwargs)
        safe_write(office / "role-memory" / f"{role.slug}.md", render_role_memory(role, spec.language), **write_kwargs)
    for directory in [
        office / "tasks" / "done",
        office / "tasks" / "archived",
        office / "messages" / "open",
        office / "messages" / "closed",
        office / "handoffs",
        office / "decisions",
        office / "context-packs",
        office / "proposals",
        office / "cadences",
        office / "archive" / "legacy-management",
    ]:
        safe_write(directory / ".gitkeep", "", **write_kwargs)
    return actions


def main() -> int:
    parser = argparse.ArgumentParser(description="Scaffold an Agent Office OS project office.")
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
    parser.add_argument("--roles", default="", help="Comma-separated role keys, e.g. pm,builder,reviewer")
    parser.add_argument("--language", choices=["en", "zh-CN"], default=None, help="Language for generated user-facing docs")
    parser.add_argument("--force", action="store_true", help="Overwrite existing scaffold files")
    parser.add_argument("--confirm-overwrite", action="store_true", help="Required with --force to overwrite existing files")
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
        "project_name": spec.project_name,
        "project_type": spec.project_type,
        "risk_level": spec.risk_level,
        "first_milestone": spec.first_milestone,
        "profile": spec.profile,
        "language": spec.language,
        "roles": [role.slug for role in spec.roles],
        "role_details": [role.__dict__ for role in spec.roles],
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
