---
id: US-002
feature: FS-351
title: Preferences cold-start retry
status: complete
priority: P1
created: 2026-02-24
project: vskill-platform
---
# US-002: Preferences cold-start retry

**Feature**: [FS-351](./FEATURE.md)

logged-in user
**I want** the preferences endpoints to retry on cold-start DB failures
**So that** I can load and save my preferences reliably

---

## Acceptance Criteria

- [x] **AC-US2-01**: `GET /api/v1/user/preferences` retries DB operations once on failure (2 attempts total), matching the search route pattern
- [x] **AC-US2-02**: `PATCH /api/v1/user/preferences` retries the entire read-merge-write block once on failure
- [x] **AC-US2-03**: Auth validation and body parsing remain outside the retry boundary
- [x] **AC-US2-04**: On retry, `console.warn` logs attempt failure with route path (no user IDs or body contents)
- [x] **AC-US2-05**: Existing preferences tests still pass

---

## Implementation

**Increment**: [0351-fix-search-preferences-cold-start](../../../../../increments/0351-fix-search-preferences-cold-start/spec.md)

