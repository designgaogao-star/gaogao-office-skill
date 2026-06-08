#!/usr/bin/env python3
"""Scaffold a lightweight GaoGao Office project office.

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
LEGACY_ARCHIVE_DIR = "Old Project Memory"
OFFICE_SCHEMA_VERSION = "0.2.3"


ROLE_DEFINITIONS = {
    "pm": {
        "title": "Project Manager",
        "zh_title": "项目总管",
        "mission": "Maintain shared project truth, task ownership, scope, and handoffs.",
        "zh_mission": "维护项目共识、任务归属、范围和交接。",
        "authority": "May update public office files and coordinate employee work.",
        "zh_authority": "可以更新办公室公共文件，并协调员工工作。",
    },
    "builder": {
        "title": "Engineer",
        "zh_title": "工程师",
        "mission": "Implement assigned work inside the approved write scope and verify it.",
        "zh_mission": "在批准的写入范围内完成执行工作，并验证结果。",
        "authority": "May change only files named by the current task.",
        "zh_authority": "只能修改当前任务明确允许的文件。",
    },
    "reviewer": {
        "title": "Reviewer",
        "zh_title": "审查员",
        "mission": "Review work for correctness, regressions, scope, quality, and missing checks.",
        "zh_mission": "检查正确性、回归风险、范围、质量和遗漏的验证。",
        "authority": "Read-heavy by default; may update review notes and handoffs.",
        "zh_authority": "默认以读取和审查为主，可以更新审查记录和交接。",
    },
    "archivist": {
        "title": "Archivist",
        "zh_title": "档案管理员",
        "mission": "Keep the office clean, absorb old project memory, and archive stale material.",
        "zh_mission": "保持办公室干净，吸收旧项目记忆，并归档过期资料。",
        "authority": "May update public office files and archive records; does not change product code.",
        "zh_authority": "可以更新公共办公室文件和归档记录，不修改产品代码。",
    },
    "architect": {
        "title": "Architect",
        "zh_title": "架构师",
        "mission": "Maintain architecture boundaries and durable technical decisions.",
        "zh_mission": "维护架构边界和长期技术决策。",
        "authority": "May update decisions and architecture notes; code changes require task assignment.",
        "zh_authority": "可以更新决策和架构记录；代码修改需要任务授权。",
    },
    "qa": {
        "title": "Release Checker",
        "zh_title": "发布检查员",
        "mission": "Own acceptance scenarios, regression checks, and release confidence.",
        "zh_mission": "负责验收场景、回归检查和发布信心。",
        "authority": "May update QA notes, task acceptance, and verification records.",
        "zh_authority": "可以更新 QA 记录、任务验收和验证记录。",
    },
    "security": {
        "title": "Security Reviewer",
        "zh_title": "安全审查员",
        "mission": "Review secrets, permissions, dependency risk, and unsafe automation.",
        "zh_mission": "审查密钥、权限、依赖风险和不安全的自动化。",
        "authority": "May update security decisions and blocker notes.",
        "zh_authority": "可以更新安全决策和阻塞记录。",
    },
    "ux": {
        "title": "UX Designer",
        "zh_title": "体验设计师",
        "mission": "Review user flows, accessibility, interaction states, and user-facing clarity.",
        "zh_mission": "审查用户流程、可访问性、交互状态和用户可理解性。",
        "authority": "May update UX notes and acceptance criteria.",
        "zh_authority": "可以更新体验记录和验收标准。",
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

ROLE_WRITE_SCOPES_ZH = {
    "pm": "Agent Office 公共文件",
    "builder": "仅限当前任务授权范围",
    "reviewer": "审查记录和任务板更新",
    "archivist": "Agent Office 公共文件和归档记录",
    "architect": "决策和架构记录",
    "qa": "验证记录和验收标准",
    "security": "安全记录和阻塞决策",
    "ux": "体验记录和验收标准",
}


@dataclass
class RoleSpec:
    slug: str
    title: str
    mission: str
    authority: str
    write_scope: str
    current_assignment: str
    domain: str = ""
    quality_standard: str = ""
    inputs: str = ""
    outputs: str = ""
    forbidden: str = ""
    current_window: bool = False
    needs_thread: bool = True
    thread_title: str = ""
    thread_id: str = "TBD"
    status: str = ""
    thread_mode: str = "local"
    handoff_to: str = ""


@dataclass
class OfficeSpec:
    project_name: str
    project_root: str
    project_goal: str
    profile: str
    project_type: str
    risk_level: str
    first_milestone: str
    language: str
    roles: list[RoleSpec]
    role_decisions: str = ""
    deferred_roles: list[str] = field(default_factory=list)
    collaboration_mode: str = "controller-dispatch"
    dispatch_policy: dict[str, Any] = field(default_factory=dict)


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


def default_dispatch_policy(language: str) -> dict[str, Any]:
    if is_zh(language):
        return {
            "mode": "adaptive-serial",
            "max_parallel_employee_tasks": 1,
            "reason": "未检测本机容量时采用保守策略；员工可全部入职，但默认一次只派一个员工执行。",
            "source": "default",
        }
    return {
        "mode": "adaptive-serial",
        "max_parallel_employee_tasks": 1,
        "reason": "Use a conservative policy when local capacity is unknown; all employees may onboard, but dispatch one employee task at a time by default.",
        "source": "default",
    }


def normalize_dispatch_policy(raw: Any, language: str) -> dict[str, Any]:
    policy = default_dispatch_policy(language)
    if not isinstance(raw, dict):
        return policy
    merged = {**policy}
    for key, value in raw.items():
        if value is None:
            continue
        merged[str(key)] = value
    try:
        max_parallel = int(merged.get("max_parallel_employee_tasks", 1))
    except (TypeError, ValueError):
        max_parallel = 1
    merged["max_parallel_employee_tasks"] = max(1, min(max_parallel, 6))
    mode = str(merged.get("mode") or "adaptive-serial").strip() or "adaptive-serial"
    merged["mode"] = mode
    return merged


def normalize_thread_mode(raw: Any) -> str:
    value = str(raw or "local").strip().lower()
    return "worktree" if value in {"worktree", "branch"} else "local"


def role_from_legacy_key(role: str, language: str) -> RoleSpec:
    definition = ROLE_DEFINITIONS[role]
    is_manager = role == "pm"
    zh = is_zh(language)
    title = definition["zh_title"] if zh else definition["title"]
    mission = definition["zh_mission"] if zh else definition["mission"]
    authority = definition["zh_authority"] if zh else definition["authority"]
    write_scope = (ROLE_WRITE_SCOPES_ZH if zh else ROLE_WRITE_SCOPES).get(role, "仅限当前任务授权范围" if zh else "current task scope only")
    return RoleSpec(
        slug=role,
        title=title,
        mission=mission,
        authority=authority,
        write_scope=write_scope,
        current_assignment="T-000" if role == "pm" else "waiting",
        domain=mission,
        quality_standard="保持范围清楚、结果可验证、下一位 Agent 容易接上。" if zh else "Keep work scoped, verified, and easy for the next agent to resume.",
        inputs="BOSS 的请求、AGENTS.md、Agent Office 公共文件，以及本员工私有文件。" if zh else "Project owner requests, AGENTS.md, Agent Office public files, and this employee's private files.",
        outputs="完成的工作、简短状态记录，以及需要别人继续时的交接。" if zh else "Updated work, concise status notes, and handoffs when another employee should continue.",
        forbidden="不要超出批准的写入范围；默认不读取其他员工文件夹。" if zh else "Do not work outside the approved write scope or read other employee folders by default.",
        current_window=is_manager,
        needs_thread=not is_manager,
        thread_title=title,
        status=("项目总管" if zh else "founding-steward") if is_manager else "waiting",
        thread_mode="worktree" if role == "builder" else "local",
        handoff_to=("项目总管" if role != "pm" else "BOSS") if zh else ("Project Manager" if role != "pm" else "Project owner"),
    )


def parse_roles(raw: str, profile: str, language: str) -> list[RoleSpec]:
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
    return [role_from_legacy_key(role, language) for role in role_keys]


def role_from_config(raw: dict[str, Any], index: int, default_handoff: str) -> RoleSpec:
    title = coalesce(raw.get("title"), raw.get("name"), default=f"Role {index + 1}")
    slug = slugify(coalesce(raw.get("slug"), default=title), f"role-{index + 1}")
    validate_slug(slug)
    current_window = bool(raw.get("current_window", raw.get("currentWindow", raw.get("founding_steward", False))))
    needs_thread_raw = raw.get("needs_thread", raw.get("needsThread", None))
    needs_thread = (not current_window) if needs_thread_raw is None else bool(needs_thread_raw)
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
        domain=coalesce(raw.get("domain"), raw.get("responsibility_domain"), raw.get("responsibilityDomain"), default=""),
        quality_standard=coalesce(raw.get("quality_standard"), raw.get("qualityStandard"), default="Work cleanly, verify the result, and leave the next action obvious."),
        inputs=coalesce(raw.get("inputs"), default="AGENTS.md, Agent Office public files, this employee's folder, and user instructions."),
        outputs=coalesce(raw.get("outputs"), default="Completed work, updated employee memory/current-task, and handoffs when needed."),
        forbidden=coalesce(raw.get("forbidden"), raw.get("do_not"), raw.get("doNot"), default="Do not exceed the approved write scope or read other employee folders by default."),
        current_window=current_window,
        needs_thread=needs_thread,
        thread_title=coalesce(raw.get("thread_title"), raw.get("threadTitle"), default=title),
        thread_id=coalesce(raw.get("thread_id"), raw.get("threadId"), default="TBD"),
        status=coalesce(raw.get("status"), default=""),
        thread_mode=normalize_thread_mode(raw.get("thread_mode", raw.get("threadMode"))),
        handoff_to=coalesce(raw.get("handoff_to"), raw.get("handoffTo"), default=default_handoff),
    )


def infer_default_handoff(roles: list[RoleSpec], language: str) -> str:
    for role in roles:
        haystack = f"{role.slug} {role.title}".lower()
        if any(token in haystack for token in ["coordinator", "owner", "lead", "manager", "producer"]):
            return role.title
        if any(token in role.title for token in ["总管", "经理", "负责人", "协调", "主理", "策展", "主编"]):
            return role.title
    if roles:
        return roles[0].title
    return "BOSS" if is_zh(language) else "Project owner"


def fill_missing_handoffs(roles: list[RoleSpec], default_handoff: str, language: str) -> None:
    fallback_owner = "BOSS" if is_zh(language) else "Project owner"
    inferred = default_handoff or infer_default_handoff(roles, language)
    for role in roles:
        if not role.handoff_to:
            role.handoff_to = fallback_owner if role.title == inferred else inferred


def ensure_founding_steward(roles: list[RoleSpec], language: str) -> None:
    """Make the current chat the first project manager unless config already did."""
    if not roles:
        return
    if any(role.current_window for role in roles):
        for role in roles:
            if role.current_window:
                role.needs_thread = False
                role.status = role.status or ("founding-steward" if not is_zh(language) else "项目总管")
                role.thread_id = role.thread_id if role.thread_id != "TBD" else "current-window"
                role.thread_title = role.thread_title or role.title
        return
    roles[0].current_window = True
    roles[0].needs_thread = False
    roles[0].status = roles[0].status or ("founding-steward" if not is_zh(language) else "项目总管")
    roles[0].thread_id = roles[0].thread_id if roles[0].thread_id != "TBD" else "current-window"
    roles[0].thread_title = roles[0].thread_title or roles[0].title


def validate_roles(roles: list[RoleSpec]) -> None:
    if not roles:
        raise SystemExit("At least one role is required.")
    slugs = [role.slug for role in roles]
    duplicates = sorted({slug for slug in slugs if slugs.count(slug) > 1})
    if duplicates:
        raise SystemExit(f"Duplicate role slug(s): {', '.join(duplicates)}")
    for role in roles:
        validate_slug(role.slug)
        role.thread_title = role.thread_title or role.title


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
    ensure_founding_steward(roles, language)
    validate_roles(roles)
    return OfficeSpec(
        project_name=coalesce(raw.get("project_name"), raw.get("name"), args.project_name, root.name, default="Project"),
        project_root=str(root),
        project_goal=coalesce(raw.get("project_goal"), raw.get("goal"), args.project_goal, default="Define the first milestone."),
        profile=coalesce(raw.get("profile"), args.profile, default="dynamic"),
        project_type=coalesce(raw.get("project_type"), raw.get("type"), args.project_type, default="unspecified"),
        risk_level=coalesce(raw.get("risk_level"), args.risk_level, default="unspecified"),
        first_milestone=coalesce(raw.get("first_milestone"), raw.get("milestone"), args.first_milestone, default="Define the first milestone."),
        language=language,
        roles=roles,
        role_decisions=coalesce(raw.get("role_decisions"), raw.get("role_strategy"), default=""),
        deferred_roles=as_string_list(raw.get("deferred_roles")),
        collaboration_mode=coalesce(raw.get("collaboration_mode"), raw.get("collaborationMode"), default="controller-dispatch"),
        dispatch_policy=normalize_dispatch_policy(raw.get("dispatch_policy", raw.get("dispatchPolicy")), language),
    )


def load_office_spec(args: argparse.Namespace, root: Path) -> OfficeSpec:
    if args.config:
        return load_config_spec(Path(args.config).resolve(), args, root)
    language = normalize_language(args.language)
    roles = parse_roles(args.roles, args.profile, language)
    ensure_founding_steward(roles, language)
    return OfficeSpec(
        project_name=args.project_name or root.name or "Project",
        project_root=str(root),
        project_goal=args.project_goal,
        profile=args.profile,
        project_type=args.project_type,
        risk_level=args.risk_level,
        first_milestone=args.first_milestone,
        language=language,
        roles=roles,
        collaboration_mode="controller-dispatch",
        dispatch_policy=default_dispatch_policy(language),
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


def dispatch_policy_summary(spec: OfficeSpec) -> str:
    policy = spec.dispatch_policy or default_dispatch_policy(spec.language)
    mode = policy.get("mode", "adaptive-serial")
    max_parallel = policy.get("max_parallel_employee_tasks", 1)
    reason = policy.get("reason", "")
    if is_zh(spec.language):
        return f"{mode}；最多同时派工 {max_parallel} 个员工。{reason}".strip()
    return f"{mode}; dispatch at most {max_parallel} employee task(s) at once. {reason}".strip()


def render_agents_proposal(language: str) -> str:
    if is_zh(language):
        return """# AGENTS.md

## GaoGao Office Protocol

本仓库使用 `Agent Office/` 作为长期 Agent 项目办公室。

开始项目工作前：
- 先读 `Agent Office/README.md`、`Agent Office/status.md`、`Agent Office/project-brief.md` 和 `Agent Office/task-board.md`。
- 如果你被分配了角色，只读 `Agent Office/Employees/{role-slug}/` 里属于自己的员工文件夹。
- 不要读取其他员工文件夹，除非用户明确要求维护、审计或恢复办公室。
- 日常工作不要读取 `Agent Office/Archive/Old Project Memory/`；那里是已吸收旧知识的历史档案。

协作规则：
- 当前窗口默认是第一任项目总管，负责给办公室挂牌、路由任务、更新公共区和处理迁移收尾。
- 多员工模式默认由项目总管做单入口总控：BOSS 主要和项目总管对话，项目总管拆任务、派给员工窗口、回收结果并统一汇报。
- 员工数量不等于并发数量；项目总管按 `Agent Office/office-plan.json` 的 `dispatch_policy` 控制同时派工数量。
- `Agent Office/thread-registry.md` 是长期 Agent 员工名册和入职提示记录。
- 跨角色请求、答复和交接写入 `Agent Office/communication.md`。
- 当前任务和责任人写入 `Agent Office/task-board.md`。
- 只有项目总管、BOSS 或被明确授权的员工才更新公共状态。
- 结束任务时说明改了什么、验证了什么、还剩什么、下一个负责人是谁。
"""
    return """# AGENTS.md

## GaoGao Office Protocol

This repository uses `Agent Office/` as the long-running agent project office.

Before project work:
- Read `Agent Office/README.md`, `Agent Office/status.md`, `Agent Office/project-brief.md`, and `Agent Office/task-board.md`.
- If assigned a role, read only your own employee folder under `Agent Office/Employees/{role-slug}/`.
- Do not read other employee folders unless the user explicitly asks for office maintenance, audit, or recovery.
- Do not read `Agent Office/Archive/Old Project Memory/` during ordinary work; it is historical material after old knowledge has been absorbed.

Coordination:
- The current chat is the founding project manager unless the user chooses otherwise.
- In multi-employee mode, the project manager is the single BOSS-facing controller by default: it splits requests, dispatches work to employee threads, collects results, and reports back.
- Employee roster size is not active concurrency; the project manager follows `dispatch_policy` in `Agent Office/office-plan.json` when dispatching employee work.
- `Agent Office/thread-registry.md` is the staff directory and onboarding prompt record for long-running agent employees.
- Cross-role requests, answers, and handoffs go in `Agent Office/communication.md`.
- Current tasks and owners go in `Agent Office/task-board.md`.
- Only the project manager, project owner, or explicitly assigned employee updates public status.
- End every task with what changed, what was verified, what remains, and who should pick it up next.
"""


def render_readme(spec: OfficeSpec) -> str:
    if is_zh(spec.language):
        return f"""# Agent Office

这是 `{spec.project_name}` 的项目办公室。

办公室版本：{OFFICE_SCHEMA_VERSION}

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

`Archive/Old Project Memory/` 是已吸收旧知识的历史档案。普通工作不要读取它。

## 项目总管

当前调用 GaoGao Office 的窗口默认接任第一任项目总管。它负责给办公室挂牌、保持公共区干净、把任务分给合适员工，并在正式接管完成后邀请其他员工入职。

多员工模式下，BOSS 可以继续主要和这个项目总管窗口对话。项目总管负责拆解需求、派工给员工窗口、读取员工回复、更新办公室记录，再把整合后的结果汇报给 BOSS。

派工策略：{dispatch_policy_summary(spec)}
"""
    return f"""# Agent Office

This is the project office for `{spec.project_name}`.

Office schema version: {OFFICE_SCHEMA_VERSION}

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

`Archive/Old Project Memory/` is historical material after old project knowledge is absorbed. Ordinary employees should not read it.

## Project Manager

The current GaoGao Office chat becomes the founding project manager by default. It opens the office, keeps the public area clean, routes work to the right employee, and invites employees only after formal takeover is complete.

In multi-employee mode, BOSS can keep using this project-manager chat as the main entry point. The project manager decomposes requests, dispatches work to employee threads, reads employee replies, updates office records, and reports the synthesized result back.

Dispatch policy: {dispatch_policy_summary(spec)}
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

BOSS 拍板后，项目总管先确认 `task-board.md` 的第一项任务是否仍然准确。若需要多人协作，项目总管先拆任务并派给必要员工，再把结果统一汇报给 BOSS。
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

After approval, the project manager should confirm whether the first task in `task-board.md` is still accurate. If multiple people are needed, the project manager should split only the necessary subtasks, dispatch them to employees, and report one synthesized result back to BOSS.
"""


def render_project_brief(spec: OfficeSpec) -> str:
    today = date.today().isoformat()
    deferred = "\n".join(f"- {item}" for item in spec.deferred_roles)
    if not deferred:
        deferred = "- None recorded yet." if not is_zh(spec.language) else "- 暂无。"
    if is_zh(spec.language):
        role_lines = "\n".join(
            f"- {role.title} (`{role.slug}`)：{role.mission} 职责域：{role.domain or role.mission} 写入范围：{role.write_scope}"
            + (" 当前窗口接任。" if role.current_window else "")
            for role in spec.roles
        )
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
- 办公室版本：{OFFICE_SCHEMA_VERSION}
- 协作方式：{spec.collaboration_mode}
- 派工策略：{dispatch_policy_summary(spec)}
- 风险等级：{spec.risk_level}
- 当前角色：{role_titles(spec.roles)}

## 角色决策

{notes}

默认协作方式：BOSS 主要和当前项目总管窗口沟通；项目总管按需派工给员工窗口，并把结果整合后汇报。
默认派工策略：员工可以全部入职，但项目总管按本机容量控制并发；配置未知或偏低时一次只派一个员工。

{role_lines}

## 暂不创建的角色

{deferred}
"""
    role_lines = "\n".join(
        f"- {role.title} (`{role.slug}`): {role.mission} Domain: {role.domain or role.mission}. Write scope: {role.write_scope}"
        + (" Current chat owns this role." if role.current_window else "")
        for role in spec.roles
    )
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
- Office schema version: {OFFICE_SCHEMA_VERSION}
- Collaboration mode: {spec.collaboration_mode}
- Dispatch policy: {dispatch_policy_summary(spec)}
- Risk level: {spec.risk_level}
- Current roles: {role_titles(spec.roles)}

## Role Decisions

{notes}

Default collaboration style: BOSS primarily talks to the current project-manager chat; the project manager dispatches work to employee threads as needed and reports back with a synthesized result.
Default dispatch policy: employees may all onboard, but the project manager controls concurrent employee work based on local capacity. Unknown or low-capacity machines dispatch one employee at a time.

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
- 多员工任务默认由项目总管拆分和派工；员工完成后回给项目总管，由项目总管统一汇报 BOSS。
- 派工并发按 `office-plan.json` 的 `dispatch_policy` 执行；本机容量未知或偏低时，一次只派一个员工。
- 如果任务变复杂，再拆出单独任务文件或归档记录。
"""
    return f"""# Task Board

Last updated: {today}

| Task | Owner | Status | Reviewer | Write Scope | Notes |
|---|---|---|---|---|---|
| T-000 | {owner} | proposed | {reviewer} | Agent Office public files | {spec.first_milestone} |

## Task Rules

- Every task needs an owner, reviewer, write scope, and verification approach.
- Multi-employee work is split and dispatched by the project manager; employees return results to the project manager, who reports back to BOSS.
- Follow `dispatch_policy` in `office-plan.json`; when local capacity is unknown or low, dispatch one employee at a time.
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

- 职责外请求不要直接抢活；先说明应该由哪个员工负责。
- BOSS 的需求默认先进入项目总管；项目总管判断是否自己处理，或拆给员工窗口。
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
- BOSS requests enter through the project manager by default; the project manager decides whether to handle them or dispatch them to employee threads.
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

## 岗位价值

{role.mission}

你不是一个功能模块，而是本项目里承担这个岗位判断的人。先守好自己的职责边界，再把工作做扎实。

## 职责域

{role.domain or role.mission}

## 判断标准

{role.quality_standard}

## 输入

{role.inputs}

## 输出

{role.outputs}

## 权限和边界

{role.authority}

## 写入范围

{role.write_scope}

## 当前任务

{role.current_assignment}

## 交接对象

{role.handoff_to}

## 禁区

{role.forbidden}

## 边界

- 默认只读取本员工文件夹。
- 不读取其他员工文件夹，除非用户明确要求维护、审计或恢复办公室。
- 日常工作不要读取 `Agent Office/Archive/Old Project Memory/`。
- 默认接收项目总管派工，完成后把结果回给项目总管；BOSS 直接点名时再直接回应。
- 职责外请求先路由给合适员工或项目总管。
- 正经完成任务后，更新 `memory.md` 的 `Next Action` 和 `Work Log`，必要时更新 `current-task.md`。
"""
    return f"""# {role.title}

## Role Value

{role.mission}

You are not a feature module; you are the person holding this job's judgment for the project. Protect the role boundary first, then do the work well.

## Responsibility Domain

{role.domain or role.mission}

## Judgment Standard

{role.quality_standard}

## Inputs

{role.inputs}

## Outputs

{role.outputs}

## Authority And Boundaries

{role.authority}

## Write Scope

{role.write_scope}

## Current Assignment

{role.current_assignment}

## Handoff Target

{role.handoff_to}

## Forbidden

{role.forbidden}

## Boundaries

- Read this employee folder by default.
- Do not read other employee folders unless the user explicitly asks for office maintenance, audit, or recovery.
- Do not read `Agent Office/Archive/Old Project Memory/` during ordinary work.
- Receive work from the project manager by default and return results to the project manager; respond directly to BOSS only when BOSS explicitly addresses this employee.
- Route out-of-scope requests to the right employee or project manager.
- After significant work, update `memory.md` `Next Action` and `Work Log`; update `current-task.md` when needed.
"""


def render_employee_memory(spec: OfficeSpec, role: RoleSpec) -> str:
    today = date.today().isoformat()
    if is_zh(spec.language):
        return f"""# {role.title} Memory

Owner role: `{role.slug}`
Privacy: protocol-private. 默认只有 `{role.title}` 读取和更新。
Last updated: {today}

## Next Action

status: waiting
next: {role.current_assignment}
reason: 初始接管状态；等待用户或项目总管确认下一步。

## Work Log

### {today}

- Completed: 员工档案已建好，等待正式入职或下一次任务。
- Result: waiting
- Validation: 未执行项目工作。
- New next action: {role.current_assignment}

## Durable Notes

- 初始使命：{role.mission}
- 职责域：{role.domain or role.mission}
- 写入范围：{role.write_scope}
- 交接对象：{role.handoff_to}

## 用户偏好

- 暂无。

## Memory Rules

- 每次正经完成任务后追加一条 Work Log。
- 如果下一步被延后，标记 `status: deferred` 并写明提醒条件。
- 如果用户明确取消，标记 `status: cancelled by user`。
- 共享项目事实写到公共区，不要塞进这里。
"""
    return f"""# {role.title} Memory

Owner role: `{role.slug}`
Privacy: protocol-private. By default only `{role.title}` reads and updates this file.
Last updated: {today}

## Next Action

status: waiting
next: {role.current_assignment}
reason: Initial takeover state; waiting for the user or project manager to confirm next work.

## Work Log

### {today}

- Completed: Employee file is ready; waiting for onboarding or the next assignment.
- Result: waiting
- Validation: No project work performed.
- New next action: {role.current_assignment}

## Durable Notes

- Initial mission: {role.mission}
- Responsibility domain: {role.domain or role.mission}
- Write scope: {role.write_scope}
- Handoff target: {role.handoff_to}

## User Preferences

- None recorded yet.

## Memory Rules

- Append one Work Log entry after meaningful work.
- If a next action is postponed, mark `status: deferred` and state when to remind the user.
- If the user cancels it, mark `status: cancelled by user`.
- Put shared project truth in the public area, not here.
"""


def render_employee_task(spec: OfficeSpec, role: RoleSpec) -> str:
    if is_zh(spec.language):
        return f"""# Current Task

status: waiting
current: {role.current_assignment}
owner: {role.title}

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

- 更新本文件状态：waiting / active / deferred / cancelled / done。
- 更新 `memory.md` 的 `Next Action` 和 `Work Log`。
- 如有跨角色交接，更新 `Agent Office/communication.md`。
"""
    return f"""# Current Task

status: waiting
current: {role.current_assignment}
owner: {role.title}

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

- Update this file status: waiting / active / deferred / cancelled / done.
- Update `memory.md` `Next Action` and `Work Log`.
- If another role needs context, update `Agent Office/communication.md`.
"""


def render_prompt_body(spec: OfficeSpec, role: RoleSpec) -> str:
    if is_zh(spec.language):
        return f"""本对话角色：{role.title}

你现在入职这个项目，岗位是「{role.title}」。先守住岗位判断和写入边界，再等项目总管派工。

项目：{spec.project_name}
项目根目录：{spec.project_root}
默认语言：中文。路径、任务 ID、status enum 和代码标识保持原样。

岗位价值：{role.mission}
职责域：{role.domain or role.mission}
判断标准：{role.quality_standard}
写入边界：{role.write_scope}

请先读取：
1. AGENTS.md
2. Agent Office/README.md
3. Agent Office/status.md
4. Agent Office/project-brief.md
5. Agent Office/task-board.md
6. Agent Office/Employees/{role.slug}/README.md
7. Agent Office/Employees/{role.slug}/memory.md
8. Agent Office/Employees/{role.slug}/current-task.md

第一轮只做入职确认，不要改文件、不要主动开工。读取后请用 5-8 行汇报：
1. 你是谁
2. 你负责什么
3. 你不能碰什么
4. 当前在等什么
5. 你建议下一步做什么

之后等待项目总管安排工作；如果 BOSS 直接点名找你，再直接回应 BOSS。完成正式任务后，更新自己的 memory.md 和 current-task.md，并按“完成了什么 / 写到哪里 / 状态更新 / 建议下一步”回复项目总管。
"""
    return f"""Conversation role: {role.title}

You are joining this project as the `{role.title}`. Protect this role's judgment and write boundary, then wait for the project manager to dispatch work.

Project: {spec.project_name}
Project root: {spec.project_root}
Default language: English. Keep paths, task IDs, status enums, and code identifiers unchanged.

Role value: {role.mission}
Responsibility domain: {role.domain or role.mission}
Quality standard: {role.quality_standard}
Write boundary: {role.write_scope}

Read first:
1. AGENTS.md
2. Agent Office/README.md
3. Agent Office/status.md
4. Agent Office/project-brief.md
5. Agent Office/task-board.md
6. Agent Office/Employees/{role.slug}/README.md
7. Agent Office/Employees/{role.slug}/memory.md
8. Agent Office/Employees/{role.slug}/current-task.md

For the first reply, only confirm onboarding. Do not edit files and do not start work. After reading, reply in 5-8 lines with:
1. who you are
2. what you own
3. what you must not touch
4. what is currently waiting
5. what you recommend next

Then wait for the project manager to dispatch work; respond directly to BOSS only when BOSS explicitly addresses this employee. After real work, update your own memory.md and current-task.md, then report to the project manager in this shape: completed work / output path / status update / recommended next step.
"""


def render_thread_registry(spec: OfficeSpec) -> str:
    today = date.today().isoformat()
    rows = []
    launch_roles = [role for role in spec.roles if role.needs_thread and not role.current_window]
    manager_titles = [role.thread_title or role.title for role in spec.roles if role.current_window]
    manager_title = manager_titles[0] if manager_titles else ("项目经理" if is_zh(spec.language) else "Project Manager")
    for role in spec.roles:
        status = role.status or ("current-window" if role.current_window else "waiting")
        thread_id = role.thread_id if role.current_window or role.thread_id != "TBD" else "TBD"
        thread_title = role.thread_title or role.title
        rows.append(
            f"| {role.title} | {thread_title} | {thread_id} | {role.thread_mode} | {role.current_assignment} | {role.write_scope} | {status} |"
        )
    if is_zh(spec.language):
        sections = [
            "# 线程登记表",
            "",
            f"最后更新：{today}",
            "",
            f"当前项目经理窗口标题：`{manager_title}`",
            "",
            "| Role | Thread Title | Thread ID | Mode | Current Assignment | Write Scope | Status |",
            "|---|---|---|---|---|---|---|",
            *rows,
            "",
            "## 员工续任 / 重启提示词",
            "",
            "> 这些提示词用于员工入职、换窗口续任或角色恢复。办公室挂牌、AGENTS.md 应用和旧资料入库完成前，不要发送这些提示词。",
            "",
            "BOSS 授权正式接管后，项目总管会先确认自己已经挂牌，再安排需要独立窗口的员工入职。员工已入职后，本区也可作为以后重建窗口时的启动材料。",
            "",
            "项目总管先给当前窗口挂牌，再邀请员工入职。Codex 桌面有线程工具时优先自动创建员工对话；工具不可用时，才手动复制下面的 `text` 代码框。",
            "",
            "当前窗口默认已接任项目总管，不需要再为项目总管开一个窗口。",
            "",
            "## 派工并发策略",
            "",
            dispatch_policy_summary(spec),
            "",
            "项目总管可以一次邀请所有员工入职，但正式派工要按这个并发上限执行；本机容量未知或偏低时，一个员工完成后再派下一个。",
            "",
            "## 项目总管派工协议",
            "",
            "BOSS 默认只需要和项目总管窗口对话。项目总管判断任务是否需要员工；需要时，先更新任务板和员工 current-task，再把下面这种派工消息发给员工窗口。",
            "",
            "```text",
            "本次派工：{任务编号或一句话任务}",
            "请先读取 AGENTS.md、Agent Office 公共文件，以及你自己的员工文件夹。",
            "写入范围：{明确路径或范围}",
            "交付内容：{期望输出}",
            "完成后请更新你的 memory.md 和 current-task.md，然后把结果回复给项目总管。",
            "```",
            "",
        ]
        if not launch_roles:
            sections.extend(["暂无需要新建的员工窗口。", ""])
        for role in launch_roles:
            sections.extend(
                [
                    f"### {role.title}",
                    "",
                    f"**员工续任 / 重启：{role.title}**",
                    f"建议标题：`{role.thread_title or role.title}`",
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
        f"Current project-manager window title: `{manager_title}`",
        "",
        "| Role | Thread Title | Thread ID | Mode | Current Assignment | Write Scope | Status |",
        "|---|---|---|---|---|---|---|",
        *rows,
        "",
        "## Employee Rejoin / Restart Prompts",
        "",
        "> Use these prompts for employee onboarding, employee restart, or role recovery after formal takeover. Do not send them before the office is created, AGENTS.md is applied, and absorbed old knowledge is archived.",
        "",
        "The project manager should title the current chat first, then onboard employees. After employees are onboarded, this section can also restart a role in a fresh chat. In Codex Desktop, create employee threads automatically when tools are available. Use these manual prompts only as fallback.",
        "",
        "The current chat is the project manager by default; do not create a second project-manager thread.",
        "",
        "## Dispatch Concurrency Policy",
        "",
        dispatch_policy_summary(spec),
        "",
        "The project manager may onboard all employees, but real work dispatch must respect this concurrency limit. When local capacity is unknown or low, wait for one employee to finish before dispatching the next.",
        "",
        "## Project-Manager Dispatch Protocol",
        "",
        "BOSS only needs to talk to the project-manager chat by default. The project manager decides whether a task needs employees; when it does, update the task board and employee current-task first, then send a concise task message like this to the employee thread.",
        "",
        "```text",
        "Dispatch task: {task id or one-sentence task}",
        "First read AGENTS.md, Agent Office public files, and your own employee folder.",
        "Write scope: {explicit paths or scope}",
        "Deliverable: {expected output}",
        "After completion, update your memory.md and current-task.md, then reply to the project manager with the result.",
        "```",
        "",
    ]
    if not launch_roles:
        sections.extend(["No additional employee windows are needed.", ""])
    for role in launch_roles:
        sections.extend(
            [
                f"### {role.title}",
                "",
                f"**Employee rejoin / restart: {role.title}**",
                f"Suggested title: `{role.thread_title or role.title}`",
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
    payload["office_schema_version"] = OFFICE_SCHEMA_VERSION
    payload["agents_apply_authorization"] = "current approved reply option or another explicit user approval"
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
        raise SystemExit("Refusing to apply AGENTS.md without --confirm-apply-agents. Use it only after the current approved reply option or another explicit user approval authorizes AGENTS.md.")
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
    parser = argparse.ArgumentParser(description="Scaffold a lightweight GaoGao Office project office.")
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
