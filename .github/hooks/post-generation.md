# Hook: Post Generation

**Description:** Executed automatically after any code generation or major changes by WebsiteExpert.

**Actions (in order):**
1. Run `./.github/scripts/check-translations.sh`
2. Run PHP linting (`php artisan pint`)
3. Run JS linting + formatting (`npm run lint && npm run format`)
4. Run relevant tests (`php artisan test --filter=NewFeature` or Vitest)
5. Run `./.github/scripts/validate-multi-tenancy.php`
6. Update `.github/live-docs/current-task.md`
7. Generate summary for user (in Polish)

**Agent must confirm** all steps completed successfully before final report.