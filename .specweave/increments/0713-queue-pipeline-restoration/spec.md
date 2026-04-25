---
increment: 0713-queue-pipeline-restoration
title: "Queue Pipeline Restoration (P0)"
type: hotfix
priority: P0
status: planned
created: 2026-04-24
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Queue Pipeline Restoration (P0)

## Overview

verified-skill.com submission pipeline is broken in production. Four bugs are stacked on top of each other: a frozen stats cron, a list endpoint that masks DB failures, malformed state-history writes, and a queue page that silently auto-flips filters when stats are stale. As a result, new submissions appear lost from the user's perspective even when the records exist in the database.

## Context

Anton submitted `https://github.com/heygen-com/hyperframes` at 2026-04-24T23:11:25Z. The system created 6 RECEIVED rows (one per discovered SKILL.md). 16+ minutes later they had not transitioned out of RECEIVED. Investigation surfaced:

- Stats counter frozen at `2026-04-24T15:17:00Z` (~8h stale) with `degraded:true`. Cron has been silently failing since commit 121de4e (0687 increment) introduced a `WITH deduped DISTINCT ON (repoUrl, skillName)` CTE that times out at 15s on the 107k-row Submission table. The regression guard then refuses to overwrite the cached non-zero with the failed zero.
- `GET /api/v1/submissions?state=*` returns `{items: [], total: 0}` for every state filter even though TOTAL=107,754. Direct ID fetch (`GET /api/v1/submissions/{id}`) still works, so the data is intact. The list endpoint masks DB errors as empty arrays instead of surfacing 503.
- State-history writes show `? -> ?` (no from/to/reason fields) — observability is gone, making it impossible to tell from history alone what happened to a row.
- Queue page's `chooseBootCandidates` (src/app/queue/data.ts:59-66) auto-selects "published" as the boot filter when `stats.active=0`, hiding new submissions even when the active filter would return them.

## User Stories

### US-001: Stats cron unfreezes and stays unfrozen (P0)
**Project**: vskill-platform

**As a** platform operator monitoring submission throughput
**I want** the queue stats counter to refresh every 10 minutes with truthful counts
**So that** dashboards, the queue page, and downstream filter logic don't lock onto a stale snapshot when the underlying query transiently fails

**Acceptance Criteria**:
- [x] **AC-US1-01**: `computeQueueStats` no longer wraps the count query in a `WITH deduped DISTINCT ON (repoUrl, skillName)` CTE. The flat `COUNT(*) FILTER (WHERE state IN (...))` is correct because the `(repoUrl, skillName)` unique index added in 0672 prevents duplicates.
- [x] **AC-US1-02**: On Phase 1 query failure (timeout, WASM OOM, DB unavailable), the cron writes a `{total: -1, active: -1, published: -1, rejected: -1, blocked: -1, onHold: -1, degraded: true}` failure sentinel to KV `submissions:stats-cache` and to the in-memory `_memQueueStats`.
- [x] **AC-US1-03**: The regression guard accepts a failure sentinel as the new "previous" state — it does NOT block subsequent successful writes that contain real positive counts.
- [x] **AC-US1-04**: The regression guard still rejects `{total: 0}` writes when the prior recorded `total > 0`. (The original 43a2790 / 0708 invariant is preserved.)
- [x] **AC-US1-05**: A successful cron run after a sentinel state is recorded MUST overwrite the sentinel and clear `degraded:true`.
- [ ] **AC-US1-06**: After deploy, `GET /api/v1/submissions/stats` returns `generatedAt` < 11 minutes old AND `degraded:false`.

### US-002: List endpoint surfaces failures honestly (P0)
**Project**: vskill-platform

**As a** queue page consumer (UI or scripts)
**I want** the list endpoint to either return real data or fail loudly with 503
**So that** I never silently see an empty list while the database is full of rows

**Acceptance Criteria**:
- [x] **AC-US2-01**: `parseUsableListCache` distinguishes "cache empty / parse failed" (returns null → fall through to DB) from "cache contains a valid response with `total: 0`" (returns the cached payload as-is). Today both paths return null.
- [x] **AC-US2-02**: When KV cache miss AND the DB query throws, the endpoint returns 503 with `Retry-After: 30` and a `hint: "database_unavailable"` body.
- [x] **AC-US2-03**: When KV cache miss AND DB returns 0 rows BUT current stats show TOTAL > 0, the endpoint logs a `list_empty_total_mismatch` warning and returns `{items: [], total: 0, warning: "list_empty_total_mismatch"}` so monitoring can alert.
- [x] **AC-US2-04**: The non-category branch of the GET handler wraps `fetchSubmissionList` in a try/catch that surfaces errors to the existing 503 fallback rather than swallowing them into an empty array.
- [ ] **AC-US2-05**: After deploy, `GET /api/v1/submissions?state=all&sort=createdAt&sortDir=desc&limit=10` returns ≥ 10 items.

### US-003: State-history writes are well-formed (P1)
**Project**: vskill-platform

**As a** debugger investigating a stuck or rejected submission
**I want** every state-history entry to carry `{timestamp, from, to, reason}` with the right field types
**So that** I can reconstruct the lifecycle from history alone, instead of guessing from `state` + `updatedAt`

**Acceptance Criteria**:
- [ ] **AC-US3-01**: The state-history writer in `src/lib/submission/db-persist.ts` requires non-null `to` always. `from` may be null only on the initial RECEIVED row.
- [ ] **AC-US3-02**: KV `hist:<id>` entries always have shape `{timestamp: ISO8601, from: SubmissionState | null, to: SubmissionState, reason: string}`. The contract is documented in a doc comment on the writer.
- [ ] **AC-US3-03**: A backfill script `scripts/backfill-state-history.ts` walks all `Submission` rows, finds entries with malformed history (missing `to`, or `from === to === null`), and reconstructs the latest entry from `state` + `updatedAt`. Idempotent. Guarded by `--dry-run`.
- [ ] **AC-US3-04**: Existing API responses for `/api/v1/submissions/{id}` and the queue page show real `from -> to` transitions for the 6 hyperframes rows after backfill, not `? -> ?`.

### US-004: Drain stuck queue and prevent recurrence (P0)
**Project**: vskill-platform

**As a** platform operator recovering from a queue stall
**I want** an admin script that re-enqueues stale RECEIVED rows, AND a recurring recovery cron that does this automatically every 30 minutes
**So that** transient queue stalls self-heal instead of leaving submissions stuck indefinitely

**Acceptance Criteria**:
- [x] **AC-US4-01**: New script `scripts/drain-stuck-received.ts` accepts `--repo-url <url>`, `--age-min <number>` (default 5), `--limit <number>` (default 50), and `--dry-run`. It lists `state=RECEIVED` rows older than `age-min` matching the optional repo filter and re-enqueues each into `SUBMISSION_QUEUE`.
- [ ] **AC-US4-02**: Running the script with `--repo-url https://github.com/heygen-com/hyperframes --age-min 5` flushes the 6 stuck rows; within 60 seconds they transition out of RECEIVED.
- [x] **AC-US4-03**: The recovery cron `recoverStaleReceived` exists, runs every 30 minutes, finds rows where `state=RECEIVED AND createdAt < NOW() - 30 min`, and re-enqueues up to 50 per tick. If absent or broken, it is wired/repaired in this increment.
- [x] **AC-US4-04**: The drain script is idempotent — running it twice in quick succession does not enqueue the same row twice (verified via `inflight` tracking or message dedup).

### US-005: Queue page renders honestly during stats degradation (P1)
**Project**: vskill-platform

**As a** queue page visitor (logged in or anonymous)
**I want** the page to honor my requested filter and show clear degradation messaging when stats are stale
**So that** I don't get silently redirected to "published" and miss new submissions that are actually in the active queue

**Acceptance Criteria**:
- [ ] **AC-US5-01**: `chooseBootCandidates` honors the URL `?filter=` parameter unconditionally — it does NOT auto-flip when stats are stale or degraded.
- [ ] **AC-US5-02**: When no URL filter is provided AND `stats.degraded === true`, the function returns `["all"]` (newest-first) — never `["published"]` based on a poisoned zero.
- [ ] **AC-US5-03**: The queue page's stats bar shows an inline "Counters refreshing…" message (or equivalent) when `stats.degraded === true`, instead of presenting the displayed zeros as truth.
- [ ] **AC-US5-04**: Per-tab default sort is applied:
  - active → `processingOrder asc` (queue position) — keep current
  - published → `updatedAt desc` (proxy for publishedAt; documented gap)
  - rejected → `updatedAt desc`
  - all → `createdAt desc` (newest first)
  - blocked → `updatedAt desc`
- [ ] **AC-US5-05**: Each tab shows ONE contextual time column instead of dual "Submitted | Updated":
  - active → "Submitted" (createdAt)
  - published → "Updated" (proxy for publishedAt)
  - rejected → "Updated" (proxy for rejectedAt)
  - all → "Last activity" (max of createdAt/updatedAt)
  - blocked → "Updated"
- [ ] **AC-US5-06**: After Phase 2 deploy, visiting `https://verified-skill.com/queue` (no filter) does NOT redirect to `?filter=published`. The URL remains `/queue` and the table renders the "all" view.
- [ ] **AC-US5-07**: After Phase 2 deploy, visiting `https://verified-skill.com/queue?filter=all` renders rows sorted by `createdAt` desc (most recent first).

## Functional Requirements

### FR-001: Failure-sentinel observability
All cron stats writes that detect underlying query failure MUST encode the failure as a `-1` sentinel rather than a real-looking zero. Health checks and dashboards can then alert specifically on sentinel presence rather than confusing "zero submissions" with "stats broken."

### FR-002: List endpoint honesty contract
The list API MUST satisfy: for any state filter, either (a) return rows that exist, (b) return an empty list with a warning when stats and DB disagree, or (c) return 503. It MUST NOT return `{items: [], total: 0}` while the underlying database has matching rows.

### FR-003: Queue page filter contract
The queue page's default-filter chooser MUST be deterministic: if the URL has `?filter=X`, X is used. If no URL filter, the chooser uses `stats.degraded` as the disambiguator — degraded → "all", healthy → ranked by non-zero counts.

## Success Criteria

- **Cron freshness**: `GET /api/v1/submissions/stats` reports `generatedAt < 11 min old` and `degraded:false` continuously for 24 hours after deploy.
- **List endpoint correctness**: `GET /api/v1/submissions?state=all&sort=createdAt&sortDir=desc&limit=10` returns ≥ 10 items.
- **Queue drainage**: All RECEIVED rows older than 30 min decrease to zero within one recovery-cron tick.
- **State history quality**: Spot-check 10 random Submission IDs — all latest history entries have non-null `to` and a non-empty `reason`.
- **No silent flip**: Visiting `/queue` does not change the URL to `?filter=published`.

## Out of Scope

The following land in follow-up increments to keep this hotfix focused:

- **0714 — queue-state-aware-ordering**: First-class `publishedAt` and `rejectedAt` columns on the Submission table (requires migration).
- **0715 — queue-find-mine**: "Mine" toggle, paste-URL search input, queue position visualization (`#3 of 247 · ETA ~90s`), live `● Live` indicator.
- **Schema changes** beyond the state-history shape contract.
- **AI/scoring pipeline changes** — Tier 1 / Tier 2 logic is untouched.

## Dependencies

- Cloudflare Workers / Queues (`SUBMISSION_QUEUE`, `submission-dlq`) — existing
- KV namespace `SUBMISSIONS_KV` (id `d21d89b0c2644c2aa9303878300332e8`) — existing
- Postgres / Neon `Submission` table with `(repoUrl, skillName)` unique index — existing (added in 0672)
- `recoverStaleReceived` cron entry in `.open-next/worker-with-queues.js` — verify presence
- 0708 increment's `-1` sentinel pattern from `platform-stats-refresh.ts` — referenced for the same approach in queue stats
