#!/usr/bin/env python3
"""Validate an Agent Office OS project office."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PureWindowsPath


REQUIRED_FILES = [
    "AGENTS.md",
    "docs/agent-office/README.md",
    "docs/agent-office/status.md",
    "docs/agent-office/thread-registry.md",
    "docs/agent-office/communication.md",
    "docs/agent-office/operating-model.md",
    "docs/agent-office/context-packs/project-brief.md",
    "docs/agent-office/context-packs/thread-launch-prompts.md",
]

REQUIRED_DIRS = [
    "docs/agent-office/roles",
    "docs/agent-office/tasks/active",
    "docs/agent-office/tasks/done",
    "docs/agent-office/tasks/archived",
    "docs/agent-office/messages/open",
    "docs/agent-office/messages/closed",
    "docs/agent-office/handoffs",
    "docs/agent-office/decisions",
    "docs/agent-office/context-packs",
    "docs/agent-office/cadences",
    "docs/agent-office/archive/legacy-management",
]

BUDGETS = {
    "AGENTS.md": 1500,
    "docs/agent-office/status.md": 1200,
    "docs/agent-office/communication.md": 900,
}

GLOB_BUDGETS = {
    "docs/agent-office/roles/*.md": 600,
    "docs/agent-office/tasks/active/*.md": 1000,
    "docs/agent-office/tasks/done/*.md": 1000,
    "docs/agent-office/messages/open/*.md": 400,
    "docs/agent-office/messages/closed/*.md": 400,
    "docs/agent-office/handoffs/*.md": 700,
    "docs/agent-office/decisions/*.md": 1200,
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


def word_count(path: Path) -> int:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return 0
    return len(re.findall(r"\S+", text))


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


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


def frontmatter_block(text: str) -> str:
    match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", text, re.DOTALL)
    if not match:
        return ""
    return match.group(1)


def frontmatter_value(text: str, key: str) -> str | None:
    frontmatter = frontmatter_block(text)
    if not frontmatter:
        return None
    pattern = re.compile(rf"^{re.escape(key)}:[ \t]*(.*)$", re.MULTILINE)
    match = pattern.search(frontmatter)
    if not match:
        return None
    return match.group(1).strip()


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


def unescape_markdown_table_code(value: str) -> str:
    return value.replace("\\|", "|")


def is_markdown_table_separator(line: str) -> bool:
    if "|" not in line:
        return False
    cells = [cell.strip() for cell in line.strip("|").split("|")]
    if not cells:
        return False
    return all(re.fullmatch(r":?-{3,}:?", cell or "") for cell in cells)


def archive_files(archive_dir: Path) -> list[Path]:
    if not archive_dir.is_dir():
        return []
    return [
        path
        for path in archive_dir.rglob("*")
        if path.is_file() and path.name != ".gitkeep" and not has_link_in_path(archive_dir, path)
    ]


def linked_archive_entries(archive_dir: Path) -> list[Path]:
    if not archive_dir.is_dir():
        return []
    entries: list[Path] = []
    for path in archive_dir.rglob("*"):
        if path.name == ".gitkeep":
            continue
        if has_link_in_path(archive_dir, path):
            entries.append(path)
    return entries


def archive_contains_source(archive_dir: Path, archived: list[Path], source: str) -> bool:
    if not is_safe_report_path(source):
        return False
    normalized_source = Path(source.replace("\\", "/"))
    source_parts = normalized_source.parts
    if not source_parts:
        return False
    for archived_file in archived:
        try:
            archived_parts = archived_file.relative_to(archive_dir).parts
        except ValueError:
            continue
        if len(archived_parts) >= len(source_parts) and archived_parts[-len(source_parts) :] == source_parts:
            return True
    return False


def is_safe_report_path(raw_path: str) -> bool:
    normalized = raw_path.replace("\\", "/")
    path = Path(normalized)
    windows_path = PureWindowsPath(raw_path)
    if path.is_absolute() or windows_path.is_absolute() or windows_path.drive:
        return False
    return ".." not in path.parts


def report_line_explanation(line: str) -> str:
    without_code = re.sub(r"(`+)(.*?)\1", " ", line)
    cleaned = re.sub(r"[\|\-\*\s]+", " ", without_code).strip(" :;,.")
    return re.sub(r"\s+", " ", cleaned)


def delete_entry_has_reason(line: str) -> bool:
    explanation = report_line_explanation(line)
    return len(re.findall(r"[A-Za-z0-9]+", explanation)) >= 2


def delete_entry_has_disposition(line: str) -> bool:
    explanation = report_line_explanation(line).lower()
    return any(token in explanation for token in ["migrated", "migration", "discarded", "discard"])


def task_id_from_stem(stem: str) -> str:
    match = re.match(r"^(T-\d+)", stem)
    if match:
        return match.group(1)
    return stem.split("-")[0]


def validate(root: Path, stale_days: int) -> list[Finding]:
    findings: list[Finding] = []
    for rel in REQUIRED_FILES:
        path = root / rel
        if path.exists() and has_link_in_path(root, path):
            findings.append(Finding("error", rel, "required file path contains a symlink or junction"))
            continue
        if not path.exists():
            findings.append(Finding("error", rel, "required file is missing"))
    launch_prompts = root / "docs/agent-office/context-packs/thread-launch-prompts.md"
    if launch_prompts.exists() and not has_link_in_path(root, launch_prompts):
        try:
            launch_text = launch_prompts.read_text(encoding="utf-8", errors="replace")
        except OSError:
            launch_text = ""
        for token in ["You are the", "project-brief.md", "thread-registry.md", "communication.md", "messages/open", "handoffs"]:
            if token not in launch_text:
                findings.append(
                    Finding(
                        "warning",
                        "docs/agent-office/context-packs/thread-launch-prompts.md",
                        f"thread launch prompts should mention `{token}`",
                    )
                )
    communication = root / "docs/agent-office/communication.md"
    if communication.exists() and not has_link_in_path(root, communication):
        try:
            communication_text = communication.read_text(encoding="utf-8", errors="replace")
        except OSError:
            communication_text = ""
        for token in ["messages/open", "messages/closed", "handoffs", "status: open", "status: resolved", "next owner"]:
            if token not in communication_text:
                findings.append(
                    Finding(
                        "warning",
                        "docs/agent-office/communication.md",
                        f"communication protocol should mention `{token}`",
                    )
                )
    project_brief = root / "docs/agent-office/context-packs/project-brief.md"
    if project_brief.exists() and not has_link_in_path(root, project_brief):
        try:
            brief_text = project_brief.read_text(encoding="utf-8", errors="replace")
        except OSError:
            brief_text = ""
        for token in ["Project type:", "Office profile:", "Risk level:", "Standing roles:", "First Milestone"]:
            if token not in brief_text:
                findings.append(
                    Finding(
                        "warning",
                        "docs/agent-office/context-packs/project-brief.md",
                        f"project brief should mention `{token}`",
                    )
                )
    for rel in REQUIRED_DIRS:
        path = root / rel
        if path.exists() and has_link_in_path(root, path):
            findings.append(Finding("error", rel, "required directory path contains a symlink or junction"))
            continue
        if not path.is_dir():
            findings.append(Finding("error", rel, "required directory is missing"))

    for rel, limit in BUDGETS.items():
        path = root / rel
        if path.exists():
            if has_link_in_path(root, path):
                findings.append(Finding("warning", rel, "skipped linked path during word budget check"))
                continue
            count = word_count(path)
            if count > limit:
                findings.append(Finding("warning", rel, f"word count {count} exceeds hard limit {limit}"))
    for pattern, limit in GLOB_BUDGETS.items():
        for path in sorted(root.glob(pattern)):
            if not path.is_file() or path.name == ".gitkeep":
                continue
            rel = str(path.relative_to(root)).replace("\\", "/")
            if has_link_in_path(root, path):
                findings.append(Finding("warning", rel, "skipped linked path during word budget check"))
                continue
            count = word_count(path)
            if count > limit:
                findings.append(Finding("warning", rel, f"word count {count} exceeds hard limit {limit}"))

    roles_dir = root / "docs/agent-office/roles"
    if roles_dir.is_dir() and not has_link_in_path(root, roles_dir):
        roles = [p for p in roles_dir.glob("*.md") if p.is_file()]
        if not roles:
            findings.append(Finding("error", "docs/agent-office/roles", "no role cards found"))

    active_dir = root / "docs/agent-office/tasks/active"
    if active_dir.is_dir() and not has_link_in_path(root, active_dir):
        for task in sorted(active_dir.glob("*.md")):
            if has_link_in_path(root, task):
                rel = str(task.relative_to(root)).replace("\\", "/")
                findings.append(Finding("warning", rel, "skipped linked task packet"))
                continue
            text = read_text(task)
            frontmatter = frontmatter_block(text)
            rel = str(task.relative_to(root)).replace("\\", "/")
            if not frontmatter:
                findings.append(Finding("warning", rel, "task packet is missing YAML frontmatter"))
            for field in ["id:", "status:", "dri:", "reviewer:", "created:"]:
                if field not in frontmatter:
                    findings.append(Finding("warning", rel, f"task packet is missing `{field}`"))
            for key in ["id", "status", "dri", "reviewer", "created"]:
                value = frontmatter_value(text, key)
                if value is not None and not value:
                    findings.append(Finding("warning", rel, f"task packet has blank `{key}`"))
            for section in ["## Goal", "## Write Scope", "## Acceptance Criteria", "## Verification"]:
                if section not in text:
                    findings.append(Finding("warning", rel, f"task packet is missing `{section}`"))

    open_messages = root / "docs/agent-office/messages/open"
    if open_messages.is_dir() and not has_link_in_path(root, open_messages):
        now = datetime.now(timezone.utc).timestamp()
        for message in sorted(open_messages.glob("*.md")):
            if message.name == ".gitkeep":
                continue
            if has_link_in_path(root, message):
                rel = str(message.relative_to(root)).replace("\\", "/")
                findings.append(Finding("warning", rel, "skipped linked open message"))
                continue
            rel = str(message.relative_to(root)).replace("\\", "/")
            findings.append(Finding("info", rel, "open message requires owner review"))
            age_days = (now - message.stat().st_mtime) / 86400
            if age_days > stale_days:
                findings.append(Finding("warning", rel, f"open message appears stale ({age_days:.0f} days old)"))

    registry = root / "docs/agent-office/thread-registry.md"
    if registry.exists() and not has_link_in_path(root, registry):
        text = read_text(registry)
        if "TBD" in text:
            findings.append(Finding("info", "docs/agent-office/thread-registry.md", "thread registry still contains TBD entries"))
        for state in ["active", "idle", "waiting", "retired", "archived"]:
            if state in text:
                break
        else:
            findings.append(Finding("warning", "docs/agent-office/thread-registry.md", "thread registry has no recognized thread states"))

    done_dir = root / "docs/agent-office/tasks/done"
    handoffs_dir = root / "docs/agent-office/handoffs"
    if done_dir.is_dir() and handoffs_dir.is_dir() and not has_link_in_path(root, done_dir) and not has_link_in_path(root, handoffs_dir):
        handoff_text = "\n".join(path.name for path in handoffs_dir.glob("*.md"))
        for task in done_dir.glob("*.md"):
            if task.name == ".gitkeep":
                continue
            if has_link_in_path(root, task):
                rel = str(task.relative_to(root)).replace("\\", "/")
                findings.append(Finding("warning", rel, "skipped linked done task"))
                continue
            task_id = task_id_from_stem(task.stem)
            if task_id and task_id not in handoff_text:
                rel = str(task.relative_to(root)).replace("\\", "/")
                findings.append(Finding("info", rel, "done task may need a matching handoff"))

    migration_report = root / "docs/agent-office/migration-report.md"
    archive_dir = root / "docs/agent-office/archive/legacy-management"
    if migration_report.exists() and not has_link_in_path(root, migration_report):
        text = read_text(migration_report)
        rel_report = "docs/agent-office/migration-report.md"
        required_sections = [
            "Candidates",
            "Likely Authoritative Files",
            "Stale Or Conflicting Files",
            "Active Tasks Found",
            "Decisions Found",
            "Recommended Roles",
            "Proposed Archive List",
            "Proposed Delete List",
            "User Questions",
            "User Approval Record",
        ]
        for heading in required_sections:
            if f"## {heading}" not in text:
                findings.append(Finding("warning", rel_report, f"migration report is missing `## {heading}`"))

        archive_section = markdown_section(text, "Proposed Archive List")
        approval_section = markdown_section(text, "User Approval Record")
        proposed_archive = table_source_paths(archive_section)
        archived = [] if has_link_in_path(root, archive_dir) else archive_files(archive_dir)
        linked_archives = [] if has_link_in_path(root, archive_dir) else linked_archive_entries(archive_dir)
        for linked in linked_archives:
            try:
                rel_linked = str(linked.relative_to(root)).replace("\\", "/")
            except ValueError:
                rel_linked = str(linked)
            findings.append(Finding("error", rel_linked, "archive entry is a symlink or junction, not a durable copy"))

        for source in proposed_archive:
            if not is_safe_report_path(source):
                findings.append(Finding("error", rel_report, f"`{source}` is not a safe project-relative archive path"))

        if proposed_archive and not archived:
            findings.append(
                Finding(
                    "warning",
                    "docs/agent-office/archive/legacy-management",
                    "migration report proposes archiving files, but the legacy archive contains no archived files yet",
                )
            )
        if proposed_archive and approval_value(approval_section, "Approved archive list") != "YES":
            findings.append(Finding("info", rel_report, "archive plan is not marked approved yet"))
        for source in proposed_archive:
            if not is_safe_report_path(source):
                continue
            source_path = root / source
            if not source_path.exists() and not archive_contains_source(archive_dir, archived, source):
                findings.append(
                    Finding(
                        "warning",
                        rel_report,
                        f"`{source}` is missing from the project and no archive copy with the same filename was found",
                    )
                )

        delete_section = markdown_section(text, "Proposed Delete List")
        delete_entries = table_source_entries(delete_section)
        proposed_delete = [entry.path for entry in delete_entries]
        for entry in delete_entries:
            source = entry.path
            if not is_safe_report_path(source):
                findings.append(Finding("error", rel_report, f"`{source}` is not a safe project-relative deletion path"))
                continue
            if not delete_entry_has_reason(entry.line):
                findings.append(Finding("error", rel_report, f"`{source}` deletion entry needs a per-file reason"))
            if not delete_entry_has_disposition(entry.line):
                findings.append(
                    Finding(
                        "error",
                        rel_report,
                        f"`{source}` deletion entry must say the content was migrated or intentionally discarded",
                    )
                )
            if not archive_contains_source(archive_dir, archived, source):
                findings.append(Finding("error", rel_report, f"`{source}` deletion entry has no durable archive copy"))
        if proposed_delete and approval_value(approval_section, "Approved deletion list") != "YES":
            findings.append(Finding("error", rel_report, "deletion list exists but is not marked approved"))

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an Agent Office OS project office.")
    parser.add_argument("--project-root", default=".", help="Project root to validate")
    parser.add_argument("--stale-days", type=int, default=7, help="Age threshold for stale open messages")
    parser.add_argument("--warn-only", action="store_true", help="Always exit 0")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    findings = validate(root, args.stale_days)

    if not findings:
        print("Agent Office OS validation passed.")
        return 0

    print("# Agent Office OS Validation Report\n")
    for finding in findings:
        print(f"- [{finding.severity.upper()}] `{finding.path}`: {finding.message}")

    has_error = any(item.severity == "error" for item in findings)
    return 0 if args.warn_only or not has_error else 1


if __name__ == "__main__":
    raise SystemExit(main())
