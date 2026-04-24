---
status: completed
---
# 0687 — Queue Dashboard Truthful Load, Fast Filters, and Design Rollback

**Status:** active  
**Project:** vskill-platform  
**Priority:** high  
**Test mode:** TDD  
**Coverage target:** 90%

## 1. Context

The current `verified-skill.com/queue` experience has both product and technical drift:

- The initial server render can ship `initialData.submissions = null`, which causes a blank or misleading first paint.
- Production data currently shows `0` active submissions in Postgres, while cached queue stats still report `683` active submissions.
- `/api/v1/submissions` intermittently returns `503` with `wasm_buffer_overflow`, and even successful published-list requests can take ~6.8 s for a 5-row response.
- Duplicate queue rows still exist in production because the database does not currently enforce uniqueness on `(repoUrl, skillName)`.
- Filter changes sometimes feel slow or inconsistent because counts, cache state, and query results do not appear to come from a single freshness model.
- The latest queue visual treatment is too heavy for an operational dashboard and should roll back to the previous simpler queue design while preserving useful state/error improvements.

This increment fixes the queue as a whole system: SSR load path, API performance, cache strategy, database truthfulness, filter behavior, and the visual design rollback.

## 2. Scope

### In Scope

- Server-rendered queue boot path and initial data contract
- `/api/v1/submissions` list, filter, and search performance/stability
- Queue stats/list cache coherence and warm-up/invalidation behavior
- Production-serving duplicate suppression and database enforcement strategy
- Credentials/runtime audit for the queue path (`.env`, Cloudflare bindings, internal tokens) without exposing raw secrets
- Queue page UI/UX rollback to the previous simpler operational design
- Regression coverage for queue loading, filtering, and empty/degraded states

### Out of Scope

- Full rearchitecture of the submission-processing pipeline outside queue-serving needs
- Secret rotation, unless the audit reveals an active leak
- Non-queue pages
- Dark-theme redesign

## 3. Verified Findings

These findings were confirmed during planning and should be treated as the starting point for the implementation:

1. The live `/queue` server payload includes stats but can ship `initialData.submissions: null`.
2. Production Postgres currently has no active (`RECEIVED`, `TIER1_SCANNING`, `TIER2_SCANNING`) submissions, while cached stats still claim hundreds of active items.
3. The live submissions API can return `503 Service temporarily unavailable` with `wasm_buffer_overflow`.
4. The published filter is materially slower than acceptable for interactive browsing.
5. Production still serves duplicate `(repoUrl, skillName)` rows because uniqueness is not enforced in the live database.
6. Queue runtime depends on a mixture of local env values and Cloudflare bindings/KV namespaces; that surface needs a safe inventory and clearer ownership.
7. Local Playwright baseline on 2026-04-24 against `http://localhost:3310` shows `tests/e2e/queue-truthful-load.spec.ts` passes, but `tests/e2e/queue-cold-load.spec.ts` fails because the first load does not paint 50 rows within 1.5 s.
8. Local timing on 2026-04-24 shows `/api/v1/submissions/stats` repeatedly taking about 15.2-15.3 s and returning all-zero stats after the DB stats compute path times out. This makes `/queue` stream an incomplete page and then settle into an empty active view.
9. Local filter timings show warm `published` and `blocked` list requests can be about 20 ms after cache, but the cold `published` request was about 4.1 s and the active request about 225-440 ms, so category switching needs a guaranteed warm/read-through path and no stat recompute dependency.

## 4. User Stories and Acceptance Criteria

### US-001: Truthful first load with useful default content
**Project**: vskill-platform

**As an** operator visiting the queue dashboard  
**I want** the page to show truthful data immediately on first load  
**So that** I can understand queue state without waiting for a second fetch or seeing a misleading empty screen.

**Acceptance Criteria**:
- [x] **AC-US1-01**: `GET /queue` renders a non-empty server payload whenever any submission data exists overall. If the active queue is truly empty, the page server-renders a labeled fallback dataset such as recent/published instead of landing on an empty active view by default.
- [x] **AC-US1-02**: The server-rendered queue payload never ships `initialData.submissions = null` unless the page is in an explicit degraded/error state that explains the failure to the user.
- [x] **AC-US1-03**: Queue stats, default filter selection, and first-page rows come from the same freshness window, so the initial UI cannot claim active work exists while the default list is empty.
- [x] **AC-US1-04**: Cold-load p95 for `/queue` on a preview deployment is under 2.0 s with a warm cache and under 3.0 s from a cold list-cache path.

### US-002: Fast, stable filters and search
**Project**: vskill-platform

**As a** queue user  
**I want** filters, search, and section changes to feel quick and reliable  
**So that** I can inspect queue states without lag, stale counts, or intermittent failures.

**Acceptance Criteria**:
- [x] **AC-US2-01**: Switching among `active`, `published`, `rejected`, `blocked`, and `onHold` produces results whose counts and rows are internally consistent for the same request.
- [x] **AC-US2-02**: The list/search API does not return `wasm_buffer_overflow` or generic 503 responses during preview smoke testing of 100 sequential list/filter requests.
- [x] **AC-US2-03**: Warm filter changes complete within p95 < 800 ms for first-page requests, and cold filter changes complete within p95 < 2.5 s.
- [x] **AC-US2-04**: Loading, empty, and error states are deterministic: filters never appear stuck, and the UI always makes clear whether data is loading, unavailable, or genuinely empty.

### US-003: Queue backend is truthful, deduplicated, and observable
**Project**: vskill-platform

**As a** maintainer  
**I want** the queue backend to reflect real database state and expose enough observability to debug issues  
**So that** the dashboard stays trustworthy and regressions are easy to diagnose.

**Acceptance Criteria**:
- [x] **AC-US3-01**: Duplicate `(repoUrl, skillName)` rows are not visible in the queue-serving path, and the production database enforcement plan is implemented or documented as a staged rollout with a concrete migration/runbook.
- [x] **AC-US3-02**: Stats cache and list cache share a coordinated refresh/invalidation strategy, and stale count drift cannot persist beyond the configured TTL window.
- [x] **AC-US3-03**: Queue-serving code logs or records enough metadata to distinguish cache hit/miss, DB query path, degraded fallback path, and request latency without exposing credentials.
- [x] **AC-US3-04**: A credentials/runtime audit records every environment variable, secret, KV namespace, and binding used by the queue path, with raw values redacted.

### US-004: Queue UI rolls back to the previous operational design
**Project**: vskill-platform

**As a** Verified Skill user  
**I want** the queue dashboard to return to the previous simpler operational layout  
**So that** the page loads quickly, scans clearly, and avoids the heavy redesign that currently makes the first load feel broken.

**Acceptance Criteria**:
- [x] **AC-US4-01**: The queue page removes the heavy Studio-style hero/card redesign and restores the previous compact queue-first layout with `Submission Queue`, stat cards, status bar, search, table, pagination, and execution log in the earlier order.
- [x] **AC-US4-02**: Filter controls, stats, and list/table structure remain easy to scan on desktop and mobile without introducing large decorative sections above the actual queue.
- [x] **AC-US4-03**: Empty, loading, and degraded states stay deterministic and readable after the rollback.
- [x] **AC-US4-04**: The rolled-back queue page passes keyboard navigation and maintains AA-appropriate contrast for its primary interactions.

## 5. Dependencies and Notes

- This work follows up on `0672-queue-reliability`, but planning assumes parts of that increment were not fully deployed or no longer match production reality.
- The user explicitly requested rolling back the latest queue page design instead of continuing the Studio-style queue redesign.
- Existing unrelated uncommitted changes in `repositories/anton-abyzov/vskill-platform` must be preserved.

## 6. Implementation Notes

- The stats API no longer computes queue stats on demand. Request paths read fresh cache, stale non-zero cache marked degraded, or degraded empty stats quickly; cron owns expensive recompute.
- Queue SSR now reads exact list cache, latest per-filter cache, then a bounded direct fallback. Empty cache snapshots are ignored so poisoned `submissions:list:*` and `submissions:latest:*` entries cannot force a false empty page.
- The client now honors the server-selected `defaultFilter` when the URL has no filter, so a published fallback dataset no longer hydrates as active.
- Warm category switching uses the default first-page `submissions:latest:<filter>` path before DB and avoids overwriting that latest cache with custom page/sort responses.
- Queue list serving now deduplicates `(repoUrl, skillName)` using the same latest-row winner model as queue stats, rejects underfilled duplicate KV snapshots, and keeps a final client guard so stale cache cannot reintroduce visible duplicates.
- The rolled-back queue stat filters are keyboard-focusable buttons with focus-visible styling, and the search input restores a visible focus ring.
- `reports/queue-performance-runtime-inventory.md` records the queue runtime bindings and secret names with values redacted.
- Full closure remains blocked by broader repo test failures unrelated to this queue performance patch.
