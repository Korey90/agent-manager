---
mode: 'agent'
description: 'Create or modify Filament 5 admin resources with proper forms, tables, policies and multi-tenancy.'
---
# Filament 5 Resource Implementation

## Rules
- Use latest Filament 5 conventions
- Implement proper Forms and Tables
- Use Spatie Translatable where needed (TranslatableTabs)
- Respect Policies and `business_id` scope — always scope queries
- Add appropriate filters, actions, bulk actions
- All labels and messages must be in Polish

## Steps
1. Run delta-analysis first
2. Create/modify Resource class in `app/Filament/Resources/`
3. Implement `form()` with all fields
4. Implement `table()` with columns, filters, actions
5. Add Policy and register it
6. Ensure multi-tenancy: scope `getEloquentQuery()` with `business_id`
7. Add translatable tabs if model uses Spatie Translatable
8. Run multi-language-check
