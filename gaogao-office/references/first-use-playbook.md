# First-Use Playbook

Use this when GAOGAO Office is invoked in a project without an active `Agent Office/`.

## Opening Move

Start in chat. Do not scaffold yet.

Say, in the user's language:

1. GAOGAO Office will design a lightweight `Agent Office/` for long-running agent work.
2. It first performs a read-only project check.
3. It creates files only after explicit approval.
4. It proposes root `AGENTS.md` first and applies it only after the user says `确认应用 AGENTS.md`.
5. It keeps public shared files in `Agent Office/` and private role memory under `Agent Office/Employees/{role-slug}/`.

Do not require Plan Mode.

## Read-Only Project Guess

Inspect:

- directory name
- full filename map, skipping dependencies, build output, caches, virtualenvs, `.git`, and existing `Agent Office/`
- README and top-level docs
- package/config files
- existing `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.cursorrules`
- `vibe/`, planning, task, context, copy, and ADR files
- Git status when available

Images, media, binary files, sensitive-looking files, and linked external paths are filename/metadata only. Do not content-read them.

If the project purpose is inferable, confirm the guess. If not, ask what the project does and what the main deliverable is.

## Lightweight Interview

Ask at most 3-5 numbered questions per round. Useful questions:

1. What is this project trying to produce?
2. Who is the primary audience or user?
3. What should the first milestone accomplish?
4. What kinds of work will happen soon: design, writing, coding, research, migration, QA, release?
5. What files or areas should be protected from casual edits?

Stop once there is enough information to propose the office.

## Dynamic Role Design

Create roles by reasoning from the project, not from a fixed role table.

- Use few, necessary roles.
- Split roles only when responsibilities, inputs, outputs, write scope, or review authority differ clearly.
- Do not let multiple writer roles own the same file scope by default.
- Defer plausible-later roles.
- Every active role needs a private folder, current assignment, write boundary, and handoff target.

The plan must include project understanding, approved roles, why each exists, why others are deferred, write scopes, first task, and whether worktree mode is useful.

## Approval Gate

Before writing files, show the office plan and ask for a clear approval phrase such as `确认创建` or `按这个方案创建`.

After scaffold, show `Agent Office/Proposals/AGENTS.proposed.md` in chat and say:

- The user may manually copy it over root `AGENTS.md`.
- Codex may apply it only after the user replies exactly `确认应用 AGENTS.md`.

## Role Prompt Output

After initialization, output role prompts in the current chat and store them in `Agent Office/thread-registry.md`.

Keep human instructions outside fenced code blocks:

````md
**新建一个窗口：角色名称**
建议标题：`项目名 / 角色名称`

```text
这里才是要发送到新窗口的第一条消息。
```
````

The fenced `text` block must contain only the message to send to the new role window.

## Language Rules

Follow the user's language for chat, generated docs, and role prompts. Keep paths, role slugs, task ids, and frontmatter-style machine fields stable.
