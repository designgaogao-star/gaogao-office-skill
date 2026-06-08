#!/usr/bin/env python3
"""Scaffold an Agent Office OS project office.

The script only writes inside the selected project root. It never deletes files
and skips existing files unless --force is provided.
"""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import date
from pathlib import Path


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


def render_agents() -> str:
    return """# AGENTS.md

## Agent Office Protocol

This repository uses `docs/agent-office/` as the project office.

Before project work:
- Read `docs/agent-office/status.md`.
- If assigned a role, read only the matching file in `docs/agent-office/roles/`.
- If assigned a task, read the task packet in `docs/agent-office/tasks/active/`.
- Do not bulk-read the whole office unless explicitly asked to audit it.

Coordination:
- Treat `docs/agent-office/thread-registry.md` as the directory of long-running agent employees.
- For message and handoff format, read `docs/agent-office/communication.md`.
- Write cross-role messages as separate files under `docs/agent-office/messages/open/`.
- Write task handoffs under `docs/agent-office/handoffs/`.
- Update `status.md` only when you are PM, Archivist, or explicitly assigned to do so.

Parallel work:
- Do not let two writers modify the same files in parallel.
- Worktree changes are isolated proposals until integrated by the owner or PM.
- End every task with what changed, what was verified, what remains, and who should pick it up next.
"""


def render_status(
    project_name: str,
    project_goal: str,
    profile: str,
    project_type: str,
    risk_level: str,
    first_milestone: str,
) -> str:
    today = date.today().isoformat()
    return f"""# Project Status

Project: {project_name}
Last updated: {today}
Office profile: {profile}
Project type: {project_type}
Risk level: {risk_level}

## Current Goal

{project_goal}

## Active Tasks

| Task | Owner | Status | Reviewer | Notes |
|---|---|---|---|---|
| T-000 | PM | proposed | Reviewer | {first_milestone} |

## Current Risks

- Risk level: {risk_level}
- No specific risks recorded yet.

## Decisions

- No durable decisions recorded yet.

## Next Step

Plan the first milestone and assign a DRI.
"""


def render_project_brief(
    project_name: str,
    project_goal: str,
    profile: str,
    project_type: str,
    risk_level: str,
    first_milestone: str,
    roles: list[str],
) -> str:
    today = date.today().isoformat()
    role_names = ", ".join(ROLE_DEFINITIONS[role]["title"] for role in roles)
    return f"""# Project Brief

Project: {project_name}
Generated: {today}

## Interview Decisions

- Project type: {project_type}
- Office profile: {profile}
- Risk level: {risk_level}
- Standing roles: {role_names}

## Goal

{project_goal}

## First Milestone

{first_milestone}

## Operating Notes

- Keep always-loaded context short.
- Put project-specific detail in task packets, ADRs, and handoffs.
- Update this brief only when the project shape changes.
"""


def render_thread_registry(project_name: str, roles: list[str]) -> str:
    today = date.today().isoformat()
    rows = []
    for role in roles:
        title = ROLE_DEFINITIONS.get(role, {"title": role.title()})["title"]
        mode = "worktree" if role == "builder" else "local"
        authority = {
            "pm": "status, task assignment",
            "architect": "architecture decisions",
            "builder": "implementation",
            "reviewer": "review",
            "archivist": "office hygiene",
            "qa": "acceptance",
            "security": "security review",
            "ux": "user experience",
            "data": "data and analytics",
            "release": "release readiness",
        }.get(role, "role-specific work")
        status = "active" if role == "pm" else "waiting"
        write_scope = ROLE_WRITE_SCOPES.get(role, "task scope only")
        assignment = ROLE_ASSIGNMENTS.get(role, "TBD")
        rows.append(f"| {title} | {project_name} / {title} | TBD | {mode} | {authority} | {assignment} | {write_scope} | {status} |")
    return "# Thread Registry\n\nLast updated: {today}\n\n| Role | Thread Title | Thread ID | Mode | Authority | Current Assignment | Write Scope | Status |\n|---|---|---|---|---|---|---|---|\n{rows}\n".format(
        today=today,
        rows="\n".join(rows),
    )


def render_thread_launch_prompts(project_name: str, roles: list[str]) -> str:
    today = date.today().isoformat()
    sections = [
        "# Thread Launch Prompts",
        "",
        f"Project: {project_name}",
        f"Generated: {today}",
        "",
        "Create one long-running agent thread for each approved role below. After each thread is created, record its thread ID in `docs/agent-office/thread-registry.md`.",
        "",
    ]
    for role in roles:
        definition = ROLE_DEFINITIONS[role]
        title = definition["title"]
        assignment = ROLE_ASSIGNMENTS.get(role, "TBD")
        write_scope = ROLE_WRITE_SCOPES.get(role, "task scope only")
        sections.extend(
            [
                f"## {title}",
                "",
                f"Suggested title: `{project_name} / {title}`",
                "",
                "```text",
                f"You are the {title} agent employee for this project.",
                "",
                "Read:",
                "1. AGENTS.md",
                "2. docs/agent-office/status.md",
                "3. docs/agent-office/context-packs/project-brief.md",
                f"4. docs/agent-office/roles/{role}.md",
                "5. docs/agent-office/communication.md",
                "6. the assigned task packet, if one exists",
                "",
                "Rules:",
                "- Load only task-relevant context.",
                f"- Current assignment: {assignment}",
                f"- Write scope: {write_scope}",
                "- Write cross-role messages as separate files under docs/agent-office/messages/open/.",
                "- End significant work with a handoff under docs/agent-office/handoffs/.",
                "- Do not silently modify unrelated project-management files.",
                "```",
                "",
            ]
        )
    return "\n".join(sections)


def render_role(role: str) -> str:
    definition = ROLE_DEFINITIONS[role]
    title = definition["title"]
    return f"""# {title}

## Mission

{definition["mission"]}

## Authority

{definition["authority"]}

## Default Inputs

- `AGENTS.md`
- `docs/agent-office/status.md`
- `docs/agent-office/communication.md`
- assigned task packet

## Default Outputs

- task updates
- messages
- handoffs
- decisions, when authorized

## Boundaries

- Do not exceed assigned write scope.
- Ask PM before changing ownership or acceptance criteria.
- End significant work with a handoff.
"""


def render_task(first_milestone: str) -> str:
    today = date.today().isoformat()
    return f"""---
id: T-000
status: proposed
dri: PM
reviewer: Reviewer
created: {today}
---

# T-000: Define First Milestone

## Goal

Plan the first implementation milestone and assign a DRI.

Milestone: {first_milestone}

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

- PM review.

## Handoff

Write a handoff if another role picks up implementation.
"""


def render_operating_model() -> str:
    return """# Agent Office Operating Model

## Context Budget

- Keep `AGENTS.md` short and index-like.
- Keep `status.md` focused on current facts.
- Put task-specific details into task packets.
- Archive stale detail instead of extending always-loaded files.

## Parallel Work

- Read-heavy work can run in parallel.
- Write-heavy work needs one DRI, one reviewer, and one write scope.
- Worktree changes are isolated proposals until integrated by PM or the owner.

## Completion Gate

Before a task is done, verify acceptance criteria, write scope, checks, risks, handoff, and decision records.
"""


def render_communication() -> str:
    return """# Communication Protocol

Use this file when agent employee threads need to ask, answer, escalate, close, or hand off work.

## Message Rules

- Create one file per cross-role request in `messages/open/`.
- Use a clear recipient, task id, requested response, and urgency.
- The receiving role may answer in the same file or create a response message.
- Move resolved or superseded messages to `messages/closed/` after the outcome is recorded.
- PM or Archivist closes old messages when the owner is unclear.

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
- Scope conflict between two writer roles should go to PM before either thread edits files.
"""


def render_readme(project_name: str) -> str:
    return f"""# Agent Office

This is the project office for `{project_name}`.

Start with:

1. `status.md`
2. `context-packs/project-brief.md` for project shape and interview decisions
3. `communication.md` for messages and handoffs
4. the relevant role card in `roles/`
5. the assigned task packet in `tasks/active/`

Do not bulk-read the entire office unless auditing or migrating it.
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
    actions: list[dict],
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


def planned_scaffold_files(root: Path, roles: list[str]) -> list[Path]:
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
    files.extend(office / "roles" / f"{role}.md" for role in roles)
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
            office / "cadences",
            office / "archive" / "legacy-management",
        ]
    )
    return files


def parse_roles(raw: str, profile: str) -> list[str]:
    if raw:
        roles = [part.strip().lower() for part in raw.split(",") if part.strip()]
    elif profile == "minimal":
        roles = ["pm", "builder", "reviewer"]
    elif profile == "expanded":
        roles = ["pm", "architect", "builder", "reviewer", "archivist", "qa", "security"]
    else:
        roles = ["pm", "architect", "builder", "reviewer", "archivist"]
    unknown = [role for role in roles if role not in ROLE_DEFINITIONS]
    if unknown:
        raise SystemExit(f"Unknown role(s): {', '.join(unknown)}")
    duplicates = sorted({role for role in roles if roles.count(role) > 1})
    if duplicates:
        raise SystemExit(f"Duplicate role(s): {', '.join(duplicates)}")
    return roles


def main() -> int:
    parser = argparse.ArgumentParser(description="Scaffold an Agent Office OS project office.")
    parser.add_argument("--project-root", default=".", help="Project root to scaffold")
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
    parser.add_argument("--profile", choices=["minimal", "standard", "expanded"], default="standard")
    parser.add_argument("--roles", default="", help="Comma-separated role keys, e.g. pm,builder,reviewer")
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
    project_name = args.project_name or root.name or "Project"
    roles = parse_roles(args.roles, args.profile)
    office = root / "docs" / "agent-office"
    actions: list[dict] = []

    for target in planned_scaffold_files(root, roles):
        assert_safe_target(root, target)

    if args.force and not args.confirm_overwrite and not args.dry_run:
        existing = [path for path in planned_scaffold_files(root, roles) if path.exists()]
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

    safe_write(root / "AGENTS.md", render_agents(), **write_kwargs)
    safe_write(office / "README.md", render_readme(project_name), **write_kwargs)
    safe_write(
        office / "status.md",
        render_status(
            project_name,
            args.project_goal,
            args.profile,
            args.project_type,
            args.risk_level,
            args.first_milestone,
        ),
        **write_kwargs,
    )
    safe_write(office / "thread-registry.md", render_thread_registry(project_name, roles), **write_kwargs)
    safe_write(office / "communication.md", render_communication(), **write_kwargs)
    safe_write(
        office / "context-packs" / "project-brief.md",
        render_project_brief(
            project_name,
            args.project_goal,
            args.profile,
            args.project_type,
            args.risk_level,
            args.first_milestone,
            roles,
        ),
        **write_kwargs,
    )
    safe_write(office / "context-packs" / "thread-launch-prompts.md", render_thread_launch_prompts(project_name, roles), **write_kwargs)
    safe_write(office / "operating-model.md", render_operating_model(), **write_kwargs)
    safe_write(office / "tasks" / "active" / "T-000-define-first-milestone.md", render_task(args.first_milestone), **write_kwargs)

    for role in roles:
        safe_write(office / "roles" / f"{role}.md", render_role(role), **write_kwargs)

    for directory in [
        office / "tasks" / "done",
        office / "tasks" / "archived",
        office / "messages" / "open",
        office / "messages" / "closed",
        office / "handoffs",
        office / "decisions",
        office / "context-packs",
        office / "cadences",
        office / "archive" / "legacy-management",
    ]:
        safe_write(directory / ".gitkeep", "", **write_kwargs)

    result = {
        "project_root": str(root),
        "project_name": project_name,
        "project_type": args.project_type,
        "risk_level": args.risk_level,
        "first_milestone": args.first_milestone,
        "profile": args.profile,
        "roles": roles,
        "dry_run": args.dry_run,
        "actions": actions,
    }
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for item in actions:
            print(f"{item['action']}: {item['path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
