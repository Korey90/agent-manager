# Architecture Plan & Decisions

**Decision Log**

| Date       | Decision                              | Reason                          | Status    |
|------------|---------------------------------------|---------------------------------|-----------|
| 2026-04-XX | Action pattern instead of Services    | Better testability              | Active    |
| 2026-05-XX | Light multi-tenancy (`business_id`)   | Simplicity + performance        | Active    |

**Folder Structure Rules:**
- `app/Actions/{Domain}/`
- `app/DataTransferObjects/`
- `app/Events/`
- etc.