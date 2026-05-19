---
mode: 'agent'
description: 'Generate final task completion report, archive to completed-tasks, clean live-docs.'
---
# Task Completion Report

Run this when a feature or task is fully done.

## Steps
1. Summarize what was implemented (files changed, patterns used, decisions made)
2. List any known limitations or follow-up tasks
3. Verify all tests pass (`php artisan test && npm run test`)
4. Run multi-language-check one final time
5. Create archive file in `.github/completed-tasks/YYYY-MM-DD-task-name.md`
6. Clean `.github/live-docs/current-task.md` — reset for next task
7. Update `.github/live-docs/status-dashboard.md` if it exists

## Report template
```markdown
# Task: {Task Name}
**Date:** {date}
**Agent:** {agent name}

## What was done
- ...

## Files changed
- ...

## Tests
- PHPUnit: X passed
- Vitest: X passed

## Follow-up tasks
- ...
```
