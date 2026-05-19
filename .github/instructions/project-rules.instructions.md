---
applyTo: "**"
---
# Project Rules for WebsiteExpert Agents

**Project Stack:**
- Backend: Laravel 13 (PHP 8.3), Filament 5.4, Sanctum, Spatie Permission, Spatie Translatable, Reverb, Stripe, Twilio
- Frontend: React 18 + Inertia.js 2 + TypeScript + Tailwind CSS 4 + Headless UI
- Architecture: Monorepo, Thin Controllers, Action/Service pattern, Event-Driven, Light Multi-Tenancy (business_id)

**Hard Rules (never violate):**
1. Always start from existing code (anchor).
2. Controllers must remain thin — business logic belongs in Actions or Services.
3. Use Form Requests for complex validation and Policies/Gates for authorization.
4. Full TypeScript — no `any` type.
5. Reuse existing UI components. Do not create new primitives if equivalent exists.
6. After every change (model, controller, component, text) — check and update translations (pl, en, pt).
7. Use Inertia `useForm` for mutations.
8. Delta-first approach — never rewrite working modules from scratch.
9. Respect existing multi-tenancy pattern (`business_id`).

**Language Policy:**
- Code & technical names: English
- User-facing text & documentation: Polish (with en + pt translations)

**Multi-Language Requirement:**
Every new or modified feature that affects user interface or data models must include translation verification using the `multi-language-check` skill.
