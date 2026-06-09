# Role Catalog

Use this only when employee boundaries need help. Do not treat it as a required roster.

## Core Principle

Create people-shaped jobs, not process-shaped modules.

Good display titles:

- Project Manager
- Designer
- Frontend Engineer
- Release Checker
- Researcher
- Writer
- Editor
- Architect
- Security Reviewer

Avoid display titles like:

- Visual Asset Pipeline
- Frontend Runtime
- QA And Publishing
- Migration Archive
- Context Maintenance

Put those process names in the responsibility domain inside the employee profile.

## Current Chat

The current GaoGao Office chat is the founding project manager by default. Do not ask the user to create another project-manager window. In Codex Desktop, rename this current chat to the project-manager job title only, such as `项目经理`, `项目总管`, or `Project Manager`, before inviting other employees. If the current chat later becomes too long, it may write a successor prompt for a new project-manager chat.

The project manager is the user-facing controller in multi-employee mode. The user can keep talking to that one chat. For each request, the manager first judges the final outcome and next responsible role, dispatches clear employee-owned work, handles only project-manager or tiny office-maintenance work directly, and records handoffs for later continuation.

## Split Test

Create a separate employee only when at least two are true:

- the work has a distinct professional judgment standard
- the write scope is different
- the employee needs long-running private memory
- context would become noisy if mixed with another employee
- the project manager benefits from delegating to that employee, or the user explicitly wants direct employee access

Merge or defer jobs that fail this test.

## Dynamic Examples

Use these as examples, not templates:

| Situation | Possible employee | Responsibility domain |
|---|---|---|
| visual portfolio with assets | Designer | visual assets, art direction, image boundaries |
| web app implementation | Frontend Engineer | UI code, components, runtime behavior |
| launch or website publishing | Release Checker | QA, broken links, release readiness |
| research-heavy project | Researcher | sources, claims, evidence notes |
| writing-heavy project | Editor | narrative, copy, structure |

## Employee Profile Requirements

Every employee needs:

- human job title
- responsibility domain
- role value
- judgment standard
- inputs and outputs
- write scope
- forbidden areas
- handoff target
- memory update rule

## Onboarding

After formal takeover, first title the current project-manager chat, then invite employees. In Codex Desktop, create threads automatically when authorized and set titles to the job title only. If manual prompts are needed, start with `Conversation role: Job Title` or `本对话角色：职位名`.

After onboarding, do not push the user into every employee window. Treat employee chats as managed workrooms unless the user asks to enter one directly.
