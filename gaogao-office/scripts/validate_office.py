#!/usr/bin/env python3
"""Validate a lightweight GaoGao Office project office."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path, PureWindowsPath


OFFICE_DIR = "Agent Office"
OFFICE_SCHEMA_VERSION = "1.0.4"

REQUIRED_FILES = [
    "Agent Office/README.md",
    "Agent Office/status.md",
    "Agent Office/project-brief.md",
    "Agent Office/project-map.md",
    "Agent Office/task-board.md",
    "Agent Office/communication.md",
    "Agent Office/decisions.md",
    "Agent Office/thread-registry.md",
    "Agent Office/office-plan.json",
    "Agent Office/Proposals/AGENTS.proposed.md",
]

REQUIRED_DIRS = [
    "Agent Office/Employees",
    "Agent Office/Proposals",
    "Agent Office/Archive/Old Project Memory",
]

BUDGETS = {
    "AGENTS.md": 1500,
    "Agent Office/status.md": 1200,
    "Agent Office/project-brief.md": 1400,
    "Agent Office/project-map.md": 2000,
    "Agent Office/task-board.md": 1200,
    "Agent Office/communication.md": 1600,
    "Agent Office/decisions.md": 1600,
    "Agent Office/thread-registry.md": 2500,
}

EMPLOYEE_BUDGETS = {
    "README.md": 1200,
    "memory.md": 1200,
    "current-task.md": 800,
}

BAD_ROLE_TITLE_TOKENS = [
    "pipeline",
    "runtime",
    "workflow",
    "system",
    "scope",
    "qa 与发布",
    "视觉资产管线",
    "前端运行层",
]

SKIP_ARCHIVE_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".cache",
    ".next",
    ".nuxt",
    ".turbo",
    ".venv",
    "__pycache__",
    "agent office",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "out",
    "target",
    "vendor",
    "venv",
}


@dataclass
class Finding:
    severity: str
    path: str
    message: str


@dataclass
class ReportEntry:
    path: str
    line: str


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def budget_units(path: Path) -> int:
    text = read_text(path)
    cjk_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
    latin_tokens = len(re.findall(r"[A-Za-z0-9_]+", text))
    return cjk_chars + latin_tokens


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


def is_unsafe_root(root: Path) -> bool:
    home = Path.home().resolve()
    if root.parent == root or root == home:
        return True
    return any(part.lower() == ".git" for part in root.parts)


def contains_any(text: str, options: list[str]) -> bool:
    return any(option in text for option in options)


def label(options: list[str]) -> str:
    return " / ".join(options)


def markdown_section(text: str, heading: str) -> str:
    marker = f"## {heading}"
    start = text.find(marker)
    if start < 0:
        return ""
    body_start = start + len(marker)
    next_heading = re.search(r"^##\s+", text[body_start:], re.MULTILINE)
    if not next_heading:
        return text[body_start:]
    return text[body_start : body_start + next_heading.start()]


def approval_value(section: str, key: str) -> str | None:
    pattern = re.compile(rf"^[ \t]*(?:[-*][ \t]*)?{re.escape(key)}:[ \t]*(YES|NO)[ \t]*$", re.MULTILINE | re.IGNORECASE)
    matches = list(pattern.finditer(section))
    if not matches:
        return None
    return matches[-1].group(1).upper()


def is_markdown_table_separator(line: str) -> bool:
    if "|" not in line:
        return False
    cells = [cell.strip() for cell in line.strip("|").split("|")]
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell or "") for cell in cells)


def unescape_markdown_table_code(value: str) -> str:
    return value.replace("\\|", "|")


def table_source_entries(section: str) -> list[ReportEntry]:
    entries: list[ReportEntry] = []
    for line in section.splitlines():
        stripped = line.strip()
        if is_markdown_table_separator(stripped) or "`" not in stripped:
            continue
        matches = []
        for match in re.finditer(r"(`+)(.*?)\1", stripped):
            value = match.group(2)
            if value.startswith(" ") and value.endswith(" ") and len(value) >= 2:
                value = value[1:-1]
            matches.append(unescape_markdown_table_code(value))
        if matches:
            entries.append(ReportEntry(matches[0], stripped))
    return entries


def table_source_paths(section: str) -> list[str]:
    return [entry.path for entry in table_source_entries(section)]


def is_safe_report_path(raw_path: str) -> bool:
    normalized = raw_path.replace("\\", "/").strip()
    if not normalized or normalized == ".":
        return False
    path = Path(normalized)
    windows_path = PureWindowsPath(raw_path)
    if path.is_absolute() or windows_path.is_absolute() or windows_path.drive or windows_path.root:
        return False
    parts = path.parts
    if not parts or ".." in parts:
        return False
    lower_parts = [part.lower() for part in parts]
    if lower_parts[0] in SKIP_ARCHIVE_DIRS:
        return False
    return not any(part in SKIP_ARCHIVE_DIRS for part in lower_parts)


def archive_files(archive_dir: Path) -> list[Path]:
    if not archive_dir.is_dir():
        return []
    return [
        path
        for path in archive_dir.rglob("*")
        if path.is_file() and path.name != ".gitkeep" and not has_link_in_path(archive_dir, path)
    ]


def archive_contains_source(archive_dir: Path, archived: list[Path], source: str) -> bool:
    if not is_safe_report_path(source):
        return False
    source_parts = Path(source.replace("\\", "/")).parts
    if not source_parts:
        return False
    for archived_file in archived:
        try:
            archived_parts = archived_file.relative_to(archive_dir).parts
        except ValueError:
            continue
        if len(archived_parts) >= len(source_parts) + 1 and archived_parts[1 : 1 + len(source_parts)] == source_parts:
            return True
    return False


def report_line_explanation(line: str) -> str:
    without_code = re.sub(r"(`+)(.*?)\1", " ", line)
    cleaned = re.sub(r"[\|\-\*\s]+", " ", without_code).strip(" :;,.")
    return re.sub(r"\s+", " ", cleaned)


def entry_has_reason(line: str) -> bool:
    explanation = report_line_explanation(line)
    return len(re.findall(r"[A-Za-z0-9\u4e00-\u9fff]+", explanation)) >= 2


def entry_has_disposition(line: str) -> bool:
    explanation = report_line_explanation(line).lower()
    return any(token in explanation for token in ["migrated", "migration", "absorbed", "absorb", "discarded", "discard", "吸收", "迁移", "丢弃"])


def entry_absorption_complete(line: str) -> bool:
    explanation = report_line_explanation(line).lower()
    if "needs absorption" in explanation or "proposed" in explanation or "pending" in explanation:
        return False
    return any(
        token in explanation
        for token in [
            "migrated",
            "migration",
            "absorbed",
            "absorb",
            "summarized",
            "summarised",
            "merged into",
            "copied into",
            "吸收",
            "归纳",
            "迁移",
            "写入",
            "并入",
        ]
    )


def validate_required_paths(root: Path, findings: list[Finding]) -> None:
    for rel in REQUIRED_FILES:
        path = root / rel
        if path.exists() and has_link_in_path(root, path):
            findings.append(Finding("error", rel, "required file path contains a symlink or junction"))
        elif not path.is_file():
            findings.append(Finding("error", rel, "required file is missing"))
    for rel in REQUIRED_DIRS:
        path = root / rel
        if path.exists() and has_link_in_path(root, path):
            findings.append(Finding("error", rel, "required directory path contains a symlink or junction"))
        elif not path.is_dir():
            findings.append(Finding("error", rel, "required directory is missing"))
    if (root / "docs" / "agent-office").exists():
        findings.append(Finding("warning", "legacy-v0.1-office", "legacy v0.1 nested office path exists; migrate or archive it before relying on v0.2 layout"))
    if (root / "Agent Office" / "Archive" / "Legacy Management").exists():
        findings.append(Finding("warning", "Agent Office/Archive/Legacy Management", "old archive directory name exists; prefer `Agent Office/Archive/Old Project Memory/`"))


def validate_content(root: Path, findings: list[Finding]) -> None:
    agents = root / "AGENTS.md"
    proposal = root / "Agent Office/Proposals/AGENTS.proposed.md"
    if agents.exists() and not has_link_in_path(root, agents):
        text = read_text(agents)
        if "Agent Office/" not in text:
            findings.append(Finding("warning", "AGENTS.md", "root AGENTS.md does not point to `Agent Office/`"))
    elif proposal.exists():
        findings.append(Finding("info", "AGENTS.md", "root AGENTS.md is not applied yet; review `Agent Office/Proposals/AGENTS.proposed.md`"))

    prompt_file = root / "Agent Office/thread-registry.md"
    if prompt_file.exists() and not has_link_in_path(root, prompt_file):
        text = read_text(prompt_file)
        if text:
            general_registry_requirements = [
                ["项目总监派工协议", "Project-Director Dispatch Protocol"],
                ["任务路由判断", "task routing judgment", "Routing decision"],
                ["任务名", "task_title", "task title"],
                ["短词", "short natural-language", "continue", "OK"],
                ["A/B/C", "手动推进", "semi-automatic", "automatic progress"],
                ["依赖", "dependency", "A/B/C progress"],
                ["heartbeat", "自动推进", "automatic follow-up"],
                ["【员工汇报】", "Employee Report"],
                ["send_message_to_thread"],
                ["项目总监 Thread ID", "Project-director Thread ID"],
                ["自动回传", "auto-return", "Employee Return Protocol"],
                ["手动复制", "manual copy", "copyable report"],
                ["汇报接收", "Report Intake", "report-intake"],
                ["waiting-dependency"],
                ["依赖", "dependency", "wait until required"],
                ["交接框架", "Handoff frame", "handoff framing"],
                ["不要替员工写最终产物", "employee-owned output", "不得替员工完成"],
                ["任务路由读取范围", "task-routing reads", "Task-routing read budget"],
                ["派工事务", "dispatch transaction", "manual dispatch packet"],
                ["岗位校准", "Role calibration", "Role Calibration"],
                ["Exchange/Dispatch", "file-first", "文件优先"],
                ["Exchange/Reports", "Full report file", "完整报告文件"],
                ["孤儿任务", "orphan task"],
                ["生命周期", "lifecycle state", "operation-router"],
                ["授权等级", "authorization level", "current valid approval"],
                ["用户", "user", "project director"],
            ]
            for options in general_registry_requirements:
                if not contains_any(text, options):
                    findings.append(Finding("warning", "Agent Office/thread-registry.md", f"thread registry should mention `{label(options)}`"))
        has_employee_launch_prompt = contains_any(text, ["本对话角色", "Conversation role"])
        if has_employee_launch_prompt:
            launch_prompt_requirements = [
                ["AGENTS.md"],
                ["Agent Office/README.md"],
                ["Agent Office/status.md"],
                ["Agent Office/project-brief.md"],
                ["Agent Office/task-board.md"],
                ["Agent Office/Employees/"],
                ["memory.md"],
                ["current-task.md"],
                ["send_message_to_thread"],
                ["thread-registry.md"],
                ["Role Calibration", "岗位校准"],
                ["Exchange/Reports", "完整报告文件", "Full report file"],
                ["需要复制回项目总监窗口", "copied back to the project-director chat"],
            ]
            for options in launch_prompt_requirements:
                if not contains_any(text, options):
                    findings.append(Finding("warning", "Agent Office/thread-registry.md", f"thread launch prompts should mention `{label(options)}`"))

    communication = root / "Agent Office/communication.md"
    if communication.exists() and not has_link_in_path(root, communication):
        text = read_text(communication)
        for options in [["out-of-scope", "职责外"], ["Handoffs", "交接"], ["Open Messages", "消息"]]:
            if not contains_any(text, options):
                findings.append(Finding("warning", "Agent Office/communication.md", f"communication protocol should mention `{label(options)}`"))
        if not contains_any(text, ["project director by default", "默认先进入项目总监"]):
            findings.append(Finding("warning", "Agent Office/communication.md", "communication protocol should explain controller-dispatch entry through the project director"))
        if not contains_any(text, ["任务路由判断", "task routing judgment", "routing decision"]):
            findings.append(Finding("warning", "Agent Office/communication.md", "communication protocol should explain task routing before dispatch or direct work"))
        if not contains_any(text, ["任务名", "task_title", "task title"]) or not contains_any(text, ["短词", "short natural-language", "continue", "OK"]):
            findings.append(Finding("warning", "Agent Office/communication.md", "communication protocol should explain title-first continuation with short natural replies"))
        if not contains_any(text, ["A/B/C", "手动推进", "semi-automatic", "automatic progress"]):
            findings.append(Finding("warning", "Agent Office/communication.md", "communication protocol should explain A/B/C progress modes"))
        if not contains_any(text, ["【员工汇报】", "Employee Report"]):
            findings.append(Finding("warning", "Agent Office/communication.md", "communication protocol should include the employee report shape"))
        if "send_message_to_thread" not in text or not contains_any(text, ["手动复制", "manual copy", "copyable report"]):
            findings.append(Finding("warning", "Agent Office/communication.md", "communication protocol should explain employee report transport and manual fallback"))
        if not contains_any(text, ["依赖等待", "Dependency Waiting", "wait for required"]):
            findings.append(Finding("warning", "Agent Office/communication.md", "communication protocol should explain dependency waiting before the next stage"))
        if not contains_any(text, ["汇报接收", "Report Intake", "report-intake"]):
            findings.append(Finding("warning", "Agent Office/communication.md", "communication protocol should include a project-director report intake record"))
        if "waiting-dependency" not in text:
            findings.append(Finding("warning", "Agent Office/communication.md", "communication protocol should include `waiting-dependency` for incomplete upstream reports"))
        if not contains_any(text, ["heartbeat", "自动推进", "automatic follow-up", "automatic progress"]):
            findings.append(Finding("warning", "Agent Office/communication.md", "communication protocol should explain opt-in automatic progress and heartbeat limits"))
        if not contains_any(text, ["生命周期状态", "lifecycle state"]) or not contains_any(text, ["授权等级", "authorization level"]):
            findings.append(Finding("warning", "Agent Office/communication.md", "communication protocol should explain lifecycle and authorization routing"))

    brief = root / "Agent Office/project-brief.md"
    if brief.exists() and not has_link_in_path(root, brief):
        text = read_text(brief)
        if not contains_any(text, ["controller-dispatch", "项目总监按需派工"]):
            findings.append(Finding("warning", "Agent Office/project-brief.md", "project brief should record the controller-dispatch collaboration style"))

    plan = root / "Agent Office/office-plan.json"
    if plan.exists() and not has_link_in_path(root, plan):
        try:
            data = json.loads(read_text(plan))
        except json.JSONDecodeError:
            findings.append(Finding("error", "Agent Office/office-plan.json", "office plan is not valid JSON"))
        else:
            if data.get("office_schema_version") != OFFICE_SCHEMA_VERSION:
                findings.append(
                    Finding(
                        "warning",
                        "Agent Office/office-plan.json",
                        f"office schema version is missing or stale; expected `{OFFICE_SCHEMA_VERSION}`",
                    )
                )
            if data.get("collaboration_mode") != "controller-dispatch":
                findings.append(Finding("warning", "Agent Office/office-plan.json", "collaboration_mode should be `controller-dispatch`"))
            if data.get("operation_model") != "stateful-router":
                findings.append(Finding("warning", "Agent Office/office-plan.json", "operation_model should be `stateful-router`"))
            expected_fields = {
                "task_reference_policy": "user-facing-title-internal-id",
                "progress_mode": "ask-per-workstream",
                "employee_report_route": "director-only",
                "employee_report_transport": "file-first-thread-index",
                "employee_report_fallback": "copyable-report",
                "employee_report_intake": "director-verifies-records-and-routes",
                "dependency_policy": "wait-for-required-inputs",
                "short_continue_policy": "contextual-natural-language",
                "role_calibration_policy": "ask-before-first-dispatch",
                "role_calibration_levels": "light-standard-deep-skip",
                "inter_agent_communication": "file-first-thread-index",
                "exchange_retention_policy": "consume-and-summarize-no-default-delete",
                "thread_permission_policy": "user-owned-per-thread",
            }
            for field, expected in expected_fields.items():
                if data.get(field) != expected:
                    findings.append(Finding("warning", "Agent Office/office-plan.json", f"{field} should be `{expected}`"))
            dispatch_policy = data.get("dispatch_policy")
            if not isinstance(dispatch_policy, dict):
                findings.append(Finding("warning", "Agent Office/office-plan.json", "dispatch_policy should record local-capacity-aware employee dispatch"))
            else:
                try:
                    max_parallel = int(dispatch_policy.get("max_parallel_employee_tasks", 0))
                except (TypeError, ValueError):
                    max_parallel = 0
                if max_parallel < 1:
                    findings.append(Finding("warning", "Agent Office/office-plan.json", "dispatch_policy.max_parallel_employee_tasks should be at least 1"))
                if not dispatch_policy.get("mode"):
                    findings.append(Finding("warning", "Agent Office/office-plan.json", "dispatch_policy.mode is missing"))


def validate_employees(root: Path, findings: list[Finding]) -> None:
    employees = root / "Agent Office/Employees"
    if not employees.is_dir() or has_link_in_path(root, employees):
        return
    employee_dirs = [path for path in employees.iterdir() if path.is_dir() and not has_link_in_path(root, path)]
    if not employee_dirs:
        findings.append(Finding("error", "Agent Office/Employees", "no employee role folders found"))
    registry_text = read_text(root / "Agent Office/thread-registry.md")
    if registry_text and not contains_any(registry_text, ["current-window", "项目总监"]):
        findings.append(Finding("warning", "Agent Office/thread-registry.md", "registry should identify the current chat as the founding project director"))
    if registry_text and not contains_any(registry_text, ["Current project-director window title", "当前项目总监窗口标题"]):
        findings.append(Finding("warning", "Agent Office/thread-registry.md", "registry should state the title for the current project-director chat"))
    if registry_text:
        for line in registry_text.splitlines():
            if line.startswith("|") and " / " in line and "Thread Title" not in line and "---" not in line:
                findings.append(Finding("warning", "Agent Office/thread-registry.md", "thread title should use the employee job title only, not `project / role`"))
                break
    for employee in sorted(employee_dirs):
        rel_employee = str(employee.relative_to(root)).replace("\\", "/")
        readme_text = read_text(employee / "README.md")
        title_match = re.search(r"^#\s+(.+)$", readme_text, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else employee.name
        current_window_employee = bool(
            registry_text
            and re.search(rf"^\|\s*{re.escape(title)}\s*\|[^\n]*(current-window|项目总监)", registry_text, re.MULTILINE)
        )
        title_lower = title.lower()
        if any(token in title_lower or token in title for token in BAD_ROLE_TITLE_TOKENS):
            findings.append(Finding("warning", f"{rel_employee}/README.md", "employee display title looks like a responsibility domain; use a human job title"))
        if not contains_any(readme_text, ["职责域", "Responsibility Domain"]):
            findings.append(Finding("warning", f"{rel_employee}/README.md", "employee profile should separate job title from responsibility domain"))
        for filename in ["README.md", "memory.md", "current-task.md"]:
            path = employee / filename
            rel = f"{rel_employee}/{filename}"
            if not path.is_file():
                findings.append(Finding("error", rel, "employee file is missing"))
                continue
            if has_link_in_path(root, path):
                findings.append(Finding("error", rel, "employee file path contains a symlink or junction"))
            limit = EMPLOYEE_BUDGETS[filename]
            count = budget_units(path)
            if count > limit:
                findings.append(Finding("warning", rel, f"budget units {count} exceeds hard limit {limit}"))
        for rel in [f"{rel_employee}/README.md", f"{rel_employee}/memory.md", f"{rel_employee}/current-task.md"]:
            if registry_text and not current_window_employee and rel not in registry_text:
                findings.append(Finding("warning", "Agent Office/thread-registry.md", f"thread launch prompts should mention `{rel}`"))
        memory_text = read_text(employee / "memory.md")
        if not contains_any(memory_text, ["## Next Action"]):
            findings.append(Finding("warning", f"{rel_employee}/memory.md", "memory should have a `## Next Action` section"))
        if not contains_any(memory_text, ["## Work Log"]):
            findings.append(Finding("warning", f"{rel_employee}/memory.md", "memory should have a `## Work Log` section"))
        if not contains_any(memory_text, ["Role Calibration", "岗位校准"]):
            findings.append(Finding("warning", f"{rel_employee}/memory.md", "memory should include a role calibration section for first-assignment self-learning"))
        task_text = read_text(employee / "current-task.md")
        if not contains_any(task_text, ["status: waiting", "status: active", "status: deferred", "status: cancelled", "status: done"]):
            findings.append(Finding("warning", f"{rel_employee}/current-task.md", "current-task should record a task status"))
        if not contains_any(task_text, ["Role Calibration", "岗位校准"]) or not contains_any(task_text, ["Exchange/Reports", "完整汇报"]):
            findings.append(Finding("warning", f"{rel_employee}/current-task.md", "current-task should mention role calibration and file-first report handling"))


def validate_budgets(root: Path, findings: list[Finding]) -> None:
    for rel, limit in BUDGETS.items():
        path = root / rel
        if not path.is_file():
            continue
        if has_link_in_path(root, path):
            findings.append(Finding("warning", rel, "skipped linked path during word budget check"))
            continue
        count = budget_units(path)
        if count > limit:
            findings.append(Finding("warning", rel, f"budget units {count} exceeds hard limit {limit}"))


def validate_migration_report(root: Path, findings: list[Finding]) -> None:
    report = root / "Agent Office/migration-report.md"
    archive_dir = root / "Agent Office/Archive/Old Project Memory"
    if not report.exists():
        return
    if has_link_in_path(root, report):
        findings.append(Finding("error", "Agent Office/migration-report.md", "migration report path contains a symlink or junction"))
        return
    text = read_text(report)
    rel_report = "Agent Office/migration-report.md"
    required_sections = [
        "Project Map",
        "Candidates",
        "Likely Authoritative Files",
        "Stale Or Conflicting Files",
        "Active Tasks Found",
        "Decisions Found",
        "Absorption Map",
        "Proposed AGENTS Replacement",
        "Recommended Roles",
        "Proposed Archive List",
        "Proposed Move List",
        "Proposed Delete List",
        "User Questions",
        "User Approval Record",
    ]
    for heading in required_sections:
        if f"## {heading}" not in text:
            findings.append(Finding("warning", rel_report, f"migration report is missing `## {heading}`"))

    agents_section = markdown_section(text, "Proposed AGENTS Replacement")
    if agents_section and "Agent Office/Proposals/AGENTS.proposed.md" not in agents_section:
        findings.append(Finding("warning", rel_report, "proposed AGENTS replacement should point to `Agent Office/Proposals/AGENTS.proposed.md`"))

    archive_section = markdown_section(text, "Proposed Archive List")
    approval_section = markdown_section(text, "User Approval Record")
    agents_replacement_approved = approval_value(approval_section, "Approved AGENTS replacement") == "YES"
    if agents_section and agents_replacement_approved and (root / "AGENTS.md").exists() and not list(root.glob("AGENTS.md.gaogao-office-*.bak")):
        findings.append(Finding("warning", "AGENTS.md", "approved AGENTS replacement should leave a dated `AGENTS.md.gaogao-office-*.bak` backup when replacing an existing root AGENTS.md"))
    proposed_archive = table_source_paths(archive_section)
    absorption_entries = {entry.path: entry for entry in table_source_entries(markdown_section(text, "Absorption Map"))}
    archived = archive_files(archive_dir) if not has_link_in_path(root, archive_dir) else []
    archive_approved = approval_value(approval_section, "Approved archive list") == "YES"
    for source in proposed_archive:
        if not is_safe_report_path(source):
            findings.append(Finding("error", rel_report, f"`{source}` is not a safe project-relative archive path"))
        elif not (root / source).exists() and not archive_contains_source(archive_dir, archived, source):
            findings.append(Finding("warning", rel_report, f"`{source}` is missing from the project and no archive copy with the same filename was found"))
        absorption_entry = absorption_entries.get(source)
        if absorption_entry is None:
            severity = "error" if archive_approved else "warning"
            findings.append(Finding(severity, rel_report, f"`{source}` appears in the archive list but not in the absorption map"))
        elif not entry_absorption_complete(absorption_entry.line):
            severity = "error" if archive_approved else "warning"
            findings.append(Finding(severity, rel_report, f"`{source}` must be marked absorbed in the absorption map before archiving"))
    if proposed_archive and not archive_approved:
        findings.append(Finding("info", rel_report, "archive plan is not marked approved yet"))

    move_entries = table_source_entries(markdown_section(text, "Proposed Move List"))
    if move_entries and not proposed_archive:
        findings.append(Finding("error", rel_report, "move list exists but no archive list was found"))
    if move_entries and not archive_approved:
        findings.append(Finding("error", rel_report, "move list exists but the archive list is not marked approved"))
    for entry in move_entries:
        source = entry.path
        if not is_safe_report_path(source):
            findings.append(Finding("error", rel_report, f"`{source}` is not a safe project-relative move path"))
            continue
        if source not in proposed_archive:
            findings.append(Finding("error", rel_report, f"`{source}` move entry must also appear in the proposed archive list"))
        if not entry_has_reason(entry.line):
            findings.append(Finding("error", rel_report, f"`{source}` move entry needs a per-file reason"))
        if not entry_has_disposition(entry.line):
            findings.append(Finding("error", rel_report, f"`{source}` move entry must say the content was absorbed, migrated, or intentionally discarded"))
    if move_entries and approval_value(approval_section, "Approved legacy move list") != "YES":
        findings.append(Finding("error", rel_report, "move list exists but is not marked approved"))

    delete_entries = table_source_entries(markdown_section(text, "Proposed Delete List"))
    for entry in delete_entries:
        source = entry.path
        if not is_safe_report_path(source):
            findings.append(Finding("error", rel_report, f"`{source}` is not a safe project-relative deletion path"))
            continue
        if not entry_has_reason(entry.line):
            findings.append(Finding("error", rel_report, f"`{source}` deletion entry needs a per-file reason"))
        if not entry_has_disposition(entry.line):
            findings.append(Finding("error", rel_report, f"`{source}` deletion entry must say the content was migrated or intentionally discarded"))
        if not archive_contains_source(archive_dir, archived, source):
            findings.append(Finding("error", rel_report, f"`{source}` deletion entry has no durable archive copy"))
    if delete_entries and approval_value(approval_section, "Approved deletion list") != "YES":
        findings.append(Finding("error", rel_report, "deletion list exists but is not marked approved"))


def validate(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    validate_required_paths(root, findings)
    validate_content(root, findings)
    validate_employees(root, findings)
    validate_budgets(root, findings)
    validate_migration_report(root, findings)
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a GaoGao Office project office.")
    parser.add_argument("--project-root", default=".", help="Project root to validate")
    parser.add_argument("--warn-only", action="store_true", help="Always exit 0")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    if is_unsafe_root(root):
        raise SystemExit(f"Refusing to validate unsafe project root: {root}")
    findings = validate(root)
    if not findings:
        print("GaoGao Office validation passed.")
        return 0
    print("# GaoGao Office Validation Report\n")
    for finding in findings:
        print(f"- [{finding.severity.upper()}] `{finding.path}`: {finding.message}")
    has_error = any(item.severity == "error" for item in findings)
    return 0 if args.warn_only or not has_error else 1


if __name__ == "__main__":
    raise SystemExit(main())
