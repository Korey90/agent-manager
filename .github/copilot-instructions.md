# WebsiteExpert — Project AI Instructions

## Stack
- **Backend:** Laravel 13 (PHP 8.3), Filament 5.4, Sanctum, Spatie Permission, Spatie Translatable, Reverb, Stripe, Twilio
- **Frontend:** React 18 + Inertia.js 2 + TypeScript + Tailwind CSS 4 + Headless UI
- **Architecture:** Monorepo, Thin Controllers, Action/Service pattern, Event-Driven, Light Multi-Tenancy (`business_id`)

## Hard Rules — Never Violate
1. Always start from existing code (delta approach — find the anchor first).
2. Controllers must remain thin — business logic belongs in Actions or Services.
3. Use Form Requests for complex validation and Policies/Gates for authorization.
4. Full TypeScript — no `any` type, ever.
5. Reuse existing UI components. Do not create new primitives if an equivalent exists.
6. After every change (model, controller, component, text) — check and update translations (pl, en, pt).
7. Use Inertia `useForm` for all mutations.
8. Delta-first: never rewrite working modules from scratch.
9. Respect existing multi-tenancy pattern (`business_id`).

## Language Policy
- Code & technical names: **English**
- User-facing text & documentation: **Polish** (with `en` + `pt` translations)

## Multi-Language Requirement
Every change affecting UI or data models must include translation verification (`multi-language-check` skill).

## Available Agent Modes
Switch in the model picker (▾) in Copilot Chat:
- **Backend Engineer** — Laravel Actions, Filament, Events, DI
- **Frontend Engineer** — React 18, Inertia.js 2, TypeScript strict, Tailwind 4
- **Database Engineer** — Migrations, Spatie Translatable, schema, indexes
- **Security Engineer** — Policies, Gates, webhook signing, secrets
- **Testing Engineer** — PHPUnit 12, Vitest, Testing Library
- **Documentation Engineer** — live-docs, translations, status dashboard
- **Automation Engineer** — Reverb, Queues, Git hooks, CI/CD
- **WebsiteExpert** — Main orchestrator (default for most tasks)

## Available Skills — invoke with `/`
| Command | When to use |
|---|---|
| `/delta-analysis` | **Mandatory first step** before any implementation |
| `/database-migration` | Create/modify migrations (multi-tenancy, translatable) |
| `/filament-resource` | Create/modify Filament 5 admin resources |
| `/laravel-action` | Implement business logic via Action pattern |
| `/react-inertia-component` | Create React + Inertia + TypeScript component |
| `/multi-language-check` | Verify translations after every UI/model change |
| `/test-generation` | Write PHPUnit + Vitest tests |
| `/stripe-integration` | Stripe payments, webhooks, subscriptions |
| `/task-completion-report` | Final report + live-docs cleanup after task |
