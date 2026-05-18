# Skill: Database Migration & Schema

**Description:** Create or modify migrations with proper multi-tenancy and translatable support.

**Rules:**
- Always add `business_id` when appropriate
- Use `Spatie\Translatable` columns correctly
- Add indexes on frequently queried columns
- Make migrations reversible
- After migration → update models and run `php artisan migrate:fresh --seed` in dev if needed