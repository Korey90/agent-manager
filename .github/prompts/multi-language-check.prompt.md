---
mode: 'agent'
description: 'Verify translation completeness after UI/model changes. Mandatory after every change affecting user-facing text.'
---
# Multi-Language Check

Run this after **every** change that affects:
- User interface (labels, messages, placeholders, tooltips)
- Validation error messages
- Email templates
- Model translatable fields
- Notification content

## Steps
1. Find all new or modified strings in the changed files
2. Check `lang/pl/` — Polish translations (primary)
3. Check `lang/en/` — English translations
4. Check `lang/pt/` — Portuguese translations
5. Add any missing translation keys to all three language files
6. Verify translation keys are used consistently (no hardcoded Polish/English strings)
7. Report: list of keys added, any remaining gaps

## Output format
```
✅ Translations verified
Added keys:
- messages.lead_created (pl ✓ en ✓ pt ✓)
- validation.business_id_required (pl ✓ en ✓ pt ✓)
```
