# Project roadmap

This provisional roadmap draws on the project’s NotebookLM notes and architecture sketches and turns them into small, reviewable milestones. Notebook summaries and generated setup instructions are leads for research, not proof that a command, feature, benchmark, or hardware claim works.

## Stage 1 — Make the project accurate

- Publish the assistant architecture and permission boundaries.
- Keep proposed work separate from implemented features and measured results.
- Confirm the actual test machine and available memory before naming it in a public hardware profile.
- Document one supported local model runtime and one model only after the setup is reproduced.

**Exit evidence:** a reviewed architecture, a verified machine inventory, and an installation note reproduced by a second person.

## Stage 2 — Build a bounded local prototype

- Connect one local model endpoint to a minimal task interface.
- Add read-only access to one explicit workspace.
- Require the user to approve proposed file changes before applying them.
- Verify each result using a diff or a direct check and record a small, private run journal.

**Exit evidence:** reproducible records for successful, failed, and interrupted example tasks, with no unrestricted shell execution.

## Stage 3 — Add inspectable continuity

- Store the project backlog and a small set of user-approved facts in plain files.
- Rehydrate only the current project's relevant state at session start.
- Let the user review, edit, export, and remove stored facts.
- Resume from task status without automatically executing pending items.

**Exit evidence:** a restart-and-resume demonstration that shows which state was loaded and does not repeat completed work.

## Stage 4 — Evaluate quality and resource use

- Compare repeated runs across documented models and settings.
- Report task success, unsupported claims, permission decisions, latency, and memory use separately.
- Use self-authored or properly licensed prompts in Norwegian, English, and Somali.
- Ask fluent reviewers to assess language quality and disclose the limits of the review.

**Exit evidence:** a public report with complete run metadata, failed runs, limitations, and no claims beyond the tested conditions.

## Stage 5 — Consider optional extensions

Only after the bounded prototype is reliable, assess retrieval indexes, voice input/output, more runtimes, or carefully scoped scheduled reminders. Any extension needs its own privacy, permission, resource, and failure review.

Unattended execution of model-generated backlog items, system-wide access, silent self-modification, and automated account or financial actions are not planned features.
