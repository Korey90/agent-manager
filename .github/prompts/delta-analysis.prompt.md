---
mode: 'agent'
description: 'Mandatory discovery step before any implementation. Finds anchor files, checks multi-tenancy, translations, events.'
---
# Delta Analysis (Discovery)

This is the **mandatory first step** before any implementation.

## Steps
1. Identify anchor files — find existing similar functionality in the codebase
2. Analyze current multi-tenancy implementation in the relevant module (`business_id` scoping)
3. Check existing translations for affected strings (pl, en, pt)
4. Review related Events, Jobs, Listeners
5. Check existing tests covering this area
6. Document gaps and risks
7. Present findings to user before planning any changes

Do NOT start implementing until this analysis is complete and confirmed by the user.
