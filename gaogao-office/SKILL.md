---
name: gaogao-office
description: 搭建、迁移或维护 GaoGao Office，用一个项目总管窗口接管长期 AI Agent 项目，并按需调度员工对话。适用于 Agent Office、多窗口员工角色、角色记忆、项目清理、旧 planning/vibe 框架 migrate/migration、AGENTS.md 审批和长期项目管理；不适合一次性 AGENTS.md 编辑、普通任务清单或没有项目文件夹的短聊天。
---

# GaoGao Office

Create and maintain a lightweight project office for AI agents. The skill is named GaoGao Office; the project folder it creates is always `Agent Office/`.

## Fit

Use this for long-running work anchored in a real project folder. It costs more upfront than a plain one-off chat, but should reduce repeated reorientation after context compaction, handoffs, or multi-window role work.

Do not use it for lightweight standalone questions, isolated file edits, or unrelated multi-task chats that do not share one durable project folder.

## Workflow Decision

Choose exactly one workflow before writing files:

1. **Initialize a new project**: user is starting a project or wants a fresh agent office.
2. **Migrate an existing project**: user has old planning docs, `vibe/` context, old agent rules, scattered memory, or wants cleanup.
3. **Maintain an existing office**: user already has `Agent Office/` and wants audit, role tuning, archival, or context reduction.
4. **Upgrade or re-take over an existing office**: user updated the skill, reruns it in a project that already has `Agent Office/`, or wants the new workflow to absorb and replace an older office setup.
5. **Retire or downsize a team**: user asks to remove employees, withdraw a team, cancel a direction, or return to a single project-manager chat.

If the request is ambiguous, inspect the project first, then ask only the questions that materially change the office design.

If `Agent Office/` already exists, do not run first-use initialization as if the project were empty. Treat the project as maintain/upgrade unless BOSS explicitly asks to discard the old office after review.

## Required First Pass

Before changing files:

- Introduce GaoGao Office briefly: it will inspect the project, propose an office organization, and wait for approval before takeover.
- Use practical office language in chat: project checkup, BOSS approval, office signboard, manager on duty, employees onboarded, old records room. Keep it clear and lightly human; do not turn command progress into cute fiction.
- In Chinese chat, address the user as `BOSS`. Do not use older boss-style Chinese titles or mixed Chinese-English owner titles in user-facing text. Machine fields such as table column `Owner` may keep their stable names.
- Make user-visible replies easy to scan. For onboarding proposals, migration reports, maintenance reports, retirement summaries, or employee launch prompts, read `references/markdown-output-guide.md`.
- Use Markdown structure deliberately: exact reply words and employee prompts go in fenced `text` blocks; safety promises and destructive-action warnings go in blockquotes or warning callouts; role lists and migration maps may use tables; completion and health checks may use task lists.
- Use only 2-4 helpful formats in one ordinary reply. Do not decorate every paragraph, and do not use table/card-style choice layouts for A/B/C/D reply options.
- On first invocation or takeover restart, show one compact Mermaid roadmap so BOSS understands the sequence before approval. Do not use Mermaid in routine progress updates.
- Before any final answer to BOSS, run a public-output preflight: remove internal notes, tentative link syntax, tool implementation details, temporary config names, and analysis-like wording. If a file link format is uncertain, show a plain absolute path instead of exposing the uncertainty.
- State that the current chat will become the founding project manager unless the user only wants a proposal.
- In multi-employee mode, make the current project manager the BOSS-facing controller by default: BOSS talks to this chat, this chat decomposes requests, dispatches work to employee threads, gathers results, updates office files, and reports back. Do not make BOSS manage several employee windows unless BOSS explicitly wants direct access.
- In Codex Desktop, after formal takeover, rename the current chat to the founding project-manager job title only, such as `项目经理`, `项目总管`, or `Project Manager`. Do this before creating other employee threads when the thread title tool is available; if it is unavailable or the current thread cannot be confidently identified, tell the user the exact manual title to use.
- Inspect project clues read-only: directory name, full filename map excluding skip directories, README, config files, existing `AGENTS.md`, `vibe/`, top-level docs, and Git status when available.
- Before dispatching multiple employee threads, run or emulate `scripts/inspect_capacity.py`. Employees may all be onboarded, but active task dispatch must follow `dispatch_policy`; unknown or low-capacity machines dispatch one employee at a time.
- Do not bulk-read every file. Full-scan filenames; read only relevant text candidates such as README, agent rules, planning, tasks, context/vibe, copy docs, ADRs, and status notes.
- Do not content-read images, media, binary files, sensitive-looking files, dependencies, build output, caches, virtualenvs, `.git`, or linked external paths.
- If this is migration, run or emulate `scripts/inspect_office.py` and present migration findings before changing legacy files.

## First-Use Consultation Gate

For first-time setup requests, read `references/first-use-playbook.md` before scaffolding. Default to lightweight chat, not Plan Mode.

On initial invocation:

- Explain fit and safety briefly: best for long-running project folders; first pass is read-only; root `AGENTS.md` gets a proposal first; confirmed overwrites create backups; old knowledge is absorbed before archive/move/delete.
- If the project purpose is inferable, confirm it. If not, ask what the project does and what the main deliverable is.
- If the project purpose is not inferable, ask one lightweight question first: "BOSS, what is this project mainly trying to do? Say it casually in one sentence; I will use that to judge how to form your team." Ask one follow-up only if that answer is still not enough to design the office.
- Present an office configuration plan before writing files: project understanding, recommended organization mode, human job titles, why each employee exists, deferred employees, public/private boundaries, write scopes, initial waiting state, and whether old materials should be absorbed or archived.
- If recommending multiple employees, explain that the default operating style is controller-dispatch: BOSS can keep talking only to the current project-manager chat while it routes work to employees in the background.
- Give plain A/B/C/D reply options for takeover only. A formally takes over with the recommended team. B lets the current project-manager chat handle the office without other employee chats. C lets BOSS specify employee count or job titles. D cancels without writing. The letters apply only to the next user reply.
- Do not ask for or draft a project direction plan in the takeover choice. After the office is created and employees are onboarded, ask whether BOSS wants a direction-advisor conversation. If yes, first ask whether BOSS already has a direction; follow BOSS's idea when they have one, and only propose directions yourself when they do not.

## New Project Flow

1. Read `references/first-use-playbook.md` and run the consultation gate.
2. If project details are unclear, read `references/interview-guide.md`.
3. Draft a dynamic office plan. Read `references/role-catalog.md` only if role boundaries need help.
4. After approval, save the approved plan as JSON and run `scripts/scaffold_office.py --config <plan>`.
5. Create the approved office:
   - `Agent Office/README.md`
   - `Agent Office/status.md`
   - `Agent Office/project-brief.md`
   - `Agent Office/project-map.md`
   - `Agent Office/task-board.md`
   - `Agent Office/communication.md`
   - `Agent Office/decisions.md`
   - `Agent Office/thread-registry.md`
   - `Agent Office/office-plan.json`
   - `Agent Office/Proposals/AGENTS.proposed.md`
   - `Agent Office/Employees/{role-slug}/README.md`
   - `Agent Office/Employees/{role-slug}/memory.md`
   - `Agent Office/Employees/{role-slug}/current-task.md`
   - `Agent Office/Archive/Old Project Memory/`
6. Do not write root `AGENTS.md` unless the user chooses formal takeover. For formal takeover, apply the proposal with a dated backup, archive absorbed old knowledge, then record the current chat as project manager.
7. Rename or clearly label the current chat as the project manager before onboarding other employees.
8. Inspect local capacity with `scripts/inspect_capacity.py` when available, record the resulting `dispatch_policy`, and default to serial dispatch if capacity is unknown.
9. Invite employees only after formal takeover is complete. Do not output role prompts before `Agent Office/`, root `AGENTS.md`, and old-knowledge disposition are in a clear state.
10. When employees are available, operate through controller-dispatch by default:
   - understand BOSS's request in the current project-manager chat
   - split only the necessary parts into employee tasks
   - respect `dispatch_policy.max_parallel_employee_tasks`; do not dispatch all employees in parallel unless BOSS explicitly approves it
   - update `Agent Office/task-board.md`, `Agent Office/communication.md`, and each assigned employee's `current-task.md`
   - send the employee prompt or task through Codex thread tools when available
   - read employee replies, verify/summarize results, update office memory, then report one clear answer to BOSS
11. In Codex Desktop, prefer automatic employee thread creation after explicit approval. If thread tools are unavailable, output fallback launch prompts from `Agent Office/thread-registry.md`.
12. Run `scripts/validate_office.py` or equivalent checks.

## Migration Flow

1. Read `references/migration-playbook.md` and `references/templates.md`.
2. Inspect old knowledge surfaces:
   - `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.cursorrules`
   - `vibe/`, context docs, roadmap, tasks, architecture, ADRs, status notes, meeting notes, copy docs, workflow docs, changelogs, checklists
   - existing `.codex/`, `.agents/`, `.github/`, issue templates, and automation notes
3. Produce `Agent Office/migration-report.md` or a proposed report before changing legacy files.
4. Build an absorption map: for each old management file, say which durable facts move into `status.md`, `project-brief.md`, `project-map.md`, `task-board.md`, `decisions.md`, `communication.md`, employee files, or archive notes.
5. Scaffold `Agent Office/` if missing, preserving root `AGENTS.md` by default.
6. Write `Agent Office/Proposals/AGENTS.proposed.md` for review. Apply it only when the current reply option authorizes formal takeover or the user gives a separate explicit AGENTS approval.
7. Move or copy approved absorbed old-knowledge files under `Agent Office/Archive/Old Project Memory/`. The migration report must mark each archived source as absorbed in `## Absorption Map`; do not leave absorbed old management files in active project roots when the user chose formal takeover.
8. Delete legacy files only after separate explicit confirmation and a reviewed deletion list.

Do not silently copy, move, delete, or overwrite old project management files.

## Existing Office Upgrade Flow

Use this when `Agent Office/` already exists and BOSS wants to use the latest skill behavior, repair an older office, or "run the skill again" in the same project.

1. Read `references/maintenance-playbook.md`, then inspect existing `Agent Office/`, root `AGENTS.md`, and active project clues read-only.
2. Run `scripts/validate_office.py --warn-only` to find missing files, stale layout, missing controller-dispatch, old archive names, missing employee memories, or oversized public files.
3. Preserve continuity: read public office files and employee memory only as needed to summarize current truth. Do not delete employee memory.
4. Produce an upgrade proposal before writing:
   - what existing office version or missing fields were detected
   - what facts will be kept
   - which active files will be refreshed
   - which old office files, stale employees, old prompts, or old project-memory sources will be archived
   - whether root `AGENTS.md` needs a new proposal and backup
5. Show A/B/C/D reply options:
   - A: upgrade the office to the current GaoGao Office workflow, preserve memories, archive stale material, and apply approved `AGENTS.md`
   - B: only audit and report; write nothing
   - C: rebuild the employee roster, but preserve old memories in archive
   - D: pause
6. After approval, update the active office with current templates and `office-plan.json`, preserving or summarizing useful old content. Use `scripts/scaffold_office.py --config <plan> --force --confirm-overwrite` only after BOSS authorizes the upgrade.
7. Archive absorbed or retired material under `Agent Office/Archive/Old Project Memory/` or an office snapshot folder. Do not leave stale old prompts or old management frameworks as active project entrances.
8. Re-run validation and report what changed.

Never silently delete the old `Agent Office/`, old employee memories, root `AGENTS.md`, or old project-memory folders. Upgrade means "absorb, back up, and refresh active entrances", not blind removal.

## Office Model

Public area:

- Files directly inside `Agent Office/` are shared context all roles may read.
- Keep public files short. If a public file grows too large, summarize and move detail into archive or a focused note.

Private area:

- Each role has one private-by-protocol folder under `Agent Office/Employees/{role-slug}/`.
- A role reads and updates only its own employee folder by default.
- Other roles may read an employee folder only when the user explicitly asks for maintenance, audit, recovery, or handoff review.

Archive:

- `Agent Office/Archive/Old Project Memory/` is historical material after old knowledge is absorbed.
- Ordinary employees must not read the old-memory archive.

Employee model:

- Display job titles must sound like human jobs, such as Project Manager, Designer, Engineer, Release Checker, Researcher, or Editor.
- Do not use process names such as visual asset pipeline, frontend runtime, or QA and release as employee titles; put those in responsibility domains.
- The current chat is the project manager by default. Do not ask the user to create a second project-manager window.
- The project manager is the default BOSS-facing controller. In multi-employee offices, ordinary employees primarily receive tasks from the project manager and return results to it; direct BOSS-to-employee work is optional, not the default.
- Each employee maintains `README.md`, `memory.md`, and `current-task.md`; meaningful work must update memory and the next action.
- When retiring employees, preserve completed work as completed. Cancel only proposed, waiting, or active future tasks. Mark employee roles as archived/withdrawn, update their memory/current-task with a retirement note, and record that archived employees must not receive new dispatches unless BOSS approves reactivation.

## Optional Codex Thread Creation

In Codex Desktop, automatic employee thread creation is the preferred path after the user approves employee onboarding and thread tools are available. First rename the current conversation to the project-manager job title only. Then create one conversation per employee except the current project manager, set each employee thread title to the job title only, and record returned thread IDs in `Agent Office/thread-registry.md`.

After employee threads exist, the project manager may dispatch work with thread tools when BOSS approves or when the office rules already authorize that employee to handle the task. Use the smallest useful task message, include required files and write scope, and ask the employee to update its own `memory.md` and `current-task.md` before replying. Dispatch according to `dispatch_policy`; if capacity is low or unknown, send the next employee task only after the previous employee is idle or done. After reading the employee reply, the project manager synthesizes and reports to BOSS; it should not dump raw multi-thread chatter unless BOSS asks.

If thread tools are unavailable, fall back to manual copy prompts and task messages from `Agent Office/thread-registry.md`, and explicitly tell the user the current project-manager window title to set manually. The Markdown office must remain usable by other agents.

## Safety Rules

- Treat context as a budget. Full-scan filenames; do not full-read the whole project.
- Keep `AGENTS.md` short and index-like.
- Do not apply root `AGENTS.md`, archive old knowledge, create employee threads, or start employee work unless the current reply option explicitly authorized that action.
- In first-use setup, formal takeover and project work are separate stages. After creating the office, applying `AGENTS.md`, and onboarding employees, stop and report the ready state, then ask whether BOSS wants a direction-advisor conversation. Do not draft a plan, dispatch work, search the web, or create task-result files until BOSS approves that separate direction flow.
- Do not let multiple writer roles own the same file scope.
- If a role is asked to work outside scope, route the request to the right role or record it in `Agent Office/communication.md`.
- Do not edit `.git`, secrets, home directory files, external configuration, or linked external paths while scaffolding.
- Refuse project-office paths that resolve outside the project root through symlinks or junctions.
- Follow the user's language by default. Keep machine identifiers such as paths, role slugs, `status: proposed`, and `T-000` stable.

## Resources

- `references/office-blueprint.md`: operating model and context-budget rules.
- `references/first-use-playbook.md`: consultation, dynamic role planning, and prompt-output rules.
- `references/markdown-output-guide.md`: user-visible Markdown output standards for readable chat interactions.
- `references/interview-guide.md`: questions for new projects, migrations, and maintenance.
- `references/templates.md`: Markdown templates for the lightweight office.
- `references/migration-playbook.md`: old-knowledge audit, absorption, archive, and move process.
- `references/maintenance-playbook.md`: office health audit and cleanup workflow.
- `references/role-catalog.md`: standing and optional employee role strategies.
- `references/github-publishing.md`: GitHub release and installation guide.
- `scripts/scaffold_office.py`: create a safe lightweight office scaffold.
- `scripts/inspect_capacity.py`: read-only local capacity check for employee dispatch concurrency.
- `scripts/inspect_office.py`: read-only filename map and migration discovery.
- `scripts/archive_legacy.py`: copy approved legacy files; optionally move originals only with explicit move approval.
- `scripts/validate_office.py`: structure and health checks.
