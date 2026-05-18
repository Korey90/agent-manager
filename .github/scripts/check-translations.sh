#!/bin/bash
# .github/scripts/check-translations.sh

echo "🌍 WebsiteExpert - Multi-language Check"

php artisan lang:missing --sync --force

echo "✅ Translation sync completed."
echo "📁 Check directories: lang/pl, lang/en, lang/pt"

# Optional: find potential hardcoded strings
echo "🔍 Scanning for potential missing translations..."
grep -r --include="*.php" --include="*.tsx" --include="*.vue" -E '"[^"]*[ąęćłńóśźżĄĘĆŁŃÓŚŹŻ][^"]*"' app/ resources/js/ --color | head -15