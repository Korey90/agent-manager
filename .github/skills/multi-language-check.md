# Skill: Multi-Language Check

**Description:** Mandatory skill executed after every change that affects user interface, models, forms, or text content.

**Triggers:**
- Any modification to controllers, Blade files, React components, models with Translatable, Filament resources, language keys.

**Executable Script:**
```bash
# .github/scripts/check-translations.sh
#!/bin/bash
echo "🌍 Running multi-language verification..."
php artisan lang:missing --sync --force
php artisan lang:publish
echo "✅ Translation check completed. Verify lang/pl, lang/en, lang/pt"