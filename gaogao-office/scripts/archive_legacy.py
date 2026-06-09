#!/usr/bin/env python3
"""Copy or explicitly move approved old-knowledge files into GaoGao Office archive."""

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
LEGACY_ARCHIVE_DIR = "Old Project Memory"

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
class ArchiveAction:
    source: str
    destination: str
    action: str
    source_material: str = ""


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


def table_source_lines(section: str) -> dict[str, str]:
    lines: dict[str, str] = {}
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
            lines[matches[0]] = stripped
    return lines


def report_line_explanation(line: str) -> str:
    without_code = re.sub(r"(`+)(.*?)\1", " ", line)
    cleaned = re.sub(r"[\|\-\*\s]+", " ", without_code).strip(" :;,.")
    return re.sub(r"\s+", " ", cleaned)


def absorption_line_is_complete(line: str) -> bool:
    explanation = report_line_explanation(line).lower()
    if not explanation:
        return False
    if "needs absorption" in explanation or "proposed" in explanation or "pending" in explanation:
        return False
    return any(
        token in explanation
        for token in [
            "absorbed",
            "absorb",
            "migrated",
            "migration",
            "summarized",
            "summarised",
            "copied into",
            "merged into",
            "吸收",
            "归纳",
            "迁移",
            "写入",
            "并入",
        ]
    )


def validate_absorption_ready(report_text: str, sources: list[str]) -> None:
    absorption_section = markdown_section(report_text, "Absorption Map")
    absorption_by_source = table_source_lines(absorption_section)
    incomplete: list[str] = []
    missing: list[str] = []
    for source in sources:
        line = absorption_by_source.get(source)
        if line is None:
            missing.append(source)
        elif not absorption_line_is_complete(line):
            incomplete.append(source)
    if missing:
        raise SystemExit(
            "Archive sources are missing from `## Absorption Map`: "
            + ", ".join(missing[:8])
            + (" ..." if len(missing) > 8 else "")
        )
    if incomplete:
        raise SystemExit(
            "Archive sources are not marked absorbed in `## Absorption Map`: "
            + ", ".join(incomplete[:8])
            + (" ..." if len(incomplete) > 8 else "")
            + ". Update each Status cell after writing the durable facts into Agent Office."
        )


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


def assert_safe_source_tree(root: Path, source: Path, raw_source: str) -> None:
    if not is_safe_report_path(raw_source):
        raise SystemExit(f"Unsafe archive source path: {raw_source}")
    if not source.exists():
        raise SystemExit(f"Archive source does not exist: {raw_source}")
    if has_link_in_path(root, source):
        raise SystemExit(f"Refusing to archive linked path: {raw_source}")
    if not is_relative_to(source.resolve(strict=False), root.resolve()):
        raise SystemExit(f"Archive source escapes project root: {raw_source}")
    if source.is_file():
        return
    if not source.is_dir():
        raise SystemExit(f"Archive source is not a regular file or directory: {raw_source}")
    for child in source.rglob("*"):
        child_rel = child.relative_to(root)
        child_raw = str(child_rel).replace("\\", "/")
        if has_link_in_path(root, child):
            raise SystemExit(f"Refusing to archive linked path inside directory: {child_raw}")
        if is_sensitive_path(child_raw):
            raise SystemExit(f"Refusing to archive sensitive-looking path inside directory: {child_raw}")


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
    if (path.exists() or path.is_symlink()) and is_link(path):
        raise SystemExit(f"Refusing destination through symlink or junction target: {path}")
    if has_link_in_path(root, path.parent if path.parent.exists() else path):
        raise SystemExit(f"Refusing destination through symlink or junction: {path}")


def load_archive_sources(report: Path, *, move_originals: bool) -> list[str]:
    text = report.read_text(encoding="utf-8", errors="replace")
    approval_section = markdown_section(text, "User Approval Record")
    if approval_value(approval_section, "Approved archive list") != "YES":
        raise SystemExit("Archive list is not approved. Set `Approved archive list: YES` in `User Approval Record` first.")
    archive_section = markdown_section(text, "Proposed Archive List")
    archive_sources = table_source_paths(archive_section)
    if not archive_sources:
        raise SystemExit("No archive sources found in `## Proposed Archive List`.")
    if move_originals:
        if approval_value(approval_section, "Approved legacy move list") != "YES":
            raise SystemExit("Move list is not approved. Set `Approved legacy move list: YES` in `User Approval Record` first.")
        move_section = markdown_section(text, "Proposed Move List")
        move_sources = table_source_paths(move_section)
        if not move_sources:
            raise SystemExit("No move sources found in `## Proposed Move List`.")
        missing = [source for source in move_sources if source not in archive_sources]
        if missing:
            raise SystemExit(
                "Move sources must also appear in `## Proposed Archive List`: "
                + ", ".join(missing[:8])
                + (" ..." if len(missing) > 8 else "")
            )
        sources = move_sources
    else:
        sources = archive_sources
    validate_absorption_ready(text, sources)
    return sources


def newest_agents_backup(root: Path) -> Path | None:
    backups = [
        path
        for path in root.glob("AGENTS.md.gaogao-office-*.bak")
        if path.is_file() and not has_link_in_path(root, path)
    ]
    if not backups:
        return None
    return sorted(backups, key=lambda path: (path.stat().st_mtime, path.name))[-1]


def archive_material_for_source(root: Path, raw_source: str, source: Path, *, move_originals: bool) -> tuple[Path, str | None]:
    normalized = raw_source.replace("\\", "/")
    if normalized != "AGENTS.md":
        return source, None
    backup = newest_agents_backup(root)
    if backup is not None:
        return backup, "copy-from-backup"
    if move_originals:
        raise SystemExit("Refusing to move root `AGENTS.md` directly. Apply the new AGENTS.md first so the old one is backed up, then archive from that backup.")
    return source, None


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
        assert_safe_source_tree(root, source, raw_source)
        source_material, forced_action = archive_material_for_source(root, raw_source, source, move_originals=move_originals)
        if source_material != source:
            material_rel = str(source_material.relative_to(root)).replace("\\", "/")
            assert_safe_source_tree(root, source_material, material_rel)
        else:
            material_rel = ""
        destination = archive_root / raw_source.replace("\\", "/")
        assert_safe_target(root, destination)
        try:
            destination.resolve(strict=False).relative_to(archive_base.resolve(strict=False))
        except ValueError:
            raise SystemExit(f"Archive destination is outside legacy archive: {destination}")
        if destination.exists():
            if has_link_in_path(root, destination):
                raise SystemExit(f"Archive destination is linked: {destination}")
            if source.is_dir():
                raise SystemExit(f"Archive destination already exists for directory source: {destination}")
            if move_originals and not forced_action:
                raise SystemExit(f"Move destination already exists. Refusing to move over archived file: {destination}")
            if destination.read_bytes() == source_material.read_bytes():
                action = "skip-existing"
            else:
                raise SystemExit(f"Archive destination already exists with different content: {destination}")
        else:
            action = forced_action or ("move" if move_originals else "copy")
        actions.append(ArchiveAction(raw_source, str(destination.relative_to(root)).replace("\\", "/"), action, material_rel))
    return actions


def render_index(actions: list[ArchiveAction], archive_stamp: str) -> str:
    lines = [
        "# Old Project Memory Archive Index",
        "",
        f"Archive stamp: {archive_stamp}",
        "Read boundary: old project memory after absorption; ordinary employees should not read this archive.",
        "",
        "| Source | Archive Copy | Action | Source Material |",
        "|---|---|---|---|",
    ]
    for action in actions:
        material = action.source_material or action.source
        lines.append(f"| `{action.source}` | `{action.destination}` | {action.action} | `{material}` |")
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
        source = root / (action.source_material or action.source)
        destination = root / action.destination
        assert_safe_target(root, destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if action.action == "move":
            shutil.move(str(root / action.source), str(destination))
        elif source.is_dir():
            shutil.copytree(source, destination)
        else:
            shutil.copy2(source, destination)
    index.parent.mkdir(parents=True, exist_ok=True)
    index.write_text(render_index(actions, archive_stamp), encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Copy or explicitly move approved old-knowledge files into the GaoGao Office archive.")
    parser.add_argument("--project-root", default=".", help="Project root containing Agent Office/migration-report.md")
    parser.add_argument("--report", default="", help="Optional migration report path inside the project root")
    parser.add_argument("--archive-stamp", default=date.today().isoformat(), help="Archive subfolder name")
    parser.add_argument("--move-originals", action="store_true", help="Move approved originals into the archive; requires explicit move approval")
    parser.add_argument("--dry-run", action="store_true", help="Plan actions without copying or moving files")
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    if is_unsafe_root(root):
        raise SystemExit(f"Refusing to archive from unsafe project root: {root}")
    if not root.exists():
        raise SystemExit(f"Project root does not exist: {root}")
    validate_archive_stamp(args.archive_stamp)
    report = resolve_inside_root(root, args.report) if args.report else root / OFFICE_DIR / "migration-report.md"
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
