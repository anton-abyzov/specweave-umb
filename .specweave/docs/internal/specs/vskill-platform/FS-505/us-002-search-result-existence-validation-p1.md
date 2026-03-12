---
id: US-002
feature: FS-505
title: "Search Result Existence Validation (P1)"
status: completed
priority: P1
created: 2026-03-12T00:00:00.000Z
tldr: "**As a** developer searching for skills via CLI or website."
project: vskill-platform
---

# US-002: Search Result Existence Validation (P1)

**Feature**: [FS-505](./FEATURE.md)

**As a** developer searching for skills via CLI or website
**I want** search results that only contain skills that actually exist
**So that** I never encounter a 404 when clicking a search result

---

## Acceptance Criteria

- [x] **AC-US2-01**: Given the search source is "edge" (KV-only, Postgres returned zero results), when the search route returns results, then each result's `name` is batch-validated against Postgres and non-existent skills are filtered out before the response
- [x] **AC-US2-02**: Given the search source is "edge+postgres" or "postgres", when the search route returns results, then no additional existence validation is performed (Postgres results are inherently fresh)
- [x] **AC-US2-03**: Given the DB validation query fails, when the search route processes edge-only results, then all edge results are returned unfiltered (graceful degradation) and a warning is logged

---

## Implementation

**Increment**: [0505-fix-stale-search-404](../../../../../increments/0505-fix-stale-search-404/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-003**: Add edge-only existence validation to search route (TDD Red → Green → Refactor)
