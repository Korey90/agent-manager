# Current Sprint

**Sprint Name:** Google Calendar — Hardening & UX
**Date:** 2026-05-18 → 2026-05-31
**Goal:** Dopracowanie integracji Google Calendar — smart-import, solidność tokenów OAuth, konfigurowalny zakres importu, paginacja listy kalendarzy, surface błędów do użytkownika

## Backlog

### To Do
- (brak)

### In Progress
- (brak)

### Done
- [x] GC-1 — Smart type detection (holiday/birthday → `reminder`) — 2026-05-18
- [x] GC-2 — Konfigurowalny zakres dat importu (modal z DatePicker) — 2026-05-18
- [x] GC-3 — Paginacja listy kalendarzy (`nextPageToken` loop) — 2026-05-18
- [x] GC-4 — Detekcja braku `refresh_token` + persistent warning z reconnect — 2026-05-18
- [x] GC-5 — Surface błędów kalendarzy do UI (warning notification) — 2026-05-18
- [x] GC-0 — Activity History, Sync All, Import multi-calendar, wire:ignore fix — 2026-05-18
- [x] T1–T5, multi-tenancy, ClientPortalAccess, ToggleColumn — 2026-05-17

### In Progress
- (brak)

### Done
- [x] GC-0 — Activity History (event_scheduled + event_deleted), Sync All, Import multi-calendar, wire:ignore fix — 2026-05-18
- [x] T1–T5, multi-tenancy, ClientPortalAccess, ToggleColumn — 2026-05-17

## Status
**Translation Status:** ✅ Wszystkie klucze uzupełnione (EN/PL/PT)
**Test Coverage:** 265/265 ✅
**Multi-Tenancy Compliance:** 100% ✅

## Backlog

### To Do
- (brak)

### In Progress
- (brak)

### Done
- [x] T1 — Usunięto `app/Services/LandingPage/LeadCaptureService.php` (martwy kod) — 2026-05-17
- [x] T2 — Komentarze ochronne w `BriefingTemplate` + `SalesOfferTemplate` — 2026-05-17
- [x] T3 — `GlobalTemplateVisibilityTest` (9 testów: BriefingTemplate + SalesOfferTemplate) — 2026-05-17
  - Bonus: naprawiono bug `BriefingTemplate::scopeForBusiness()` (type hint `?int` → `string|null`)
- [x] T4 — Pokryte przez istniejący `PublicLeadCaptureTest.php` (20+ testów HTTP) — 2026-05-17
- [x] T5 — 54 brakujące klucze tłumaczeń dodane w EN/PL/PT + nowe pliki `sales_offers.php` — 2026-05-17
- [x] Multi-tenancy unification (BelongsToTenant na 5 modelach + TenantIsolationTest) — 2026-05-17
- [x] ClientPortalAccess refactor (nowy model, migracja, 9 plików produkcyjnych, 11 testów) — 2026-05-17
- [x] ClientResource: ToggleColumn portal_access w tabeli /admin/clients — 2026-05-17
- [x] MySQL migration uruchomiona — 2026-05-17

## Status
**Translation Status:** ✅ Wszystkie klucze uzupełnione (EN/PL/PT)
**Test Coverage:** 260/260 ✅
**Multi-Tenancy Compliance:** 100% ✅