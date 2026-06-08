#!/usr/bin/env python3
"""Copy or explicitly move approved legacy files into GAOGAO Office archive."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path, PureWindowsPath


OFFICE_DIR = "Agent Office"
ARCHIVE_DIR = "Archive"
LEGACY_ARCHIVE_DIR = "Legacy Management"

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


@dataclass
class ArchiveAction:
    source: str
    destination: str
    action: str


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


def is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


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


def table_source_paths(section: str) -> list[str]:
    paths: list[str] = []
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
            paths.append(matches[0])
    return paths


def is_safe_report_path(raw_path: str) -> bool:
    normalized = raw_path.replace("\\", "/")
    path = Path(normalized)
    windows_path = PureWindowsPath(raw_path)
    if path.is_absolute() or windows_path.is_absolute() or windows_path.drive:
        return False
    return ".." not in path.parts


def is_sensitive_path(raw_path: str) -> bool:
    path = Path(raw_path.replace("\\", "/"))
    lower_parts = {part.lower() for part in path.parts}
    lower_name = path.name.lower()
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


def validate_archive_stamp(archive_stamp: str) -> None:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,79}", archive_stamp):
        raise SystemExit("Unsafe archive stamp. Use one folder name containing only letters, numbers, dots, underscores, or hyphens.")


def assert_safe_target(root: Path, path: Path) -> None:
    resolved_root = root.resolve()
    resolved_target = path.resolve(strict=False)
    try:
        resolved_target.relative_to(resolved_root)
    except ValueError:
        raise SystemExit(f"Refusing destination outside project root: {path}")
    if has_link_in_path(root, path.parent if path.parent.exists() else path):
        raise SystemExit(f"Refusing destination through symlink or junction: {path}")


def load_archive_sources(report: Path, *, move_originals: bool) -> list[str]:
    text = report.read_text(encoding="utf-8", errors="replace")
    approval_section = markdown_section(text, "User Approval Record")
    if approval_value(approval_section, "Approved archive list") != "YES":
        raise SystemExit("Archive list is not approved. Set `Approved archive list: YES` in `User Approval Record` first.")
    if move_originals and approval_value(approval_section, "Approved legacy move list") != "YES":
        raise SystemExit("Move list is not approved. Set `Approved legacy move list: YES` in `User Approval Record` first.")
    archive_section = markdown_section(text, "Proposed Archive List")
    sources = table_source_paths(archive_section)
    if not sources:
        raise SystemExit("No archive sources found in `## Proposed Archive List`.")
    return sources


def plan_archive(root: Path, sources: list[str], archive_stamp: str, *, move_originals: bool) -> list[ArchiveAction]:
    archive_base = root / OFFICE_DIR / ARCHIVE_DIR / LEGACY_ARCHIVE_DIR
    archive_root = archive_base / archive_stamp
    actions: list[ArchiveAction] = []
    seen: set[str] = set()
    for raw_source in sources:
        if raw_source in seen:
            raise SystemExit(f"Duplicate archive source: {raw_source}")
        seen.add(raw_source)
        if not is_safe_report_path(raw_source):
            raise SystemExit(f"Unsafe archive source path: {raw_source}")
        if is_sensitive_path(raw_source):
            raise SystemExit(f"Refusing to archive sensitive-looking path: {raw_source}")
        source = root / raw_source
        if has_link_in_path(root, source):
            raise SystemExit(f"Refusing to archive linked path: {raw_source}")
        if not is_relative_to(source.resolve(strict=False), root.resolve()):
            raise SystemExit(f"Archive source escapes project root: {raw_source}")
        if not source.is_file():
            raise SystemExit(f"Archive source is not a regular file: {raw_source}")
        destination = archive_root / raw_source.replace("\\", "/")
        assert_safe_target(root, destination)
        try:
            destination.resolve(strict=False).relative_to(archive_base.resolve(strict=False))
        except ValueError:
            raise SystemExit(f"Archive destination is outside legacy archive: {destination}")
        if destination.exists():
            if has_link_in_path(root, destination):
                raise SystemExit(f"Archive destination is linked: {destination}")
            if move_originals:
                raise SystemExit(f"Move destination already exists. Refusing to move over archived file: {destination}")
            if destination.read_bytes() == source.read_bytes():
                action = "skip-existing"
            else:
                raise SystemExit(f"Archive destination already exists with different content: {destination}")
        else:
            action = "move" if move_originals else "copy"
        actions.append(ArchiveAction(raw_source, str(destination.relative_to(root)).replace("\\", "/"), action))
    return actions


def render_index(actions: list[ArchiveAction], archive_stamp: str) -> str:
    lines = [
        "# Legacy Management Archive Index",
        "",
        f"Archive stamp: {archive_stamp}",
        "Read boundary: human-review/audit only; ordinary employees should not read this archive.",
        "",
        "| Source | Archive Copy | Action |",
        "|---|---|---|",
    ]
    for action in actions:
        lines.append(f"| `{action.source}` | `{action.destination}` | {action.action} |")
    return "\n".join(lines) + "\n"


def write_archive(root: Path, actions: list[ArchiveAction], archive_stamp: str, dry_run: bool) -> None:
    archive_root = root / OFFICE_DIR / ARCHIVE_DIR / LEGACY_ARCHIVE_DIR / archive_stamp
    index = archive_root / "_archive-index.md"
    assert_safe_target(root, index)
    if dry_run:
        return
    for action in actions:
        if action.action == "skip-existing":
            continue
        source = root / action.source
        destination = root / action.destination
        destination.parent.mkdir(parents=True, exist_ok=True)
        if action.action == "move":
            shutil.move(str(source), str(destination))
        else:
            shutil.copy2(source, destination)
    index.parent.mkdir(parents=True, exist_ok=True)
    index.write_text(render_index(actions, archive_stamp), encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Copy or explicitly move approved legacy files into the GAOGAO Office archive.")
    parser.add_argument("--project-root", default=".", help="Project root containing Agent Office/migration-report.md")
    parser.add_argument("--report", default="", help="Optional migration report path inside the project root")
    parser.add_argument("--archive-stamp", default=date.today().isoformat(), help="Archive subfolder name")
    parser.add_argument("--move-originals", action="store_true", help="Move approved originals into the archive; requires explicit move approval")
    parser.add_argument("--dry-run", action="store_true", help="Plan actions without copying or moving files")
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    if not root.exists():
        raise SystemExit(f"Project root does not exist: {root}")
    validate_archive_stamp(args.archive_stamp)
    report = Path(args.report).resolve() if args.report else root / OFFICE_DIR / "migration-report.md"
    if not is_relative_to(report, root):
        raise SystemExit("--report must be inside --project-root")
    if has_link_in_path(root, report):
        raise SystemExit("Refusing to read migration report through symlink or junction")
    if not report.is_file():
        raise SystemExit(f"Migration report does not exist: {report}")

    sources = load_archive_sources(report, move_originals=args.move_originals)
    actions = plan_archive(root, sources, args.archive_stamp, move_originals=args.move_originals)
    write_archive(root, actions, args.archive_stamp, args.dry_run)
    payload = {
        "project_name": root.name,
        "archive_stamp": args.archive_stamp,
        "move_originals": args.move_originals,
        "dry_run": args.dry_run,
        "actions": [asdict(action) for action in actions],
    }
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        for action in actions:
            print(f"{action.action}: {action.source} -> {action.destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
