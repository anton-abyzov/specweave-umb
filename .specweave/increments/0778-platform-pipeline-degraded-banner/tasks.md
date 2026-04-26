# Tasks: Studio Bell — Surface Platform Pipeline Degraded State

## Phase 1 — Server proxy (US-001)

### T-001: RED — health endpoint contract + degraded gating
**User Story**: US-001 | **AC**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**Test Plan**: Vitest unit. Mock global `fetch` to return synthetic `submissions/stats` + `queue/health` payloads. Three table-driven cases:
  - Healthy → `{ degraded: false, reason: null, statsAgeMs: 5000, oldestActiveAgeMs: 30000 }`
  - `stats.degraded=true` → `{ degraded: true, reason: contains "platform reports degraded", ... }`
  - heartbeat 2h stale → `{ degraded: true, reason: contains "heartbeat stale" }`
  - oldest active 31d → `{ degraded: true, reason: contains "oldest active submission" }`
**File**: `src/eval-server/__tests__/api-platform-health.test.ts` (new).

### T-002: GREEN — implement /api/platform/health route
**User Story**: US-001 | **AC**: AC-US1-01, AC-US1-02, AC-US1-04 | **Status**: [x] completed
**Test Plan**: T-001 passes. In-memory 60s cache implemented; second call within window does NOT hit fetch (assert via mock call count).
**File**: `src/eval-server/api-routes.ts`.

### T-003: RED+GREEN — failure → safe fallback
**User Story**: US-001 | **AC**: AC-US1-03 | **Status**: [x] completed
**Test Plan**: Three failure cases — (a) AbortSignal timeout, (b) `fetch` rejects with TypeError, (c) malformed JSON. All return `{ degraded: false, reason: "platform-unreachable", statsAgeMs: 0, oldestActiveAgeMs: 0 }` and DO NOT throw.
**File**: same as T-001.

## Phase 2 — Client hook (US-001 wire)

### T-004: RED+GREEN — usePlatformHealth wraps useSWR with 60s TTL
**User Story**: US-001 | **AC**: AC-US1-04 | **Status**: [x] completed
**Test Plan**: Mock global `fetch` to return a fixed payload. Render the hook in a harness; assert the returned `data` matches and a second render within the TTL does NOT re-fetch.
**File**: `src/eval-ui/src/hooks/__tests__/usePlatformHealth.test.tsx` (new) + `src/eval-ui/src/hooks/usePlatformHealth.ts` (new).

## Phase 3 — UpdateBell amber state (US-002, US-003)

### T-005: RED — bell glyph + aria/title shift when degraded
**User Story**: US-002 | **AC**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Test Plan**: Render `<UpdateBell />` with `usePlatformHealth` mocked to `{ degraded: true, reason: "stats stale" }`. Assert the bell button's `title` matches the AC copy exactly, `aria-label` ends with `"platform crawler degraded"`, and the inner `svg` element has fill or `currentColor` resolving to `var(--color-own)`.
**File**: `src/eval-ui/src/components/__tests__/UpdateBell-degraded.test.tsx` (new).

### T-006: RED — dropdown banner renders with reason
**User Story**: US-003 | **AC**: AC-US3-01, AC-US3-02, AC-US3-04 | **Status**: [x] completed
**Test Plan**: Open the dropdown; assert a `[role="status"][aria-live="polite"]` element exists, contains "Platform crawler degraded" AND the mocked reason. Assert the existing "No updates available" or "X updates" line still renders below.
**File**: same as T-005.

### T-007: RED — healthy path is unchanged (regression gate)
**User Story**: US-002, US-003 | **AC**: AC-US2-04, AC-US3-03 | **Status**: [x] completed
**Test Plan**: Render with `degraded: false`. Assert NO `[role="status"]` banner, bell `aria-label` is the default, and no amber color in the glyph.
**File**: same as T-005.

### T-008: GREEN — implement degraded branch in UpdateBell
**User Story**: US-002, US-003 | **AC**: AC-US2-01..04, AC-US3-01..04 | **Status**: [x] completed
**Test Plan**: T-005, T-006, T-007 pass. Verify existing UpdateBell tests still pass (no regression on the loading/empty/non-empty paths).
**File**: `src/eval-ui/src/components/UpdateBell.tsx`.

## Phase 4 — Verify + sync

### T-009: Run vitest sweep
**User Story**: cross-cutting | **Status**: [x] completed
**Test Plan**: `npx vitest run src/eval-server/__tests__/api-platform-health.test.ts src/eval-ui/src/hooks/__tests__/usePlatformHealth.test.tsx src/eval-ui/src/components/__tests__/UpdateBell-degraded.test.tsx src/eval-ui/src/components/__tests__/UpdateBell.test.tsx` — all green.

### T-010: Sync living docs
**User Story**: cross-cutting | **Status**: [x] completed
**Test Plan**: `specweave sync-living-docs 0778-platform-pipeline-degraded-banner` exits 0.
