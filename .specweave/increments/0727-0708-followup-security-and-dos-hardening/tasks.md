---
increment: 0727-0708-followup-security-and-dos-hardening
title: "0708 Follow-up: Security & DoS Hardening (F-CR2/3/4 + 6 mediums + live E2E)"
type: tasks
status: pending
created: 2026-04-25
---

# Tasks — 0727: 0708 Follow-up Security & DoS Hardening

## US-001: SSE Filter Cap (F-CR2 HIGH)

### T-001: [TDD-RED] SSE route filter-cap test — 501 IDs → 400 with body shape
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [ ] pending
**Test Plan**:
  - Given: SSE route handler with no filter-id cap
  - When: GET request arrives with `?skills=<csv of 501 unique IDs>`
  - Then: handler returns HTTP 400 with JSON body `{ code: "subscription_filter_too_large", maxIds: 500, providedIds: 501 }`; `Content-Type: application/json`; test fails (red — cap not yet implemented)
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/app/api/v1/skills/stream/__tests__/route.test.ts` (new)

---

### T-002: [TDD-RED] SSE route boundary test — exactly 500 IDs → 200
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [ ] pending
**Test Plan**:
  - Given: SSE route handler (pre-cap implementation)
  - When: GET request arrives with `?skills=<csv of exactly 500 unique IDs>`
  - Then: handler returns HTTP 200 with `Content-Type: text/event-stream`; written before implementation so it locks the off-by-one direction (red until T-003 lands)
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/app/api/v1/skills/stream/__tests__/route.test.ts` (update)

---

### T-003: [TDD-GREEN] Inline filter-id cap in SSE route handler
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [ ] pending
**Test Plan**:
  - Given: T-001 and T-002 tests are red
  - When: inline validation added between the existing empty-filter guard and the `getCloudflareContext` call — split CSV, filter empty strings, if `count > 500` return `Response.json({ code: "subscription_filter_too_large", maxIds: 500, providedIds: count }, { status: 400 })`; inline JSDoc cites `POST /api/v1/skills/stream/subscribe` as the path for filters >500
  - Then: 501-ID request → 400 JSON body; 500-ID request → 200 `text/event-stream`; all pre-existing tests stay green; no Zod, no middleware change
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/app/api/v1/skills/stream/route.ts` (update)

> **NFR-NR-02 checklist**: After landing T-003, run a local p99 latency spot-check on the accept path (≤500 IDs) to confirm no regression. Document result as a comment here.

---

## US-002: Timing-Safe HMAC Comparison (F-CR3 HIGH)

### T-004: [TDD-RED] Unit tests for `timing-safe-equal.ts` shared helper
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03 | **Status**: [ ] pending
**Test Plan**:
  - Given: `src/lib/crypto/timing-safe-equal.ts` does not exist yet
  - When: tests are written asserting: (a) equal same-length strings → true; (b) unequal same-length strings → false; (c) strings of different length → false (early return, no throw); (d) XOR-fold computes correctly across all bit positions
  - Then: tests fail (file not found)
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/crypto/__tests__/timing-safe-equal.test.ts` (new)

---

### T-005: [TDD-GREEN] Implement `timingSafeEqualString` shared helper
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03 | **Status**: [ ] pending
**Test Plan**:
  - Given: T-004 tests are red
  - When: `src/lib/crypto/timing-safe-equal.ts` created exporting `timingSafeEqualString(a: string, b: string): boolean` using the XOR-fold algorithm lifted verbatim from `webhook-auth.ts:54-61`; unequal-length → `false` early return documented in JSDoc
  - Then: all T-004 tests pass green; `tsc --noEmit` passes
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/crypto/timing-safe-equal.ts` (new)

---

### T-006: Audit — grep for `===` digest comparisons across auth paths
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [ ] pending
**Test Plan**:
  - Given: codebase before refactor
  - When: run `grep -rn "key === \|signature === \|digest === \|hmac === " repositories/anton-abyzov/vskill-platform/src/` and inspect all hits
  - Then: each hit is marked in the checklist below; any unprotected timing-unsafe path beyond the known sites is fixed in T-007
**Audit checklist** (mark each line verified):
  - [ ] `src/lib/internal-auth.ts:14` — `key === env.INTERNAL_BROADCAST_KEY`
  - [ ] `src/lib/internal-auth.ts:22` — second `key ===` site
  - [ ] `src/lib/webhook-auth.ts:54-61` — local `timingSafeEqual` (correct algorithm, duplicate)
  - [ ] `src/app/api/v1/webhooks/github/route.ts:65-70` — local `timingSafeEqual` (correct algorithm, duplicate)
  - [ ] `src/lib/submission/**` — confirm no string `===` on signed values
  - [ ] `src/app/api/v1/internal/**` — confirm no string `===` on signed values
**Files**:
  - (read-only audit — no file changes in this task)

---

### T-007: [TDD-RED/GREEN] Refactor `internal-auth.ts` + deduplicate local timing-safe helpers
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [ ] pending
**Test Plan**:
  - Given: T-005 shared helper exists; T-006 audit complete
  - When: (red) spy-based test added asserting `timingSafeEqualString` is invoked on the compare hot path in `internal-auth.ts`; (green) replace `===` at lines 14 and 22 with `timingSafeEqualString(key, env.INTERNAL_BROADCAST_KEY)`; delete local `timingSafeEqual` definitions from `webhook-auth.ts:54-61` and `webhooks/github/route.ts:65-70`; both files import shared helper
  - Then: spy test green; `grep "=== " src/lib/internal-auth.ts src/lib/webhook-auth.ts src/app/api/v1/webhooks/github/route.ts` on key/signature patterns returns 0 hits; integration tests confirm valid HMAC passes and invalid (including length-mismatched) rejects; `tsc --noEmit` passes
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/internal-auth.ts` (update)
  - `repositories/anton-abyzov/vskill-platform/src/lib/webhook-auth.ts` (update)
  - `repositories/anton-abyzov/vskill-platform/src/app/api/v1/webhooks/github/route.ts` (update)
  - `repositories/anton-abyzov/vskill-platform/src/lib/crypto/__tests__/timing-safe-equal.test.ts` (update — add spy integration tests)

---

## US-003: Atomic Anti-Replay via Durable Object (F-CR4 HIGH)

### T-008: Wrangler binding + migration v4 for `WebhookDeliveryDedupDO`
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [ ] pending
**Test Plan**:
  - Given: `wrangler.jsonc` has existing DO bindings and v1–v3 migrations
  - When: binding `{ "name": "WEBHOOK_DEDUP_DO", "class_name": "WebhookDeliveryDedupDO" }` and migration `{ "tag": "v4", "new_classes": ["WebhookDeliveryDedupDO"] }` are appended to the existing `durable_objects.bindings` and `migrations` arrays
  - Then: `npx wrangler dev` starts without error; `WEBHOOK_DEDUP_DO` binding is reachable; no existing bindings or migrations are modified
**Files**:
  - `repositories/anton-abyzov/vskill-platform/wrangler.jsonc` (update)

---

### T-009: [TDD-RED] DO unit tests — `blockConcurrencyWhile`, TTL, alarm GC
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [ ] pending
**Test Plan**:
  - Given: `webhook-dedup-do.ts` does not yet exist; test uses a `Map`-backed `DurableObjectState` shim with a serial-promise `blockConcurrencyWhile`
  - When: tests are written for: (a) first call with new `deliveryId` → `{ firstSeen: true }`; (b) 100 concurrent `Promise.all` calls with same `deliveryId` → exactly 1 `firstSeen: true`, 99 `firstSeen: false`; (c) after `vi.advanceTimersByTime(TTL_MS + 1000)`, same `deliveryId` → `firstSeen: true` again; (d) `alarm()` invocation purges expired `delivery:` keys
  - Then: all four tests fail (file not found)
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/__tests__/webhook-dedup-do.test.ts` (new)

---

### T-010: [TDD-GREEN] Implement `WebhookDeliveryDedupDO` class
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [ ] pending
**Test Plan**:
  - Given: T-009 tests are red
  - When: `webhook-dedup-do.ts` created implementing: `fetch()` dispatching `POST /dedup-and-record` to `dedupAndRecord(deliveryId)`; `blockConcurrencyWhile` wrapping get→conditional put; `TTL_MS = 300_000`; `GC_INTERVAL_MS = 60_000`; lazy `setAlarm` if no alarm is armed; `alarm()` that purges entries where `expiresAt <= now` and re-arms if any entries remain; named instance pattern via `idFromName("global")` documented in class JSDoc
  - Then: all T-009 tests pass green; `tsc --noEmit` passes
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/webhook-dedup-do.ts` (new)

---

### T-011: [TDD-RED] Webhook route concurrency test — 100 same-delivery → exactly 1 enqueue
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02 | **Status**: [ ] pending
**Test Plan**:
  - Given: webhook route handler using current non-atomic GET-then-PUT; `enqueueScanHigh` is mocked
  - When: 100 concurrent `Promise.all` calls are made to the webhook handler with the same `X-GitHub-Delivery` header and a valid HMAC signature
  - Then: `enqueueScanHigh` mock is called exactly once; 99 responses carry `{ ok: true, duplicate: true }`; test fails before DO integration (race window causes >1 enqueue)
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/app/api/v1/webhooks/github/__tests__/route.test.ts` (new or update)

---

### T-012: [TDD-GREEN] Refactor webhook route — swap KV GET-then-PUT for DO atomic dedup
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [ ] pending
**Test Plan**:
  - Given: T-011 red; T-008 binding in place; T-010 DO class exists
  - When: `webhooks/github/route.ts:99-110` refactored — retrieve `WEBHOOK_DEDUP_DO` stub via `idFromName("global")`; POST to `https://do/dedup-and-record` with `{ deliveryId }`; on `!firstSeen` return `NextResponse.json({ ok: true, duplicate: true }, { status: 200 })`; old `RATE_LIMIT_KV` `gh-delivery:` reads and writes removed
  - Then: T-011 concurrency test passes green (exactly 1 `enqueueScanHigh`); all pre-existing webhook route tests stay green
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/app/api/v1/webhooks/github/route.ts` (update)

> **NFR-NR-03 checklist**: After T-012 lands, fire 50 sequential signed webhooks against `wrangler dev` and compare p50 latency (curl timing) before and after DO refactor. Document result here.

---

### T-013: [TDD-RED/GREEN] TTL expiry test — replay after 300s is accepted
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03 | **Status**: [ ] pending
**Test Plan**:
  - Given: DO class implemented (T-010); `vi.useFakeTimers()` active
  - When: (red) test asserts that after `vi.advanceTimersByTime(TTL_MS + 1000)` a second call with the same `deliveryId` returns `{ firstSeen: true }`; (green) DO's `existing > Date.now()` branch handles expired entries correctly
  - Then: TTL expiry test passes; test co-located in `webhook-dedup-do.test.ts`
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/__tests__/webhook-dedup-do.test.ts` (update)

---

## US-004: Six Medium-Severity Quality Fixes (F-CR6–F-CR11)

### T-014: [TDD-RED] Scanner contentHash regression test — `sha256:pending:<sha12>` format
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01 | **Status**: [ ] pending
**Test Plan**:
  - Given: `scanner.ts` produces deterministic placeholder `contentHash` for unresolved skills
  - When: test is written asserting an unresolved skill's `contentHash` matches `/^sha256:pending:[0-9a-f]{12}$/`
  - Then: test fails if the format diverges (red-to-lock); green if format is already correct but coverage gap is closed
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/__tests__/scanner.test.ts` (update)

---

### T-015: [TDD-GREEN] Confirm or fix scanner contentHash format
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01 | **Status**: [ ] pending
**Test Plan**:
  - Given: T-014 test exists
  - When: `scanner.ts` hash computation is confirmed to produce `sha256:pending:<12-char lowercase hex prefix>` or corrected if it diverges
  - Then: T-014 test passes green; no other scanner behavior changes
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/scanner.ts` (update only if format needs fixing)

---

### T-016: [TDD-RED] queue-consumer.test.ts — annotate `as any` sites to expose type errors
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02 | **Status**: [ ] pending
**Test Plan**:
  - Given: `queue-consumer.test.ts` has 2 `as any` casts that currently suppress type errors
  - When: `// @ts-expect-error` suppressions are added at each `as any` site to make the error visible
  - Then: `tsc --noEmit` emits errors at those sites (red)
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/__tests__/queue-consumer.test.ts` (update)

---

### T-017: [TDD-GREEN] Replace `as any` casts with proper `vi.hoisted()` + `Mock<>` generics
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02 | **Status**: [ ] pending
**Test Plan**:
  - Given: T-016 annotations in place
  - When: `as any` casts replaced — use `vi.hoisted(() => ({ batch: {} as MessageBatch<ScanQueueMessage> }))` and `Partial<MessageBatch<ScanQueueMessage>>` where partial is needed; `@ts-expect-error` annotations removed
  - Then: `tsc --noEmit` passes with no `@ts-expect-error`; runtime tests stay green
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/__tests__/queue-consumer.test.ts` (update)

---

### T-018: [TDD-RED] Outbox reconciler — test `updateEventId` correlation in error log + AE tag
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03 | **Status**: [ ] pending
**Test Plan**:
  - Given: `outbox-reconciler.ts` catch path calls `logger.error` without event ID; AE metric write lacks correlation tag
  - When: test is written asserting `logger.error` is called with an object containing `updateEventId` field and the AE metric tag includes `update_event_id:<id>`
  - Then: test fails (correlation fields not yet in error log)
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/__tests__/outbox-reconciler.test.ts` (new or update)

---

### T-019: [TDD-GREEN] Add `eventId` to outbox reconciler error log and AE metric tag
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03 | **Status**: [ ] pending
**Test Plan**:
  - Given: T-018 test is red
  - When: `outbox-reconciler.ts` lines 91-105 updated — catch path adds `eventId: row.eventId` to `logger.error` call; AE metric write adds `blobs[3] = row.eventId` as correlation tag
  - Then: T-018 test passes green; no other reconciler behavior changes
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/outbox-reconciler.ts` (update)

---

### T-020: [TDD-RED] publish.ts — test that non-targeted `Error` propagates through fingerprint catch
**User Story**: US-004 | **Satisfies ACs**: AC-US4-04 | **Status**: [ ] pending
**Test Plan**:
  - Given: `publish.ts` has a broad `try/catch` around fingerprint computation that swallows all errors
  - When: test is written throwing a synthetic `new Error("unexpected")` (not `TypeError` or `RangeError`) inside the fingerprint block and asserting it propagates to the caller (is not swallowed)
  - Then: test fails (broad catch currently swallows it)

> **Audit note before T-021**: grep `repositories/anton-abyzov/vskill-platform/src/lib/submission/publish.ts` for fingerprint-adjacent `try/catch`. If the broad catch was already removed (refactor since 0708), close T-020 and T-021 as no-ops with a note.

**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/submission/__tests__/publish.test.ts` (new or update)

---

### T-021: [TDD-GREEN] Narrow catch in publish.ts to `TypeError | RangeError`
**User Story**: US-004 | **Satisfies ACs**: AC-US4-04 | **Status**: [ ] pending
**Test Plan**:
  - Given: T-020 test is red
  - When: fingerprint catch narrowed to `catch (err) { if (err instanceof TypeError || err instanceof RangeError) { /* warn + proceed */ } else throw err; }`
  - Then: T-020 test passes green; `TypeError`/`RangeError` are still caught; arbitrary `Error` propagates
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/submission/publish.ts` (update)

---

### T-022: [TDD-RED] outbox-writer.test.ts — annotate `as never` site to expose type error
**User Story**: US-004 | **Satisfies ACs**: AC-US4-05 | **Status**: [ ] pending
**Test Plan**:
  - Given: `outbox-writer.test.ts` uses `as never` Prisma type cast
  - When: `// @ts-expect-error` annotation added at the `as never` site
  - Then: `tsc --noEmit` emits an error at that site (red)
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/__tests__/outbox-writer.test.ts` (update)

---

### T-023: [TDD-GREEN] Replace `as never` with `Prisma.TransactionClient` cast
**User Story**: US-004 | **Satisfies ACs**: AC-US4-05 | **Status**: [ ] pending
**Test Plan**:
  - Given: T-022 annotation in place
  - When: `as never` replaced with `as unknown as Prisma.TransactionClient`; `import type { Prisma } from "@prisma/client"` added at top of file; `@ts-expect-error` removed
  - Then: `tsc --noEmit` passes in strict mode; runtime tests stay green
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/__tests__/outbox-writer.test.ts` (update)

---

### T-024: [TDD-RED] build-worker-entry.ts — smoke test asserts cold-start log line
**User Story**: US-004 | **Satisfies ACs**: AC-US4-06 | **Status**: [ ] pending
**Test Plan**:
  - Given: `scripts/build-worker-entry.ts` generates scheduled handler attachment without a cold-start log
  - When: smoke test is written asserting the generated entry string contains `"[cron] scheduled handler attached"`
  - Then: test fails (log line not present in generated output)
**Files**:
  - `repositories/anton-abyzov/vskill-platform/scripts/__tests__/build-worker-entry.test.ts` (new or update)

---

### T-025: [TDD-GREEN] Add `[cron] scheduled handler attached` cold-start log
**User Story**: US-004 | **Satisfies ACs**: AC-US4-06 | **Status**: [ ] pending
**Test Plan**:
  - Given: T-024 test is red
  - When: `scripts/build-worker-entry.ts` adds `console.log("[cron] scheduled handler attached")` at the scheduled handler attachment site (module top level if module-scoped, or once on first invocation guarded by a module-level boolean)
  - Then: T-024 test passes green

> **Runbook — `wrangler tail` manual verification**: after deploy, run `npx wrangler tail --format=pretty` and trigger one cron invocation. Confirm `[cron] scheduled handler attached` appears in the tail output. Mark this checklist item done after verification.
> - [ ] `wrangler tail` verified in staging/prod

**Files**:
  - `repositories/anton-abyzov/vskill-platform/scripts/build-worker-entry.ts` (update)

---

## US-005: Live-Wire E2E for Skill-Update Pipeline

### T-026: Playwright config — `live` project + second `webServer` + `PLAYWRIGHT_RUN_LIVE` gate
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-03 | **Status**: [ ] pending
**Test Plan**:
  - Given: `playwright.config.ts` has one `webServer` entry (eval server port 3077) and one `default` project
  - When: second `webServer` entry is added for `cd ../vskill-platform && npx wrangler dev --port 8788` with `timeout: 30_000` gated on `process.env.PLAYWRIGHT_RUN_LIVE === "1"`; new `live` project added with `testMatch: /-live\.spec\.ts$/` and `grep: /@live/`; `default` project gets `testIgnore: /-live\.spec\.ts$/`
  - Then: `npx playwright test` (no flag) skips live tests entirely; `npx playwright test --project=live` (with `PLAYWRIGHT_RUN_LIVE=1`) spawns wrangler dev on port 8788 and runs live tests; `tsc --noEmit` passes
**Files**:
  - `repositories/anton-abyzov/vskill/playwright.config.ts` (update)

---

### T-027: Live E2E global setup — DB reset + fixture seed
**User Story**: US-005 | **Satisfies ACs**: AC-US5-02 | **Status**: [ ] pending
**Test Plan**:
  - Given: `E2E_DATABASE_URL` points to a local `vskill_e2e` Postgres
  - When: `globalSetup` script runs `prisma migrate reset --force` against `E2E_DATABASE_URL` then seeds one `Skill` row with `sourceRepoUrl: "https://github.com/test-org/test-skill"` matching the E2E fixture
  - Then: DB is clean and seeded before suite starts; each re-run is hermetic; `e2e:db-reset` npm script works standalone
**Files**:
  - `repositories/anton-abyzov/vskill-platform/__tests__/e2e/global-setup.ts` (new or update)
  - `repositories/anton-abyzov/vskill-platform/package.json` (update — add `e2e:db-reset` script: `prisma migrate reset --force`)

---

### T-028: [TDD-RED/GREEN] New live-wire E2E spec — `skill-update-pipeline-live.spec.ts`
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03 | **Status**: [ ] pending
**Test Plan**:
  - Given: T-026 config in place; T-027 global setup runs; wrangler dev on port 8788; DB seeded
  - When: spec exercises the full wire path — (1) POST signed `push` webhook to `http://localhost:8788/api/v1/webhooks/github` with `x-hub-signature-256`, `x-github-event: push`, unique `x-github-delivery`; (2) poll via `expect.poll` until `UpdateEvent` row lands in DB (timeout 5s); (3) assert Studio page's EventSource receives `skill.updated` SSE within 2s; (4) assert `[data-testid="update-bell-badge"]` text equals "1"
  - Then: `npx playwright test --project=live` passes; spec contains zero `page.route(...)` calls for skill-update endpoints; spec is tagged `@live`; `PLAYWRIGHT_RUN_LIVE=1` required to run
**Files**:
  - `repositories/anton-abyzov/vskill/e2e/skill-update-pipeline-live.spec.ts` (new)

---

### T-029: Nightly CI workflow — `.github/workflows/e2e-live-nightly.yml`
**User Story**: US-005 | **Satisfies ACs**: AC-US5-03 | **Status**: [ ] pending
**Test Plan**:
  - Given: live spec exists (T-028); wrangler and Postgres available in CI environment
  - When: GitHub Actions workflow is created with `schedule: cron: '0 6 * * *'` and `workflow_dispatch` trigger; sets `PLAYWRIGHT_RUN_LIVE=1`; runs `npx playwright test --project=live` in `repositories/anton-abyzov/vskill/`
  - Then: workflow file is valid YAML; default PR workflow (existing CI) is unchanged; live tests never run on the default PR lane

> **Runbook — local live E2E boot sequence**:
> 1. Start local Postgres, export `E2E_DATABASE_URL=postgresql://localhost/vskill_e2e`
> 2. `cd repositories/anton-abyzov/vskill-platform && npm run e2e:db-reset`
> 3. Export env vars: `GITHUB_WEBHOOK_SECRET=test-secret-for-e2e` and `INTERNAL_BROADCAST_KEY=test-broadcast-key`
> 4. From `repositories/anton-abyzov/vskill/`: `PLAYWRIGHT_RUN_LIVE=1 npx playwright test --project=live`

**Files**:
  - `.github/workflows/e2e-live-nightly.yml` (new)

---

## Final Verification Gate

### T-030: Full regression sweep — all tests green, `tsc` clean
**User Story**: US-001, US-002, US-003, US-004, US-005 | **Satisfies ACs**: all 18 ACs | **Status**: [ ] pending
**Test Plan**:
  - Given: all T-001 through T-029 tasks completed
  - When: full test suite is run in both repos:
    ```bash
    cd repositories/anton-abyzov/vskill-platform && npx vitest run && npx tsc --noEmit
    cd repositories/anton-abyzov/vskill && npx vitest run && npx playwright test
    ```
  - Then: both commands exit 0; test count equals or exceeds 297 pre-existing; no new `@ts-expect-error` or `as never` casts introduced; `code-review-report.json` for this increment shows zero findings traceable to F-CR2, F-CR3, F-CR4, F-CR6–F-CR11
**Files**:
  - (gate task — no code changes)
