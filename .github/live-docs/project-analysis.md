# Project Analysis & Current State

**Last Updated:** 2026-05-17  
**Status:** Living Document

## Project Overview
B2B SaaS platform for web agency management with Client Portal + Filament Admin.

## Critical Areas (Current Status)

| Module                  | Status      | Notes / Technical Debt                  | Last Reviewed |
|-------------------------|-------------|-----------------------------------------|---------------|
| Lead Capture            | ✅ OK       | `LeadCaptureService` (dead code) usunięty; `PublicLeadCaptureService` aktywny, pokryty 20+ testami HTTP | 2026-05-17    |
| Multi-Tenancy           | ✅ Unified  | BelongsToTenant na wszystkich kluczowych modelach; 13 isolation testów; GlobalTemplateVisibilityTest (9 testów) | 2026-05-17    |
| Pipeline & Stages       | ✅ Stable    | Missing tenant scope in some places     | 2026-05-10    |
| Client Portal           | ✅ Refactored | `ClientPortalAccess` model + migracja produkcyjna; ToggleColumn w Filament | 2026-05-17 |
| Stripe Integration      | ✅ Good      | —                                       | —             |
| Translations            | ✅ Complete  | 54 brakujące klucze uzupełnione w EN/PL/PT; nowy plik `sales_offers.php` | 2026-05-17 |

## Architecture Decisions
- Light multi-tenancy via `business_id`
- Action pattern for business logic
- Event-driven architecture
- Spatie Translatable on key models

**Important:** Always read this file before starting new features.