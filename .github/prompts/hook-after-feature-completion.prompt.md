---
mode: 'ask'
description: 'Post-feature-completion checklist — translations, tests, multi-tenancy, security review.'
---
# After Feature Completion

Run this checklist after finishing a feature.

## Checks
- [ ] All new texts have translations (pl, en, pt)
- [ ] All tests passing (`php artisan test && npm run test`)
- [ ] Multi-tenancy respected — no data leaks between businesses
- [ ] Code follows project rules (thin controllers, Action pattern, no `any`)
- [ ] Documentation updated if needed
- [ ] Performance & security review done
- [ ] Run `task-completion-report` to archive the work
