# 0687 — Queue Dashboard Truthful Load, Backend Stabilization, and Studio Light Refresh

**Status:** planned  
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
- The queue UI does not visually match the stronger light-theme language already established in vSkill Studio.

This increment fixes the queue as a whole system: SSR load path, API performance, cache strategy, database truthfulness, filter behavior, and the visual design of the dashboard.

## 2. Scope

### In Scope

- Server-rendered queue boot path and initial data contract
- `/api/v1/submissions` list, filter, and search performance/stability
- Queue stats/list cache coherence and warm-up/invalidation behavior
- Production-serving duplicate suppression and database enforcement strategy
- Credentials/runtime audit for the queue path (`.env`, Cloudflare bindings, internal tokens) without exposing raw secrets
- Queue page UI/UX refresh aligned to the vSkill Studio light theme
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

## 4. User Stories and Acceptance Criteria

### US-001: Truthful first load with useful default content
**Project**: vskill-platform

**As an** operator visiting the queue dashboard  
**I want** the page to show truthful data immediately on first load  
**So that** I can understand queue state without waiting for a second fetch or seeing a misleading empty screen.

**Acceptance Criteria**:
- [ ] **AC-US1-01**: `GET /queue` renders a non-empty server payload whenever any submission data exists overall. If the active queue is truly empty, the page server-renders a labeled fallback dataset such as recent/published instead of landing on an empty active view by default.
- [ ] **AC-US1-02**: The server-rendered queue payload never ships `initialData.submissions = null` unless the page is in an explicit degraded/error state that explains the failure to the user.
- [ ] **AC-US1-03**: Queue stats, default filter selection, and first-page rows come from the same freshness window, so the initial UI cannot claim active work exists while the default list is empty.
- [ ] **AC-US1-04**: Cold-load p95 for `/queue` on a preview deployment is under 2.0 s with a warm cache and under 3.0 s from a cold list-cache path.

### US-002: Fast, stable filters and search
**Project**: vskill-platform

**As a** queue user  
**I want** filters, search, and section changes to feel quick and reliable  
**So that** I can inspect queue states without lag, stale counts, or intermittent failures.

**Acceptance Criteria**:
- [ ] **AC-US2-01**: Switching among `active`, `published`, `rejected`, `blocked`, and `onHold` produces results whose counts and rows are internally consistent for the same request.
- [ ] **AC-US2-02**: The list/search API does not return `wasm_buffer_overflow` or generic 503 responses during preview smoke testing of 100 sequential list/filter requests.
- [ ] **AC-US2-03**: Warm filter changes complete within p95 < 800 ms for first-page requests, and cold filter changes complete within p95 < 2.5 s.
- [ ] **AC-US2-04**: Loading, empty, and error states are deterministic: filters never appear stuck, and the UI always makes clear whether data is loading, unavailable, or genuinely empty.

### US-003: Queue backend is truthful, deduplicated, and observable
**Project**: vskill-platform

**As a** maintainer  
**I want** the queue backend to reflect real database state and expose enough observability to debug issues  
**So that** the dashboard stays trustworthy and regressions are easy to diagnose.

**Acceptance Criteria**:
- [ ] **AC-US3-01**: Duplicate `(repoUrl, skillName)` rows are not visible in the queue-serving path, and the production database enforcement plan is implemented or documented as a staged rollout with a concrete migration/runbook.
- [ ] **AC-US3-02**: Stats cache and list cache share a coordinated refresh/invalidation strategy, and stale count drift cannot persist beyond the configured TTL window.
- [ ] **AC-US3-03**: Queue-serving code logs or records enough metadata to distinguish cache hit/miss, DB query path, degraded fallback path, and request latency without exposing credentials.
- [ ] **AC-US3-04**: A credentials/runtime audit records every environment variable, secret, KV namespace, and binding used by the queue path, with raw values redacted.

### US-004: Queue UI matches the Studio light-theme quality bar
**Project**: vskill-platform

**As a** Verified Skill user  
**I want** the queue dashboard to feel visually consistent with the current Studio light theme  
**So that** the page looks intentional, modern, and easier to scan.

**Acceptance Criteria**:
- [ ] **AC-US4-01**: The queue page adopts the Studio light-theme direction: warm light surfaces, stronger typography hierarchy, and accent usage consistent with the current Studio experience.
- [ ] **AC-US4-02**: Filter controls, stats, and list/table structure have clearer hierarchy and affordance on both desktop and mobile.
- [ ] **AC-US4-03**: Empty, loading, and degraded states are designed as first-class UI states rather than default browser-like placeholders.
- [ ] **AC-US4-04**: The refreshed queue page passes keyboard navigation and maintains AA-appropriate contrast for its primary interactions.

## 5. Dependencies and Notes

- This work follows up on `0672-queue-reliability`, but planning assumes parts of that increment were not fully deployed or no longer match production reality.
- This work should reuse the vSkill Studio light-theme direction rather than introducing a separate visual language for the queue.
- Existing unrelated uncommitted changes in `repositories/anton-abyzov/vskill-platform` must be preserved.
