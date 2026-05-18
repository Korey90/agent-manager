# Skill: Task Completion Report

**Description:** Generates a professional final markdown report after completing a task/feature and archives it. Also cleans live documents for the next task.

**Trigger:** Use this skill after successful completion of any user task (after user confirmation or when all implementation + validation steps are done).

**Output Folder:** `.github/completed-tasks/`

**File Naming Convention:** 
`YYYY-MM-DD - Krótki tytuł zadania.md`

**Instructions for the Agent:**

1. **Read current live documents** (mandatory):
   - `.github/live-docs/current-task.md`
   - `.github/live-docs/current-sprint.md`
   - `.github/live-docs/status-dashboard.md`
   - `.github/live-docs/project-analysis.md` (if relevant)

2. **Generate a complete report** in Polish using the exact structure below:

```markdown
# YYYY-MM-DD - Tytuł Zadania

**Status:** Zakończone sukcesem
**Data realizacji:** 2026-05-17
**Czas trwania:** X godzin / dni

## Cel zadania
(Opis celu z current-task.md)

## Zakres wykonanych prac
- [Lista wszystkich wykonanych elementów]

## Użyte agenty i skille
- @BackendEngineer
- @FrontendEngineer
- Skill: laravel-action
- Skill: multi-language-check
- itd.

## Zmodyfikowane / utworzone pliki
- `app/Actions/...`
- `resources/js/Pages/...`
- `database/migrations/...`

## Walidacja końcowa
- ✅ PHP Coding Standard (Laravel Pint)
- ✅ JavaScript / TypeScript Lint + Prettier
- ✅ Multi-language check (pl, en, pt)
- ✅ Multi-tenancy compliance
- ✅ PHPUnit + Vitest tests
- ✅ Full validation script

## Uwagi i rekomendacje
(Wszystkie ważne obserwacje, sugestie na przyszłość, potencjalne ryzyka)

## Next steps (opcjonalnie)
- Co można zrobić w kolejnym kroku

**Raport wygenerowany automatycznie przez WebsiteExpert**