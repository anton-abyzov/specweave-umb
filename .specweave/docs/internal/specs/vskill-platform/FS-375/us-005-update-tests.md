---
id: US-005
feature: FS-375
title: Update tests
status: complete
priority: P1
created: 2026-02-28
project: vskill-platform
---
# US-005: Update tests

**Feature**: [FS-375](./FEATURE.md)

platform developer
**I want** all tests updated to reflect the removal of fake seed data
**So that** the test suite passes cleanly after the refactor

---

## Acceptance Criteria

- [x] **AC-US5-01**: `seed-data-accuracy.test.ts` is deleted (it validates the now-removed fake skill data)
- [x] **AC-US5-02**: `data.test.ts` mock path updated from `../seed-data` to `../agent-data`
- [x] **AC-US5-03**: `popularity-fetcher.test.ts` seed data import test (TC-021) is removed or updated
- [x] **AC-US5-04**: `data-enrichment.test.ts` continues to pass (no dependency on seed skills)
- [x] **AC-US5-05**: Enrichment cron tests are updated with new 404 counter tests (US-003)
- [x] **AC-US5-06**: All existing tests pass after the refactor

---

## Implementation

**Increment**: [0375-remove-fake-seed-data](../../../../../increments/0375-remove-fake-seed-data/spec.md)

