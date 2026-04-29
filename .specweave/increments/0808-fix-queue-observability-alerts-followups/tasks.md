# Tasks: Fix queue observability alerts follow-ups (0807 judge-llm)

## Task Notation

- `[T###]`: Task ID
- `[ ]` not started · `[x]` completed
- TDD phases: `[RED]` write failing test → `[GREEN]` minimal implementation → `[REFACTOR]` clean up

---

## Phase 1: J-001 — Info-severity dedup gate

### T-001: TC-046 — failing test for info dedup [RED]
**AC**: AC-US1-03
**File**: `repositories/anton-abyzov/vskill-platform/src/app/api/v1/internal/alerts-evaluator/__tests__/route.test.ts` (append)
**Test plan**:
- Given fallback counts `{claude: 15, ollama: 15}` (over threshold) and a fresh KV.
- When POST is invoked twice in sequence with the same `X-Internal-Key`.
- Then first call: `body.counts.info === 1` AND `kvStore.get("alerts:dedup:llm-fallback-spike:<today>")` is set.
- Then second call: `body.counts.info === 0`, `body.counts.suppressed >= 1`, AND `kvStore.get("alerts:digest:count:llm-fallback-spike").value === "1"`.
**Status**: [x] completed

### T-002: J-001 gate info-severity through shouldFire() [GREEN]
**AC**: AC-US1-01, AC-US1-02
**File**: `src/app/api/v1/internal/alerts-evaluator/route.ts:222-229`
**Test**: Given T-001 RED → When info branch checks `shouldFire(alertsKV, alert.kind, alert.key)` before `recordFired()` → Then TC-046 passes (and existing TC-037 still passes).
**Status**: [x] completed

---

## Phase 2: J-005 — Drain-window cleanup

### T-003: TC-047 — failing test for env-driven drain window [RED]
**AC**: AC-US5-03
**File**: `src/app/api/v1/internal/alerts-evaluator/__tests__/route.test.ts` (append)
**Test plan**:
- Given `process.env.ALERT_DRAIN_WINDOW_HOURS = "3"` and three KV buckets `qm:<H>`, `qm:<H-1>`, `qm:<H-2>` with `{processed: 5, failed: 1}` each.
- When POST is invoked.
- Then mockKV.get is called with all three bucket keys (in reverse-chronological order) AND the drain-stalled detector receives `drainLast1h = 18` (3 × (5+1)).
**Status**: [x] completed

### T-004: J-005 env-driven drain window [GREEN]
**AC**: AC-US5-01, AC-US5-02
**File**: `src/app/api/v1/internal/alerts-evaluator/route.ts:39-53`
**Test**: Given T-003 RED → When loop reads `envInt("ALERT_DRAIN_WINDOW_HOURS", 1)` buckets with one inline comment naming the env var → Then TC-047 passes; TC-007/008/009 (default windowHours=1) still pass.
**Status**: [x] completed

---

## Phase 3: J-002 — Test-only ring-buffer seed endpoint

### T-005: _test-seed route tests [RED]
**AC**: AC-US2-03
**File**: `src/app/api/v1/admin/alerts/_test-seed/__tests__/route.test.ts` (NEW)
**Test plan**:
- TC-048 — Given `ALLOW_ALERT_SEED` unset, When POST runs (with admin cookie), Then 403 with `{error: "disabled"}`.
- TC-049 — Given flag set but no admin auth, When POST runs, Then forwards `requireAdmin`'s 401/403.
- TC-050 — Given flag set + admin cookie + `{kind:"heartbeat-stale"}`, When POST runs, Then 200 + `{seeded:true,id}` + `kvStore.get("alerts:recent")` contains an alert with that id.
**Status**: [x] completed

### T-006: _test-seed route impl [GREEN]
**AC**: AC-US2-01, AC-US2-02
**File**: `src/app/api/v1/admin/alerts/_test-seed/route.ts` (NEW)
**Test**: Given T-005 RED → When POST handler implemented per plan.md → Then TC-048..TC-050 pass.
**Status**: [x] completed

### T-007: e2e admin-alerts.spec.ts — seed flow [GREEN]
**AC**: AC-US2-04
**File**: `tests/e2e/admin-alerts.spec.ts:84-106`
**Test**: Given `ALLOW_ALERT_SEED=1` in CI env → When test seeds via `_test-seed` and runs ack flow → Then panel shows seeded alert, ack button moves it to `[data-testid="alerts-acknowledged-section"]`. Local-dev fallback: `test.skip` once if `_test-seed` returns 403.
**Status**: [x] completed

---

## Phase 4: J-003 — Spec wording alignment

### T-008: Update 0807 AC-US3-05 wording
**AC**: AC-US3-01
**File**: `.specweave/increments/0807-queue-observability-alerts/spec.md:71`
**Test**: Given the line "09:00 / 13:00 / 17:00 / 21:00 UTC" → When edited to "00:00 / 06:00 / 12:00 / 18:00 UTC" with an inline `(see 0808 for code/spec alignment)` note → Then `grep -n "06:00" spec.md` returns the line; code unchanged.
**Status**: [x] completed

---

## Phase 5: J-004 — RecentAlertsPanel RTL tests

### T-009: RecentAlertsPanel.test.tsx [RED+GREEN]
**AC**: AC-US4-01, AC-US4-02, AC-US4-03
**File**: `src/app/admin/queue/__tests__/RecentAlertsPanel.test.tsx` (NEW)
**Test plan**:
- TC-051 (empty): mock GET `/api/v1/admin/alerts/recent` → `{alerts:[]}` → after `await screen.findByTestId("alerts-empty")` → assert visible.
- TC-052 (loading): mock GET as never-resolving → assert `Loading…` text visible immediately on mount.
- TC-053 (error): mock GET → 500 → after error settle → assert `[data-testid="alerts-error"]` text contains "HTTP 500".
- TC-054 (grouping): mock GET → 1 critical + 1 warning + 1 info → assert all three `alerts-{sev}` sections render in `SEVERITY_ORDER`; counts pill shows `(3 active, 0 acknowledged)`.
- TC-055 (ack): mock GET (1st) → 1 alert; mock POST `/api/v1/admin/alerts/<id>/ack` → 200; mock GET (2nd) → same alert with `acknowledged:true`. Click `ack-btn-<id>`. Assert POST called with method POST + correct URL. After reload, assert row is under `[data-testid="alerts-acknowledged-section"]`.
**Status**: [x] completed

---

## Phase 6: Verification + deploy + commit

### T-010: vitest + tsc --noEmit on alerts paths
**AC**: success criteria #1, #2
**Cmd**: `npx vitest run src/lib/alerts src/app/api/v1/admin/alerts src/app/api/v1/internal/alerts-evaluator src/app/admin/queue` then `npx tsc --noEmit 2>&1 | grep -E "(alerts|email|RecentAlertsPanel|_test-seed)"`
**Status**: [x] completed

### T-011: Build + deploy to Cloudflare prod
**Cmd**: `rm -rf .open-next && npm run build && npm run build:worker && npm run deploy` then `echo 0 | npx wrangler secret put ALLOW_ALERT_SEED`
**Status**: [x] completed

### T-012: Production smoke (J-001 + J-003 + US-006 submission guarantee)
**AC**: AC-US6-01, AC-US6-02, AC-US6-03 + success criteria #3, #4
**Action**:
1. Seed `ai:fallback:claude:<today>` + `ai:fallback:ollama:<today>` KV values that sum > 20.
2. Wait two `*/10` cron ticks.
3. Confirm `alerts:digest:count:llm-fallback-spike` value is `"1"` (NOT incrementing) AND `alerts:dedup:llm-fallback-spike:<today>` is set.
4. Read `alerts:digest:fired:<window-start>` — confirm window-start matches `T(00|06|12|18):00Z` (J-003).
5. POST a fresh submission to `/api/v1/submissions` against a test repo; poll `state` every 5s; record elapsed seconds. Must be ≤ 300s for closure to succeed.
**Status**: [x] completed

### T-013: Commit + push (vskill-platform + umbrella)
**Cmd**: `git add` only the 0808-related files, `git commit`, `git push`. Same in the umbrella for `.specweave/increments/0808-*` files.
**Status**: [x] completed
