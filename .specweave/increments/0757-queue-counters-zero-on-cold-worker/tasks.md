# Tasks: Queue counters render 0/0/0/0/0 on cold Cloudflare workers

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Tests live in `repositories/anton-abyzov/vskill-platform/`

## TDD Discipline

RED → GREEN → REFACTOR per layer. Tests write first; implementation follows; verify all pass; then move to next layer.

---

### T-001: Write failing tests for Layer A (DB timeout bump)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01 | **Status**: [x] completed

**Test Plan**:
- **Given** `src/lib/queue/queue-stats-cache.ts` exports `DB_STATS_FALLBACK_TIMEOUT_MS`
- **When** the test reads the constant
- **Then** it equals `800` (currently `150`, so this test must fail before the bump)

**Implementation**: Add a unit test in `src/lib/queue/__tests__/queue-stats-cache.timeout.test.ts` that imports the constant and asserts `expect(DB_STATS_FALLBACK_TIMEOUT_MS).toBe(800)`. RUN — must fail.

---

### T-002: Write failing tests for Layer B (stats route 503 on empty)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04 | **Status**: [x] completed

**Test Plan**:
- **Given** `readQueueStatsSnapshot` is mocked to return `{ stats: { total:0, ..., degraded:true }, source: "empty", freshness: "missing" }`
- **When** `GET /api/v1/submissions/stats` handler is called
- **Then** response status is 503 AND `Retry-After: 5` header is present AND body equals the snapshot stats AND `X-Queue-Stats-Source: empty` and `X-Queue-Stats-Freshness: missing` headers are present

- **Given** `readQueueStatsSnapshot` returns `{ stats: { total:111091, ..., degraded:true }, source: "db", freshness: "fresh" }`
- **When** the handler is called
- **Then** response status is 200 (not 503) — degraded but with real numbers stays 200

**Implementation**: Add `src/app/api/v1/submissions/stats/__tests__/route.test.ts` (or extend if it exists). Mock `@/lib/queue/queue-stats-cache` via `vi.hoisted` + `vi.mock`. Run — must fail (current handler always returns 200).

---

### T-003: Write failing tests for Layer C (SSR stats:null on unavailable)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x] completed

**Test Plan**:
- **Given** `getQueueStatsSSR` (or the cache module it wraps) is mocked to return `{ total:0, degraded:true, ... }`
- **When** `getQueueInitialDataSSR({})` is called
- **Then** the returned object has `stats: null`

- **Given** healthy stats `{ total:111091, degraded:false, ... }`
- **When** `getQueueInitialDataSSR({})` is called
- **Then** `stats` equals the healthy stats object (unchanged behavior)

- **Given** the type definition of `QueueInitialData`
- **When** TypeScript compiles
- **Then** `stats` is typed as `QueueStats | null` (compile-time check; existing tests must still type-check)

**Implementation**: Extend `src/app/queue/__tests__/data.initial-data.test.ts`. Reuse existing mock setup; add 2 new test cases. Run — must fail.

---

### T-004: Write failing tests for Layer D (client em-dash + retry)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [x] completed

**Test Plan**:
- **Given** `<QueuePageClient initialData={{ stats: null, submissions: [], total: 0, queuePositions: {}, defaultFilter: "active", mode: "ready" }} />`
- **When** rendered (jsdom)
- **Then** all 6 StatCards (Total, Active, Published, Rejected, Blocked, Avg Score) display `—` (em-dash, U+2014); none display the literal `0`

- **Given** `fetchStats` is mocked: returns `Response(503)` once, then `Response(200, { total:111091, active:153, ..., degraded:false })`
- **When** the component mounts (with `vi.useFakeTimers()`); advance timers by 1100ms
- **Then** `fetch` is called twice; after the second call resolves, the StatCards render real numbers (`111,091` formatted)

- **Given** `fetchStats` returns 503 four times in a row
- **When** mount + advance timers through all retry windows (1s + 3s + 7s = 11s)
- **Then** `fetch` is called exactly 4 times total (1 initial + 3 retries) and no further calls happen

- **Given** SSE delivers a `submission_created` event after a failed retry chain
- **When** the event handler runs
- **Then** the retry counter resets (next 503 triggers a new 1s/3s/7s chain) AND `fetch` is called immediately for both stats and submissions

**Implementation**: Extend `src/app/queue/__tests__/QueuePageClient.test.tsx` (or .sse.test.tsx for the SSE case). Use `vi.useFakeTimers()`, `vi.spyOn(global, "fetch")`. Render via `@testing-library/react`. Run — must fail.

---

### T-005: GREEN Layer A — bump DB timeout to 800ms
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01 | **Status**: [x] completed

**Test Plan**: T-001 must pass after this change.

**Implementation**: In `src/lib/queue/queue-stats-cache.ts`, change `const DB_STATS_FALLBACK_TIMEOUT_MS = 150;` to `const DB_STATS_FALLBACK_TIMEOUT_MS = 800;`. Update the inline comment to explain the cold-Neon rationale.

---

### T-006: GREEN Layer B — stats route returns 503 on empty
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04 | **Status**: [x] completed

**Test Plan**: T-002 must pass after this change.

**Implementation**: In `src/app/api/v1/submissions/stats/route.ts`, after `const snapshot = await readQueueStatsSnapshot();`, branch:

```ts
const isEmpty = snapshot.source === "empty";
const status = isEmpty ? 503 : 200;
const headers: Record<string, string> = {
  "X-Queue-Stats-Source": snapshot.source,
  "X-Queue-Stats-Freshness": snapshot.freshness,
};
if (isEmpty) headers["Retry-After"] = "5";
return NextResponse.json(clampSentinelForResponse(snapshot.stats), { status, headers });
```

Keep `clampSentinelForResponse` invocation unchanged so the body shape is identical.

---

### T-007: GREEN Layer C — SSR returns stats:null when degraded+zero
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x] completed

**Test Plan**: T-003 must pass after this change.

**Implementation**: In `src/app/queue/data.ts`:
1. Change `QueueInitialData.stats` type from `QueueStats` to `QueueStats | null`.
2. In `getQueueInitialDataSSR`, when computing the return object, set `stats: statsUnavailable ? null : stats` (both the `chosenData` branch and the no-data fallback branch). The existing `statsUnavailable = !!stats.degraded && stats.total === 0` predicate is reused.
3. Update any helpers that consume `stats.total` for branching (e.g., `chooseBootCandidates(stats, ...)`) to handle the null case — the existing `statsUnavailable` predicate already triggers the `["all"]` fallback path, so this is a refactor not a behavior change. Verify by reading the function.

---

### T-008: GREEN Layer D — client em-dash placeholders + retry chain
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05 | **Status**: [x] completed

**Test Plan**: T-004 must pass after this change.

**Implementation**: In `src/app/queue/QueuePageClient.tsx`:

1. Type `stats` state as `QueueStats | null`. Initialize from `initialData.stats` (which can be null).
2. Keep `EMPTY_STATS` constant only for the SSE optimistic-delta path (where `prev` exists).
3. Add `RETRY_DELAYS_MS = [1000, 3000, 7000] as const` and refs `retryAttemptRef`, `retryTimerRef`.
4. Add `clearPendingRetry` and `scheduleRetry` callbacks (per `plan.md` sketch).
5. Modify `fetchStats`: on `res.status === 503`, call `scheduleRetry` and return. On `res.ok`, if `json.total > 0 || !json.degraded` proceed to setStats AND reset `retryAttemptRef.current = 0` AND call `clearPendingRetry`. Else (zero+degraded body), `scheduleRetry`.
6. In SSE `submission_created` handler, reset `retryAttemptRef.current = 0` and call `clearPendingRetry` BEFORE the existing `fetchQueueRef/fetchStatsRef` calls.
7. Add `useEffect(() => () => clearPendingRetry(), [clearPendingRetry])` for unmount cleanup.

In `src/app/queue/QueuePageComponents.tsx` (`StatCard`):

1. Type `value` prop as `number | null`.
2. In render, if `value === null` show `—` (em-dash, U+2014) using existing `var(--text-faint)` color; otherwise format `value.toLocaleString()`.

In the Avg Score StatCard at `QueuePageClient.tsx:681-686`, pass `value={stats?.avgScore ?? null}` and `color={stats && stats.avgScore > 0 ? STATUS_VARS[scoreIntent(stats.avgScore)].text : undefined}`.

In the 5 main StatCards (lines 663-680), pass `value={stats ? stats[key] : null}` and `highlight={stats ? stats[key] > 0 : false}`.

---

### T-009: Run full Vitest suite (vskill-platform)
**User Story**: ALL | **Satisfies ACs**: success criteria + AC-US3-03 | **Status**: [x] completed

**Test Plan**:
- `npx vitest run` from `repositories/anton-abyzov/vskill-platform`
- All new tests (T-001..T-004) pass
- All existing queue/* tests pass without modification (the type widening from `QueueStats` to `QueueStats | null` is the only breaking change; existing tests that pass `stats: <object>` to QueuePageClient continue to work because the type is wider)

**Implementation**: Run command. If failures, fix until clean.

---

### T-010: Refactor + simplify pass
**Status**: [x] completed

**Test Plan**: All vitest tests still green after refactor.

**Implementation**: Re-read the diff. Look for:
- Duplicated `EMPTY_STATS` references that can collapse.
- Dead code (e.g. EMPTY_STATS may now be unused if SSE delta path doesn't need it).
- Comment hygiene — only WHY comments, no WHAT.
- Type safety — no `as` casts unless necessary.

---

### T-011: Commit + push to main
**Status**: [x] completed

**Test Plan**: `git status` shows clean tree after commit; `git push` succeeds; CI build passes.

**Implementation**:
- `cd repositories/anton-abyzov/vskill-platform`
- `git add` the changed files (queue-stats-cache.ts, stats/route.ts, queue/data.ts, queue/QueuePageClient.tsx, queue/QueuePageComponents.tsx, all new + extended __tests__)
- Commit message: `0757: queue counters never show fake zeros on cold workers`
- `git push origin main`

---

### T-012: Post-deploy live verification
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US4-02, AC-US4-03 | **Status**: [x] completed

**Test Plan**:
- 20 cache-busted curl probes of `/queue?_cb=N` HTML — zero `Total=0  Published=0` simultaneous occurrences
- 10 probes of `/api/v1/submissions/stats` — count `source=empty` rate; expect ≤ 5% (down from observed ~20%)
- 5 probes timing the stats endpoint — P95 ≤ 1s

**Implementation**: Run shell loops from spec.md "Verification" section. If still seeing zero counters or empty rate >5%, escalate (rollback or follow-up increment).

---

## Sequencing

T-001..T-004 in parallel (RED — independent test files). Then T-005..T-008 in parallel (GREEN per layer; no shared files). Then T-009 (suite verification). Then T-010..T-012 sequentially.
