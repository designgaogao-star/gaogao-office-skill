#!/usr/bin/env python3
"""Inspect a project for GaoGao Office migration and cleanup.

Default mode is read-only and writes the report to stdout. If --output is used,
the output path must stay inside the selected project root.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path


OFFICE_PREFIX_LOWER = ("agent office",)

SKIP_DIRS = {
    ".git",
    "node_modules",
    "vendor",
    "dist",
    "build",
    "target",
    ".venv",
    "venv",
    "__pycache__",
    ".cache",
    ".playwright-cli",
    ".gpt-image-venv",
    "output",
    "outputs",
    "tmp",
    "temp",
    "logs",
}

SENSITIVE_DIRS = {".ssh", ".aws", ".gnupg"}
SENSITIVE_NAMES = {
    ".env",
    ".env.local",
    ".env.production",
    ".npmrc",
    ".pypirc",
    "credentials.json",
    "secrets.json",
    "secrets.yaml",
    "secrets.yml",
    "id_rsa",
    "id_ed25519",
}

EXACT_NAMES = {
    "AGENTS.md",
    "AGENTS.override.md",
    "CLAUDE.md",
    "GEMINI.md",
    "VIBE.md",
    ".cursorrules",
    "PLANS.md",
    "README.md",
}
EXACT_NAMES_LOWER = {name.lower() for name in EXACT_NAMES}

KEYWORD_ORDER = [
    "vibe",
    "task",
    "todo",
    "adr",
    "decision",
    "status",
    "handoff",
    "context",
    "roadmap",
    "milestone",
    "planning",
    "plan",
    "architecture",
    "requirements",
    "spec",
    "sprint",
    "meeting",
    "copy",
    "brief",
    "guide",
    "rule",
    "boundary",
    "workflow",
    "checklist",
    "changelog",
    "文案",
    "策划",
    "任务",
    "计划",
    "上下文",
    "规则",
    "边界",
    "流程",
    "检查",
    "交接",
    "决策",
]

PLAIN_TEXT_EXTS = {".md", ".txt", ".rst", ".adoc"}
STRUCTURED_TEXT_EXTS = {".toml", ".yaml", ".yml", ".json", ".jsonl", ".csv", ".tsv"}
TEXT_EXTS = PLAIN_TEXT_EXTS | STRUCTURED_TEXT_EXTS
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".bmp", ".tiff"}
MEDIA_EXTS = {".mp4", ".mov", ".avi", ".mp3", ".wav", ".m4a"}
MAX_TEXT_BYTES = 2_000_000


@dataclass
class FileEntry:
    path: str
    kind: str
    read_policy: str
    size: int


@dataclass
class Candidate:
    path: str
    kind: str
    score: int
    reasons: list[str]


def is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


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


def resolve_inside_root(root: Path, raw: str) -> Path:
    candidate = Path(raw)
    if candidate.is_absolute():
        return candidate.resolve()
    return (root / candidate).resolve()


def should_prune_dir(root: Path, path: Path) -> bool:
    if path.name.lower() in SKIP_DIRS:
        return True
    try:
        rel = path.relative_to(root)
    except ValueError:
        return True
    if len(rel.parts) >= 1 and tuple(part.lower() for part in rel.parts[:1]) == OFFICE_PREFIX_LOWER:
        return True
    return has_link_in_path(root, path)


def is_sensitive_path(rel_path: Path) -> bool:
    lower_parts = {part.lower() for part in rel_path.parts}
    lower_name = rel_path.name.lower()
    if lower_parts & SENSITIVE_DIRS:
        return True
    if lower_name in SENSITIVE_NAMES:
        return True
    if lower_name.startswith(".env"):
        return True
    if "secret" in lower_name or "credential" in lower_name or "token" in lower_name:
        return True
    if lower_name.endswith((".pem", ".key")) and ("key" in lower_name or "private" in lower_name):
        return True
    return False


def skip_reason(rel_parts: tuple[str, ...]) -> str | None:
    lower = tuple(part.lower() for part in rel_parts)
    if len(rel_parts) >= 1 and tuple(part.lower() for part in rel_parts[:1]) == OFFICE_PREFIX_LOWER:
        return "existing office skipped"
    for part in lower:
        if part in SKIP_DIRS:
            return f"skipped directory: {part}"
    return None


def file_kind(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in IMAGE_EXTS:
        return "image"
    if suffix in MEDIA_EXTS:
        return "media"
    if suffix in TEXT_EXTS or path.name.lower() in EXACT_NAMES_LOWER:
        return "text"
    return "binary-or-unknown"


def has_management_hint(rel: Path) -> bool:
    lower_path = str(rel).replace("\\", "/").lower()
    lower_name = rel.name.lower()
    if lower_name in EXACT_NAMES_LOWER:
        return True
    if ".github/" in lower_path or ".codex/" in lower_path or ".agents/" in lower_path:
        return True
    return any(keyword in lower_path for keyword in KEYWORD_ORDER)


def read_policy(path: Path, rel: Path, root: Path) -> str:
    if has_link_in_path(root, path):
        return "linked-skip"
    if is_sensitive_path(rel):
        return "sensitive-skip"
    kind = file_kind(path)
    if kind in {"image", "media", "binary-or-unknown"}:
        return "metadata-only"
    try:
        size = path.stat().st_size
    except OSError:
        return "unreadable"
    if size > MAX_TEXT_BYTES:
        return "large-text-skip"
    if path.suffix.lower() in STRUCTURED_TEXT_EXTS and not has_management_hint(rel):
        return "structured-metadata-only"
    return "candidate-text"


def iter_inventory(root: Path) -> list[FileEntry]:
    entries: list[FileEntry] = []
    for dirpath, dirnames, filenames in os.walk(root):
        current_dir = Path(dirpath)
        if has_link_in_path(root, current_dir):
            dirnames[:] = []
            continue
        dirnames[:] = [
            dirname
            for dirname in dirnames
            if not should_prune_dir(root, current_dir / dirname)
        ]
        for filename in filenames:
            path = current_dir / filename
            try:
                rel = path.relative_to(root)
            except ValueError:
                continue
            reason = skip_reason(rel.parts)
            if reason:
                continue
            if not path.is_file():
                continue
            try:
                size = path.stat().st_size
            except OSError:
                size = 0
            entries.append(
                FileEntry(
                    str(rel).replace("\\", "/"),
                    file_kind(path),
                    read_policy(path, rel, root),
                    size,
                )
            )
    entries.sort(key=lambda item: item.path.lower())
    return entries


def classify(rel_path: str, text: str) -> tuple[str, int, list[str]]:
    name = Path(rel_path).name
    lower_name = name.lower()
    lower_path = rel_path.lower()
    lower_text = text.lower()
    score = 0
    reasons: list[str] = []

    if lower_name in EXACT_NAMES_LOWER:
        score += 8
        reasons.append("known project, agent, or planning filename")
    for keyword in KEYWORD_ORDER:
        if keyword in lower_name or keyword in lower_path:
            score += 3
            reasons.append(f"path contains '{keyword}'")
            break
    content_hits = [keyword for keyword in KEYWORD_ORDER if keyword in lower_text]
    if content_hits:
        score += min(5, len(content_hits))
        reasons.append("content contains management keywords")
    if ".github" in lower_path or ".codex" in lower_path or ".agents" in lower_path:
        score += 3
        reasons.append("tooling or agent configuration area")

    if lower_name in {"agents.md", "agents.override.md", "claude.md", "gemini.md", ".cursorrules"}:
        kind = "agent-instructions"
    elif "adr" in lower_path or "decision" in lower_path or "决策" in lower_path:
        kind = "decision-record"
    elif "task" in lower_path or "todo" in lower_path or "任务" in lower_path:
        kind = "task-tracking"
    elif "roadmap" in lower_path or "plan" in lower_path or "milestone" in lower_path or "计划" in lower_path:
        kind = "planning"
    elif (
        "status" in lower_path
        or "handoff" in lower_path
        or "context" in lower_path
        or "vibe" in lower_path
        or "rule" in lower_path
        or "boundary" in lower_path
        or "workflow" in lower_path
        or "checklist" in lower_path
        or "changelog" in lower_path
        or "上下文" in lower_path
        or "规则" in lower_path
        or "边界" in lower_path
        or "流程" in lower_path
    ):
        kind = "project-memory"
    elif "copy" in lower_path or "文案" in lower_path:
        kind = "project-copy"
    elif ".github" in lower_path or ".codex" in lower_path or ".agents" in lower_path:
        kind = "tooling-config"
    else:
        kind = "possible-management-doc"
    return kind, score, reasons


def inspect_candidates(root: Path, inventory: list[FileEntry]) -> list[Candidate]:
    candidates: list[Candidate] = []
    by_path = {item.path: item for item in inventory}
    for rel_path, entry in by_path.items():
        if entry.read_policy != "candidate-text":
            if entry.read_policy in {"linked-skip", "sensitive-skip"}:
                candidates.append(Candidate(rel_path, entry.read_policy, 0, [f"{entry.read_policy} without reading contents"]))
            continue
        path = root / rel_path
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        kind, score, reasons = classify(rel_path, text)
        if score >= 3:
            candidates.append(Candidate(rel_path, kind, score, reasons))
    candidates.sort(key=lambda item: (-item.score, item.path.lower()))
    return candidates


def markdown_code(value: str) -> str:
    longest = max((len(match.group(0)) for match in re.finditer(r"`+", value)), default=0)
    fence = "`" * (longest + 1)
    if "`" in value:
        return f"{fence} {value} {fence}"
    return f"{fence}{value}{fence}"


def markdown_table_cell(value: str) -> str:
    return value.replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ")


def render_inventory_table(inventory: list[FileEntry]) -> list[str]:
    if not inventory:
        return ["No files found."]
    lines = ["| Path | Kind | Read Policy | Size |", "|---|---|---|---:|"]
    for item in inventory:
        lines.append(
            f"| {markdown_table_cell(markdown_code(item.path))} | {item.kind} | {item.read_policy} | {item.size} |"
        )
    return lines


def render_candidate_table(candidates: list[Candidate]) -> list[str]:
    if not candidates:
        return ["No items found."]
    lines = ["| Path | Kind | Score | Reasons |", "|---|---|---:|---|"]
    for item in candidates:
        lines.append(
            f"| {markdown_table_cell(markdown_code(item.path))} | {item.kind} | {item.score} | {markdown_table_cell('; '.join(item.reasons))} |"
        )
    return lines


def absorption_destination(kind: str) -> tuple[str, str]:
    if kind == "agent-instructions":
        return ("build/test/safety rules and office entrypoint", "Agent Office/Proposals/AGENTS.proposed.md")
    if kind == "task-tracking":
        return ("active or historical work items", "Agent Office/task-board.md; Agent Office/communication.md")
    if kind == "decision-record":
        return ("accepted decisions and tradeoffs", "Agent Office/decisions.md")
    if kind == "planning":
        return ("goals, milestones, and roadmap constraints", "Agent Office/status.md; Agent Office/project-brief.md")
    if kind == "project-memory":
        return ("durable project context, vibe, blockers, and open questions", "Agent Office/project-brief.md; Agent Office/project-map.md")
    if kind == "project-copy":
        return ("durable copy direction and user-facing content constraints", "Agent Office/project-brief.md; employee current-task.md")
    if kind == "tooling-config":
        return ("tooling rules that still affect agent work", "Agent Office/Proposals/AGENTS.proposed.md")
    return ("possible durable project-management facts", "Agent Office/project-map.md user questions")


def render_absorption_table(candidates: list[Candidate]) -> list[str]:
    migratable = [item for item in candidates if item.kind not in {"linked-skip", "sensitive-skip"}]
    if not migratable:
        return ["No migratable items found."]
    lines = ["| Source | Durable Facts To Absorb | New Office Destination | Status |", "|---|---|---|---|"]
    for item in migratable:
        facts, destination = absorption_destination(item.kind)
        lines.append(
            f"| {markdown_table_cell(markdown_code(item.path))} | {markdown_table_cell(facts)} | {markdown_table_cell(markdown_code(destination))} | needs absorption note |"
        )
    return lines


def render_archive_table(candidates: list[Candidate], archive_stamp: str) -> list[str]:
    migratable = [item for item in candidates if item.kind not in {"linked-skip", "sensitive-skip"}]
    if not migratable:
        return ["No items proposed."]
    lines = ["| Source | Proposed Archive Destination | Reason |", "|---|---|---|"]
    for item in migratable:
        destination = f"Agent Office/Archive/Old Project Memory/{archive_stamp}/{item.path}"
        facts, office_destination = absorption_destination(item.kind)
        reason = f"archive after absorbing {facts} into {office_destination}; source classified as {item.kind}"
        lines.append(
            f"| {markdown_table_cell(markdown_code(item.path))} | {markdown_table_cell(markdown_code(destination))} | {markdown_table_cell(reason)} |"
        )
    return lines


def render_markdown(root: Path, inventory: list[FileEntry], candidates: list[Candidate]) -> str:
    archive_stamp = date.today().isoformat()
    sensitive = [item for item in candidates if item.kind == "sensitive-skip"]
    linked = [item for item in candidates if item.kind == "linked-skip"]
    migratable = [item for item in candidates if item.kind not in {"sensitive-skip", "linked-skip"}]
    authoritative = [item for item in migratable if item.kind in {"agent-instructions", "decision-record"} or item.score >= 10]
    active_tasks = [item for item in migratable if item.kind == "task-tracking"]
    decisions = [item for item in migratable if item.kind == "decision-record"]
    conflicts = [item for item in migratable if item.kind in {"agent-instructions", "tooling-config", "possible-management-doc"} and item not in authoritative]

    lines = [
        "# GaoGao Office Migration Report",
        "",
        f"Project: `{root.name}`",
        "Project root: current `--project-root`; absolute path omitted to avoid leaking local paths.",
        "Status: discovery-only; no archive, move, overwrite, or deletion is approved by this report.",
        "",
        "## Summary",
        "",
        f"- Files listed in project map: {len(inventory)}",
        f"- Migration candidates found: {len(candidates)}",
        f"- Migratable candidates: {len(migratable)}",
        f"- Sensitive files skipped without reading: {len(sensitive)}",
        f"- Linked paths skipped without reading: {len(linked)}",
            "- Absorb durable facts into `Agent Office/` before archiving or moving old knowledge files.",
        "",
        "## Project Map",
        "",
        "This is a filename-level map. `metadata-only`, `structured-metadata-only`, `sensitive-skip`, `linked-skip`, and `large-text-skip` entries were not content-read.",
        "",
    ]
    lines.extend(render_inventory_table(inventory))
    for heading, rows in [
        ("Candidates", render_candidate_table(candidates)),
        ("Likely Authoritative Files", render_candidate_table(authoritative)),
        ("Stale Or Conflicting Files", render_candidate_table(conflicts)),
        ("Active Tasks Found", render_candidate_table(active_tasks)),
        ("Decisions Found", render_candidate_table(decisions)),
    ]:
        lines.extend(["", f"## {heading}", ""])
        lines.extend(rows)
    lines.extend(
        [
            "",
            "## Absorption Map",
            "",
            "Use this as the migration checklist before archive or move actions.",
            "",
        ]
    )
    lines.extend(render_absorption_table(candidates))
    lines.extend(
        [
            "",
            "## Proposed AGENTS Replacement",
            "",
            "Draft path: `Agent Office/Proposals/AGENTS.proposed.md`",
            "",
            "Keep root `AGENTS.md` unchanged until the current approved reply option explicitly authorizes formal takeover or AGENTS application.",
            "",
            "## Recommended Roles",
            "",
            "These are role-design hints, not an approved roster. Choose final roles dynamically after the user confirms current deliverables, write scopes, and handoff targets.",
            "",
            "- Project Director: the current chat should take this job by default.",
            "- Human job titles: use names like Designer, Engineer, Release Checker, Researcher, or Editor.",
            "- Responsibility domains: put pipeline/process wording inside employee profiles, not in the job title.",
            "",
            "## Proposed Archive List",
            "",
            "Archive only after durable facts have been absorbed and the user approves this exact list. This is historical memory, not ordinary working context.",
            "",
        ]
    )
    lines.extend(render_archive_table(candidates, archive_stamp))
    lines.extend(
        [
            "",
            "## Proposed Move List",
            "",
            "Move originals only after absorption, archive approval, and explicit move approval. Default to copy-only archiving.",
            "",
            "No files are proposed for moving yet.",
            "",
            "## Proposed Delete List",
            "",
            "Deletion is not the default.",
            "",
            "No files are proposed for deletion yet.",
            "",
            "## User Questions",
            "",
            "- Which candidate files are authoritative project truth?",
            "- Should `Agent Office/Proposals/AGENTS.proposed.md` replace root `AGENTS.md`?",
            "- Should absorbed old knowledge originals be moved into `Old Project Memory` after archive verification?",
            "- Which employees should be invited after formal takeover is complete?",
            "",
            "## User Approval Record",
            "",
            "Approved archive list: NO",
            "Approved AGENTS replacement: NO",
            "Approved legacy move list: NO",
            "Approved deletion list: NO",
            "Approved by: <pending>",
            "Approval date: <pending>",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect a project for GaoGao Office migration candidates.")
    parser.add_argument("--project-root", default=".", help="Project root to inspect")
    parser.add_argument("--output", default="", help="Optional report path inside project root")
    parser.add_argument("--force-output", action="store_true", help="Overwrite --output if it already exists")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of Markdown")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    if is_unsafe_root(root):
        raise SystemExit(f"Refusing to inspect unsafe project root: {root}")
    if not root.exists():
        raise SystemExit(f"Project root does not exist: {root}")
    inventory = iter_inventory(root)
    candidates = inspect_candidates(root, inventory)

    if args.json:
        payload = {
            "project_name": root.name,
            "project_root": "<omitted>",
            "inventory": [asdict(item) for item in inventory],
            "candidates": [asdict(item) for item in candidates],
        }
        report = json.dumps(payload, indent=2, ensure_ascii=False)
    else:
        report = render_markdown(root, inventory, candidates)

    if args.output:
        output = resolve_inside_root(root, args.output)
        if not is_relative_to(output, root):
            raise SystemExit("--output must be inside --project-root")
        if (output.exists() or output.is_symlink()) and is_link(output):
            raise SystemExit("Refusing to write output through symlink or junction target")
        if has_link_in_path(root, output.parent if output.parent.exists() else output):
            raise SystemExit("Refusing to write output through symlink or junction")
        if output.exists() and not args.force_output:
            raise SystemExit(f"Output already exists. Use --force-output to overwrite: {output}")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(report, encoding="utf-8", newline="\n")
        print(f"wrote: {output}")
    else:
        print(report, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
