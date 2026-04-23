# Tasks — 0687 Queue Dashboard Truthful Load, Backend Stabilization, and Studio Light Refresh

## Track A — Truthful First Load

### T-001: Write failing tests for queue boot payload and fallback default
**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Status**: [ ] pending

**Test Plan** (BDD):
- Given the active queue is empty but published submissions exist → When the server queue loader builds the initial payload → Then it returns a non-null `submissions` list, a truthful `defaultFilter`, and a labeled non-error state.

### T-002: Implement server-side truthful boot contract
**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Status**: [ ] pending

**Test Plan** (BDD):
- Given the boot payload tests are red → When the queue server data path is updated → Then `/queue` no longer ships `initialData.submissions = null` during healthy operation, and first render matches the chosen default filter.

### T-003: Add performance coverage for cold/warm queue load
**User Story**: US-001
**Satisfies ACs**: AC-US1-04
**Status**: [ ] pending

**Test Plan** (BDD):
- Given a preview-like environment with cold and warm cache states → When queue page load timings are measured for `/queue` → Then warm-cache p95 is under 2.0 s and cold-cache p95 is under 3.0 s.

## Track B — Filter and Search Stability

### T-004: Write failing integration tests for filter/list/count coherence
**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-04
**Status**: [ ] pending

**Test Plan** (BDD):
- Given multiple queue states with known seeded counts → When the list and stats APIs are queried for first-page filters → Then row sets, totals, and UI state flags remain internally consistent for each filter.

### T-005: Optimize list/search query path and cache usage
**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [ ] pending

**Test Plan** (BDD):
- Given the list/search performance tests are red → When query shape, indexes, payload selection, and cache fallbacks are improved → Then the API no longer returns overflow failures in smoke coverage and filter timings fall within the target thresholds.

### T-006: Implement deterministic loading, empty, and error states in the client
**User Story**: US-002
**Satisfies ACs**: AC-US2-04
**Status**: [ ] pending

**Test Plan** (BDD):
- Given list requests can succeed, return empty data, or degrade → When a user changes filters and searches from the queue UI → Then the interface always shows a clear loading, empty, or degraded state and never appears stuck.

## Track C — Database and Cache Truthfulness

### T-007: Add failing coverage for deduplicated queue-serving behavior
**User Story**: US-003
**Satisfies ACs**: AC-US3-01
**Status**: [ ] pending

**Test Plan** (BDD):
- Given duplicate `(repoUrl, skillName)` submissions exist in storage → When the queue-serving path returns rows and counts → Then only one visible row is served per logical submission identity, following the defined winner rule.

### T-008: Implement duplicate control and production enforcement/runbook
**User Story**: US-003
**Satisfies ACs**: AC-US3-01
**Status**: [ ] pending

**Test Plan** (BDD):
- Given dedup coverage is failing → When the queue-serving path and migration/runbook work are completed → Then duplicates are suppressed in served results and the database enforcement plan is explicit and executable.

### T-009: Unify stats/list cache freshness and add observability
**User Story**: US-003
**Satisfies ACs**: AC-US3-02, AC-US3-03
**Status**: [ ] pending

**Test Plan** (BDD):
- Given stats and list caches can drift or miss independently → When cache refresh and instrumentation are updated → Then stale count drift is bounded by TTL policy and logs/metrics identify cache path, query path, fallback path, and latency.

### T-010: Produce a redacted queue runtime credential inventory
**User Story**: US-003
**Satisfies ACs**: AC-US3-04
**Status**: [ ] pending

**Test Plan** (BDD):
- Given the queue path loads environment variables and Cloudflare bindings from multiple sources → When the runtime inventory is generated or documented → Then every secret/binding used by the queue is accounted for by name and purpose, with values redacted.

## Track D — Studio-Aligned UI Refresh

### T-011: Design and implement the Studio light-theme queue shell
**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-02
**Status**: [ ] pending

**Test Plan** (BDD):
- Given the current queue UI and the current Studio light-theme reference → When the queue shell, filters, and stats areas are redesigned → Then the page uses a consistent warm light palette, clearer typography, and stronger interaction hierarchy across desktop and mobile.

### T-012: Design polished empty/loading/degraded states and verify accessibility
**User Story**: US-004
**Satisfies ACs**: AC-US4-03, AC-US4-04
**Status**: [ ] pending

**Test Plan** (BDD):
- Given the refreshed queue UI → When the page is navigated by keyboard and exercised through loading, empty, and degraded scenarios → Then all states are intentional, readable, and accessible with maintained contrast and focus behavior.

## Track E — Verification and Sync

### T-013: Run full queue verification suite and update increment state
**User Story**: US-001, US-002, US-003, US-004
**Satisfies ACs**: AC-US1-04, AC-US2-02, AC-US2-03, AC-US4-04
**Status**: [ ] pending

**Test Plan** (BDD):
- Given all implementation tasks are complete → When `npx vitest run`, `npx playwright test`, and `npx vitest run --coverage` are executed and the increment docs are synced → Then the queue changes are verified, tasks/spec are updated, and the increment is ready for closure.
