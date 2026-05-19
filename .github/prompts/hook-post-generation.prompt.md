---
mode: 'ask'
description: 'Post-generation review — verify code quality after any large code generation or refactor.'
---
# Post Generation Review

Run this after any major code generation or significant changes.

## Checks
- [ ] Generated code follows project architecture (thin controllers, Actions, DTOs)
- [ ] No `any` types introduced in TypeScript
- [ ] No hardcoded strings without translation keys
- [ ] Multi-tenancy (`business_id`) correctly applied
- [ ] No obvious security issues (no raw queries, no unvalidated input)
- [ ] Code is consistent with existing patterns in the codebase
