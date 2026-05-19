---
mode: 'agent'
description: 'Create or modify database migrations with multi-tenancy and Spatie Translatable support.'
---
# Database Migration & Schema

## Rules
- Always add `business_id` when the table belongs to a tenant
- Use `Spatie\Translatable` columns correctly (JSON columns for translatable fields)
- Add indexes on frequently queried columns (`business_id`, foreign keys, status fields)
- Make migrations reversible — always implement `down()` method
- After migration — update affected models and run `php artisan migrate:fresh --seed` in dev if needed

## Steps
1. Run delta-analysis on the affected table/module first
2. Create migration file with proper naming (`create_`, `add_`, `modify_`)
3. Add `business_id` foreign key if tenant-scoped
4. Add translatable columns as JSON
5. Add indexes
6. Update model (fillable, casts, HasTranslations trait if needed)
7. Update factories and seeders
8. Run `php artisan migrate` and verify
