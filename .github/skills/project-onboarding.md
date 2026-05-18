# Skill: Project Onboarding & Deep Analysis

**Description:** Initial deep project familiarization skill. Should be executed when WebsiteExpert starts working with the project for the first time or after significant changes in architecture.

**When to use:** 
- First interaction with the project
- After major refactoring
- When user says "poznaj projekt", "zapoznaj się z projektem", "onboarding" etc.

**Instructions for WebsiteExpert:**

You are starting a new session. Perform a complete, structured project analysis using the following steps:

### Step 1: Core Project Understanding
- Read `copilot-instructions.md`, `.github/instructions/project-rules.md`
- Read `.github/live-docs/project-analysis.md`
- Analyze `composer.json` and `package.json` to confirm current stack versions
- Check key configuration files (`config/`, `.env.example`)

### Step 2: Architecture & Context Analysis
- Understand the 3 contexts: Public Site, Client Portal, Admin Panel (Filament)
- Map existing multi-tenancy implementation (`business_id`)
- Identify main business domains (Leads, Projects, Invoices, Quotes, etc.)
- Check current state of critical modules (especially Lead Capture)

### Step 3: Code Structure Analysis
- Explore folder structure (`app/Actions/`, `app/Models/`, `resources/js/Pages/`, etc.)
- Identify existing Action classes and Services
- Check how translations are handled (Spatie Translatable + lang/ files)
- Review existing Filament Resources

### Step 4: Technical Debt & Risks
- Read all files in `.github/live-docs/`
- Identify known problems (especially from `project-analysis.md`)
- Note inconsistencies in multi-tenancy
- Check test coverage level

### Step 5: Final Summary
Prepare a detailed onboarding report in Polish with sections:

1. **Zrozumienie projektu** – czym jest produkt
2. **Aktualny stan techniczny** (co działa dobrze, co wymaga uwagi)
3. **Kluczowe ryzyka i dług techniczny**
4. **Najważniejsze konwencje i twarde reguły**
5. **Gotowość do pracy** – na ile mogę zaczynać nowe zadania

After completing the analysis, ask the user for confirmation and any additional context.