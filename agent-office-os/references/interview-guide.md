# Interview Guide

Use this guide to ask only questions that change the office design. Prefer answering discoverable facts by inspecting the repo first.

## New Project Questions

Ask these when the project is new or empty:

1. What is the project name and one-sentence goal?
2. What kind of project is it: app, library, website, research, content, infrastructure, data, or mixed?
3. How large do you expect it to become: solo/small, multi-module, production-critical, or enterprise?
4. Which roles should be standing threads now: PM, Builder, Reviewer, Architect, Archivist, QA, Security, UX, Data, Release?
5. Should the office be minimal, standard, or expanded?
6. Does the project use Git and should implementation agents use worktrees?
7. What should count as done for the first milestone?
8. Do you want GitHub publishing materials or only local project management docs?

Recommended default: standard office with PM, Architect, Builder, Reviewer, and Archivist. Use the minimal profile with PM, Builder, and Reviewer for small solo projects.

## Existing Project Questions

Ask after inspecting the project:

1. Which existing docs are authoritative and which are stale?
2. Should old management files be archived inside the new office before deletion?
3. Which old framework names should be preserved for compatibility?
4. Are there current active tasks or branches that must not be disturbed?
5. Are any docs sensitive and unsuitable for migration summaries?
6. Who should be the first long-running agent roles after migration?

Recommended default: copy old framework files under `docs/agent-office/archive/legacy-management/` and delete originals only after explicit confirmation.

## Maintenance Questions

Ask only if not obvious:

1. Should the audit be read-only or should the agent clean up stale office docs?
2. What age makes a message stale: 7, 14, or 30 days?
3. Should retired threads remain in the registry or move to archive?
4. Should completed tasks be summarized into status before archiving?

Recommended default: read-only report first, then small cleanup after user approval.

## Role Recommendation Heuristic

- Solo prototype: PM, Builder, Reviewer in one or two threads.
- Production app: PM, Architect, Builder, Reviewer, Archivist.
- Security-sensitive project: add Security as optional or standing.
- UI-heavy project: add UX/QA as optional.
- Data-heavy project: add Data role.
- Old or messy project: add Archivist from day one.
