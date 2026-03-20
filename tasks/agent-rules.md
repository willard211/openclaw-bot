# Agent Rules

These repo-local rules capture the user's required working style for this project.

## Planning

- Default to plan mode for any task that is not simple.
- If a task exceeds three steps, includes architecture decisions, or has ambiguity, write a detailed plan first.
- If uncertainty appears during execution, stop, re-evaluate, and update the plan before proceeding.
- Treat verification as planned work, not an afterthought.

## Sub-Agents

- Use sub-agents for research, exploration, and parallel analysis when the task is complex enough to justify them.
- Keep each sub-agent scoped to one clear task.
- Aggregate sub-agent results in the main context before making final decisions.

## Lessons

- Read relevant entries in `tasks/lessons.md` before starting work in this repo.
- When the user corrects process or quality expectations, update `tasks/lessons.md` immediately.
- Turn repeated corrections into permanent local rules.

## Validation

- Do not mark work complete until behavior is verified.
- Run relevant tests when available.
- Check logs or runtime output when that evidence matters.
- Compare behavior against the prior baseline when the change could alter user-visible behavior.
- Ask whether the result meets a senior-engineer approval bar before closing the task.

## Design Standard

- Prefer the smallest correct change.
- Reject temporary patches when a root-cause fix is available.
- Reconsider any non-trivial solution and ask whether a simpler or more elegant approach exists.

## Task Management

- Keep the active checklist in `tasks/todo.md`.
- Mark progress in that file as work advances.
- End each task with a short review note in `tasks/todo.md`.
