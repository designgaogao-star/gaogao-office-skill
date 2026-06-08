# First-Use Playbook

Use this playbook when Agent Office OS is invoked in a project that does not already have an active `docs/agent-office/` workflow.

## Contents

- [Opening Move](#opening-move)
- [Suitability Check](#suitability-check)
- [Read-Only Project Guess](#read-only-project-guess)
- [Lightweight Interview](#lightweight-interview)
- [Dynamic Role Design](#dynamic-role-design)
- [Feedback Adaptation](#feedback-adaptation)
- [Approval Gate](#approval-gate)
- [Role Prompt Output](#role-prompt-output)
- [Optional Codex Threads](#optional-codex-threads)
- [Language Rules](#language-rules)

## Opening Move

Start in chat. Do not scaffold yet.

Say, in the user's language:

1. Agent Office OS will help design a durable project office for long-running agent work.
2. It is best for a real project folder that will be used over time; a short one-off task is cheaper as a normal chat.
3. The next step is a read-only look at the project folder.
4. It will ask a few short numbered questions if needed.
5. It will show an office configuration plan before creating files.
6. It will write files only after explicit approval. Existing files are skipped by default; existing `AGENTS.md` gets a proposed replacement first; confirmed overwrites create backups; migration archives copy files before any separate move or deletion approval. If the user is unhappy with a change, they can ask for a restore plan based on those backups or archive copies.
7. Each approved role gets its own small role memory file so a replacement chat window can continue the same role without rereading old chats.

Do not require Plan Mode. If the user asks for a highly formal planning pass, say Plan Mode is optional.

## Suitability Check

Before a full interview, decide from the user's request and lightweight folder clues whether Agent Office OS fits the job.

Likely overkill:

- a quick standalone question
- an isolated file edit
- unrelated tasks that do not share one project memory
- no durable project folder
- a user who wants the cheapest possible short chat

If it looks like overkill, say in one or two sentences that ordinary chat is likely cheaper and Agent Office OS is only worth it if the user wants a durable project office. Do not scaffold unless the user chooses the durable office path.

If the work appears long-running, folder-anchored, migration-heavy, or likely to involve multiple role windows over time, continue to the read-only project guess.

## Read-Only Project Guess

Inspect only lightweight clues:

- current directory name
- README or top-level docs index
- package/config files such as `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `.openai/hosting.json`
- existing `docs/`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.cursorrules`
- Git status and whether the repo is clean
- obvious app folders such as `src/`, `app/`, `pages/`, `content/`, `data/`, `infra/`

Then either:

- confirm the guess using the actual evidence: "I think this is a {project kind} for {likely goal}. Is that right?"
- or ask: "I could not infer enough from the folder. What does this project do, and what is its main deliverable?"

Do not write `migration-report.md` or run `inspect_office.py --output` during first-use consultation. Keep findings in chat until the user explicitly approves file creation.

## Lightweight Interview

Ask at most 3-5 numbered questions per round. Let users answer with numbered lines.

Useful questions:

1. What is this project trying to produce?
2. Who is the primary user or audience?
3. What should the first milestone accomplish?
4. What kinds of work will happen soon: design, writing, coding, data, review, migration, release, research?
5. What files or areas should be protected from casual edits?

Stop after enough information to make a reasonable first office plan. Do not interview forever.

## Dynamic Role Design

The office document structure is stable. The role roster is dynamic.

Create roles by reasoning from the actual project, not from a fixed project-type table. Use these constraints:

- Use few, necessary roles.
- Do not split roles just to sound professional.
- Split a role only when responsibilities, inputs, outputs, write scope, or review authority are clearly different.
- Do not let multiple writer roles own the same file scope by default.
- Defer roles that are plausible later but not needed for the first milestone.
- Every active role must have a current assignment, default reading material, write boundary, and handoff target.
- Every active role gets one private-by-protocol memory file under `docs/agent-office/role-memory/`.
- Prefer one coordinating role when more than one role can write office docs.
- Prefer one implementation owner per active task.

Before proposing the roster, run a role compression check:

- Could one role handle this first milestone without confusion?
- Do any proposed roles share the same write scope or output?
- Is a role useful now, or merely plausible later?
- Would the user understand why each separate window exists?

Merge or defer roles that fail this check.

The plan should include:

- project understanding
- approved roles
- why each role exists now
- why likely-but-not-now roles are deferred
- each role's write scope
- each role's memory file and read/write boundary
- first task and reviewer
- whether worktree mode is useful

## Feedback Adaptation

If the user says the roster is too large, too fixed, too generic, or uses the wrong names, revise the office plan before scaffolding.

Use the user's correction as project evidence. Prefer renaming, merging, or deferring roles over defending the first plan. After revising, show the new role list, changed write scopes, and any tradeoff, then ask for approval again.

## Approval Gate

Before writing files, show the proposed plan and ask for a clear approval phrase.

Do not create `AGENTS.md`, `docs/agent-office/`, role cards, task packets, or reports until the user says something equivalent to:

- `确认创建`
- `按这个方案创建`
- `create this office`
- `apply this plan`

If the user edits the plan, update the plan first, then ask for approval again.

## Role Prompt Output

After initialization, output prompts in the current chat as well as writing `docs/agent-office/context-packs/thread-launch-prompts.md`.

Keep human instructions outside fenced code blocks:

````md
**新建一个窗口：角色名称**
建议标题：`项目名 / 角色名称`

```text
这里才是要发送到新窗口的第一条消息。
```
````

The fenced `text` block must contain only the message to send to the new role thread. It must not contain labels such as "new window", "suggested title", "copy this", or "paste below".

Each role prompt should tell the role to read its own `docs/agent-office/role-memory/{role-slug}.md`, avoid other role memory files by default, and update its own memory after significant work.

Each role prompt should also tell ordinary worker roles not to read `docs/agent-office/archive/legacy-management/` unless the user explicitly assigns migration, audit, or recovery work.

## Optional Codex Threads

Manual prompt copy is the default.

Only create real Codex conversations when all are true:

- the user explicitly asks to automatically create Codex conversations
- thread management tools are available in the current environment
- the role plan has already been approved

After creating threads, write the returned thread IDs into `docs/agent-office/thread-registry.md`. If thread tools are unavailable, explain the fallback and provide manual prompts.

## Language Rules

Follow the user's language for chat, generated docs, and role prompts.

For Chinese users, generate Chinese `AGENTS.md`, `status.md`, `communication.md`, `project-brief.md`, role cards, role memory, task packets, and launch prompts.

Keep these machine-facing values stable:

- paths
- frontmatter keys
- role slug
- `status: proposed`
- task ids such as `T-000`
- directory names such as `messages/open`
