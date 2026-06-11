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
import sys
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path
from typing import Any


OFFICE_DIR = "Agent Office"
EMPLOYEES_DIR = "Employees"
PROPOSALS_DIR = "Proposals"
ARCHIVE_DIR = "Archive"
LEGACY_ARCHIVE_DIR = "Old Project Memory"
OFFICE_SCHEMA_VERSION = "1.0.0"


ROLE_DEFINITIONS = {
    "pm": {
        "title": "Project Director",
        "zh_title": "项目总监",
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
    operation_model: str = "stateful-router"
    dispatch_policy: dict[str, Any] = field(default_factory=dict)
    task_reference_policy: str = "user-facing-title-internal-id"
    progress_mode: str = "ask-per-workstream"
    employee_report_route: str = "director-only"
    dependency_policy: str = "wait-for-required-inputs"
    short_continue_policy: str = "contextual-natural-language"


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
        inputs="用户的请求、AGENTS.md、Agent Office 公共文件，以及本员工私有文件。" if zh else "User requests, AGENTS.md, Agent Office public files, and this employee's private files.",
        outputs="完成的工作、简短状态记录，以及需要别人继续时的交接。" if zh else "Updated work, concise status notes, and handoffs when another employee should continue.",
        forbidden="不要超出批准的写入范围；默认不读取其他员工文件夹。" if zh else "Do not work outside the approved write scope or read other employee folders by default.",
        current_window=is_manager,
        needs_thread=not is_manager,
        thread_title=title,
        status="current-window" if is_manager else "waiting",
        thread_mode="worktree" if role == "builder" else "local",
        handoff_to=("项目总监" if role != "pm" else "用户") if zh else ("Project Director" if role != "pm" else "User"),
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


def role_from_config(raw: dict[str, Any], index: int, default_handoff: str, language: str) -> RoleSpec:
    zh = is_zh(language)
    title = coalesce(raw.get("title"), raw.get("name"), default=f"Role {index + 1}")
    slug = slugify(coalesce(raw.get("slug"), default=title), f"role-{index + 1}")
    validate_slug(slug)
    current_window = bool(raw.get("current_window", raw.get("currentWindow", False)))
    needs_thread_raw = raw.get("needs_thread", raw.get("needsThread", None))
    needs_thread = (not current_window) if needs_thread_raw is None else bool(needs_thread_raw)
    default_mission = "负责一个经过批准的清晰工作范围，并把结果交接干净。" if zh else "Own a distinct part of the approved workflow."
    default_authority = "只更新批准的写入范围和本员工私有文件夹。" if zh else "May update only the approved write scope and this employee's private folder."
    default_write_scope = "仅限当前任务授权范围" if zh else "current task scope only"
    default_assignment = "等待项目总监派工" if zh else "waiting"
    default_quality = "边界清楚、结果可验证、下一步容易接上。" if zh else "Work cleanly, verify the result, and leave the next action obvious."
    default_inputs = "AGENTS.md、Agent Office 公共文件、本员工文件夹，以及项目总监或用户指令。" if zh else "AGENTS.md, Agent Office public files, this employee's folder, and user instructions."
    default_outputs = "完成的工作、更新后的员工记忆和当前任务，以及必要交接。" if zh else "Completed work, updated employee memory/current-task, and handoffs when needed."
    default_forbidden = "不要超出批准的写入范围；默认不要读取其他员工文件夹或旧档案。" if zh else "Do not exceed the approved write scope or read other employee folders or old archives by default."
    return RoleSpec(
        slug=slug,
        title=title,
        mission=coalesce(raw.get("mission"), raw.get("purpose"), default=default_mission),
        authority=coalesce(
            raw.get("authority"),
            raw.get("boundaries"),
            default=default_authority,
        ),
        write_scope=coalesce(raw.get("write_scope"), raw.get("writeScope"), default=default_write_scope),
        current_assignment=coalesce(raw.get("current_assignment"), raw.get("assignment"), raw.get("currentAssignment"), default=default_assignment),
        domain=coalesce(raw.get("domain"), raw.get("responsibility_domain"), raw.get("responsibilityDomain"), default=""),
        quality_standard=coalesce(raw.get("quality_standard"), raw.get("qualityStandard"), default=default_quality),
        inputs=coalesce(raw.get("inputs"), default=default_inputs),
        outputs=coalesce(raw.get("outputs"), default=default_outputs),
        forbidden=coalesce(raw.get("forbidden"), raw.get("do_not"), raw.get("doNot"), default=default_forbidden),
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
        if any(token in role.title for token in ["总监", "协调", "主理", "策展", "主编"]):
            return role.title
    if roles:
        return roles[0].title
    return "用户" if is_zh(language) else "User"


def fill_missing_handoffs(roles: list[RoleSpec], default_handoff: str, language: str) -> None:
    fallback_owner = "用户" if is_zh(language) else "User"
    inferred = default_handoff or infer_default_handoff(roles, language)
    for role in roles:
        if not role.handoff_to:
            role.handoff_to = fallback_owner if role.title == inferred else inferred


def ensure_project_manager(roles: list[RoleSpec], language: str) -> None:
    """Make the current chat the first project director unless config already did."""
    if not roles:
        return
    if any(role.current_window for role in roles):
        for role in roles:
            if role.current_window:
                role.needs_thread = False
                role.status = role.status or "current-window"
                role.thread_id = role.thread_id if role.thread_id != "TBD" else "current-window"
                role.thread_title = role.thread_title or role.title
        return
    roles[0].current_window = True
    roles[0].needs_thread = False
    roles[0].status = roles[0].status or "current-window"
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
        title_lc = role.title.strip().lower()
        process_tokens = [
            "pipeline",
            "runtime",
            "archive",
            "context maintenance",
            "module",
            "workflow",
            "管线",
            "运行时",
            "模块",
            "流程",
            "系统",
        ]
        if (
            not role.title.strip()
            or re.fullmatch(r"role\s+\d+", title_lc)
            or any(token in title_lc or token in role.title for token in process_tokens)
        ):
            print(
                f"Warning: role title `{role.title}` looks process-shaped. Prefer a human job title such as Designer, Engineer, Release Checker, Researcher, Editor, 设计师, 工程师, 发布检查员, 研究员, or 编辑.",
                file=sys.stderr,
            )


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
    roles = [role_from_config(item, index, default_handoff, language) for index, item in enumerate(role_items) if isinstance(item, dict)]
    if len(roles) != len(role_items):
        raise SystemExit("Each role in config must be a JSON object.")
    fill_missing_handoffs(roles, default_handoff, language)
    ensure_project_manager(roles, language)
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
        operation_model=coalesce(raw.get("operation_model"), raw.get("operationModel"), default="stateful-router"),
        dispatch_policy=normalize_dispatch_policy(raw.get("dispatch_policy", raw.get("dispatchPolicy")), language),
        task_reference_policy=coalesce(raw.get("task_reference_policy"), raw.get("taskReferencePolicy"), default="user-facing-title-internal-id"),
        progress_mode=coalesce(raw.get("progress_mode"), raw.get("progressMode"), default="ask-per-workstream"),
        employee_report_route=coalesce(raw.get("employee_report_route"), raw.get("employeeReportRoute"), default="director-only"),
        dependency_policy=coalesce(raw.get("dependency_policy"), raw.get("dependencyPolicy"), default="wait-for-required-inputs"),
        short_continue_policy=coalesce(raw.get("short_continue_policy"), raw.get("shortContinuePolicy"), default="contextual-natural-language"),
    )


def load_office_spec(args: argparse.Namespace, root: Path) -> OfficeSpec:
    if args.config:
        return load_config_spec(Path(args.config).resolve(), args, root)
    language = normalize_language(args.language)
    roles = parse_roles(args.roles, args.profile, language)
    ensure_project_manager(roles, language)
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
        operation_model="stateful-router",
        dispatch_policy=default_dispatch_policy(language),
        task_reference_policy="user-facing-title-internal-id",
        progress_mode="ask-per-workstream",
        employee_report_route="director-only",
        dependency_policy="wait-for-required-inputs",
        short_continue_policy="contextual-natural-language",
    )


def first_role_title(spec: OfficeSpec) -> str:
    return spec.roles[0].title if spec.roles else "User"


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
- 如果你被分配了角色，读取公共区和 `Agent Office/Employees/{role-slug}/` 里属于自己的员工文件夹。
- 不要读取其他员工文件夹，除非用户明确要求维护、审计或恢复办公室。
- 日常工作不要读取 `Agent Office/Archive/Old Project Memory/`；那里是已吸收旧知识的历史档案。

协作规则：
- 当前窗口默认是第一任项目总监，负责给办公室挂牌、路由任务、更新公共区和处理迁移收尾。
- 项目总监每次行动前先判断生命周期状态和授权等级：说明书、只读体检、接管方案、已批准接管、就绪、已派工、自动跟进、维护或阻塞。
- 会写文件、改 `AGENTS.md`、移动旧资料或操作线程的动作，必须有当前有效选项或明确授权。
- 多员工模式默认由项目总监做单入口总控：用户主要和项目总监对话，项目总监拆任务、派给员工窗口、记录交接，并等待员工向项目总监汇报。
- 员工不默认互相派工；所有员工完成正式任务后都用 `【员工汇报】` 格式回项目总监，由项目总监根据全局、依赖和风险决定下一步。
- 用户安排较长任务时，项目总监先说明预计步骤、参与员工和下一个用户检查点，并让用户用 A/B/C 选择手动推进、半自动推进或自动推进到检查点。
- 项目总监每次收到需求都先做任务路由判断：员工职责明确就派给员工；没有合适员工或只是办公室小事时自己处理；归属会影响方向时只补问一句。
- 如果后续阶段依赖多个员工结果，项目总监必须等待依赖齐全；收到部分员工汇报时，只记录当前结果并说明还在等谁。
- 项目总监可以写交接框架、输入约束和验收标准，但不得替员工完成创意、提示词、设计、代码、研究、检查或发布产物，除非用户明确要求项目总监接手。
- 员工数量不等于并发数量；项目总监按办公室派工策略控制同时派工数量。
- `Agent Office/thread-registry.md` 是长期 Agent 员工名册和入职提示记录。
- 跨角色请求、答复和交接写入 `Agent Office/communication.md`。
- 当前任务和责任人写入 `Agent Office/task-board.md`。
- 员工完成有意义工作后，先更新自己的 `memory.md` 和 `current-task.md`，再向项目总监汇报。
- 用户侧默认使用任务名和自然语言短词，例如 `跟进`、`继续`、`OK`；`task_id` 只作为内部账本字段，日常对话不要求用户记编号。
- 只有用户选择自动推进模式或明确要求自动跟进时，项目总监才可以设置或更新 Codex heartbeat；自动化不能越权执行删除、归档、发布或改 `AGENTS.md`。
- `A/B/C/D` 只用于会触发不同动作的授权选择；`1/2/3` 只用于信息说明或多任务消歧。
- 只有项目总监、用户或被明确授权的员工才更新公共状态。
- 结束任务时说明改了什么、验证了什么、还剩什么、下一个负责人是谁。
"""
    return """# AGENTS.md

## GaoGao Office Protocol

This repository uses `Agent Office/` as the long-running agent project office.

Before project work:
- Read `Agent Office/README.md`, `Agent Office/status.md`, `Agent Office/project-brief.md`, and `Agent Office/task-board.md`.
- If assigned a role, read the public office files and your own employee folder under `Agent Office/Employees/{role-slug}/`.
- Do not read other employee folders unless the user explicitly asks for office maintenance, audit, or recovery.
- Do not read `Agent Office/Archive/Old Project Memory/` during ordinary work; it is historical material after old knowledge has been absorbed.

Coordination:
- The current chat is the founding project director unless the user chooses otherwise.
- Before acting, the project director classifies lifecycle state and authorization level: manual, checkup, proposal, takeover-approved, ready, active-dispatch, automatic-progress, maintenance, or blocked.
- Any action that writes files, changes `AGENTS.md`, moves old memory, or operates threads requires the current valid option or explicit approval.
- In multi-employee mode, the project director is the single user-facing controller by default: it splits requests, dispatches work to employee threads, records the handoff, and waits for employees to report back to the project director.
- Employees do not dispatch work to each other by default. After meaningful work, every employee reports back with an `Employee Report` shape; the project director decides the next step from the full project context, dependencies, and risk.
- Before longer work starts, the project director gives the user an expected step count, participating employees, and the next user checkpoint, then asks the user to choose A/B/C: manual progress, semi-automatic progress, or automatic progress until the checkpoint.
- The project director runs a task routing judgment for every request: dispatch clear employee-owned work, handle unowned or small office-maintenance work directly, and ask one brief question when ownership affects direction.
- If a downstream stage depends on several employee results, the project director must wait until required inputs are complete. Partial reports should be recorded, not rushed into the next stage.
- The project director may write handoff framing, input constraints, and acceptance criteria, but must not create employee-owned creative, prompt, design, code, research, QA, or release output unless the user explicitly asks the project director to take over.
- Employee roster size is not active concurrency; the project director follows the office dispatch policy when dispatching employee work.
- `Agent Office/thread-registry.md` is the staff directory and onboarding prompt record for long-running agent employees.
- Cross-role requests, answers, and handoffs go in `Agent Office/communication.md`.
- Current tasks and owners go in `Agent Office/task-board.md`.
- After meaningful work, employees update their own `memory.md` and `current-task.md` before reporting back to the project director.
- User-facing replies use task titles and natural short words such as `continue`, `ok`, or `proceed`; `task_id` stays as an internal ledger field and is not required in daily chat.
- The project director may create or update a Codex heartbeat only when the user chooses automatic progress or explicitly asks for automatic follow-up. Automation never authorizes delete, archive, publish, or `AGENTS.md` changes.
- Use A/B/C/D only for current action choices that authorize different actions; use 1/2/3 only for informational guidance or task disambiguation.
- Only the project director, project owner, or explicitly assigned employee updates public status.
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

`Employees/` 下每个角色一个文件夹。角色默认读取公共区和自己的员工文件夹，不读其他员工文件夹。

## 归档区

`Archive/Old Project Memory/` 是已吸收旧知识的历史档案。普通工作不要读取它。

## 项目总监

当前调用 GaoGao Office 的窗口默认接任第一任项目总监。它负责给办公室挂牌、保持公共区干净、先判断任务归属，再把合适任务分给员工，并在正式接管完成后邀请其他员工入职。

多员工模式下，用户可以继续主要和这个项目总监窗口对话。项目总监负责判断最终目标、识别下一位负责人、派工给员工窗口、写清交接记录，并按用户选择的 A/B/C 推进模式继续。它不会绕过员工汇报和依赖状态抢跑，也不会抢员工的职责。

v1.0 协作方式：员工完成后统一向项目总监汇报。项目总监收到部分结果时先记录和等待依赖齐全，再推进下一阶段；用户日常只需要说 `跟进`、`继续`、`OK` 这类短词即可。

办公室派工策略：{dispatch_policy_summary(spec)}
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

Each role has one folder under `Employees/`. A role reads public office files and its own employee folder by default.

## Archive

`Archive/Old Project Memory/` is historical material after old project knowledge is absorbed. Ordinary employees should not read it.

## Project Director

The current GaoGao Office chat becomes the founding project director by default. It opens the office, keeps the public area clean, judges task ownership before work starts, routes employee-owned work to the right employee, and invites employees only after formal takeover is complete.

In multi-employee mode, the user can keep using this project-director chat as the main entry point. The project director identifies the final outcome and next owner, dispatches work to employee threads, records handoffs, and follows the user's A/B/C progress mode. It does not bypass employee reports, dependency status, or employee ownership.

v1.0 collaboration style: employees report back to the project director. The project director records partial results, waits for required dependencies, then advances the next stage. In daily chat, the user can simply say `continue`, `ok`, or similar short natural-language replies.

Office dispatch policy: {dispatch_policy_summary(spec)}
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

用户拍板后，项目总监先确认 `task-board.md` 的第一项任务是否仍然准确。若需要多人协作，项目总监先说明预计步骤、参与员工和下一个用户检查点，再让用户用 A/B/C 选择手动推进、半自动推进或自动推进到检查点。员工汇报未齐时只记录和等待，不抢跑下一阶段。
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

After approval, the project director should confirm whether the first task in `task-board.md` is still accurate. For multi-employee work, first state expected steps, participating employees, and the next user checkpoint, then ask the user to choose A/B/C: manual progress, semi-automatic progress, or automatic progress to the checkpoint. When required employee reports are missing, record partial results and wait instead of rushing the next stage.
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
- 运行模型：{spec.operation_model}
- 办公室派工策略：{dispatch_policy_summary(spec)}
- 任务引用方式：{spec.task_reference_policy}
- 推进模式：{spec.progress_mode}
- 员工汇报路径：{spec.employee_report_route}
- 依赖策略：{spec.dependency_policy}
- 短词推进策略：{spec.short_continue_policy}
- 风险等级：{spec.risk_level}
- 当前角色：{role_titles(spec.roles)}

## 角色决策

{notes}

默认协作方式：用户主要和当前项目总监窗口沟通；项目总监按需派工给员工窗口，员工统一向项目总监汇报，项目总监根据依赖是否齐全再推进下一阶段。
运行中枢规则：项目总监每次行动前判断生命周期状态、动作授权等级和任务归属；没有当前有效授权时，只能报告、提案或询问。
任务路由规则：每次收到需求先判断最终目标、当前阶段和下一位负责人；员工职责明确就派工，办公室小事自己处理，归属不清且影响方向时只补问一句。
默认派工策略：员工可以全部入职，但项目总监按本机容量控制并发；配置未知或偏低时一次只派一个员工。
开工前预期：较长或多员工任务开始前，项目总监先说明预计步骤、参与员工和下一个用户检查点，再让用户选择 A/B/C 推进模式。
日常推进方式：用户侧优先使用任务名和自然语言短词；内部 `task_id` 只用于账本记录。

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
- Operation model: {spec.operation_model}
- Office dispatch policy: {dispatch_policy_summary(spec)}
- Task reference policy: {spec.task_reference_policy}
- Progress mode: {spec.progress_mode}
- Employee report route: {spec.employee_report_route}
- Dependency policy: {spec.dependency_policy}
- Short continue policy: {spec.short_continue_policy}
- Risk level: {spec.risk_level}
- Current roles: {role_titles(spec.roles)}

## Role Decisions

{notes}

Default collaboration style: the user primarily talks to the current project-director chat; the project director dispatches employee-owned work as needed, employees report back to the project director, and the project director advances only after required dependencies are ready.
Operation router rule: before acting, the project director classifies lifecycle state, authorization level, and task owner; without current valid approval, it can only report, propose, or ask.
Task routing rule: dispatch clear employee-owned work, handle tiny office-maintenance work directly, and ask one brief clarification when ownership affects direction.
Default dispatch policy: employees may all onboard, but the project director controls concurrent employee work based on local capacity. Unknown or low-capacity machines dispatch one employee at a time.
Before longer work starts, the project director states expected steps, participating employees, and the next user checkpoint, then asks for A/B/C progress mode.
Daily continuation uses task titles and short natural-language replies; internal `task_id` values are for the ledger only.

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

| task_id | task_title | Owner | Status | Reviewer | Write Scope | Expected Steps | Next User Checkpoint | Dependency Status | Notes |
|---|---|---|---|---|---|---|---|---|---|
| T-000 | {spec.first_milestone} | {owner} | proposed | {reviewer} | Agent Office public files | 待项目总监评估 | 待用户确认开工 | none | {spec.first_milestone} |

## 任务规则

- `task_id` 是内部账本字段；用户可见沟通优先使用 `task_title`。
- 每项任务必须有 owner、reviewer、写入范围、预计步骤、下一次用户检查点和依赖状态。
- 多员工任务默认由项目总监先做任务路由判断，再拆分和派工；员工统一向项目总监汇报。
- 依赖未齐时，项目总监只记录已返回结果并等待缺失汇报，不提前推进下一阶段。
- 派工并发按办公室派工策略执行；本机容量未知或偏低时，一次只派一个员工。
- 如果任务变复杂，再拆出单独任务文件或归档记录。
"""
    return f"""# Task Board

Last updated: {today}

| task_id | task_title | Owner | Status | Reviewer | Write Scope | Expected Steps | Next User Checkpoint | Dependency Status | Notes |
|---|---|---|---|---|---|---|---|---|---|
| T-000 | {spec.first_milestone} | {owner} | proposed | {reviewer} | Agent Office public files | pending project-director estimate | waiting for user approval | none | {spec.first_milestone} |

## Task Rules

- `task_id` is an internal ledger field; user-facing conversation should prefer `task_title`.
- Every task needs an owner, reviewer, write scope, expected steps, next user checkpoint, and dependency status.
- Multi-employee work starts with task routing judgment, then is split and dispatched by the project director; employees report back to the project director.
- When dependencies are missing, record returned results and wait for the missing reports before advancing.
- Follow the office dispatch policy; when local capacity is unknown or low, dispatch one employee at a time.
- If a task grows too large, split it into a separate task note or archive record.
"""


def render_decisions(language: str) -> str:
    if is_zh(language):
        return """# 决策记录

| ID | Status | Owner | Decision | Notes |
|---|---|---|---|---|
| D-000 | proposed | 用户 | 暂无长期决策 | 需要时再记录 |
"""
    return """# Decisions

| ID | Status | Owner | Decision | Notes |
|---|---|---|---|---|
| D-000 | proposed | User | No durable decisions yet | Record when needed |
"""


def render_communication(language: str) -> str:
    if is_zh(language):
        return """# 沟通与交接

## 消息规则

- 职责外请求不要直接抢活；先说明应该由哪个员工负责。
- 用户的需求默认先进入项目总监；项目总监先做任务路由判断：最终交付物、当前阶段、候选负责人、是否派工、是否自办、是否补问一句。
- 项目总监先判断生命周期状态和授权等级；写文件、改 `AGENTS.md`、移动旧资料或操作线程前，必须确认当前回复已经授权。
- 需要跨角色处理时，在本文件追加一条消息记录，写清楚 from、to、task_title、task_id、routing decision、requested response、next owner。
- 员工不默认互相派工。员工完成正式任务后必须用 `【员工汇报】` 格式向项目总监汇报。
- 用户侧推进优先使用任务名和自然语言短词，例如 `跟进`、`继续`、`OK`、`好的`。如果多个任务都可推进，项目总监列出任务名让用户选。
- `A/B/C/D` 只用于会触发不同动作的授权选择；`1/2/3` 只用于信息说明或多任务消歧。
- 用户选择自动推进模式或明确要求自动跟进时，项目总监才可以创建/更新 Codex heartbeat；自动化只负责继续未完成工作或在完成/阻塞/需用户反馈时停下。
- 任务完成、阻塞、换 owner 或进入 review 时，在本文件追加交接记录。

## 员工汇报格式

```text
【员工汇报】
汇报人：{员工职位}
任务：{任务名}
状态：已完成 / 阻塞 / 需要确认
产出位置：{路径或窗口结果摘要}
结论摘要：{短摘要}
建议下一步：{下一步或等待项目总监判断}
需要用户介入：是/否
```

## 依赖等待记录

```text
【依赖等待】
任务：{任务名}
已收到：{员工 A, 员工 B}
仍在等待：{员工 C, 员工 D}
下一阶段：{依赖齐全后要推进的工作}
```

## 自动推进记录

```text
【自动推进】
模式：C / 用户明确授权
下一个用户检查点：{检查点}
heartbeat：已设置 / 未设置 / 工具不可用
停止条件：完成 / 阻塞 / 需要用户反馈 / 风险动作
```

## 未处理消息

暂无。

## 交接记录

暂无。
"""
    return """# Communication And Handoffs

## Message Rules

- Do not perform out-of-scope requests directly; name the role that should own the work.
- User requests enter through the project director by default; the project director first runs a task routing judgment: final deliverable, current stage, candidate owner, whether to dispatch, whether to handle directly, or whether to ask one clarification.
- The project director classifies lifecycle state and authorization level first; before writing files, changing `AGENTS.md`, moving old memory, or operating threads, it must confirm the current reply authorized that action.
- When cross-role coordination is needed, append a message here with from, to, task_title, task_id, routing decision, requested response, and next owner.
- Employees do not dispatch to each other by default. After meaningful work, employees report back to the project director with the `Employee Report` shape.
- User-facing continuation uses task titles and short natural-language replies such as `continue`, `ok`, or `proceed`. If several tasks can continue, list task titles and ask the user to choose.
- Use A/B/C/D only for choices that authorize different actions; use 1/2/3 only for informational guidance or task disambiguation.
- The project director may create/update a Codex heartbeat only when the user chooses automatic progress or explicitly asks for automatic follow-up. Automation only continues unfinished work or stops at completion, blockers, user feedback, or risky actions.
- When work is done, blocked, changes owner, or enters review, append a handoff here.

## Employee Report Shape

```text
[Employee Report]
Reporter: {employee job title}
Task: {task title}
Status: done / blocked / needs confirmation
Output: {path or concise result}
Summary: {short summary}
Recommended next step: {next step or project-director judgment}
Needs user input: yes/no
```

## Dependency Waiting Record

```text
[Dependency Waiting]
Task: {task title}
Received: {employee A, employee B}
Still waiting for: {employee C, employee D}
Next stage: {work to start after dependencies are complete}
```

## Automatic Progress Record

```text
[Automatic Progress]
Mode: C / explicit user authorization
Next user checkpoint: {checkpoint}
Heartbeat: set / not set / tool unavailable
Stop condition: completion / blocker / user feedback / risky action
```

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

- 默认读取公共区和本员工文件夹。
- 不读取其他员工文件夹，除非用户明确要求维护、审计或恢复办公室。
- 日常工作不要读取 `Agent Office/Archive/Old Project Memory/`。
- 默认接收项目总监派工，完成后把结果回给项目总监；不要默认把任务直接派给其他员工。
- 回给项目总监时必须使用 `【员工汇报】` 格式，写清汇报人、任务名、状态、产出位置、结论摘要、建议下一步和是否需要用户介入。
- 职责外请求先路由给合适员工或项目总监。
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

- Read public office files and this employee folder by default.
- Do not read other employee folders unless the user explicitly asks for office maintenance, audit, or recovery.
- Do not read `Agent Office/Archive/Old Project Memory/` during ordinary work.
- Receive work from the project director by default and return results to the project director; do not dispatch work directly to other employees by default.
- Report back with the `Employee Report` shape, naming reporter, task title, status, output, summary, recommended next step, and whether user input is needed.
- Route out-of-scope requests to the right employee or project director.
- After significant work, update `memory.md` `Next Action` and `Work Log`; update `current-task.md` when needed.
"""


def render_employee_memory(spec: OfficeSpec, role: RoleSpec) -> str:
    today = date.today().isoformat()
    if is_zh(spec.language):
        return f"""# {role.title} Memory

员工标识：`{role.slug}`
隐私：protocol-private。默认只有 `{role.title}` 读取和更新。
最后更新：{today}

## Next Action

status: waiting
next: {role.current_assignment}
reason: 初始接管状态；等待用户或项目总监确认下一步。

## Work Log

### {today}

- 完成：员工档案已建好，等待正式入职或下一次任务。
- 结果：waiting
- 验证：未执行项目工作。
- 新的下一步：{role.current_assignment}

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
reason: Initial takeover state; waiting for the user or project director to confirm next work.

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

- `AGENTS.md`
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
- 使用 `【员工汇报】` 格式把结果回给项目总监。
- 不默认直接派其他员工；建议下一步即可，由项目总监决定是否推进。
"""
    return f"""# Current Task

status: waiting
current: {role.current_assignment}
owner: {role.title}

## Required Reading

- `AGENTS.md`
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
- Report back to the project director with the `Employee Report` shape.
- Do not dispatch other employees directly by default; recommend the next step and let the project director decide.
"""


def render_prompt_body(spec: OfficeSpec, role: RoleSpec) -> str:
    if is_zh(spec.language):
        return f"""本对话角色：{role.title}

你现在入职这个项目，岗位是「{role.title}」。先守住岗位判断、读取边界和写入边界；第一轮只做入职确认，不主动开工。

项目：{spec.project_name}
项目根目录：{spec.project_root}
默认语言：中文。路径、内部任务 ID、status enum 和代码标识保持原样。

岗位价值：{role.mission}
职责域：{role.domain or role.mission}
判断标准：{role.quality_standard}
写入边界：{role.write_scope}
禁区：{role.forbidden}
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

第一轮只做入职确认，不要改文件、不要主动开工。读取后请用 5-8 行汇报：
1. 你是谁
2. 你负责什么
3. 你不能碰什么
4. 当前等待什么派工
5. 如需开工，你需要项目总监给什么输入

之后等待项目总监派工；只有用户明确点名找你时，才直接回应用户。完成正式任务后，先更新自己的 memory.md 和 current-task.md，再用下面格式回复项目总监：

【员工汇报】
汇报人：{role.title}
任务：{{任务名}}
状态：已完成 / 阻塞 / 需要确认
产出位置：{{路径或窗口结果摘要}}
结论摘要：{{短摘要}}
建议下一步：{{下一步或等待项目总监判断}}
需要用户介入：是/否
"""
    return f"""Conversation role: {role.title}

You are joining this project as the `{role.title}`. Protect this role's judgment, reading boundary, and write boundary. For the first reply, confirm onboarding only; do not start work.

Project: {spec.project_name}
Project root: {spec.project_root}
Default language: English. Keep paths, task IDs, status enums, and code identifiers unchanged.

Role value: {role.mission}
Responsibility domain: {role.domain or role.mission}
Quality standard: {role.quality_standard}
Write boundary: {role.write_scope}
Forbidden: {role.forbidden}
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

For the first reply, only confirm onboarding. Do not edit files and do not start work. After reading, reply in 5-8 lines with:
1. who you are
2. what you own
3. what you must not touch
4. what dispatch you are waiting for
5. what input you would need from the project director to start

Then wait for the project director to dispatch work; respond directly to the user only when explicitly addressed. After real work, update your own memory.md and current-task.md, then report to the project director in this shape:

[Employee Report]
Reporter: {role.title}
Task: {{task title}}
Status: done / blocked / needs confirmation
Output: {{path or concise result}}
Summary: {{short summary}}
Recommended next step: {{next step or project-director judgment}}
Needs user input: yes/no
"""


def render_thread_registry(spec: OfficeSpec) -> str:
    today = date.today().isoformat()
    rows = []
    launch_roles = [role for role in spec.roles if role.needs_thread and not role.current_window]
    manager_titles = [role.thread_title or role.title for role in spec.roles if role.current_window]
    manager_title = manager_titles[0] if manager_titles else ("项目总监" if is_zh(spec.language) else "Project Director")
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
            f"当前项目总监窗口标题：`{manager_title}`",
            "",
            "| Role | Thread Title | Thread ID | Mode | Current Assignment | Write Scope | Status |",
            "|---|---|---|---|---|---|---|",
            *rows,
            "",
            "## 员工续任 / 重启提示词",
            "",
            "> 这些提示词用于员工入职、换窗口续任或角色恢复。办公室挂牌、AGENTS.md 应用和旧资料入库完成前，不要发送这些提示词。",
            "",
            "用户授权正式接管后，项目总监会先确认自己已经挂牌，再安排需要独立窗口的员工入职。员工已入职后，本区也可作为以后重建窗口时的启动材料。",
            "",
            "项目总监先给当前窗口挂牌，再邀请员工入职。Codex 桌面有线程工具时优先自动创建员工对话；工具不可用时，才手动复制下面的 `text` 代码框。",
            "",
            "当前窗口默认已接任项目总监，不需要再为项目总监开一个窗口。",
            "",
            "## 派工并发策略",
            "",
            dispatch_policy_summary(spec),
            "",
            "项目总监可以一次邀请所有员工入职，但正式派工要按这个并发上限执行；本机容量未知或偏低时，一个员工完成后再派下一个。",
            "",
            "## 项目总监派工协议",
            "",
            "行动前先做运行中枢自检：当前生命周期状态、用户意图、动作授权等级、是否已有当前有效授权、员工归属、执行后该停止、等待依赖，还是进入自动推进。",
            "",
            "用户默认只需要和项目总监窗口对话。项目总监每次先做任务路由判断：最终交付物、当前阶段、候选负责人、是否派工、是否自办、是否需要补问一句。员工职责明确时必须派给员工；没有合适员工或只是办公室小事时，项目总监可以自己处理并记录结果。",
            "较长或多员工任务开始前，项目总监先给用户预计步骤、参与员工和下一个用户检查点，并用 A/B/C 让用户选择：A 手动推进，B 半自动推进，C 自动推进到检查点。",
            "任务路由读取范围要小：读取 `office-plan.json`、`task-board.md`、`thread-registry.md`、`project-brief.md`、可选根 `AGENTS.md`，以及候选负责人的 `current-task.md`；不要为了选负责人而通读所有员工档案或记忆，也不要在普通派工前跑完整校验。",
            "",
            "项目总监可以写路由理由、交接框架、输入材料、约束和验收标准；不得替员工完成最终创意、提示词、设计、代码、研究、检查或发布产物，除非用户明确要求项目总监接手。若给出建议，必须标注为“交接框架，待员工判断”。",
            "",
            "会写文件、改 AGENTS.md、移动旧资料或操作线程的动作，必须有当前有效选项或明确授权。A/B/C/D 只用于授权动作或推进模式选择；过期字母不能当作批准。",
            "",
            "需要员工时，先更新任务板、communication.md 和员工 current-task，再把下面这种派工消息发给员工窗口。",
            "派工事务要小：最多更新 `task-board.md`、一条 `communication.md` 交接、被派员工的 `current-task.md`；最多发送一条员工线程消息；然后立刻向用户汇报并停止。写入或线程发送不可用时，输出手动派工包并停止。",
            "如果目标员工 Thread ID 是 `TBD`、缺失或不能确认属于本项目，不要把任务标成 active，也不要写孤儿任务；直接输出手动派工包并停止。等用户确认已发给员工、线程登记完成或员工结果返回后，再记录任务。",
            "员工汇报统一回项目总监。项目总监听到部分员工汇报时，先更新依赖状态；如果下一阶段还缺其他员工输入，只说明已收到哪些、还在等谁，不提前推进。",
            "",
            "```text",
            "本次派工：{任务名}",
            "路由判断：{为什么这件事归这个员工；如果有下一棒，写下一棒是谁}",
            "交接框架：{目标、约束、输入材料、验收标准；不要替员工写最终产物}",
            "请先读取 AGENTS.md、Agent Office 公共文件，以及你自己的员工文件夹。",
            "写入范围：{明确路径或范围}",
            "交付内容：{期望输出}",
            "完成后请更新你的 memory.md 和 current-task.md，然后用【员工汇报】格式回复项目总监。",
            "```",
            "",
            "派工发出后，项目总监按用户选择的 A/B/C 推进模式工作。A 手动推进时，等待用户短词触发，如 `跟进`、`继续`、`OK`；B 半自动推进时，按员工汇报推进到关键检查点；C 自动推进到检查点时，可以设置或更新 heartbeat。",
            "",
            "用户侧不要求记内部任务编号。只有一个待推进任务时，`跟进`、`继续`、`推进`、`OK`、`好的`、`可以` 都可理解为继续当前任务；多个候选任务时，列出任务名让用户选。",
            "自动推进只在用户选择 C 或明确要求时启用。每次项目总监被激活且仍有未完成工作时，可以创建或重置当前线程 heartbeat，约 5 小时 05 分后提醒自己检查；如果工作完成、阻塞、需要用户反馈或没有工作，立刻停止并简短汇报。",
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
        f"Current project-director window title: `{manager_title}`",
        "",
        "| Role | Thread Title | Thread ID | Mode | Current Assignment | Write Scope | Status |",
        "|---|---|---|---|---|---|---|",
        *rows,
        "",
        "## Employee Rejoin / Restart Prompts",
        "",
        "> Use these prompts for employee onboarding, employee restart, or role recovery after formal takeover. Do not send them before the office is created, AGENTS.md is applied, and absorbed old knowledge is archived.",
        "",
        "The project director should title the current chat first, then onboard employees. After employees are onboarded, this section can also restart a role in a fresh chat. In Codex Desktop, create employee threads automatically when tools are available. Use these manual prompts only as fallback.",
        "",
        "The current chat is the project director by default; do not create a second project-director thread.",
        "",
        "## Dispatch Concurrency Policy",
        "",
        dispatch_policy_summary(spec),
        "",
        "The project director may onboard all employees, but real work dispatch must respect this concurrency limit. When local capacity is unknown or low, wait for one employee to finish before dispatching the next.",
        "",
        "## Project-Director Dispatch Protocol",
        "",
        "Before acting, run the operation-router self-check: lifecycle state, user intent, authorization level, current valid approval, employee owner, and whether to stop, wait for dependencies, or enter automatic progress.",
        "",
        "The user only needs to talk to the project-director chat by default. The project director runs task routing judgment first: final deliverable, current stage, candidate owner, whether to dispatch, whether to handle directly, or whether to ask one clarification. Clear employee-owned work must be dispatched; unowned or small office-maintenance work may be handled by the project director and recorded.",
        "Before longer or multi-employee work starts, the project director states expected steps, participating employees, and the next user checkpoint, then asks the user to choose A/B/C: A manual progress, B semi-automatic progress, C automatic progress to the checkpoint.",
        "Keep task-routing reads small: read `office-plan.json`, `task-board.md`, `thread-registry.md`, `project-brief.md`, optional root `AGENTS.md`, and only the likely owner's `current-task.md`; do not read every employee profile or memory, and do not run full validation before ordinary dispatch.",
        "",
        "The project director may write routing rationale, handoff framing, inputs, constraints, and acceptance criteria. It must not create final creative, prompt, design, code, research, QA, or release output for an employee-owned task unless the user explicitly asks the project director to take over. Any suggestion must be labeled as handoff framing for the employee to judge.",
        "",
        "Actions that write files, change AGENTS.md, move old memory, or operate threads require a current valid option or explicit approval. A/B/C/D are only for authorization or progress-mode choices; stale letters are not approval.",
        "",
        "When an employee is needed, update the task board, communication.md, and employee current-task before sending a concise task message like this.",
        "Keep the dispatch transaction small: update at most `task-board.md`, one `communication.md` handoff, and the assigned employee's `current-task.md`; send at most one employee-thread message; then report to the user and stop. If writes or thread sends are unavailable, show a manual dispatch packet and stop.",
        "If the target employee Thread ID is `TBD`, missing, or not clearly tied to this project, do not mark the task active or create orphan task records. Show the manual dispatch packet and stop. Record the task after the user confirms it was sent, the thread is registered, or the employee result returns.",
        "Employees report back to the project director. When only some required employee reports are in, update dependency status and wait for the missing inputs instead of advancing prematurely.",
        "",
        "```text",
        "Dispatch task: {task title}",
        "Routing decision: {why this belongs to this employee; name the likely next owner if any}",
        "Handoff frame: {goal, constraints, inputs, acceptance criteria only; do not write the employee-owned output}",
        "First read AGENTS.md, Agent Office public files, and your own employee folder.",
        "Write scope: {explicit paths or scope}",
        "Deliverable: {expected output}",
        "After completion, update your memory.md and current-task.md, then reply to the project director with the Employee Report shape.",
        "```",
        "",
        "After dispatch, the project director follows the user's A/B/C progress mode. A waits for a short natural-language reply such as `continue`, `ok`, or `proceed`; B advances from employee reports but stops at key checkpoints; C may create or update a heartbeat and continue until the next user checkpoint.",
        "",
        "Do not ask the user to remember internal task IDs. If exactly one task is waiting or active, short replies such as `continue`, `ok`, or `proceed` mean continue that task. If several tasks are candidates, list readable task titles and ask the user to choose.",
        "Automatic progress is only for user choice C or explicit authorization. When active work remains, the project director may create or reset a current-thread heartbeat for about 5 hours 5 minutes later. If work is done, blocked, needs user feedback, or no work remains, stop and give a concise report.",
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
    if (path.exists() or path.is_symlink()) and is_link(path):
        raise SystemExit(f"Refusing to write through symlink or junction target: {path}")
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
    if not args.config:
        print(
            "Warning: no --config provided; using legacy fallback roles. "
            "Formal GaoGao Office takeover should pass an approved dynamic office-plan config.",
            file=sys.stderr,
        )
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
