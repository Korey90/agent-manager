---
mode: 'ask'
description: 'Pre-commit quality checklist — formatting, lint, translations, security. Run before every commit.'
---
# Pre-Commit Checklist

Run this before committing code. Verify all points below.

## Checks
- [ ] PHP Pint formatting — `./vendor/bin/pint --test`
- [ ] ESLint + Prettier — `npm run lint`
- [ ] Translation check — no missing keys in pl/en/pt
- [ ] No hardcoded Polish/English strings without translation keys
- [ ] Basic security scan — no obvious secrets in changed files
- [ ] All tests pass — `php artisan test`

> **Note:** To automate this as an actual Git pre-commit hook, add a script to `.git/hooks/pre-commit` or use Husky.
