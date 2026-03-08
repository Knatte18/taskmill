---
description: "Write a plan from the current discussion"
argument-hint: "<task name>"
---

Write an implementation plan from the current discussion.

## Steps

1. Take task name from argument or infer from conversation.
2. Create `.llm/plans/YYYY-MM-DD-HHMMSS-<slug>.md` (using current UTC date and time) with:
   - **YAML frontmatter:** `started:` (copied from the task's `started:` sub-bullet in `doc/backlog.md`) and `finished:` (current UTC timestamp, matches filename timestamp)
   - **Context:** summary of discussion and key decisions
   - **Files:** flat list of file paths the plan expects to modify (used for staleness detection and fast implementation start)
   - **Steps:** concrete, actionable `- [ ]` items (see step-writing rules below)
3. Run `python ${CLAUDE_PLUGIN_ROOT}/scripts/task_plan.py doc/backlog.md "<task-name>" <plan-path>` to change state to `[p]` and add/replace the `plan:` sub-bullet.

## Step-writing rules

- **One step per file** (or a small cluster of tightly coupled files). Never bundle unrelated file operations into a single step.
- **Explicit names.** Each step must include the target file path and the specific functions, classes, or fields being added or changed.
- **No slash commands or skill references.** Steps must describe concrete actions, never `/taskmill.*` commands or `@taskmill:` skill references — the executor treats these as requiring user invocation or skill loading, stalling execution.
- **Test steps required for source code tasks.** When `## Files` contains source code files, the plan must include steps for writing new tests or updating existing tests that cover the changes. Omit test steps only when the task is purely doc or config changes.

## Rules
- Do not edit any files other than `.llm/plans/`. No code edits, no build changes. All backlog mutations go through scripts.
- Use @taskmill:formats skill for plan and backlog format rules.
