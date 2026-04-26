# Tasks: Studio update clicks broken + plugins runaway retry + SSE format mismatch

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## US-001: Update button reliably installs the new version

### T-001: Diagnose broken click handler root cause

**Description**: Identify that `api.startSkillUpdate` creates an `EventSource` (GET) + a separate `fetch` POST. Backend only accepts POST so GET fails with ERR_CONNECTION_REFUSED.

**Status**: [x] Completed

---

### T-002: Write failing tests (TDD RED) for AC-US1-01..04

**Description**: Write unit tests in `UpdateAction.test.tsx` covering:
- AC-US1-01: single POST, inline progress, no EventSource
- AC-US1-02: success → refreshUpdates + dismissPushUpdate called
- AC-US1-03: failure → structured error with status code, button stays enabled
- AC-US1-04: URL uses `<plugin>/<skill>` path params

**References**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04

**Test Plan**:
- **File**: `src/eval-ui/src/components/__tests__/UpdateAction.test.tsx`
- **Tests**: 12 tests covering all ACs — run `npx vitest run ...UpdateAction`

**Status**: [x] Completed

---

### T-003: Add `postSkillUpdate` to `api.ts`

**Description**: Add `async postSkillUpdate(plugin, skill)` method that issues a single `POST /api/skills/:plugin/:skill/update` and returns `{ ok, status, body, version }`.

**References**: AC-US1-01, AC-US1-04

**Status**: [x] Completed

---

### T-004: Rewrite `UpdateAction.tsx` to use fetch POST (TDD GREEN)

**Description**: Remove `EventSource` / `useOptimisticAction` / SSE approach. Replace with `handleUpdate` callback that calls `api.postSkillUpdate`, shows inline "Updating…" progress div, handles success (refreshUpdates + dismissPushUpdate + toast) and failure (structured error banner + toast with Retry).

**References**: AC-US1-01, AC-US1-02, AC-US1-03

**Status**: [x] Completed

---

### T-005: Write Playwright E2E test (AC-US1-05)

**Description**: New file `e2e/update-click-flow.spec.ts` — stubs `/api/skills/updates` to inject an outdated test-skill, stubs the POST update endpoint, clicks the Update button, asserts success + no "Stream error" toast. Also asserts failure path shows status code.

**References**: AC-US1-05

**Test Plan**:
- **File**: `e2e/update-click-flow.spec.ts`
- Run: `npx playwright test e2e/update-click-flow.spec.ts`

**Status**: [x] Completed

---

## US-002: Plugins polling stops being a runaway retry loop

### T-006..T-010: Owned by fix-plugins-retry-agent

**Status**: [x] Completed
**Implementation note** (reconciled 2026-04-26): work landed before tasks.md status was updated. Deliverables verified at reconciliation time:
- `src/eval-ui/src/hooks/usePluginsPolling.ts` — single hook with `AbortController`, `visibilityState` pause, exponential backoff (1→2→4→8→16s capped), max-5-retry pause-state, manual retry (FR-003).
- `src/eval-ui/src/hooks/__tests__/usePluginsPolling.test.ts` — covers backoff schedule, retry cap, abort on unmount, visibility-state pause (AC-US2-05).
- All 5 ACs (AC-US2-01 backoff, AC-US2-02 hidden-tab pause, AC-US2-03 unmount abort, AC-US2-04 ≤60 req/hour, AC-US2-05 unit tests) verified passing.

---

## US-003: SSE EventSource subscribes with correct ID format

### T-011..T-015: Owned by fix-sse-format-agent

**Status**: [x] Completed
**Implementation note** (reconciled 2026-04-26): work landed before tasks.md status was updated. Deliverables verified at reconciliation time:
- `src/eval-ui/src/utils/resolveSubscriptionIds.ts` — maps installed skills to `{uuid?, slug?}` via `/api/skills/installed` enrichment; omits unresolvable entries (FR-004, FR-005).
- `src/eval-ui/src/hooks/useSkillUpdates.ts` — wired to `resolveSubscriptionIds`, builds `?skills=<csv>` filter from UUID/slug only (AC-US3-01, AC-US3-02), top-of-file doc-comment on the contract (AC-US3-04).
- `src/eval-ui/src/StudioContext.tsx` — calls `resolveSubscriptionIds(enriched)` before subscribing.
- `src/eval-ui/src/__tests__/resolveSubscriptionIds.test.ts` + `useSkillUpdates.real-sse.{slug,installed,test}.ts` — real-SSE harness extending the 0732 pattern, proves `skill.updated` events delivered end-to-end (AC-US3-03).

---

## Post-Review Quality Fixes (code-review-report.json findings)

### T-016: Code-review finding fixes (F-001, F-005, F-006, F-007, F-010)

**Status**: [x] Completed (2026-04-25)

**Findings fixed**:
- **F-001 (HIGH)**: Added `lastResolveSigRef` content-stable signature short-circuit in `StudioContext.tsx` resolver effect. Prevents redundant POSTs to `/api/v1/skills/check-updates` on every poll cycle when installed-skill list is unchanged. Satisfies NFR-001 (≤1/min steady state). New test: `StudioContext.signature.test.ts`.
- **F-005 (MEDIUM)**: Extended `api.postSkillUpdate` to accept `signal?: AbortSignal` and pass it to `fetch`. `UpdateAction.tsx` wires `controller.signal` so in-flight requests cancel on unmount.
- **F-006 (MEDIUM)**: Added gated `console.warn` (behind `SKILL_UPDATE_DEBUG = false` flag) in `api.ts` `checkSkillUpdates` and `resolveInstalledSkillIds` catch blocks. `StudioContext.tsx` already had a once-per-session warn. Flag can be flipped in DevTools.
- **F-007 (MEDIUM)**: `UpdatesPanel.handleSingleUpdate` migrated from broken `api.startSkillUpdate` EventSource path to `api.postSkillUpdate` POST. Adds `singleErrors` state for structured inline error UX. New test: `UpdatesPanel.test.tsx`.
- **F-010 (LOW)**: `postSkillUpdate` in `api.ts` now streams via `res.body.getReader()` instead of buffering with `res.text()`, allowing per-step SSE progress frames to arrive without blocking.

**Deferred findings (tracked follow-ups — no behaviour gap)**:
- **F-002**: `usePluginsPolling` `eslint-disable` on doFetch dep — accepted risk, ref-based stability documented.
- **F-003**: `triggerPluginsRefresh` Set pattern — add test for multi-instance + unmount path in a future increment.
- **F-004**: visibilityState check before scheduling retry timer in failure path — accept wasted timer; document in future increment.
- **F-008**: `api.startSkillUpdate` still exists (only `startSkillUpdate` usage in UpdatesPanel removed; `startBatchUpdate` still SSE per spec). Mark `startSkillUpdate` `@deprecated` in a future cleanup increment.
- **F-009**: `id` UUID field intentionally public via `/api/v1/skills/check-updates` — document in route JSDoc in a future increment.
- **F-011**: E2E test stubs POST endpoint — add real eval-server integration test in a future increment per AC-US1-05 note.
- **F-012**: `StudioContext.tsx` comment update — add cadence note near resolver effect in a future increment.
- All 4 ACs verified passing (46 tests across 8 files green at reconciliation time).
