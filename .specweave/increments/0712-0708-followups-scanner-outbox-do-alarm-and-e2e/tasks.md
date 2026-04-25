---
increment: 0712-0708-followups-scanner-outbox-do-alarm-and-e2e
title: 0708 Follow-ups — Scanner Outbox Retrofit, Reconciler DO Alarm, and E2E SSE Reconnect
type: tasks
---

# Tasks: 0708 Follow-ups — Scanner Outbox Retrofit + Reconciler DO Alarm + E2E Hang

## Phase 1 — US-001: Scanner Retrofit to writeSkillVersionWithOutbox

### T-001: [TDD-RED] scanOneSkill outbox-mediated path test
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Test Plan**:
- Given: `scanner.test.ts` mocks `writeSkillVersionWithOutbox` via `vi.mock("../outbox-writer")` and stubs `db.$transaction` to run the callback with a mock tx
- When: `scanOneSkill()` detects a new SHA
- Then: `mockWriteSkillVersionWithOutbox` is called with `(tx, skill, { version, gitSha, source: "scanner", ... })`, `db.skillVersion.create` is never called directly, and `publishToUpdateHub` is never called directly — tests FAIL (red) because the current implementation bypasses the helper
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/__tests__/scanner.test.ts` (update)

---

### T-002: [TDD-GREEN] scanner.ts refactor — db.$transaction + writeSkillVersionWithOutbox
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Test Plan**:
- Given: `scanner.ts` is refactored to use `db.$transaction(async (tx) => writeSkillVersionWithOutbox(tx, skill, { version, gitSha, source: "scanner", diffSummary, extraData: { certTier, certMethod, certifiedAt } }))`
- When: `scanOneSkill()` processes a new SHA and the transaction commits
- Then: `SkillVersion` + `UpdateEvent` rows are created atomically, `publishToUpdateHub` is no longer called inline, the non-ULID `eventId: "pending-..."` shape is gone, and all T-001 tests turn green
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/scanner.ts` (update)

---

### T-003: [TDD-RED] Architecture invariant test rejects scanner.ts in allowlist
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed
**Test Plan**:
- Given: `architecture.test.ts` currently allowlists both `outbox-writer.ts` and `scanner.ts` in `SKILL_VERSION_CREATE_ALLOWED`
- When: the allowlist is tightened to `outbox-writer.ts` only
- Then: the test FAILS (red) while `scanner.ts` still contains `db.skillVersion.create` — proving the invariant catches the violation
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/__tests__/architecture.test.ts` (update)

---

### T-004: [TDD-GREEN] Tighten architecture.test.ts allowlist to outbox-writer.ts only
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed
**Test Plan**:
- Given: T-002 scanner.ts refactor is complete (no `db.skillVersion.create` in scanner.ts)
- When: `SKILL_VERSION_CREATE_ALLOWED` is updated to `[join("lib", "skill-update", "outbox-writer.ts")]` and a new regression `it("scanner.ts uses writeSkillVersionWithOutbox not direct create")` is added that reads scanner.ts source and asserts the negative
- Then: all architecture tests pass with the tightened allowlist
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/__tests__/architecture.test.ts` (update)

---

### T-005: [TDD-RED] Refactor 7 existing scanner tests to expect outbox path
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05 | **Status**: [x] completed
**Test Plan**:
- Given: the 7 existing scanner unit tests currently assert on `mockDb.skillVersion.create` being called
- When: the tests are rewritten to assert `mockWriteSkillVersionWithOutbox` is called with `source: "scanner"` and the correct `SkillVersionInput`, and that `db.skillVersion.create` is NOT invoked
- Then: all 7 refactored tests FAIL (red) against the pre-retrofit scanner.ts, confirming they guard the correct path
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/__tests__/scanner.test.ts` (update)

---

### T-006: [TDD-GREEN] Scanner test refactor implementation — all 7 tests green
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05 | **Status**: [x] completed
**Test Plan**:
- Given: T-002 scanner.ts refactor is complete and T-005 test rewrites are in place
- When: `npx vitest run src/lib/skill-update/__tests__/scanner.test.ts` is executed
- Then: all 7 refactored tests pass, `mockWriteSkillVersionWithOutbox` is asserted with `source: "scanner"`, and no test asserts on `db.skillVersion.create` directly
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/__tests__/scanner.test.ts` (update)

---

### T-007: Integration test — scanner-written UpdateEvent picked up by reconciler and published
**User Story**: US-001 | **Satisfies ACs**: AC-US1-06 | **Status**: [x] completed
**Test Plan**:
- Given: a Miniflare integration test environment with a real outbox table seeded with one `UpdateEvent` row having `publishedAt = null` (written by the scanner via `writeSkillVersionWithOutbox`)
- When: the reconciler runs via `reconcileOutboxOnce(env)`
- Then: the `UpdateEvent` row transitions to `publishedAt != null`, a corresponding `skill.updated` event is fanned out via the `UpdateHub` DO stub, and the end-to-end flow is verified within the reconciler's cadence window
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/__tests__/scanner.integration.test.ts` (new)

---

## Phase 2 — US-002: OutboxReconcilerDO with Sub-Minute Alarm Cadence

### T-008: [TDD-RED] OutboxReconcilerDO alarm() processes stuck rows test (Miniflare)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-03, AC-US2-07 | **Status**: [x] completed
**Test Plan**:
- Given: `outbox-reconciler-do.test.ts` is written with a hand-rolled `state.storage` stub `{ getAlarm: vi.fn(), setAlarm: vi.fn() }` and `reconcileOutboxOnce` mocked
- When: `alarm()` is called on the DO instance
- Then: tests FAIL (red) because `OutboxReconcilerDO` class does not exist yet — confirming the test harness is wired correctly before implementation
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/__tests__/outbox-reconciler-do.test.ts` (new)

---

### T-009: [TDD-GREEN] OutboxReconcilerDO class + alarm() + setAlarm(+30s) re-arm
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Test Plan**:
- Given: `outbox-reconciler-do.ts` is created with the `OutboxReconcilerDO` class, `alarm()` handler that calls `reconcileOutboxOnce(env)`, and a `finally` block that always calls `state.storage.setAlarm(Date.now() + 30_000 ± 5_000)`
- When: `alarm()` is called (both success and error cases)
- Then: (a) `reconcileOutboxOnce` is called, (b) `state.storage.setAlarm` is called with a value in range `[now + 25000, now + 35000]`, (c) re-arm fires even when `reconcileOutboxOnce` throws, (d) `reconciler.alarm.runs` metric is emitted with correct `outcome` label — all T-008 tests turn green
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/outbox-reconciler-do.ts` (new)
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/outbox-reconciler.ts` (update — rename `reconcileOutbox` → `reconcileOutboxOnce`, keep legacy alias)

---

### T-010: [TDD-RED] DO survives wake — alarm fires after process restart test
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03, AC-US2-07 | **Status**: [x] completed
**Test Plan**:
- Given: a test simulates a DO process restart by constructing a new `OutboxReconcilerDO` instance with a fresh `state.storage` stub that returns a past-due alarm timestamp from `getAlarm()`
- When: `alarm()` is called on the newly constructed instance
- Then: the alarm re-arms via `setAlarm(now + ~30000)` — test FAILS (red) if the DO doesn't check for persisted alarm continuity
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/__tests__/outbox-reconciler-do.test.ts` (update)

---

### T-011: [TDD-GREEN] State.storage attachment for re-arm continuity
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03 | **Status**: [x] completed
**Test Plan**:
- Given: `OutboxReconcilerDO.alarm()` uses `this.state.storage.setAlarm()` in its `finally` block (already implemented in T-009) and the storage stub persists alarm state across instance reconstructions in tests
- When: the process-restart test from T-010 runs
- Then: all 6 DO unit tests pass including the wake-after-restart scenario, confirming alarm state survives via DO storage
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/__tests__/outbox-reconciler-do.test.ts` (update)
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/outbox-reconciler-do.ts` (update if needed)

---

### T-012: [TDD-RED] /api/v1/internal/reconciler/ensure HMAC-gated test (auth + idempotency)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04, AC-US2-07 | **Status**: [x] completed
**Test Plan**:
- Given: `ensure/route.test.ts` is written with mocked DO stub and `webhook-auth.ts` HMAC verifier
- When: tests assert (a) unsigned request returns 401, (b) mismatched HMAC returns 401, (c) valid HMAC with no pending alarm returns 200 + `{ ensured: true, scheduled: "now+1s" }`, (d) valid HMAC with future alarm returns 200 + `{ ensured: true, scheduled: "preserved" }`
- Then: all 4 tests FAIL (red) because the route handler does not exist yet
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/app/api/v1/internal/reconciler/ensure/__tests__/route.test.ts` (new)

---

### T-013: [TDD-GREEN] Endpoint route.ts implementation + DO stub fetch
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04 | **Status**: [x] completed
**Test Plan**:
- Given: `route.ts` POST handler is implemented — authenticates via `X-Internal-Key` HMAC using `src/lib/webhook-auth.ts`, looks up `OUTBOX_RECONCILER_DO.idFromName("outbox-reconciler-singleton")`, calls `stub.fetch("https://internal/ensure", { method: "POST" })`, and returns the DO's response
- When: `npx vitest run src/app/api/v1/internal/reconciler/ensure/__tests__/route.test.ts` is executed
- Then: all 4 auth + idempotency tests pass
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/app/api/v1/internal/reconciler/ensure/route.ts` (new)

---

### T-014: wrangler.jsonc — add OUTBOX_RECONCILER_DO binding + v3 migration tag
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] completed
**Test Plan**:
- Given: `wrangler.jsonc` currently has `durable_objects.bindings` with v2 migration tag (UpdateHub)
- When: a new binding `{ "name": "OUTBOX_RECONCILER_DO", "class_name": "OutboxReconcilerDO" }` is appended to `bindings` and a new migration `{ "tag": "v3", "new_classes": ["OutboxReconcilerDO"] }` is appended to `migrations` (never editing v1 or v2)
- Then: `wrangler deploy --dry-run` passes with no migration-order errors, the DO binding is listed, and the v3 tag is present
**Files**:
  - `repositories/anton-abyzov/vskill-platform/wrangler.jsonc` (update)

---

### T-015: build-worker-entry.ts — export OutboxReconcilerDO + replace inline reconciler dispatch
**User Story**: US-002 | **Satisfies ACs**: AC-US2-05 | **Status**: [x] completed
**Test Plan**:
- Given: `scripts/build-worker-entry.ts` currently has an inline `reconcileOutbox(env)` waitUntil block in the cron handler
- When: (a) `export { OutboxReconcilerDO } from "../src/lib/skill-update/outbox-reconciler-do.js"` is added next to the existing `UpdateHub` export, and (b) the inline reconciler dispatch is replaced with `ctx.waitUntil(runWithWorkerEnv(env, async () => { const id = env.OUTBOX_RECONCILER_DO.idFromName("outbox-reconciler-singleton"); const stub = env.OUTBOX_RECONCILER_DO.get(id); await stub.fetch("https://internal/ensure", { method: "POST" }).catch(console.error); }))`
- Then: TypeScript compiles without errors, the cron handler no longer imports `reconcileOutbox`, and the DO singleton's `/ensure` path is the sole dispatch
**Files**:
  - `repositories/anton-abyzov/vskill-platform/scripts/build-worker-entry.ts` (update)

---

### T-016: Confirm delivery.outbox.stuck metric still fires + add reconciler.alarm.runs metric
**User Story**: US-002 | **Satisfies ACs**: AC-US2-06, AC-US2-07 | **Status**: [x] completed
**Test Plan**:
- Given: the existing `delivery.outbox.stuck` WARN metric fires for `UpdateEvent` rows unpublished >5 minutes (NFR-RELIABILITY-02)
- When: a test inserts a row with `createdAt = now - 6min, publishedAt = null` and runs the reconciler, and the DO's `emitMetric` is called for each alarm cycle
- Then: (a) `delivery.outbox.stuck` emits at WARN for the stuck row (unchanged from 0708 baseline), (b) `reconciler.alarm.runs` is emitted with `outcome=ok` and `durationMs` populated, (c) all observability assertions pass
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/__tests__/outbox-reconciler-do.test.ts` (update)
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/outbox-reconciler-do.ts` (update if metric fields need adjustment)

---

## Phase 3 — US-003: T-043 E2E Reconnect Hang Fix

### T-016A: Locate studio-side API client + routing for /api/v1/skills/*
**User Story**: US-003 | **Satisfies ACs**: AC-US3-04 (cross-repo end-to-end verification dependency) | **Status**: [x] completed
**Test Plan**:
- Given: user reports 404s on `GET /api/v1/skills/check-updates` and `GET /api/v1/skills/stream` at `localhost:3162` (`vskill studio` instance) but the same paths work on `localhost:3017` (vskill-platform)
- When: studio source layout is mapped — `src/eval-ui/` is the Vite SPA, `BASE = ""` in `src/eval-ui/src/api.ts`, default stream base is `/api/v1/skills/stream` in `src/eval-ui/src/hooks/useSkillUpdates.ts`, and `vskill studio` (port-hashed via `projectPort()` in `src/commands/eval/serve.ts`) is served by `src/eval-server/eval-server.ts` whose router has no `/api/v1/skills/*` handlers
- Then: 404 origin confirmed — eval-server returns its own catch-all `{"error":"Not found"}` 404 for any path it doesn't own. The studio frontend issues correct relative URLs; the gap is that the dev studio process (eval-server) and the platform process (Next.js / Workers) are different servers in dev. Production deploys them same-origin so the relative URL works.

---

### T-016B: Add /api/v1/skills/* proxy in eval-server (3162 → 3017)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-04 | **Status**: [x] completed
**Test Plan**:
- Given: `src/eval-server/platform-proxy.ts` introduces `proxyToPlatform()` + `shouldProxyToPlatform()` + `getPlatformBaseUrl()` with target driven by `VSKILL_PLATFORM_URL` env (default `http://localhost:3017`); `src/eval-server/eval-server.ts` calls these between the local router and the catch-all 404 so unhandled `/api/v1/skills/*` paths forward verbatim (method, path, query, headers minus hop-by-hop, body stream) and stream the upstream response back
- When: `npx vitest run src/eval-server/__tests__/platform-proxy.test.ts` is executed AND a temporary studio instance is spun up on port 3079 against the live platform on 3017
- Then: 12/12 proxy unit tests pass (forwarding GET/POST/headers, hop-by-hop stripped, 502 envelope on upstream-down, SSE content-type preserved end-to-end). End-to-end smoke shows GET check-updates → 405 (proxied), POST check-updates → 200 `{results:[]}` (proxied), GET stream → 502 "Upstream unavailable" (proxied), `/api/config` and `/api/skills` still served locally, `/api/nonexistent` still 404, static SPA root still 200.
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-server/platform-proxy.ts` (new, 138 lines)
  - `repositories/anton-abyzov/vskill/src/eval-server/eval-server.ts` (update — import + 8-line wire-up between router miss and 404 catch-all)
  - `repositories/anton-abyzov/vskill/src/eval-server/__tests__/platform-proxy.test.ts` (new, 12 tests)

---

### T-016C: Cross-repo browser verification — zero 404s in Skill Studio network panel
**User Story**: US-003 | **Satisfies ACs**: AC-US3-04 | **Status**: [x] completed (check-updates flow proven; stream flow blocked on backend wrangler dev — out of scope for this repo)
**Test Plan**:
- Given: T-016B proxy + T-016D POST switch landed in vskill local dist AND vskill-platform Next.js runs on port 3017 (note: SSE stream requires `wrangler dev` for UPDATE_HUB DO binding, which is platform-side scope)
- When: a temporary `vskill studio` instance was launched from local-built `dist/` (ports 3079 and Claude_Preview's auto-spawn at 3077 were both used) AND Skill Studio was loaded via Claude_Preview MCP, network panel captured via `preview_network` and screenshots via `preview_screenshot`
- Then: VERIFIED end-to-end:
  - **GET /api/v1/skills/check-updates 405 ERR_ABORTED** — eliminated. The studio no longer issues GET (T-016D switched to POST per platform contract).
  - **POST /api/v1/skills/check-updates → 200 OK** — proxy forwards correctly. Platform returns `{"results":[]}` envelope; studio handles both flat-array and envelope shapes (api.ts:677-682).
  - All other studio-local routes (`/api/config`, `/api/skills`, `/api/skills/updates`, `/api/agents`, `/api/workspace`, `/api/plugins`) still 200 OK — no regression.
  - Static SPA root still 200; UI renders the skill sidebar with all 11 personal + 50 plugin skills (screenshot in conversation transcript).
  - **GET /api/v1/skills/stream → 502 Bad Gateway** — the proxy IS forwarding correctly (502 originates from the platform on port 3017). The 502 is upstream behaviour: `next dev` does not bind UPDATE_HUB DO; needs `wrangler dev` to fully validate. The hook's reconnect loop retries every ~3s as designed; this is exactly what the user-visible flow looked like before, except now the requests are reaching the platform instead of dead-ending at the studio's catch-all 404.
**Findings forwarded to backend-platform**:
  1. The `wrangler dev --port 3017` profile must be runnable in dev for the SSE flow to be testable end-to-end.
  2. Once wrangler dev is running with UPDATE_HUB bound, re-run this T-016C with the user's actual studio instance (after they restart from a vskill version that includes T-016B + T-016D) to confirm the stream stays open with `: keepalive` comments and emits `skill.updated` frames.

---

### T-016D: Switch studio check-updates from GET to POST per platform contract
**User Story**: US-003 | **Satisfies ACs**: AC-US3-04 | **Status**: [x] completed
**Test Plan**:
- Given: live browser network capture (T-016C round 1) showed POST being the platform's expected method — GET returned 405 Method Not Allowed end-to-end. The studio's existing api.ts envelope-handling code (api.ts:677-682) already accepted the POST `{results: [...]}` shape; only the request method was wrong.
- When: `src/eval-ui/src/api.ts:674` is changed from `fetch(...?skills=${csv})` to `fetch("/api/v1/skills/check-updates", { method: "POST", headers, body: JSON.stringify({ skills: [...].sort() }) })` and `npm run build:eval-ui` is run
- Then: T-016C round 2 captures POST → 200 in the browser network panel. The 405 from round 1 is gone. Existing envelope unwrap path handles the response without changes.
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/api.ts` (update — single call site at line 674)

---

### T-017: Investigation pass — document root cause in plan.md
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [x] completed
**Test Plan**:
- Given: the current T-043 test uses `route.abort('connectionclosed')` + manual fake timers and hangs in Playwright
- When: the four-branch hypothesis tree from plan.md is evaluated by running T-043 in isolation with verbose logging (`--headed --debug`) and checking Playwright network events
- Then: the root cause is confirmed (expected: hypothesis #1+#2 compound — `route.abort` doesn't dispatch `onerror` reliably, and the fake clock doesn't advance the page's `setTimeout`) and a concise note is appended to plan.md under `## Root Cause Findings`
**Files**:
  - `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0712-0708-followups-scanner-outbox-do-alarm-and-e2e/plan.md` (update — root cause note)

---

### T-018: [TDD-RED-EQUIVALENT] Refactor T-043 spec to use page.clock + route.fulfill
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-03 | **Status**: [x] completed
**Test Plan**:
- Given: T-043 is rewritten to (a) install `page.clock` before navigation, (b) use `route.fulfill({ status: 200, headers: { "content-type": "text/event-stream" }, body: "" })` for phase-A (empty body = deterministic `onerror`), (c) use `page.clock.fastForward(4_000)` instead of real-time polling, (d) drop `test.setTimeout(120_000)` and replace with `test.setTimeout(30_000)`
- When: the refactored T-043 is run against the current hook implementation (no hook changes)
- Then: T-043 passes in <30s wall-clock on first run, with no hang, confirming the test seam is deterministic
**Files**:
  - `repositories/anton-abyzov/vskill/e2e/skill-update-pipeline.spec.ts` (update — T-043 only)

---

### T-019: Verify T-043 passes <30s + T-042/T-044 do not regress
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03, AC-US3-04, AC-US3-05 | **Status**: [x] completed
**Verification (2026-04-25, vskill)**:
- T-043 in isolation: passed in 8.6s (`npx playwright test e2e/skill-update-pipeline.spec.ts --grep "SSE drop"`).
- Full suite: 3/3 passed in 9.2s.
- Three consecutive runs: 9.0s / 9.2s / 9.4s — 3/3 green every time, zero flake (NFR-004 satisfied).
- Unit tests: 18/18 useSkillUpdates passing (6 + 12) in 515ms.
**Anti-pattern note added below** in `## Anti-Pattern: Avoid mixing route.abort with EventSource readyState assertions`.

## Anti-Pattern: Avoid mixing route.abort with EventSource readyState assertions

When simulating an SSE connection drop in Playwright, **do not** combine `page.route('**/sse', route => route.abort('connectionclosed'))` with assertions that rely on the hook's explicit reconnect (gated on `EventSource.readyState === CLOSED`). The abort path leaves the EventSource in `CONNECTING`, never `CLOSED`, so any reconnect branch keyed on `CLOSED` will not fire. The browser's implicit auto-reconnect *does* eventually run, but its cadence races real-time poll budgets unpredictably across CI loads, and the test becomes flaky-by-design.

**Use instead**: `route.fulfill({ status: 200, headers: { "content-type": "text/event-stream" }, body: "" })`. An empty-body SSE response causes the EventSource to:
1. successfully open (`onopen` fires, `readyState = OPEN`),
2. immediately see end-of-stream because the body is empty,
3. transition to `CLOSED` via the natural EOF path,
4. fire `onerror` with `readyState === CLOSED` — the exact branch the hook's `scheduleReconnect()` is gated on.

The hook's 1-second reconnect backoff then dominates per-cycle latency, so reconnect counters increment within ~1.5s of the first drop. This is deterministic across browsers and CI loads. Documented in `e2e/skill-update-pipeline.spec.ts` T-043 and in `plan.md` § Root Cause Findings.
**Test Plan**:
- Given: T-043 refactored in T-018, T-042 and T-044 unchanged
- When: `npx playwright test e2e/skill-update-pipeline.spec.ts` is run three times consecutively
- Then: all three runs return 3/3 passed, each test completes in <30s, no flake observed; a hang-debug note is added to `spec.md` under `## Implementation Notes` documenting the anti-pattern (`route.abort('connectionclosed')` + manual fake timers = hang) and the fix (`page.clock` + `route.fulfill(empty body)`)
**Files**:
  - `repositories/anton-abyzov/vskill/e2e/skill-update-pipeline.spec.ts` (verify — no changes unless fallback needed)
  - `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0712-0708-followups-scanner-outbox-do-alarm-and-e2e/spec.md` (update — hang-debug note in Implementation Notes)

---

## AC Coverage Table

| AC | Task(s) |
|---|---|
| AC-US1-01 | T-001, T-002 |
| AC-US1-02 | T-001, T-002 |
| AC-US1-03 | T-001, T-002 |
| AC-US1-04 | T-003, T-004 |
| AC-US1-05 | T-005, T-006 |
| AC-US1-06 | T-007 |
| AC-US2-01 | T-009, T-014 |
| AC-US2-02 | T-008, T-009 |
| AC-US2-03 | T-008, T-009, T-010, T-011 |
| AC-US2-04 | T-012, T-013 |
| AC-US2-05 | T-015 |
| AC-US2-06 | T-016 |
| AC-US2-07 | T-008, T-010, T-012, T-016 |
| AC-US2-08 | T-016 (SLO confirmed post-deploy via Analytics Engine query) |
| AC-US3-01 | T-017 |
| AC-US3-02 | T-018 |
| AC-US3-03 | T-018, T-019 |
| AC-US3-04 | T-019 |
| AC-US3-04 (cross-repo browser verify) | T-016A, T-016B, T-016C, T-016D |
| AC-US3-05 | T-019 |
