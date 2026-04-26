---
increment: 0752-search-index-dirty-flag-coverage
title: "Search-index dirty-flag on all state transitions"
type: bug
priority: P2
status: planned
created: 2026-04-26
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Search-index dirty-flag on all state transitions

## Overview

Centralize the `search-index:dirty` KV write into a single helper and call it on every Submission state transition (PUBLISHED, BLOCKED, REJECTED) so the every-2h cron rebuild reflects new and removed skills without a manual `POST /api/v1/admin/rebuild-search` trigger.

**Root cause** — 2026-04-26 incident: Anton's `skill-builder` reached `state=PUBLISHED` (score 95, CERTIFIED) at 05:52 UTC, but `vskill find skill-builder` did NOT surface it for ~50 minutes. Recovery required a manual rebuild (cursor-based, 73 shards, 113,240 skills, 15.5s).

**Three concrete defects identified by exploration:**
1. `src/lib/submission/publish.ts:671` already sets the dirty flag but is **missing `expirationTtl: 86400`** — inconsistent with the cron-handler write at `scripts/build-worker-entry.ts:165-167`.
2. **Multiple state-transition paths bypass `publishSkill()` entirely** and never set the flag: 3 BLOCKED transitions in `finalize-scan/route.ts` (lines 292/417/485), admin reject (`admin/submissions/[id]/reject/route.ts:99`), and bulk repo-block (`admin/repo-block/route.ts:116`).
3. **Race window in admin approve** — `admin/submissions/[id]/approve/route.ts:134` commits `state: PUBLISHED` via `updateMany`, but the dirty flag is only set later at line 193 inside `publishSkill()`. If `publishSkill()` throws after the DB write, the skill is PUBLISHED but the index never knows.

The fix centralizes the flag-write into `markSearchIndexDirty()`, plugs every gap, and adds a canary test that fails if a future contributor adds a `state: 'PUBLISHED' | 'BLOCKED' | 'REJECTED'` write without an adjacent flag-set call.

## User Stories

### US-001: Centralized dirty-flag helper (foundation) (P1)
**Project**: vskill-platform

**As a** maintainer of vskill-platform
**I want** a single helper `markSearchIndexDirty()` that writes `search-index:dirty=1` with TTL 86400 to `SEARCH_CACHE_KV`, resolving the binding via worker env then Cloudflare context fallback, and swallowing all failures
**So that** every state-transition path can reuse one tested code path instead of copy-pasting the env-resolve + put block

**Acceptance Criteria**:
- [ ] **AC-US1-01**: New file `src/lib/search-index/mark-dirty.ts` exports a single async function `markSearchIndexDirty(): Promise<void>`.
- [ ] **AC-US1-02**: Helper resolves `SEARCH_CACHE_KV` via `getWorkerEnv()` first, falling back to `getCloudflareContext({ async: true })` — same dual-path pattern currently inlined at `src/lib/submission/publish.ts:657-674`.
- [ ] **AC-US1-03**: Helper writes the value `'1'` to key `'search-index:dirty'` with `{ expirationTtl: 86400 }` (24h) — closes the TTL gap currently present in `publish.ts:671`.
- [ ] **AC-US1-04**: Helper is best-effort: wraps the resolution and put in try/catch and never throws; on failure, logs at debug level and returns. No caller ever sees a rejection.
- [ ] **AC-US1-05**: New file `src/lib/search-index/__tests__/mark-dirty.test.ts` covers exactly four cases: (a) KV resolved via worker env, put called with `expirationTtl: 86400`; (b) KV resolved via CF context fallback when worker env returns null; (c) both unavailable → no throw; (d) `KV.put` rejects → swallowed, no throw.

---

### US-002: `publishSkill()` uses helper + adds TTL (P1)
**Project**: vskill-platform

**As a** maintainer of vskill-platform
**I want** the inline env-resolve + put block at `src/lib/submission/publish.ts:657-674` replaced with a single `await markSearchIndexDirty()` call
**So that** the inline copy-paste is eliminated AND the missing `expirationTtl: 86400` is now baked in via the centralized helper

**Acceptance Criteria**:
- [ ] **AC-US2-01**: `src/lib/submission/publish.ts` no longer contains an inline `searchKv.put('search-index:dirty', '1')` invocation; the env-resolution code at lines 657-674 is removed.
- [ ] **AC-US2-02**: `publish.ts` imports `markSearchIndexDirty` from `@/lib/search-index/mark-dirty` (or relative path) and calls it exactly once, after the DB transaction commits, on the success path.
- [ ] **AC-US2-03**: All existing `publish.ts` tests continue to pass unchanged.
- [ ] **AC-US2-04**: A new (or updated) test in `src/lib/submission/__tests__/publish.test.ts` mocks `markSearchIndexDirty` and asserts it is invoked exactly once on a successful publish, and zero times when the surrounding DB transaction throws/rolls back (the helper must be called only after the commit).

---

### US-003: BLOCKED transitions in finalize-scan set the flag (P1)
**Project**: vskill-platform

**As a** user searching skills via `vskill find`
**I want** a previously-PUBLISHED skill that gets BLOCKED (blocklist hit, LLM-confirmed threat, or DCI violation) to disappear from search within the next 2h-aligned cron tick, not 2h+enrichment-touch later
**So that** harmful skills stop being discoverable promptly after the scanner blocks them

**Acceptance Criteria**:
- [ ] **AC-US3-01**: At `src/app/api/v1/internal/finalize-scan/route.ts` line 292 (blocklist BLOCKED transition), call `markSearchIndexDirty()` immediately after the `updateState(..., "BLOCKED", ...)` call, gated by a check that the prior state was `PUBLISHED` or `AUTO_APPROVED` (the only two states where the skill could already be in the search index).
- [ ] **AC-US3-02**: Same conditional `markSearchIndexDirty()` call added at line 417 (LLM-confirmed-threat BLOCKED transition).
- [ ] **AC-US3-03**: Same conditional `markSearchIndexDirty()` call added at line 485 (DCI-violation BLOCKED transition).
- [ ] **AC-US3-04**: The prior-state check is implemented by reading the submission's `state` value before the update and passing it (or the relevant boolean) into the conditional — no new query against the DB.
- [ ] **AC-US3-05**: Tests in `src/app/api/v1/internal/finalize-scan/__tests__/route.test.ts` assert the flag fires for each of the three paths when prior state is `PUBLISHED`, AND assert it does NOT fire when prior state is `RECEIVED` (skill never indexed → no need to invalidate).

---

### US-004: Admin reject sets the flag for PUBLISHED→REJECTED downgrades (P1)
**Project**: vskill-platform

**As a** user searching skills via `vskill find`
**I want** a previously-PUBLISHED skill that an admin rejects to disappear from search within the next 2h-aligned cron tick
**So that** admin-rejected content stops being discoverable without a manual rebuild

**Acceptance Criteria**:
- [ ] **AC-US4-01**: At `src/app/api/v1/admin/submissions/[id]/reject/route.ts` (~line 99), call `markSearchIndexDirty()` only when the submission's prior `state === "PUBLISHED"` (the downgrade case where the skill is currently in the index).
- [ ] **AC-US4-02**: When prior state is anything other than `PUBLISHED` (e.g., `RECEIVED → REJECTED` — first-time rejection of a never-published submission), the helper is NOT called.
- [ ] **AC-US4-03**: The conditional uses the prior state already read by the route (no extra DB roundtrip).
- [ ] **AC-US4-04**: Test in `src/app/api/v1/admin/submissions/[id]/reject/__tests__/route.test.ts` asserts the flag fires for `PUBLISHED → REJECTED` and does NOT fire for `RECEIVED → REJECTED`.

---

### US-005: Admin repo-block sets the flag once on bulk match (P1)
**Project**: vskill-platform

**As a** user searching skills via `vskill find`
**I want** a bulk repo-block to remove all matching PUBLISHED skills from search within the next 2h-aligned cron tick, with the dirty flag set exactly once regardless of how many skills the block matched
**So that** a single bulk-block does not waste KV ops by writing the flag N times

**Acceptance Criteria**:
- [ ] **AC-US5-01**: At `src/app/api/v1/admin/repo-block/route.ts` (~line 116), if the `updateMany` result indicates ANY rows that were previously `PUBLISHED` were affected, call `markSearchIndexDirty()` exactly once after the `updateMany` returns.
- [ ] **AC-US5-02**: When the `updateMany` matched zero rows, OR matched only non-PUBLISHED rows (no skills currently in the index), the helper is NOT called.
- [ ] **AC-US5-03**: The "any PUBLISHED row affected" check is implemented either by scoping the `updateMany` `where` clause to `state: 'PUBLISHED'` and using `count > 0`, or by querying the matched rows once before the update — whichever requires no additional KV calls.
- [ ] **AC-US5-04**: Test in `src/app/api/v1/admin/repo-block/__tests__/route.test.ts` asserts: (a) when `updateMany` reports 5 PUBLISHED rows blocked, helper is called exactly 1 time (not 5); (b) when `updateMany` reports 0 PUBLISHED rows, helper is NOT called.

---

### US-006: Admin approve belt-and-suspenders flag-set (P2)
**Project**: vskill-platform

**As a** maintainer of vskill-platform
**I want** the dirty flag set immediately after the `updateMany` at `src/app/api/v1/admin/submissions/[id]/approve/route.ts:134`, BEFORE the later `publishSkill()` call at line 193
**So that** the flag is set even if `publishSkill()` throws after the state was committed to PUBLISHED, closing the race window where the DB says PUBLISHED but the index never gets invalidated

**Acceptance Criteria**:
- [ ] **AC-US6-01**: At `src/app/api/v1/admin/submissions/[id]/approve/route.ts:134`, call `await markSearchIndexDirty()` immediately after the `updateMany` succeeds and before any subsequent code path that could throw.
- [ ] **AC-US6-02**: The later call to `publishSkill()` (which now also calls the helper internally per US-002) is allowed to set the flag a second time — double-set is documented as harmless and idempotent.
- [ ] **AC-US6-03**: Test in `src/app/api/v1/admin/submissions/[id]/approve/__tests__/route.test.ts` asserts: (a) on the success path, helper is observed to be called at least once (twice is acceptable); (b) when `publishSkill()` is mocked to throw AFTER the `updateMany` commits, the early helper call still fired (the flag is set even though publishSkill blew up).

---

### US-007: Architectural canary test (P2)
**Project**: vskill-platform

**As a** maintainer of vskill-platform
**I want** an automated test that fails CI if a future contributor adds a `state: 'PUBLISHED' | 'BLOCKED' | 'REJECTED'` write to a non-test source file without an adjacent `markSearchIndexDirty()` or `publishSkill()` call
**So that** silent regression of this fix is structurally impossible — anyone who adds a new state-transition path must also wire up the flag

**Acceptance Criteria**:
- [ ] **AC-US7-01**: New file `src/lib/search-index/__tests__/state-transition-coverage.test.ts` greps `src/` (excluding any path containing `__tests__`, `.test.ts`, or `scripts/build-worker-entry.ts` — the cron handler that consumes the flag, not produces it) for the three string patterns: `state: 'PUBLISHED'`, `state: 'BLOCKED'`, `state: 'REJECTED'` (and double-quote variants).
- [ ] **AC-US7-02**: For each match, the test reads a sliding window of the next 15 lines (within the same file) and asserts at least one of: a literal `markSearchIndexDirty(` substring OR a literal `publishSkill(` substring appears in that window.
- [ ] **AC-US7-03**: When any match fails the proximity check, the test fails with a clear message naming the offending `file:line` and the matched pattern, so the contributor knows exactly where to add the helper call.
- [ ] **AC-US7-04**: The test is purely string-based (no AST parsing, no TypeScript compiler usage) to keep it fast and dependency-free; it runs as a regular Vitest case under `npx vitest run`.
- [ ] **AC-US7-05**: The test passes after US-001 through US-006 are implemented — i.e., every existing PUBLISHED/BLOCKED/REJECTED write in the codebase already satisfies the proximity rule once this increment lands.

---

### US-008: Test coverage + live verification (P1)
**Project**: vskill-platform

**As a** maintainer of vskill-platform
**I want** all the new behavior covered by unit tests AND a live end-to-end verification on production after deploy
**So that** we have proof the fix actually closes the 2026-04-26 incident pattern, not just a green test suite

**Acceptance Criteria**:
- [ ] **AC-US8-01**: All new and modified Vitest tests pass via `npx vitest run` scoped to `src/lib/search-index src/lib/submission src/app/api/v1/internal/finalize-scan src/app/api/v1/admin/submissions src/app/api/v1/admin/repo-block`.
- [ ] **AC-US8-02**: `npx tsc --noEmit` reports zero errors in vskill-platform.
- [ ] **AC-US8-03**: The Cloudflare Worker is built (`npm run build:worker`) and deployed (`npx wrangler deploy`) from `repositories/anton-abyzov/vskill-platform`.
- [ ] **AC-US8-04**: A fresh test skill is submitted via `vskill submit anton-abyzov/<test-repo> --skill <test-name>`, and at the next 2h-aligned cron tick (`minute === 0 && hour % 2 === 0`), `wrangler tail` shows `[cron] search index rebuild completed in <Nms>: <total> skills, <shards> shards` and `vskill find <test-name>` returns the skill — without any manual `POST /api/v1/admin/rebuild-search`.
- [ ] **AC-US8-05**: The same test skill is then blocked via the admin repo-block route; at the next 2h-aligned tick, `vskill find <test-name>` no longer returns it — again without manual rebuild.
- [ ] **AC-US8-06**: Manual verification steps and observed timestamps/log lines are recorded at `reports/manual-verification.md` inside the increment folder.

## Functional Requirements

### FR-001: Single source of truth for the dirty flag
All KV writes of `search-index:dirty=1` from application code (i.e., outside `scripts/build-worker-entry.ts`, which is the cron consumer/producer pair) must go through `markSearchIndexDirty()`. The helper is the only place where the key, value, and TTL constants are written. Inline copy-pastes of the put-with-env-resolution pattern are forbidden going forward (enforced softly by code review and structurally by US-007).

### FR-002: Best-effort, never-throws semantics
The helper must NEVER throw under any circumstance — KV unavailable, env-resolution failure, put rejection, malformed binding. All callers can `await markSearchIndexDirty()` without a try/catch wrapper. This matches the spirit of the existing `publish.ts:657-674` block, which intentionally swallows errors so a transient KV blip doesn't roll back a successful publish.

### FR-003: Conditional invocation on downgrades
For BLOCKED and REJECTED transitions, the helper is called ONLY when the prior state could have placed the skill in the search index — i.e., prior state ∈ `{PUBLISHED, AUTO_APPROVED}` for BLOCKED, and prior state === `PUBLISHED` for REJECTED. This avoids wasteful KV writes on first-time-rejected submissions that were never indexed.

### FR-004: Idempotent double-set on admin approve
The admin approve path will set the flag twice on the success case (once at line 134 belt-and-suspenders, once inside `publishSkill()` at line 193). This is acceptable: a second `KV.put` of the same value is a ~1ms operation and the cron rebuild only ever cares whether the flag is `1` at the time of the next tick, not how many times it was written.

### FR-005: Cron handler stays untouched
`scripts/build-worker-entry.ts:165-167` (cron's own dirty-flag write) and `scripts/build-worker-entry.ts:194-220` (cron's read+rebuild+delete loop) are NOT modified. The cron's existing flag-write at line 165-167 stays as a backup signal for enrichment-only changes.

## Success Criteria

- **Time-to-index for new skills**: A freshly-PUBLISHED skill appears in `vskill find` within at most 2h-after-publish (one cron tick). Today's worst-case is unbounded (gated on a future enrichment touch). Measured by the live verification in AC-US8-04.
- **Time-to-deindex for blocked skills**: A previously-PUBLISHED skill that gets BLOCKED or REJECTED disappears from `vskill find` within at most 2h-after-block. Today's worst-case is unbounded. Measured by AC-US8-05 and the analogous block flow.
- **Zero manual rebuilds required for the next 30 days post-deploy** for normal publish/block/reject flows. (Measured by absence of `POST /api/v1/admin/rebuild-search` calls in worker logs.)
- **CI canary test prevents regression**: US-007's coverage test fails any future PR that adds a new state-transition write without the helper.

## Out of Scope

- **Tightening the 2h cron cadence** — the every-2h-at-minute-0 schedule is a deliberate KV-ops budget; revisiting it is a separate increment if needed.
- **Re-architecting search-index sharding** — the 73-shard, 113K-skill cursor-based rebuild stays as-is.
- **Watchdog territory (0748 increment)** — already shipped, separate concern.
- **Investigating the deeper question of why the 06:00 UTC cron rebuild on 2026-04-26 didn't pick up Anton's skill** (could be transient KV consistency or Postgres read-replica lag). The structural fix (cover all paths + TTL) makes the dirty flag set redundantly enough that a single transient miss won't matter; if we still see misses after this lands, file a separate investigation increment.
- **Replacing the cron's own dirty-flag write at `scripts/build-worker-entry.ts:165-167`** — left as a backup signal.

## Dependencies

- **Cloudflare Workers KV binding** `SEARCH_CACHE_KV` — already provisioned and bound; no infra changes.
- **Cron handler** at `scripts/build-worker-entry.ts:194-220` — already reads the flag, rebuilds the index, and deletes the flag on success. No changes required.
- **Existing test infrastructure**: Vitest is configured in vskill-platform; the mock-KV pattern from `src/app/api/v1/admin/submissions/[id]/approve/__tests__/route.test.ts:180-186` is reused for the new conditional-set tests.
- **No new npm packages, no schema changes, no env vars.**
