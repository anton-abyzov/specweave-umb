---
increment: 0721-tier2-llm-scan-restoration-and-clarity
title: "Tier-2 LLM Scan Restoration, Cost Optimization, and Trust-Tier Label Clarification"
status: planned
coverage_target: 90
test_mode: TDD
---

# Tasks: 0721 — Tier-2 LLM Scan Restoration, Cost Optimization, and Trust-Tier Label Clarification

> **Hard dependency**: 0713-queue-pipeline-restoration must ship before Phase A backfill (T-006/T-007) can run. T-001 is the sentinel gate.
> **TDD strict mode active**: every task must have a failing test (RED) committed before implementation (GREEN). No task may be marked `[x]` until its tests pass.
> **AC traceability**: every task references one or more `AC-USn-NN` IDs. Coverage target: 90%.

---

## Phase A — Diagnose and Restore (US-001, US-002)

### T-001: Sentinel — verify 0713 has shipped and RECEIVED rows are advancing
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [ ] pending

**Test Plan**:
- Given: a live DB connection to the Neon Postgres instance
- When: the sentinel query `SELECT COUNT(*) FROM "Submission" WHERE state = 'RECEIVED' AND "updatedAt" > now() - interval '10 minutes'` runs
- Then: the count is decreasing over time (queue is draining), confirming 0713 is live and processing
- Test file: `crawl-worker/scripts/sentinel-0713-check.js` (manual run, output logged)
- Test type: manual gate / smoke

**Implementation**:
1. Run `SELECT COUNT(*) FROM "ScanResult" WHERE tier=2 AND "createdAt" > now() - interval '24 hours'` against prod DB and record result.
2. Run `SELECT state, COUNT(*) FROM "Submission" GROUP BY state` to confirm queue is flowing.
3. If either query shows stale state, do NOT proceed to T-002 or T-006. Block and notify team-lead.
4. Record gate verdict (`PASS` / `BLOCK`) in `reports/cliff-diagnosis.md` as a preamble entry.

**TDD sequence**:
- RED: this is a manual gate; block is enforced by this task's status
- GREEN: confirm 0713 closed and DB shows queue draining
- REFACTOR: n/a

**Files touched**:
- `.specweave/increments/0721-tier2-llm-scan-restoration-and-clarity/reports/cliff-diagnosis.md` (create stub)

---

### T-002 (RED): Write failing diagnostic test — cliff root-cause capture
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-07 | **Status**: [ ] pending

**Test Plan**:
- Given: a snapshot fixture with a `ScanResult` table and three sample `.env` files for vm1/vm2/vm3
- When: the diagnostic script runs against the fixture
- Then: the output report contains verdicts for all four checks — (a) Workers AI quota exhaustion, (b) `cfAccountId`/`cfApiToken` drift across vm1/2/3, (c) JSON-parse failure rate spike at `tier2-scan.js:202`, (d) downstream queue starvation from 0708/0713 — each verdict is one of `CONFIRMED`, `REFUTED`, or `INCONCLUSIVE` with evidence
- Test file: `crawl-worker/scripts/__tests__/diagnose-cliff.test.js`
- Test type: unit

**TDD sequence**:
- RED: write test asserting the four-check structure in output; run `npx vitest run crawl-worker/scripts/__tests__/diagnose-cliff.test.js` — expect FAIL (no script yet)
- GREEN: implement `crawl-worker/scripts/diagnose-cliff.js` in T-003 until test passes
- REFACTOR: extract env-diff and log-parse helpers

**Files touched**:
- `crawl-worker/scripts/__tests__/diagnose-cliff.test.js` (NEW)

---

### T-003 (GREEN): Implement diagnose-cliff.js and produce cliff-diagnosis.md
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-06, AC-US1-07 | **Status**: [ ] pending

**Test Plan**:
- Given: the T-002 test is written and failing
- When: `diagnose-cliff.js` runs with prod credentials
- Then: `reports/cliff-diagnosis.md` is produced with verdicts for all four checks and the closing verification query result included
- Given: a forced failure injection in `submission-scanner.js`
- When: the scanner runs
- Then: a JSON log entry with fields `skill_id`, `failure_stage`, `error_class`, `error_message` is captured
- Test file: `crawl-worker/sources/__tests__/submission-scanner.failure-log.test.js`
- Test type: unit (failure-log emission — AC-US1-07)

**Implementation**:
1. Query `SELECT MAX("createdAt") FROM "ScanResult" WHERE tier=2` to find the last successful tier-2 row.
2. Diff `crawl-worker/.env.vm1`, `.env.vm2`, `.env.vm3` for `cfAccountId` and `cfApiToken`; record CONFIRMED/REFUTED/INCONCLUSIVE.
3. Pull CF Worker logs (or AE estimate) for JSON-parse failure spike near 2026-03-26; record verdict.
4. Cross-reference 0708 stats-cron freeze date with `ScanResult` gap start date; record verdict.
5. Add structured failure-log (`JSON.stringify({ skill_id, failure_stage, error_class, error_message })`) to `submission-scanner.js` error handler.
6. Write findings to `reports/cliff-diagnosis.md` including closing verification query.
7. Run `npx vitest run` — all green.

**TDD sequence**:
- RED: T-002 test already written; write the failure-log test too before implementing
- GREEN: implement until both tests pass
- REFACTOR: extract env-diff helper into `crawl-worker/lib/env-diff.js`

**Files touched**:
- `crawl-worker/scripts/diagnose-cliff.js` (NEW)
- `crawl-worker/sources/submission-scanner.js`
- `crawl-worker/sources/__tests__/submission-scanner.failure-log.test.js` (NEW)
- `.specweave/increments/0721-tier2-llm-scan-restoration-and-clarity/reports/cliff-diagnosis.md` (NEW)

---

### T-004 (RED): Write failing tests for backfill script idempotency, dry-run, priority, and confirm guard
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05 | **Status**: [ ] pending

**Test Plan**:
- Given: a fixture `Submission` that already has a tier-2 `ScanResult` with `createdAt > '2026-04-25'`
- When: backfill runs against the fixture
- Then: no new `ScanResult` row is written and the log contains `skip (already scanned)` for that submission
- Given: `--dry-run --limit 10` against a fixture DB with 15 candidate submissions
- When: backfill runs
- Then: zero rows written, log lists exactly 10 candidates
- Given: `--priority heygen-com/hyperframes/hyperframes` with a 50-skill fixture
- When: backfill runs
- Then: hyperframes is the first skill in the processed-order log
- Given: backfill invoked without `--confirm` flag
- When: the script runs
- Then: exit code non-zero, zero rows written, refusal message in stderr
- Test file: `crawl-worker/scripts/__tests__/backfill-tier2.test.js`
- Test type: unit (DB fixture via in-memory mock)

**TDD sequence**:
- RED: write all four test cases; run `npx vitest run crawl-worker/scripts/__tests__/backfill-tier2.test.js` — expect FAIL
- GREEN: implement script in T-005
- REFACTOR: n/a

**Files touched**:
- `crawl-worker/scripts/__tests__/backfill-tier2.test.js` (NEW)

---

### T-005 (GREEN): Implement backfill-tier2.js with dry-run, rate-limit, priority, confirm guard
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06 | **Status**: [ ] pending

**Test Plan**:
- Continuation from T-004 tests
- Test file: `crawl-worker/scripts/__tests__/backfill-tier2.test.js`
- Test type: unit

**Implementation**:
1. Create `crawl-worker/scripts/` directory.
2. Implement `crawl-worker/scripts/backfill-tier2.js` accepting: `--dry-run`, `--limit N`, `--rate-per-hour 1000` (default), `--priority <skillSlug>`, `--confirm`.
3. Guard: if `--confirm` absent or `INTERNAL_KEY` env var unset, exit 1 with refusal message.
4. Query `Submission` rows where `state IN ('PUBLISHED', 'AUTO_APPROVED')` AND no `ScanResult` with `tier=2 AND createdAt > '2026-04-25'` exists.
5. If `--priority` provided, move matching `Skill.slug` entries to head of queue.
6. Dry-run: log candidates without writing. Live mode: re-enqueue via token-bucket (1000/hour default).
7. Per-row exception handling: log to `backfill-skipped.jsonl`, continue.
8. Log closing verification SQL: `SELECT MAX("createdAt"), COUNT(*) FROM "ScanResult" WHERE tier=2 AND "createdAt" > now() - interval '24 hours'`.
9. Run `npx vitest run crawl-worker/scripts/__tests__/backfill-tier2.test.js` — all green.

**TDD sequence**:
- RED: T-004 tests already written
- GREEN: implement until all T-004 tests pass
- REFACTOR: extract token-bucket into `crawl-worker/lib/token-bucket.js`

**Files touched**:
- `crawl-worker/scripts/backfill-tier2.js` (NEW)
- `crawl-worker/lib/token-bucket.js` (NEW)
- `crawl-worker/scripts/__tests__/backfill-tier2.test.js`

---

### T-006: Run backfill in dry-run against prod (manual gate — requires 0713 shipped)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-04 | **Status**: [ ] pending

**Test Plan**:
- Given: 0713 is confirmed shipped (T-001 gate PASS) and T-005 tests are green
- When: `node crawl-worker/scripts/backfill-tier2.js --dry-run --limit 10 --priority heygen-com/hyperframes/hyperframes --confirm` runs against prod
- Then: log shows exactly 10 candidate skills with hyperframes at position 1, zero DB writes, exit code 0
- Test file: manual run / stdout log artifact
- Test type: smoke / manual gate

**Implementation**:
1. Confirm T-001 gate is PASS.
2. Run dry-run command above.
3. Verify output: hyperframes is position 1, 10 candidates listed, 0 writes.
4. Paste output snippet into `reports/cliff-diagnosis.md` as dry-run confirmation.

**TDD sequence**:
- RED: dry-run execution (non-destructive)
- GREEN: confirm log matches expected shape
- REFACTOR: n/a

**Files touched**:
- `.specweave/increments/0721-tier2-llm-scan-restoration-and-clarity/reports/cliff-diagnosis.md`

---

### T-007: Execute full backfill against prod (manual gate — requires user confirmation)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04, AC-US1-06 | **Status**: [ ] pending

> **MANUAL GATE**: requires explicit confirmation from Anton before execution (~30h run at 1000/hour for ~30k skills).

**Test Plan**:
- Given: T-006 dry-run verified clean
- When: `node crawl-worker/scripts/backfill-tier2.js --rate-per-hour 1000 --priority heygen-com/hyperframes/hyperframes --confirm` runs
- Then: hyperframes has at least one `ScanResult.tier=2` row within 1 hour of script start, and `Skill.trustTier='T3'` for hyperframes after finalize-scan processes it
- Test file: prod DB query (closing verification per AC-US1-06)
- Test type: production smoke

**Implementation**:
1. Get explicit user confirmation before running.
2. Execute backfill with `--priority heygen-com/hyperframes/hyperframes --confirm`.
3. Monitor `backfill-skipped.jsonl` for errors.
4. After hyperframes batch (~first hour), run closing verification query and record in `reports/cliff-diagnosis.md`.

**TDD sequence**:
- RED: production run
- GREEN: closing verification query returns `COUNT(*) > 0`
- REFACTOR: n/a

**Files touched**:
- `.specweave/increments/0721-tier2-llm-scan-restoration-and-clarity/reports/cliff-diagnosis.md`

---

### T-008 (RED): Write failing integration tests for in-transaction updateSkillTrust (ADR 0721-01)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06 | **Status**: [ ] pending
**ADR**: 0721-01

**Test Plan**:
- Given: verdict=PASS and score=75 submitted to finalize-scan
- When: the handler runs (Miniflare integration)
- Then: both `ScanResult.tier=2` row and `Skill.trustTier='T3'` exist in DB atomically
- Given: verdict=CONCERNS and score=70
- When: finalize-scan runs
- Then: `Skill.trustTier='T3'`
- Given: verdict=FAIL
- When: finalize-scan runs
- Then: `Skill.trustTier='T2'` (unchanged), `ScanResult` row exists
- Given: `updateSkillTrust` throws inside the transaction
- When: finalize-scan runs
- Then: `ScanResult` count is unchanged (rollback verified — AC-US2-05)
- Given: two concurrent finalize-scan calls with identical payloads for the same skillId
- When: both complete
- Then: `ScanResult` count = 1 and `Skill.trustTier='T3'` exactly once (AC-US2-06)
- Test file: `src/lib/trust/__tests__/trust-updater.in-tx.test.ts`
- Test type: integration (Miniflare)

**TDD sequence**:
- RED: write all five test cases; run `npx vitest run src/lib/trust/__tests__/trust-updater.in-tx.test.ts` — expect FAIL
- GREEN: implement transaction wrapper in T-009
- REFACTOR: n/a

**Files touched**:
- `src/lib/trust/__tests__/trust-updater.in-tx.test.ts` (NEW)

---

### T-009 (GREEN): Wrap finalize-scan tier-2 branch in prisma.$transaction with updateSkillTrust (ADR 0721-01)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06, AC-US2-07 | **Status**: [ ] pending
**ADR**: 0721-01

**Implementation**:
1. In `src/app/api/v1/internal/finalize-scan/route.ts`, locate the tier-2 success branch (~lines 362-454).
2. Wrap `storeScanResult` (tier-2 branch only) and `updateSkillTrust` inside `prisma.$transaction(async (tx) => { ... })` per ADR 0721-01 implementation contract.
3. In `src/lib/submission-store.ts`, ensure `storeScanResult` accepts optional `tx: Prisma.TransactionClient`; pass `tx` when called from inside the transaction.
4. Verify `TrustPrismaClient` in `src/lib/trust/trust-updater.ts` is structurally compatible with `Prisma.TransactionClient` (no signature change needed per plan).
5. Run `npx vitest run src/lib/trust/__tests__/trust-updater.in-tx.test.ts` — all green.
6. Run `npx vitest run` — full suite green.

**TDD sequence**:
- RED: T-008 tests already written
- GREEN: implement transaction wrapper until all T-008 tests pass
- REFACTOR: extract `runFinalizeTransaction` helper if the block exceeds 30 lines

**Files touched**:
- `src/app/api/v1/internal/finalize-scan/route.ts`
- `src/lib/submission-store.ts`

---

## Phase B — Cost Optimization (US-003, US-004)

### T-010 (RED): Write failing tests for feature flag resolvePrimaryModel (ADR 0721-04)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-03 | **Status**: [ ] pending
**ADR**: 0721-04

**Test Plan**:
- Given: KV returns `tier2-rollout-pct=0`
- When: `resolvePrimaryModel(submissionId, config)` is called
- Then: returns `@cf/meta/llama-4-scout-17b-16e-instruct` (control arm during ramp)
- Given: KV returns `tier2-rollout-pct=100`
- When: `resolvePrimaryModel` is called with any submissionId
- Then: returns `@cf/qwen/qwen3-30b-a3b-fp8`
- Given: KV returns `tier2-rollout-pct=10` and a fixed `submissionId='abc123'`
- When: `resolvePrimaryModel` is called N times with the same submissionId
- Then: the same model is always returned (deterministic bucket — AC-US3-03)
- Given: KV is unreachable
- When: `resolvePrimaryModel` is called
- Then: defaults to 0% Qwen3 (Llama 4 Scout returned)
- Test file: `crawl-worker/lib/__tests__/tier2-scan.feature-flag.test.js`
- Test type: unit

**TDD sequence**:
- RED: write test cases; run `npx vitest run crawl-worker/lib/__tests__/tier2-scan.feature-flag.test.js` — expect FAIL
- GREEN: implement `resolvePrimaryModel` in T-011
- REFACTOR: n/a

**Files touched**:
- `crawl-worker/lib/__tests__/tier2-scan.feature-flag.test.js` (NEW)

---

### T-011 (GREEN): Implement resolvePrimaryModel with KV-backed feature flag and auto-rollback (ADR 0721-04)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-03, AC-US3-08 | **Status**: [ ] pending
**ADR**: 0721-04

**Implementation**:
1. Add `resolvePrimaryModel(submissionId, config)` to `crawl-worker/lib/tier2-scan.js` per ADR 0721-04 implementation contract.
2. Bucket logic: `parseInt(sha256(submissionId).slice(0, 8), 16) % 100 < pct` selects Qwen3; else Llama 4 Scout.
3. KV fallback: if `RATE_LIMIT_KV` unreachable, default `pct=0`.
4. Auto-rollback: if kill-switch trips during rollout (pct > 0), write `tier2-rollout-pct=0` to KV and emit `tier2_killswitch_tripped` AE event.
5. Run `npx vitest run crawl-worker/lib/__tests__/tier2-scan.feature-flag.test.js` — all green.

**TDD sequence**:
- RED: T-010 tests already written
- GREEN: implement until T-010 tests pass
- REFACTOR: extract sha256 bucket helper into `crawl-worker/lib/sha256-bucket.js`

**Files touched**:
- `crawl-worker/lib/tier2-scan.js`
- `crawl-worker/lib/sha256-bucket.js` (NEW)
- `crawl-worker/lib/__tests__/tier2-scan.feature-flag.test.js`

---

### T-012 (RED): Write failing tests for Qwen3-30B model chain and retry policy (ADR 0721-03)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-04, AC-US3-06 | **Status**: [ ] pending
**ADR**: 0721-03

**Test Plan**:
- Given: mocked Workers AI returns invalid JSON for all Qwen3-30B attempts
- When: `callLlm` runs
- Then: exactly 2 retries occur with 250ms / 750ms gaps, then falls through to Llama 3.3 70B
- Given: all Workers AI models (Qwen3 + 70B) return 503
- When: `callLlm` runs
- Then: falls through to Gemini 2.0 Flash (external fallback is called, Workers AI not called again)
- Given: Neuron consumption simulated past 50k in rolling 24h window
- When: `callLlm` runs
- Then: Workers AI is skipped entirely; only Gemini external is called
- Given: primary model constant is inspected
- When: `PRIMARY_MODEL` value is read
- Then: equals `@cf/qwen/qwen3-30b-a3b-fp8`; `FALLBACK_MODEL` equals `@cf/meta/llama-3.3-70b-instruct-fp8-fast`; Llama 4 Scout constant is absent (AC-US3-01 — post-cleanup)
- Test file: `crawl-worker/lib/__tests__/tier2-scan.model-chain.test.js`
- Test type: unit

**TDD sequence**:
- RED: write test cases; run `npx vitest run crawl-worker/lib/__tests__/tier2-scan.model-chain.test.js` — expect FAIL
- GREEN: implement model chain in T-013
- REFACTOR: n/a

**Files touched**:
- `crawl-worker/lib/__tests__/tier2-scan.model-chain.test.js` (NEW)

---

### T-013 (GREEN): Implement Qwen3-30B model chain, retry policy, kill-switch, and Zod parse (ADR 0721-03)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-04, AC-US3-05, AC-US3-06 | **Status**: [ ] pending
**ADR**: 0721-03

**Implementation**:
1. Update constants in `crawl-worker/lib/tier2-scan.js`: `PRIMARY_MODEL = "@cf/qwen/qwen3-30b-a3b-fp8"`, `FALLBACK_MODEL = "@cf/meta/llama-3.3-70b-instruct-fp8-fast"`. Keep `PRIMARY_MODEL_SCOUT` temporarily for the 48h ramp (removed in T-026).
2. Implement `callWithRetry(callFn, model, label)` with `RETRY_DELAYS_MS = [250, 750]` per ADR 0721-03 implementation contract.
3. Implement `callLlm` chain: kill-switch check → `resolvePrimaryModel` → primary → 70B fallback → Gemini external.
4. Implement `isKillSwitchTripped(config)`: reads `tier2-neurons-day:YYYY-MM-DD` from `RATE_LIMIT_KV`; returns true if >= 50,000.
5. Replace `text.match(/\{[\s\S]*\}/)` at line 161 with `TIER2_ZOD_SCHEMA.safeParse(JSON.parse(text))`; on failure return typed error (not throw) — also fixes AC-US3-05.
6. Define `TIER2_SCHEMA` json_schema object and `TIER2_ZOD_SCHEMA` Zod mirror per ADR 0721-03.
7. Run `npx vitest run crawl-worker/lib/__tests__/tier2-scan.model-chain.test.js` — all green.

**TDD sequence**:
- RED: T-012 tests already written
- GREEN: implement until T-012 tests pass
- REFACTOR: consolidate retry into a single `callWithRetry` helper

**Files touched**:
- `crawl-worker/lib/tier2-scan.js`
- `crawl-worker/lib/__tests__/tier2-scan.model-chain.test.js`

---

### T-014 (RED): Write failing tests for json_schema response mode and Zod validator (ADR 0721-03)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-05 | **Status**: [ ] pending
**ADR**: 0721-03

**Test Plan**:
- Given: a malformed-but-recoverable JSON response (e.g., trailing comma, wrapped in prose)
- When: `parseAnalysisResponse(raw)` is called
- Then: the Zod validator returns `{ success: false, error: ZodError }` — no thrown exception, no discarded completion
- Given: a valid JSON response matching `TIER2_SCHEMA`
- When: `parseAnalysisResponse(raw)` is called
- Then: returns `{ success: true, data: { verdict, score, concerns, ... } }`
- Test file: `crawl-worker/lib/__tests__/tier2-scan.parse.test.js`
- Test type: unit

**TDD sequence**:
- RED: write test cases; run `npx vitest run crawl-worker/lib/__tests__/tier2-scan.parse.test.js` — expect FAIL
- GREEN: T-013 implementation covers this; fix any gaps
- REFACTOR: n/a

**Files touched**:
- `crawl-worker/lib/__tests__/tier2-scan.parse.test.js` (NEW)

---

### T-015 (RED): Write failing tests for AI Gateway cache key and headers (ADR 0721-02)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-07 | **Status**: [ ] pending
**ADR**: 0721-02

**Test Plan**:
- Given: a tier-2 scan call with any content shape
- When: `callModelViaGateway` constructs the outgoing fetch request
- Then: headers include `cf-aig-cache-key` matching `/^[a-f0-9]{64}$/` and `cf-aig-cache-ttl: 2592000` (AC-US4-01)
- Given: two calls with identical body + SCANNER_VERSION + SYSTEM_PROMPT_VERSION
- When: cache keys are computed
- Then: the two keys are identical
- Given: `wrangler.jsonc` is parsed
- When: `TIER2_AI_GATEWAY_SLUG` is searched
- Then: it is referenced as a secret binding — no plaintext slug literal (AC-US4-02)
- Given: any content shape
- When: the `cf-aig-cache-key` header value is inspected
- Then: it matches `/^[a-f0-9]{64}$/` and contains no substring of the raw content (AC-US4-07)
- Test file: `crawl-worker/lib/__tests__/tier2-scan.cache-key.test.js`
- Test type: unit

**TDD sequence**:
- RED: write test cases; run `npx vitest run crawl-worker/lib/__tests__/tier2-scan.cache-key.test.js` — expect FAIL
- GREEN: implement `callModelViaGateway` and `buildCacheKey` in T-016
- REFACTOR: n/a

**Files touched**:
- `crawl-worker/lib/__tests__/tier2-scan.cache-key.test.js` (NEW)

---

### T-016 (GREEN): Implement AI Gateway wrapper — callModelViaGateway and buildCacheKey (ADR 0721-02)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-07 | **Status**: [ ] pending
**ADR**: 0721-02

**Implementation**:
1. Implement `buildCacheKey(body)` in `tier2-scan.js`: `sha256(body + |v${SCANNER_VERSION}|p${SYSTEM_PROMPT_VERSION})` returning 64-char hex.
2. Implement `callModelViaGateway(model, messages, config)` with URL `https://gateway.ai.cloudflare.com/v1/${config.cfAccountId}/${config.aiGatewaySlug}/workers-ai/${model}` and `cf-aig-cache-key` / `cf-aig-cache-ttl: 2592000` headers per ADR 0721-02 implementation contract.
3. Read `aiGatewaySlug` from `TIER2_AI_GATEWAY_SLUG` env var (default `tier2-scan-gateway`).
4. Update `wrangler.jsonc`: add `ai_gateway` binding for Workers-side paths (reserved for future migration); ensure `TIER2_AI_GATEWAY_SLUG` is a Cloudflare secret binding (no plaintext).
5. Add `TIER2_AI_GATEWAY_SLUG` documentation to `crawl-worker/.env.vm1.example`, `.env.vm2.example`, `.env.vm3.example`.
6. Run `npx vitest run crawl-worker/lib/__tests__/tier2-scan.cache-key.test.js` — all green.

**TDD sequence**:
- RED: T-015 tests already written
- GREEN: implement until T-015 tests pass
- REFACTOR: move sha256 utility to shared `crawl-worker/lib/crypto.js`

**Files touched**:
- `crawl-worker/lib/tier2-scan.js`
- `crawl-worker/lib/crypto.js` (NEW or extend)
- `crawl-worker/.env.vm1.example`, `.env.vm2.example`, `.env.vm3.example`
- `wrangler.jsonc`

---

### T-017 (RED): Write failing integration tests for AI Gateway cache hit path (ADR 0721-02)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03, AC-US4-04, AC-US4-05 | **Status**: [ ] pending
**ADR**: 0721-02

**Test Plan**:
- Given: two identical scans of the same content (Miniflare)
- When: the second scan runs
- Then: the response carries `cf-aig-cache-status: HIT` metadata, and the AE event has `cache_hit=true`
- Given: SCANNER_VERSION bumped between first and second scan of identical content
- When: the second scan runs
- Then: the response is a cache MISS (AC-US4-04)
- Given: >= 20 cache-hit scans run
- When: p95 latency is measured
- Then: p95 <= 200ms (AC-US4-05)
- Test file: `crawl-worker/lib/__tests__/tier2-scan.cache-integration.test.js`
- Test type: integration (Miniflare)

**TDD sequence**:
- RED: write test cases; run `npx vitest run crawl-worker/lib/__tests__/tier2-scan.cache-integration.test.js` — expect FAIL
- GREEN: T-016 covers cache-key construction; additional wiring for cache-hit metadata handling may be needed
- REFACTOR: n/a

**Files touched**:
- `crawl-worker/lib/__tests__/tier2-scan.cache-integration.test.js` (NEW)

---

### T-018 (RED): Write failing tests for Workers Analytics Engine tier2_scan_completed event
**User Story**: US-003, US-004 | **Satisfies ACs**: AC-US3-07, AC-US4-03, AC-US4-06 | **Status**: [ ] pending

**Test Plan**:
- Given: a successful tier-2 scan completes
- When: AE writes are inspected (Miniflare integration)
- Then: a `tier2_scan` dataset event is captured with all five fields: `model_id`, `cache_hit`, `latency_ms`, `neurons_used`, `verdict`
- Given: a kill-switch trip during active Qwen3 rollout
- When: the auto-rollback trigger fires
- Then: `tier2_killswitch_tripped` AE event is emitted and `tier2-rollout-pct` KV key is set to `0`
- Test file: `src/app/api/v1/internal/finalize-scan/__tests__/ae-event.test.ts`
- Test type: integration (Miniflare)

**TDD sequence**:
- RED: write test cases; run `npx vitest run src/app/api/v1/internal/finalize-scan/__tests__/ae-event.test.ts` — expect FAIL
- GREEN: implement AE emission in T-019
- REFACTOR: n/a

**Files touched**:
- `src/app/api/v1/internal/finalize-scan/__tests__/ae-event.test.ts` (NEW)

---

### T-019 (GREEN): Implement tier2_scan_completed AE event emission in finalize-scan/route.ts
**User Story**: US-003, US-004 | **Satisfies ACs**: AC-US3-07, AC-US3-08, AC-US4-03, AC-US4-06 | **Status**: [ ] pending

**Implementation**:
1. In `src/app/api/v1/internal/finalize-scan/route.ts`, after the `prisma.$transaction` block, call `emitAnalyticsEvent("tier2_scan_completed", { model_id, cache_hit, latency_ms, neurons_used, verdict, parse_retry_count, promotion_applied })` using new AE dataset name `tier2_scan`.
2. Extend `Tier2Payload` interface with optional fields `cacheHit`, `neuronsUsed`, `parseRetryCount`.
3. Wire `aiGatewaySlug` from `TIER2_AI_GATEWAY_SLUG` into the scanner config object in `crawl-worker/sources/submission-scanner.js`.
4. Emit `tier2_killswitch_tripped` AE event from `isKillSwitchTripped` when the 50k threshold is crossed and auto-rollback fires.
5. Run `npx vitest run src/app/api/v1/internal/finalize-scan/__tests__/ae-event.test.ts` — all green.

**TDD sequence**:
- RED: T-018 tests already written
- GREEN: implement AE emission until T-018 tests pass
- REFACTOR: deduplicate AE event shape with a `buildTier2AeEvent` helper if the payload is assembled in more than one place

**Files touched**:
- `src/app/api/v1/internal/finalize-scan/route.ts`
- `crawl-worker/sources/submission-scanner.js`
- `src/app/api/v1/internal/finalize-scan/__tests__/ae-event.test.ts`

---

### T-020 (RED): Write failing tests for Neuron budget kill-switch routing (ADR 0721-03)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-06, AC-US3-08 | **Status**: [ ] pending
**ADR**: 0721-03, 0721-04

**Test Plan**:
- Given: KV counter `tier2-neurons-day:YYYY-MM-DD` is set to 50,001
- When: `isKillSwitchTripped(config)` is called
- Then: returns `true`
- Given: kill-switch is tripped
- When: `callLlm` runs
- Then: Workers AI calls are skipped entirely; only Gemini external is called (fetch-call spy — AC-US3-06)
- Given: kill-switch trips during active Qwen3 rollout (pct > 0 in KV)
- When: auto-rollback fires
- Then: `tier2-rollout-pct` in KV is `0` and a `tier2_killswitch_tripped` AE event is emitted (AC-US3-08)
- Test file: `crawl-worker/lib/__tests__/tier2-scan.killswitch.test.js`
- Test type: unit

**TDD sequence**:
- RED: write test cases; run `npx vitest run crawl-worker/lib/__tests__/tier2-scan.killswitch.test.js` — expect FAIL
- GREEN: T-013 and T-011 cover the implementation; fix any gaps until tests pass
- REFACTOR: n/a

**Files touched**:
- `crawl-worker/lib/__tests__/tier2-scan.killswitch.test.js` (NEW)

---

## Phase C — UX Clarification (US-005)

### T-021 (RED): Write failing component tests for TrustBadge T2 PARTIAL label and tooltip (ADR 0721-05)
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-06 | **Status**: [ ] pending
**ADR**: 0721-05

**Test Plan**:
- Given: a skill at trust tier `T2`
- When: `TrustBadge` renders
- Then: visible text is `T2 PARTIAL` (not `T2 BASIC`) — AC-US5-01
- Given: the rendered `T2 PARTIAL` badge
- When: the `title` attribute is read
- Then: equals exactly `Pattern scan complete; deep LLM verification pending` — AC-US5-02
- Given: all other tiers rendered (T0, T1, T3, T4)
- When: badge labels are checked
- Then: `BLOCKED`, `UNSCANNED`, `VERIFIED`, `CERTIFIED` — unchanged
- Given: before/after visual snapshots of the badge
- When: pixel-diffed
- Then: non-text pixel diff = 0 (no layout reflow, no color change) — AC-US5-06
- Test file: `src/app/components/__tests__/TrustBadge.test.tsx`
- Test type: unit (component snapshot + title attribute assertion)

**TDD sequence**:
- RED: write test cases; run `npx vitest run src/app/components/__tests__/TrustBadge.test.tsx` — expect FAIL on `T2 PARTIAL` assertion
- GREEN: implement label change in T-022
- REFACTOR: n/a

**Files touched**:
- `src/app/components/__tests__/TrustBadge.test.tsx` (NEW or update existing)

---

### T-022 (GREEN): Update TrustBadge.tsx — T2 BASIC to T2 PARTIAL with tooltip (ADR 0721-05)
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-06 | **Status**: [ ] pending
**ADR**: 0721-05

**Implementation**:
1. In `src/app/components/TrustBadge.tsx` (lines 7-16), update `TRUST_TIERS` per ADR 0721-05 implementation contract:
   - `T2: { label: "PARTIAL", tooltip: "Pattern scan complete; deep LLM verification pending", cssVar: "var(--trust-t2)" }`
   - Add `tooltip` field to all other tiers (T0, T1, T3, T4) per ADR 0721-05.
2. Add `title={config.tooltip}` to the rendered `<span>`. If a richer `Tooltip` component exists, assess and use it.
3. Run `grep -rn '"BASIC"' src/` — confirm zero remaining references.
4. Run `npx vitest run src/app/components/__tests__/TrustBadge.test.tsx` — all green.

**TDD sequence**:
- RED: T-021 tests already written
- GREEN: implement label change until T-021 tests pass
- REFACTOR: extract `BadgeTooltip` sub-component only if it genuinely simplifies the main component

**Files touched**:
- `src/app/components/TrustBadge.tsx`
- `src/app/components/__tests__/TrustBadge.test.tsx`

---

### T-023 (RED): Write failing tests for SAST gate label rename on skill detail page (ADR 0721-05)
**User Story**: US-005 | **Satisfies ACs**: AC-US5-03, AC-US5-04 | **Status**: [ ] pending
**ADR**: 0721-05

**Test Plan**:
- Given: a skill page with `ExternalScanResult` rows for tier 1 PASS and tier 2 PASS
- When: the page renders
- Then: ScanChip labels read `Static Scan PASS` and `Deep Scan PASS` (not `Tier 1 PASS` / `Tier 2 PASS`) — AC-US5-03
- Given: tier 1 FAIL, tier 2 with no result
- When: the page renders
- Then: labels read `Static Scan FAIL` and `Deep Scan --`
- Given: `npx prisma migrate status` is run after implementation
- When: output is inspected
- Then: zero new migrations reported — AC-US5-04
- Test file: `src/app/skills/[owner]/[repo]/[skill]/__tests__/ScanChipLabels.test.tsx`
- Test type: unit (component snapshot)

**TDD sequence**:
- RED: write test cases; run `npx vitest run 'src/app/skills/**/__tests__/ScanChipLabels.test.tsx'` — expect FAIL
- GREEN: implement label change in T-024
- REFACTOR: n/a

**Files touched**:
- `src/app/skills/[owner]/[repo]/[skill]/__tests__/ScanChipLabels.test.tsx` (NEW)

---

### T-024 (GREEN): Update skill detail page — SAST gate labels Tier 1/2 to Static/Deep Scan (ADR 0721-05)
**User Story**: US-005 | **Satisfies ACs**: AC-US5-03, AC-US5-04 | **Status**: [ ] pending
**ADR**: 0721-05

**Implementation**:
1. In `src/app/skills/[owner]/[repo]/[skill]/page.tsx`, update lines 362-363 per ADR 0721-05 implementation contract:
   - `<ScanChip label="Static Scan" status={tier1Pass ? "PASS" : "FAIL"} score={skill.certScore} />`
   - `<ScanChip label="Deep Scan" status={tier2Pass ? "PASS" : "--"} />`
2. Keep `tier1Pass` / `tier2Pass` TypeScript variable names unchanged (refactoring is out-of-scope).
3. Run `npx prisma migrate status` — confirm zero new migrations.
4. Run `npx vitest run 'src/app/skills/**/__tests__/ScanChipLabels.test.tsx'` — all green.

**TDD sequence**:
- RED: T-023 tests already written
- GREEN: implement label change until T-023 tests pass
- REFACTOR: n/a

**Files touched**:
- `src/app/skills/[owner]/[repo]/[skill]/page.tsx`
- `src/app/skills/[owner]/[repo]/[skill]/__tests__/ScanChipLabels.test.tsx`

---

## Phase D — Verification and Closure

### T-025: Full pipeline integration test — submission to T3 VERIFIED
**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US4-03 | **Status**: [ ] pending

**Test Plan**:
- Given: a fixture skill submission entering the pipeline (tier1 → tier2 → finalize-scan)
- When: the full flow completes
- Then: `Skill.trustTier='T3'`, a `ScanResult.tier=2` row exists, and a `tier2_scan_completed` AE event was emitted with all 5 required fields
- Test file: `src/lib/trust/__tests__/trust-updater.in-tx.test.ts` (extend with full-pipeline test case)
- Test type: integration (Miniflare)

**Implementation**:
1. Extend `trust-updater.in-tx.test.ts` with a full-pipeline scenario: fixture `Submission` → tier-1 result → tier-2 PASS result → `finalize-scan` POST.
2. Assert final state: `Skill.trustTier='T3'`, `ScanResult.tier=2` exists, AE event captured with all 5 fields.
3. Run `npx vitest run src/lib/trust/__tests__/trust-updater.in-tx.test.ts` — all green.

**TDD sequence**:
- RED: add new full-pipeline test case to existing file
- GREEN: confirm integration passes end-to-end
- REFACTOR: extract fixture builder helpers if reused across test cases

**Files touched**:
- `src/lib/trust/__tests__/trust-updater.in-tx.test.ts`

---

### T-026: E2E test (Playwright) — hyperframes renders T3 VERIFIED and new SAST labels (after backfill)
**User Story**: US-005 | **Satisfies ACs**: AC-US5-05, AC-US5-06 | **Status**: [ ] pending

**Test Plan**:
- Given: T-007 backfill has completed for hyperframes
- When: Playwright loads `https://verified-skill.com/skills/heygen-com/hyperframes/hyperframes`
- Then: trust badge text is `T3 VERIFIED`, and SAST gate rows show `Static Scan PASS` and `Deep Scan PASS` — AC-US5-05
- Given: sweep of rendered skill pages
- When: badge text is checked via `page.locator('"T2 BASIC"').count()`
- Then: count = 0 (no `T2 BASIC` strings remain) — AC-US5-06 sweep
- Test file: `tests/e2e/tier2-restoration.spec.ts`
- Test type: e2e (Playwright)

**Implementation**:
1. Create `tests/e2e/tier2-restoration.spec.ts`:
   - Test 1: load hyperframes skill page, assert `T3 VERIFIED` badge text and `Static Scan PASS` + `Deep Scan PASS` ScanChip labels.
   - Test 2: load skills listing page, assert `page.getByText('T2 BASIC').count()` = 0.
2. Run `npx playwright test tests/e2e/tier2-restoration.spec.ts` — all green.

**TDD sequence**:
- RED: write spec before running against live; first run will fail until T-007 and T-022/T-024 are live
- GREEN: confirms backfill + UI changes all landed
- REFACTOR: n/a

**Files touched**:
- `tests/e2e/tier2-restoration.spec.ts` (NEW)

---

### T-027: Llama 4 Scout cleanup — remove from model chain after 48h at 100% (ADR 0721-04)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [ ] pending
**ADR**: 0721-04

**Test Plan**:
- Given: `tier2-rollout-pct=100` has been stable for 48h with no auto-rollback events
- When: `PRIMARY_MODEL_SCOUT` constant and related bucket code are removed from `tier2-scan.js`
- Then: `npx vitest run crawl-worker/lib/__tests__/tier2-scan.model-chain.test.js` passes with Llama 4 Scout absent
- Test file: `crawl-worker/lib/__tests__/tier2-scan.model-chain.test.js` (update to assert Scout absent)
- Test type: unit

**Implementation**:
1. Confirm 48h ramp at 100% completed with no rollback events in AE dashboard.
2. Remove `PRIMARY_MODEL_SCOUT` constant from `tier2-scan.js`.
3. Remove `resolvePrimaryModel` KV lookup (replace with hard-coded `@cf/qwen/qwen3-30b-a3b-fp8` primary).
4. Delete `tier2-rollout-pct` KV key via `wrangler kv:key delete`.
5. Update model-chain test to assert Llama 4 Scout constant absent.
6. Run `npx vitest run crawl-worker/lib/__tests__/tier2-scan.model-chain.test.js` — all green.

**TDD sequence**:
- RED: update test to assert Scout absent (will fail while Scout still in file)
- GREEN: remove Scout code until test passes
- REFACTOR: simplify `callLlm` now that `resolvePrimaryModel` is no longer needed

**Files touched**:
- `crawl-worker/lib/tier2-scan.js`
- `crawl-worker/lib/__tests__/tier2-scan.model-chain.test.js`

---

### T-028: Full unit + integration test suite run and coverage gate
**User Story**: US-001, US-002, US-003, US-004, US-005 | **Satisfies ACs**: (all ACs — coverage gate) | **Status**: [ ] pending

**Test Plan**:
- Given: all implementation tasks complete (T-003 through T-027)
- When: `npx vitest run --coverage` is executed
- Then: coverage for all changed files >= 90%
- When: `npx playwright test` runs
- Then: all E2E tests pass
- Test file: all test files created in this increment
- Test type: coverage gate + E2E gate

**Implementation**:
1. Run `npx vitest run --coverage` from `repositories/anton-abyzov/vskill-platform/`.
2. Run `npx vitest run --coverage` from `crawl-worker/` for scanner-side tests.
3. If any changed file is below 90% coverage, add missing tests before proceeding.
4. Run `npx playwright test tests/e2e/tier2-restoration.spec.ts`.

**Files touched**:
- No new source files; confirms coverage thresholds.

---

### T-029: Code-review report (sw:code-reviewer)
**User Story**: US-001, US-002, US-003, US-004, US-005 | **Satisfies ACs**: (closure gate) | **Status**: [ ] pending

**Test Plan**:
- Given: all implementation tasks complete
- When: `/sw:code-reviewer` runs
- Then: `code-review-report.json` is produced with zero critical / high / medium findings
- Test file: `.specweave/increments/0721-tier2-llm-scan-restoration-and-clarity/reports/code-review-report.json`
- Test type: automated quality gate

**Implementation**:
1. Run `/sw:code-reviewer` against all changed files in this increment.
2. Fix any critical/high/medium findings (max 3 fix iterations per CLAUDE.md).
3. Run `/simplify` after code-review passes.

**Files touched**:
- `.specweave/increments/0721-tier2-llm-scan-restoration-and-clarity/reports/code-review-report.json` (auto-generated)

---

### T-030: Grill report (sw:grill)
**User Story**: US-001, US-002, US-003, US-004, US-005 | **Satisfies ACs**: (closure gate) | **Status**: [ ] pending

**Test Plan**:
- Given: code-review report has zero critical/high/medium findings
- When: `/sw:grill` runs
- Then: `grill-report.json` is produced
- Test file: `.specweave/increments/0721-tier2-llm-scan-restoration-and-clarity/reports/grill-report.json`
- Test type: automated quality gate

**Implementation**:
1. Run `/sw:grill` against this increment.

**Files touched**:
- `.specweave/increments/0721-tier2-llm-scan-restoration-and-clarity/reports/grill-report.json` (auto-generated)

---

### T-031: Judge-LLM report (sw:judge-llm)
**User Story**: US-001, US-002, US-003, US-004, US-005 | **Satisfies ACs**: (closure gate) | **Status**: [ ] pending

**Test Plan**:
- Given: grill report exists
- When: `/sw:judge-llm` runs
- Then: `judge-llm-report.json` is produced (or waived if consent denied)
- Test file: `.specweave/increments/0721-tier2-llm-scan-restoration-and-clarity/reports/judge-llm-report.json`
- Test type: automated quality gate

**Implementation**:
1. Run `/sw:judge-llm` against this increment.

**Files touched**:
- `.specweave/increments/0721-tier2-llm-scan-restoration-and-clarity/reports/judge-llm-report.json` (auto-generated)

---

### T-032: Final closure (sw:done 0721)
**User Story**: US-001, US-002, US-003, US-004, US-005 | **Satisfies ACs**: (all 36 ACs — final gate) | **Status**: [ ] pending

**Test Plan**:
- Given: all T-001 through T-031 tasks are marked `[x]`
- When: `/sw:done 0721` runs
- Then: increment is closed and synced to GitHub `anton-abyzov/vskill-platform`, JIRA `SWE2E`, ADO `EasyChamp/SpecWeaveSync`
- Test file: n/a
- Test type: closure gate

**Implementation**:
1. Confirm all tasks `[x]` in this file.
2. Confirm all 36 ACs `[x]` in `spec.md`.
3. Run `/sw:done 0721`.

**Files touched**:
- `.specweave/increments/0721-tier2-llm-scan-restoration-and-clarity/metadata.json` (status → closed)

---

## AC Coverage Map

| AC | Task(s) |
|---|---|
| AC-US1-01 | T-001, T-002, T-003 |
| AC-US1-02 | T-004, T-005 |
| AC-US1-03 | T-004, T-005, T-006 |
| AC-US1-04 | T-004, T-005, T-006, T-007 |
| AC-US1-05 | T-004, T-005 |
| AC-US1-06 | T-005, T-007 |
| AC-US1-07 | T-002, T-003 |
| AC-US2-01 | T-008, T-009 |
| AC-US2-02 | T-008, T-009 |
| AC-US2-03 | T-008, T-009 |
| AC-US2-04 | T-008, T-009 |
| AC-US2-05 | T-008, T-009 |
| AC-US2-06 | T-008, T-009 |
| AC-US2-07 | T-009 (ADR existence verified at closure) |
| AC-US3-01 | T-012, T-013, T-027 |
| AC-US3-02 | T-010, T-011 |
| AC-US3-03 | T-010, T-011 |
| AC-US3-04 | T-012, T-013 |
| AC-US3-05 | T-014, T-013 |
| AC-US3-06 | T-020, T-013 |
| AC-US3-07 | T-018, T-019 |
| AC-US3-08 | T-011, T-018, T-020 |
| AC-US4-01 | T-015, T-016 |
| AC-US4-02 | T-015, T-016 |
| AC-US4-03 | T-017, T-018, T-019, T-025 |
| AC-US4-04 | T-017 |
| AC-US4-05 | T-017 |
| AC-US4-06 | T-018, T-019 |
| AC-US4-07 | T-015, T-016 |
| AC-US5-01 | T-021, T-022 |
| AC-US5-02 | T-021, T-022 |
| AC-US5-03 | T-023, T-024 |
| AC-US5-04 | T-023, T-024 |
| AC-US5-05 | T-026 |
| AC-US5-06 | T-021, T-022, T-026 |
