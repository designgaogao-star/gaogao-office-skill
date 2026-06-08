#!/usr/bin/env python3
"""Inspect a project for legacy management surfaces.

Default mode is read-only and writes the report to stdout. If --output is used,
the output path must be inside the selected project root.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict
from datetime import date
from pathlib import Path


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
}

SENSITIVE_DIRS = {
    ".ssh",
    ".aws",
    ".gnupg",
}

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
    ".cursorrules",
    "PLANS.md",
}
EXACT_NAMES_LOWER = {name.lower() for name in EXACT_NAMES}

KEYWORDS = {
    "roadmap",
    "plan",
    "planning",
    "task",
    "todo",
    "status",
    "architecture",
    "decision",
    "adr",
    "context",
    "handoff",
    "milestone",
    "sprint",
    "meeting",
    "requirements",
    "spec",
}

KEYWORD_ORDER = [
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
]

TEXT_EXTS = {".md", ".txt", ".rst", ".adoc", ".toml", ".yaml", ".yml", ".json"}
MAX_BYTES = 2_000_000
OFFICE_PREFIX = ("docs", "agent-office")


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


def classify(path: Path, text: str) -> tuple[str, int, list[str]]:
    name = path.name
    lower_name = name.lower()
    lower_path = str(path).lower()
    lower_text = text.lower()
    score = 0
    reasons: list[str] = []

    if lower_name == "agents.md" and ("agent office protocol" in lower_text or "codex office protocol" in lower_text):
        return "agent-office-entrypoint", 0, ["generated Agent Office entrypoint skipped"]

    if lower_name in EXACT_NAMES_LOWER:
        score += 8
        reasons.append("known agent or planning instruction filename")
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
    elif "adr" in lower_path or "decision" in lower_path:
        kind = "decision-record"
    elif "task" in lower_path or "todo" in lower_path:
        kind = "task-tracking"
    elif "roadmap" in lower_path or "plan" in lower_path or "milestone" in lower_path:
        kind = "planning"
    elif "status" in lower_path or "handoff" in lower_path or "context" in lower_path:
        kind = "project-memory"
    elif ".github" in lower_path or ".codex" in lower_path or ".agents" in lower_path:
        kind = "tooling-config"
    else:
        kind = "possible-management-doc"
    return kind, score, reasons


def iter_files(root: Path):
    for path in root.rglob("*"):
        try:
            rel_parts = path.relative_to(root).parts
        except ValueError:
            continue
        rel_parts_lower = tuple(part.lower() for part in rel_parts)
        if any(part in SKIP_DIRS for part in rel_parts_lower):
            continue
        if len(rel_parts_lower) >= 2 and rel_parts_lower[:2] == OFFICE_PREFIX:
            continue
        linked = has_link_in_path(root, path)
        if not path.is_file():
            continue
        if linked:
            yield path, False, True
            continue
        sensitive = is_sensitive_path(path.relative_to(root))
        if not sensitive and path.suffix.lower() not in TEXT_EXTS and path.name.lower() not in EXACT_NAMES_LOWER:
            continue
        try:
            if path.stat().st_size > MAX_BYTES:
                continue
        except OSError:
            continue
        yield path, sensitive, False


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


def inspect(root: Path) -> list[Candidate]:
    candidates: list[Candidate] = []
    for path, sensitive, linked in iter_files(root):
        rel = path.relative_to(root)
        if linked:
            candidates.append(
                Candidate(
                    str(rel).replace("\\", "/"),
                    "linked-skipped",
                    0,
                    ["linked path skipped without reading contents"],
                )
            )
            continue
        if sensitive:
            candidates.append(
                Candidate(
                    str(rel).replace("\\", "/"),
                    "sensitive-skipped",
                    0,
                    ["sensitive filename skipped without reading contents"],
                )
            )
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        kind, score, reasons = classify(rel, text)
        if score >= 3:
            candidates.append(Candidate(str(rel).replace("\\", "/"), kind, score, reasons))
    candidates.sort(key=lambda item: (-item.score, item.path))
    return candidates


def markdown_code(value: str) -> str:
    longest = max((len(match.group(0)) for match in re.finditer(r"`+", value)), default=0)
    fence = "`" * (longest + 1)
    if "`" in value:
        return f"{fence} {value} {fence}"
    return f"{fence}{value}{fence}"


def markdown_table_cell(value: str) -> str:
    return value.replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ")


def render_candidate_table(candidates: list[Candidate]) -> list[str]:
    if not candidates:
        return ["No items found."]
    lines = [
        "| Path | Kind | Score | Reasons |",
        "|---|---|---:|---|",
    ]
    for item in candidates:
        reasons = markdown_table_cell("; ".join(item.reasons))
        lines.append(
            f"| {markdown_table_cell(markdown_code(item.path))} | {markdown_table_cell(item.kind)} | {item.score} | {reasons} |"
        )
    return lines


def render_path_table(candidates: list[Candidate], archive_stamp: str | None = None) -> list[str]:
    if not candidates:
        return ["No items proposed."]
    if archive_stamp:
        lines = [
            "| Source | Proposed Archive Destination | Reason |",
            "|---|---|---|",
        ]
        for item in candidates:
            destination = f"docs/agent-office/archive/legacy-management/{archive_stamp}/{item.path}"
            lines.append(
                f"| {markdown_table_cell(markdown_code(item.path))} | "
                f"{markdown_table_cell(markdown_code(destination))} | {markdown_table_cell(item.kind)} |"
            )
        return lines
    lines = [
        "| Path | Reason |",
        "|---|---|",
    ]
    for item in candidates:
        lines.append(f"| {markdown_table_cell(markdown_code(item.path))} | {markdown_table_cell(item.kind)} |")
    return lines


def render_markdown(root: Path, candidates: list[Candidate]) -> str:
    sensitive = [item for item in candidates if item.kind == "sensitive-skipped"]
    linked = [item for item in candidates if item.kind == "linked-skipped"]
    migratable = [item for item in candidates if item.kind not in {"sensitive-skipped", "linked-skipped"}]
    authoritative = [
        item
        for item in migratable
        if item.kind in {"agent-instructions", "decision-record"}
        or item.path in {"README.md", "docs/README.md"}
        or item.score >= 10
    ]
    conflicts = [
        item
        for item in migratable
        if item.kind in {"agent-instructions", "tooling-config", "possible-management-doc"}
        and item not in authoritative
    ]
    active_tasks = [item for item in migratable if item.kind == "task-tracking"]
    decisions = [item for item in migratable if item.kind == "decision-record"]
    roles = ["PM", "Architect", "Builder", "Reviewer", "Archivist"]
    if active_tasks:
        roles.append("QA")
    if sensitive:
        roles.append("Security")
    archive_stamp = date.today().isoformat()

    lines = [
        "# Agent Office Migration Report",
        "",
        f"Project: `{root.name}`",
        "Project root: current `--project-root`; absolute path omitted to avoid leaking local paths.",
        "Status: discovery-only; no archive, overwrite, or deletion is approved by this report.",
        "",
        "## Summary",
        "",
        f"- Candidates found: {len(candidates)}",
        f"- Migratable candidates: {len(migratable)}",
        f"- Sensitive files skipped without reading: {len(sensitive)}",
        f"- Linked paths skipped without reading: {len(linked)}",
        "- This report is discovery only. Do not delete legacy files until the user approves an exact list.",
        "",
        "## Candidates",
        "",
    ]
    lines.extend(render_candidate_table(candidates))
    lines.extend(
        [
            "",
            "## Likely Authoritative Files",
            "",
        ]
    )
    lines.extend(render_candidate_table(authoritative))
    lines.extend(
        [
            "",
            "## Stale Or Conflicting Files",
            "",
        ]
    )
    lines.extend(render_candidate_table(conflicts))
    lines.extend(
        [
            "",
            "## Active Tasks Found",
            "",
        ]
    )
    lines.extend(render_candidate_table(active_tasks))
    lines.extend(
        [
            "",
            "## Decisions Found",
            "",
        ]
    )
    lines.extend(render_candidate_table(decisions))
    lines.extend(
        [
            "",
            "## Recommended Roles",
            "",
        ]
    )
    for role in roles:
        lines.append(f"- {role}")
    lines.extend(
        [
            "",
            "## Proposed Archive List",
            "",
            "Archive only after the user approves this exact list.",
            "",
        ]
    )
    lines.extend(render_path_table(migratable, archive_stamp=archive_stamp))
    lines.extend(
        [
            "",
            "## Proposed Delete List",
            "",
            "No files are proposed for deletion by the scanner. Deletion requires a separate exact list and explicit user approval.",
            "",
            "## Sensitive Skipped",
            "",
        ]
    )
    lines.extend(render_candidate_table(sensitive))
    lines.extend(
        [
            "",
            "## Linked Skipped / Manual Review",
            "",
            "These paths point through symlinks or junctions. Review them manually; do not archive or delete them through the automated migration plan.",
            "",
        ]
    )
    lines.extend(render_candidate_table(linked))
    lines.extend(
        [
            "",
            "## User Questions",
            "",
            "- Which listed files are authoritative project truth?",
            "- Should any old agent rules be merged into the new short `AGENTS.md` entrypoint?",
            "- Is the proposed archive list approved exactly as shown?",
            "- Are there files the user wants deleted after archive verification?",
            "- Which roles should become long-running agent employee threads?",
            "",
            "## User Approval Record",
            "",
            "Approved archive list: NO",
            "Approved deletion list: NO",
            "Approved by: <pending>",
            "Approval date: <pending>",
            "",
            "## Recommended Next Steps",
            "",
            "1. Confirm which candidate files are authoritative.",
            "2. Scaffold `docs/agent-office/` if missing.",
            "3. Summarize durable facts into `status.md`, task packets, role cards, and ADRs.",
            "4. Copy approved legacy framework files under `docs/agent-office/archive/legacy-management/`.",
            "5. Delete old files only after explicit user confirmation.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect a project for Agent Office migration candidates.")
    parser.add_argument("--project-root", default=".", help="Project root to inspect")
    parser.add_argument("--output", default="", help="Optional report path inside project root")
    parser.add_argument("--force-output", action="store_true", help="Overwrite --output if it already exists")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of Markdown")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    if not root.exists():
        raise SystemExit(f"Project root does not exist: {root}")
    candidates = inspect(root)

    if args.json:
        payload = {
            "project_name": root.name,
            "project_root": "<omitted>",
            "candidates": [asdict(item) for item in candidates],
        }
        report = json.dumps(payload, indent=2)
    else:
        report = render_markdown(root, candidates)

    if args.output:
        output = Path(args.output).resolve()
        if not is_relative_to(output, root):
            raise SystemExit("--output must be inside --project-root")
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
