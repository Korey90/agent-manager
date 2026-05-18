# Hook: Pre-Commit

**Description:** Git pre-commit hook — protects code quality.

**Checks:**
- PHP Pint formatting
- ESLint + Prettier
- Translation check (no missing keys)
- No hardcoded strings in Polish/English without translation keys
- Basic security scan (no obvious secrets)

**If any check fails → block commit** with clear message.