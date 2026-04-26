---
increment: 0757-queue-counters-zero-on-cold-worker
title: Queue counters render 0/0/0/0/0 on cold Cloudflare workers
type: hotfix
priority: P0
status: completed
created: 2026-04-26T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Hotfix: Queue counters render 0/0/0/0/0 on cold Cloudflare workers

## Overview

The verified-skill.com `/queue` page renders `Total=0  Active=0  Published=0  Rejected=0  Blocked=0  AvgScore=0.0` on roughly 40% of page loads, while the submission table on the same page renders real rows (e.g. `tournament-manager` with score 95). Production has 111,091 submissions (105,999 published) — the data exists; only the counter cards are broken.

**Verified by direct probing (2026-04-26 ~08:25Z):**

- 20 cache-busted SSR probes against `/queue` → 8/20 returned `Total=0  Published=0` HTML; 12/20 returned `Total=111,091  Published=105,999`.
- 10 probes against `/api/v1/submissions/stats` → 8/10 returned real numbers (`source=db|memory, freshness=fresh`); 2/10 returned `{total:0,…,degraded:true}` (`source=empty, freshness=missing`, HTTP 200).

**Root cause:** Cloudflare-cold-worker problem. `readQueueStatsSnapshot()` (`src/lib/queue/queue-stats-cache.ts:81`) has a 4-tier fallback (KV → in-process memory → DB-with-150ms-timeout → empty). When all three primary tiers miss on a cold worker, it falls to the 4th tier and returns `{total:0,…,degraded:true,source:"empty"}` — **with HTTP 200**, indistinguishable from a genuinely empty queue. SSR ships those zeros into initialData; the client's existing guard correctly skips zero-degraded responses but no retry is scheduled, so a page can stay at zeros until the next SSE `submission_created` event.

**Cost/value constraint (per user direction during planning):** "Find the right balance between money and quick data return, even if not fully accurate." This rules out always-on freshness mechanisms (extra cron writes, increased polling, on-demand DB compute on the hot path). It allows the existing DB-fallback read path a more realistic timeout, and trades silent fake zeros for honest 503s + brief client retries.

The fix has 4 stacked layers ordered by impact:

1. **Bump DB fallback timeout 150ms → 800ms** (`queue-stats-cache.ts`) — biggest single improvement; cold workers now usually serve real data instead of falling to empty tier. No new queries; just gives the existing one a fair budget.
2. **API returns 503 + Retry-After: 5 when source=empty** (`stats/route.ts`) — safety net for genuine DB outage; lets clients distinguish cold-worker miss from real empty queue.
3. **SSR returns `stats: null` when degraded+zero** (`queue/data.ts`) — don't ship fake zeros into the HTML.
4. **Client renders em-dash placeholders + retries with bounded backoff 1s/3s/7s (cap 3)** (`QueuePageClient.tsx`) — gives the page a path to recovery without burning cache or hammering the worker.

## User Stories

### US-001: Queue page never displays bare-zero counters when real data exists (P0)
**Project**: vskill-platform

**As a** verified-skill.com visitor opening `https://verified-skill.com/queue`
**I want** the stat counter cards to show either real numbers or a clear placeholder
**So that** I never see misleading zeros that contradict the real submission table on the same page

**Acceptance Criteria**:
- [x] **AC-US1-01**: 20 cache-busted curl probes of `/queue?_cb=N` HTML must return 0 instances of literal `Total=0  Published=0` simultaneously. Each probe returns either real numbers (e.g. `Total=111,091  Published=105,999`) OR the em-dash placeholder (`Total=—  Published=—`). Verification: shell loop in `tasks.md` T-007.
- [x] **AC-US1-02**: Inspecting the rendered DOM after page load, when no fresh stats are available the 6 StatCards (Total, Active, Published, Rejected, Blocked, Avg Score) all display `—` (em-dash, U+2014) using the existing `var(--text-faint)` color token — not `0`.
- [x] **AC-US1-03**: When the client receives an HTTP 503 from `/api/v1/submissions/stats` OR a `{total:0, degraded:true}` body, it schedules retries via `setTimeout` at 1s, 3s, and 7s (cap 3). On any successful response (HTTP 200 with `total>0` OR not degraded), the retry counter resets and the StatCards switch from `—` to real numbers.
- [x] **AC-US1-04**: When an SSE `submission_created` event fires during or after a failed retry chain, the retry counter resets so subsequent fetches get a fresh chain.
- [x] **AC-US1-05**: When the queue is genuinely empty (zero submissions in DB), the page correctly shows `0` (not em-dash) — distinguished by the API returning `{degraded:false, source:"kv"}` or similar non-empty source.

---

### US-002: Stats API distinguishes cold-worker miss from real empty queue (P0)
**Project**: vskill-platform

**As an** API client calling `/api/v1/submissions/stats`
**I want** the response status code to honestly signal whether the worker has data or is in a degraded fallback state
**So that** I can decide whether to retry briefly or render a real result

**Acceptance Criteria**:
- [x] **AC-US2-01**: `GET /api/v1/submissions/stats` returns HTTP **503** with header `Retry-After: 5` when the underlying snapshot has `source: "empty"` (all 3 tiers — KV, memory, DB — failed/missed/timed-out).
- [x] **AC-US2-02**: `GET /api/v1/submissions/stats` continues to return HTTP **200** when source is `"kv"`, `"memory"`, or `"db"` — even when `degraded: true` (the data is still useful, just stale or imperfect).
- [x] **AC-US2-03**: The 503 response body shape is identical to the prior 200 body (still includes `{total:0, ..., degraded:true, generatedAt: <iso>}`) so existing parsers don't break — only the status code changes.
- [x] **AC-US2-04**: The `X-Queue-Stats-Source` and `X-Queue-Stats-Freshness` debug headers are present on both 200 and 503 responses, unchanged from current behavior.

---

### US-003: SSR doesn't ship fake zeros to the browser (P0)
**Project**: vskill-platform

**As a** developer maintaining the queue page render path
**I want** SSR to pass `null` instead of a zero-filled stats object when the snapshot is degraded+empty
**So that** the client component can render placeholders rather than baking zeros into the initial HTML

**Acceptance Criteria**:
- [x] **AC-US3-01**: `QueueInitialData.stats` in `src/app/queue/data.ts` is typed as `QueueStats | null`.
- [x] **AC-US3-02**: `getQueueInitialDataSSR(...)` returns `stats: null` whenever `stats.degraded === true && stats.total === 0` (the existing `statsUnavailable` predicate at line 254). All other initialData fields (submissions, total, queuePositions, defaultFilter, mode, message) are unchanged.
- [x] **AC-US3-03**: When stats are healthy (`degraded: false` OR `total > 0`), `getQueueInitialDataSSR(...)` continues to pass the real stats object through unchanged.

---

### US-004: DB fallback gets a fair budget on cold Neon connections (P0)
**Project**: vskill-platform

**As a** Cloudflare Worker handling `/queue` SSR or `/api/v1/submissions/stats` on a cold isolate
**I want** the DB fallback read to have a realistic timeout for cold Neon connections
**So that** the request doesn't fall to the empty tier and serve fake zeros when the DB could have answered in 300-500ms

**Acceptance Criteria**:
- [x] **AC-US4-01**: `DB_STATS_FALLBACK_TIMEOUT_MS` constant in `src/lib/queue/queue-stats-cache.ts` is bumped from `150` to `800`.
- [x] **AC-US4-02**: After deploy, 20 cache-busted probes of `/api/v1/submissions/stats` should yield ≤ 5% `source: "empty"` responses (down from the observed ~20%). Verification: shell loop in `tasks.md` T-008.
- [x] **AC-US4-03**: P95 latency of `/api/v1/submissions/stats` is bounded by ~1s (800ms DB timeout + ~200ms KV+memory checks + serialization). The route has no new code paths that can add unbounded latency.

## Functional Requirements

### FR-001: API status code semantics
The stats endpoint maps snapshot source to HTTP status as follows:

| `snapshot.source` | HTTP status | Header |
|---|---|---|
| `"kv"` | 200 | (existing) |
| `"memory"` | 200 | (existing) |
| `"db"` | 200 | (existing) |
| `"empty"` | **503** | **`Retry-After: 5`** |

Body shape unchanged in all cases.

### FR-002: SSR initialData stats nullability
`QueueInitialData.stats: QueueStats | null`. Consumers (currently only `QueuePageClient`) handle `null` as "loading / unknown".

### FR-003: Client placeholder + retry chain
- StatCard value rendering: `stats === null ? "—" : stats[fieldName].toLocaleString()`.
- Retry trigger: `fetchStats` receives HTTP 503 OR `{total:0, degraded:true}` body.
- Backoff: `setTimeout(fetchStats, 1000)`, then `3000`, then `7000`. Each successful retry chain attempt increments a ref-tracked counter; cap at 3 attempts. Counter resets on any successful response or on `submission_created` SSE event.
- Cleanup: any pending `setTimeout` is cleared on component unmount and on every new `fetchStats` call.

### FR-004: DB fallback timeout
Single constant change: `DB_STATS_FALLBACK_TIMEOUT_MS = 800` (was `150`).

## Success Criteria

- After deploy, the `for i in $(seq 1 20); do curl -sS "https://verified-skill.com/queue?_cb=$RANDOM" | ...` shell probe returns **zero** lines containing `0 | 0` for Total | Published. Every line shows real numbers OR em-dash placeholder.
- Manual test: hard-refresh the `/queue` page in a browser ≥10 times — counters never show `0`s alongside real submission rows.
- All existing Vitest suites for `queue/`, `api/v1/submissions/stats/`, `lib/queue/queue-stats-cache` continue to pass.
- New Vitest specs for the 4 ACs above pass.
- No regression in `/api/v1/submissions` (list endpoint), `/api/v1/submissions/<id>` (detail endpoint), or `/api/v1/submissions/stream` (SSE).

## Out of Scope

- **Removing the legacy in-Worker `refreshQueueStats` from `/api/v1/internal/cache-warm/route.ts:43`.** It currently overwrites Hetzner-written clean stats with `degraded:true`. Decoupling the writers is a separate increment.
- **Investigating why Hetzner-written stats are 72+ minutes old.** Cron lag on the VM or silent writer failure — separate diagnosis.
- **Changing `MAX_QUEUE_STATS_AGE_MS = 90 * 60 * 1000` (90-minute freshness window) in `queue-stats-freshness.ts`.** The existing `rememberStale` path already serves >90-minute data when nothing better exists; tweaking the window is a separate UX call.
- **Increasing polling frequency or shortening Cache-Control TTLs.** User explicitly ruled out cost-increasing always-on mechanisms.
- **E2E Playwright test.** Cloudflare cold-worker behavior cannot be reliably reproduced from a browser test against prod. Verification is via post-deploy curl probes.

## Dependencies

- `@/lib/queue/queue-stats-cache` (modified — timeout constant)
- `@/lib/queue/queue-stats-freshness` (unchanged — `isFailureSentinel`, `MAX_QUEUE_STATS_AGE_MS`)
- `@/lib/cron/queue-stats-refresh` (unchanged — `QueueStats` type, `getMemQueueStats/setMemQueueStats`)
- `@opennextjs/cloudflare` (unchanged — request context for KV reads in SSR)
- `@/components/SectionDivider`, `STATUS_VARS`, `mono` (unchanged — used by `QueuePageClient`)

## Risks and Mitigations

- **Risk:** 800ms timeout could make the stats endpoint feel slow on persistent cold-worker conditions.
  **Mitigation:** Cache-Control `s-maxage=10` means Cloudflare's edge cache absorbs most repeated requests within 10s. The 800ms ceiling only applies when KV+memory both miss, which is a small fraction of total traffic.

- **Risk:** Client retry chain could storm the worker if a popular page sees thousands of cold-worker hits at once.
  **Mitigation:** Hard cap 3 retries per page load; total max ~11s of retry window per client. Cloudflare per-worker concurrency easily absorbs this. No global rate limit triggers.

- **Risk:** The em-dash placeholder might confuse users who expect to see numbers.
  **Mitigation:** The existing "Counters refreshing…" ribbon (which renders when `stats.degraded === true`) gives the user a clear signal that the system is recovering. Em-dash is a standard "unknown / loading" affordance; auto-resolves within seconds in the common case.

- **Risk:** Existing tests for the `data.ts` module pin the type as non-nullable.
  **Mitigation:** The plan touches every test file that asserts on `initialData.stats`; types are updated in lockstep with the implementation. CI catches regressions.
