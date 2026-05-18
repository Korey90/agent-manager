#!/bin/bash
# .github/scripts/run-full-validation.sh

echo "🚀 WebsiteExpert - Full Validation"

echo "1. PHP Lint..."
php artisan pint --test

echo "2. JS Lint..."
npm run lint

echo "3. Translations..."
./.github/scripts/check-translations.sh

echo "4. Tests..."
php artisan test --parallel --stop-on-failure

echo "5. Multi-tenancy check..."
php .github/scripts/validate-multi-tenancy.php

echo "✅ Full validation completed."