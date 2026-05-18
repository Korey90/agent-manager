#!/bin/bash
# .github/scripts/analyze-delta.sh

echo "📊 Delta Analysis for: $1"

echo "Related files:"
find app/ -name "*$1*" -type f | head -10
find resources/js/ -name "*$1*" -type f | head -10

echo "Multi-tenancy check in context..."
grep -l "business_id" app/Models/ app/Actions/ | head -8