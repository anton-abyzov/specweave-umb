---
increment: 0721-tier2-llm-scan-restoration-and-clarity
title: "Tier-2 LLM Scan Restoration, Cost Optimization, and Trust-Tier Label Clarification"
type: bug
priority: P0
status: planned
created: 2026-04-25
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Tier-2 LLM Scan Restoration, Cost Optimization, and Trust-Tier Label Clarification

## Overview

The verified-skill.com tier-2 LLM scanner stopped writing `ScanResult` rows on **2026-03-26**, leaving every skill submitted in the last 30 days (including the visible-symptom case `heygen-com/hyperframes/hyperframes`) stuck at trust tier `T2 BASIC` with no path to promotion. The trust-ladder promotion gate at `src/lib/trust/trust-score.ts:184-190` requires a tier-2 PASS or CONCERNS row that no longer exists; the badge label `T2 BASIC` itself misrepresents a *partial* scan state as a stable end-state; and the pre-outage scanner used Llama 4 Scout primary at $1.56/1k scans with no caching, ~30× more expensive than necessary.

This increment restores the pipeline, backfills the 30-day dead window, swaps the primary model to `@cf/qwen/qwen3-30b-a3b-fp8` behind a feature flag with AI Gateway exact-match caching (target effective cost ~$0.05/1k), inlines the T2→T3 promotion into the `ScanResult` write transaction so promotion is deterministic without a separate cron, and clarifies two coincidentally-overloaded "Tier" labels on the public skill page.

**Source materials**:
- Pre-approved plan: `~/.claude/plans/jaunty-gliding-sunrise.md` (decision matrix, root-cause hypothesis, file map)
- Increment plan: `plan.md` (component design, sequence diagram, migration strategy, rollback plan)
- Deep interview state: `.specweave/state/interview-0721-tier2-llm-scan-restoration-and-clarity.json` (8 resolved decisions across architecture / integrations / UI-UX / performance / security / edge-cases)
- ADRs (`.specweave/docs/internal/architecture/adr/`):
  - `0721-01-in-transaction-trust-tier-recompute.md` — promotion safety net (in-transaction vs cron)
  - `0721-02-ai-gateway-cache-key-strategy.md` — `sha256(body + SCANNER_VERSION + SYSTEM_PROMPT_VERSION)`, 30d TTL
  - `0721-03-model-fallback-chain.md` — Qwen3-30B → Llama 3.3 70B → Gemini 2.0 Flash + 50k Neuron/day kill-switch
  - `0721-04-feature-flagged-rollout.md` — KV-backed `tier2-rollout-pct`, 10/25/50/100% over 48h
  - `0721-05-trust-tier-label-semantics.md` — T2 PARTIAL + Static/Deep Scan chip labels

**Hard dependency**: `0713-queue-pipeline-restoration` must ship first. Tier-2 starvation is most likely a downstream consequence of the broken submission queue 0713 fixes (RECEIVED rows never advance → scanner never receives work). The 2026-03-26 cliff coincides with the 0708 stats-cron freeze that 0713 traces. **Backfill is gated on 0713 closure.** Diagnosis (US-001 AC-US1-01) may begin in parallel; restoration verification cannot complete until 0713 is live.

**Type / priority / WIP**: type `bug` qualifies for the WIP override (currently 3/3 active). Priority **P0** because every skill submitted since 2026-03-26 is stuck at the wrong trust tier — this is a production correctness bug, not an enhancement.

## Personas

- **Platform Operator (primary)** — Owns scanner uptime, Workers AI cost, and the AI Gateway dashboard. Needs reliable scans, observable cost, and a kill-switch when something goes sideways. Primary user of US-001, US-002, US-003, US-004.
- **Skill Author (secondary)** — Submits a skill and watches the trust badge progress from `T1 UNSCANNED` → `T2 PARTIAL` → `T3 VERIFIED`. Needs the badge to honestly represent scan state. Primary user of US-005.
- **Security Reviewer (tertiary)** — Reviews skills the scanner flagged as `CONCERNS`. Needs the verdict surfaced consistently and the SAST gate labels not confused with the trust ladder. Affected by US-002, US-005.

---

## User Stories

### US-001: Restore Tier-2 LLM scan pipeline (P0)
**Project**: vskill-platform

**As a** Platform Operator
**I want** the tier-2 LLM scanner to resume producing `ScanResult` rows and to backfill the 30-day dead window
**So that** every skill submitted since 2026-03-26 (including hyperframes) gets a tier-2 verdict and can be promoted past `T2 PARTIAL`

**Acceptance Criteria**:
- [ ] **AC-US1-01**: A diagnosis report artifact at `.specweave/increments/0721-tier2-llm-scan-restoration-and-clarity/reports/cliff-diagnosis.md` confirms or refutes the queue-starvation hypothesis. The report enumerates checks for (a) Workers AI quota exhaustion on the relevant CF account, (b) `cfAccountId` / `cfApiToken` drift across `crawl-worker/.env.vm{1,2,3}`, (c) JSON-parse failure rate spike at `crawl-worker/lib/tier2-scan.js:202`, and (d) downstream queue starvation from 0708/0713. Each check has a verdict (CONFIRMED / REFUTED / INCONCLUSIVE) with evidence (query results, log snippets, or env-diff output).
- [ ] **AC-US1-02**: `crawl-worker/scripts/backfill-tier2.js` exists and is idempotent — re-running it on the same set of skills does not duplicate `ScanResult` rows. Idempotency is enforced by skipping any `Submission` whose `Skill` already has a `ScanResult` with `tier=2 AND createdAt > '2026-04-25'` (cutover date).
- [ ] **AC-US1-03**: The backfill script accepts `--dry-run` (logs what it would do, writes nothing) and `--rate-limit 1000/hour` (default; configurable). Running with `--dry-run --limit 10` against a fixture DB produces a deterministic plan log.
- [ ] **AC-US1-04**: The backfill script accepts `--priority hyperframes` (or equivalent), which moves `heygen-com/hyperframes/hyperframes` to the head of the queue. After the script processes the priority entry, hyperframes has at least one `ScanResult` row with `tier=2` and a non-null verdict.
- [ ] **AC-US1-05**: The backfill script requires `--confirm` and a valid `INTERNAL_KEY` header to mutate; running without either exits non-zero with a refusal message and writes nothing.
- [ ] **AC-US1-06**: After backfill completes, the diagnostic query `SELECT MAX("createdAt"), COUNT(*) FROM "ScanResult" WHERE tier=2 AND "createdAt" > now() - interval '24 hours'` returns a non-zero count and a `MAX(createdAt)` within the last hour of the scan window. The query is recorded in the diagnosis report as a closing verification.
- [ ] **AC-US1-07**: The submission scanner (`crawl-worker/sources/submission-scanner.js`) emits a structured failure log entry (JSON, with fields `skill_id`, `failure_stage`, `error_class`, `error_message`) every time a tier-2 attempt fails. The log entry is testable from a Vitest unit run with a mocked failure injection.

**Test Plan (per AC)**:
- AC-US1-01: Given a snapshot of `ScanResult` and the three VM `.env` files, when the diagnosis script runs, then `cliff-diagnosis.md` is produced with verdicts for all four checks.
- AC-US1-02: Given a `Submission` row with an existing post-cutover `ScanResult.tier=2`, when backfill runs, then no new `ScanResult` is written and the script logs `skip (already scanned)`.
- AC-US1-03: Given `--dry-run --limit 10`, when backfill runs against fixtures, then the log lists exactly 10 candidate skills and writes zero rows.
- AC-US1-04: Given the priority flag, when backfill runs, then hyperframes is the first `Skill.id` in the processed-order log and has a `tier=2 ScanResult` afterward.
- AC-US1-05: Given backfill invoked without `--confirm`, when the script runs, then it exits with code ≠ 0 and writes zero rows.
- AC-US1-06: Given a freshly backfilled DB, when the verification query runs, then `COUNT(*) > 0` and `MAX(createdAt)` is within the last hour.
- AC-US1-07: Given a forced failure injection (invalid model response), when the scanner runs, then a JSON log entry with all four fields is captured.

---

### US-002: Promotion safety net (T2 → T3 in-transaction) (P0)
**Project**: vskill-platform

**As a** Platform Operator
**I want** a successful tier-2 PASS (or CONCERNS) verdict to deterministically promote a skill from `T2 PARTIAL` to `T3 VERIFIED` within the same DB transaction that writes `ScanResult`
**So that** promotion does not depend on a separate cron job (which is itself the subject of 0708/0713 outages) and partial-state attacks (half-written promotion) become impossible

> Architecture lock: **ADR 0721-01** (`0721-01-in-transaction-trust-tier-recompute.md`). The CONCERNS-promotes-T3 default at `trust-score.ts:184-190` is preserved (verdict-semantics rework explicitly out of scope).

**Acceptance Criteria**:
- [ ] **AC-US2-01**: `src/app/api/v1/internal/finalize-scan/route.ts` invokes `updateSkillTrust()` from `src/lib/trust/trust-updater.ts` *inside* the same Prisma `$transaction` block that writes the `ScanResult` row, per ADR 0721-01. Both writes commit together or both roll back; no intermediate state is observable.
- [ ] **AC-US2-02**: When a tier-2 scan returns verdict `PASS` and the skill's tier-2 `score >= 60`, the `Skill.trustTier` column is upserted from `T2` to `T3` in the same transaction as the `ScanResult` insert. Verified by Miniflare integration test that asserts both rows after a single API call.
- [ ] **AC-US2-03**: When a tier-2 scan returns verdict `CONCERNS` and `score >= 60`, the same T2→T3 promotion fires. (Preserves current `trust-score.ts:184-190` behavior; verdict-semantics rework is explicitly out of scope.) Verified by Miniflare integration test with `verdict='CONCERNS'`.
- [ ] **AC-US2-04**: When a tier-2 scan returns verdict `FAIL` or any scanner-error, the skill's `trustTier` remains at `T2` (no promotion, no auto-block). Verified by Miniflare integration test with `verdict='FAIL'` and a forced-error case.
- [ ] **AC-US2-05**: If the `updateSkillTrust()` call throws inside the transaction, the `ScanResult` insert rolls back. Verified by integration test that injects a throw in `updateSkillTrust` and asserts `ScanResult` count is unchanged.
- [ ] **AC-US2-06**: Concurrent finalize-scan calls for the same `skillId` (same content hash) are idempotent: only one `ScanResult` row exists post-call, and `Skill.trustTier` is `T3` exactly once (no double-write). Verified by an integration test that fires two parallel `finalize-scan` requests with identical payloads.
- [ ] **AC-US2-07**: ADR `0721-01-in-transaction-trust-tier-recompute.md` exists and documents the in-transaction-vs-cron decision, atomicity guarantees, rollback semantics, and the explicit deferral of the verdict-semantics rework (CONCERNS-promotes-T3 default preserved).

**Test Plan (per AC)**:
- AC-US2-01: Given a tier-2 scan completes, when finalize-scan runs, then both `ScanResult` and `Skill.trustTier` writes are observed atomically (test inspects Prisma transaction call shape via spy).
- AC-US2-02: Given verdict=PASS and score=75, when finalize-scan runs, then `Skill.trustTier='T3'` and a tier-2 `ScanResult` row exists.
- AC-US2-03: Given verdict=CONCERNS and score=70, when finalize-scan runs, then `Skill.trustTier='T3'`.
- AC-US2-04: Given verdict=FAIL, when finalize-scan runs, then `Skill.trustTier='T2'` (unchanged).
- AC-US2-05: Given a forced throw in `updateSkillTrust`, when finalize-scan runs, then no `ScanResult` row is committed.
- AC-US2-06: Given two concurrent finalize-scan calls for the same skill, when both complete, then `ScanResult` count = 1 and `Skill.trustTier='T3'`.
- AC-US2-07: Given closure check, when listing ADRs, then `0721-01-in-transaction-trust-tier-recompute.md` exists and references this increment.

---

### US-003: Model swap to Qwen3-30B-A3B-fp8 with feature flag (P1)
**Project**: vskill-platform

**As a** Platform Operator
**I want** to swap the tier-2 primary model from Llama 4 Scout to `@cf/qwen/qwen3-30b-a3b-fp8` behind a feature flag with a graduated rollout and an automatic kill-switch
**So that** I cut unit cost ~84% (uncached) while catching JSON-adherence regressions before they hit 100% of traffic, and a Neuron-budget runaway (e.g., from a malicious mass-submission flood) auto-fails over to Gemini external rather than burning through quota

> Architecture locks: **ADR 0721-03** (model chain + retry policy + 50k Neuron/day kill-switch) and **ADR 0721-04** (KV-backed `tier2-rollout-pct` flag, 10/25/50/100% over 48h, auto-rollback triggers).

**Acceptance Criteria**:
- [ ] **AC-US3-01**: `crawl-worker/lib/tier2-scan.js` model chain (per ADR 0721-03) is updated so the primary is `@cf/qwen/qwen3-30b-a3b-fp8`, fallback is Llama 3.3 70B (`@cf/meta/llama-3.3-70b-instruct-fp8-fast`), and external fallback is Gemini 2.0 Flash (`gemini-2.0-flash`). Llama 4 Scout remains in the file *only* during the 48h rollout ramp as the legacy primary; cleanup removes it (see AC-US3-09).
- [ ] **AC-US3-02**: Primary-model selection is gated behind a runtime KV flag `tier2-rollout-pct` (per ADR 0721-04), stored in `RATE_LIMIT_KV` (or equivalent CF KV namespace named in `plan.md`). The scanner reads the flag on each scan and assigns the submission to the Qwen3 cohort if `bucket(submissionId) < tier2-rollout-pct`. When `tier2-rollout-pct=0`, every scan uses the legacy primary (Llama 4 Scout) until cleanup. Verified by unit test that toggles the KV value and asserts which model is invoked first.
- [ ] **AC-US3-03**: Cohort assignment is deterministic per `submissionId` (a single submission does not flap models between retries within the same scan). The bucket function is `bucket = parseInt(sha256(submissionId).slice(0,8), 16) % 100`. Verified by unit test that fixes `submissionId` and asserts a stable bucket across N invocations.
- [ ] **AC-US3-04**: Invalid-JSON retry policy: 2 retries per model with 250ms / 750ms exponential backoff before fallthrough to the next model in the chain. Total chain budget: Qwen3-30B (2) → Llama 3.3 70B (2) → Gemini 2.0 Flash (1). Verified by unit test with mocked invalid-JSON responses that asserts total fetch-call count and timing pattern.
- [ ] **AC-US3-05**: The regex `text.match(/\{[\s\S]*\}/)` at line 161 is removed and replaced with Workers AI `json_schema`-mode response + Zod re-validation. Parse failures return a typed error rather than throwing-and-discarding the completion. Verified by unit test that feeds a malformed-but-recoverable response and asserts the typed error path.
- [ ] **AC-US3-06**: A Neuron-budget kill-switch trips at 50,000 Neurons consumed in a rolling 24-hour window (counter stored in `RATE_LIMIT_KV`, resets at midnight UTC). When tripped, the model chain skips Workers AI entirely and routes directly to Gemini external. Verified by unit test that simulates Neuron consumption past the threshold and asserts external-only routing.
- [ ] **AC-US3-07**: A `tier2_scan_completed` event is emitted to Workers Analytics Engine on every tier-2 scan with fields `submissionId`, `model_id`, `cache_hit` (boolean), `latency_ms`, `neurons_used`, `parse_retry_count`, `promotionApplied`, `trustTier`, and `verdict`. New AE dataset name `tier2_scan` (separate from existing `UPDATE_METRICS_AE`). Verified by integration test that captures the AE write shape.
- [ ] **AC-US3-08**: Auto-rollback fires (sets `tier2-rollout-pct=0` in KV and emits an alert event) when **any** of these thresholds are breached over a 30-minute rolling window during the ramp: (a) error rate > 5%, (b) p95 latency > 40s, (c) FAIL-verdict rate > 2× the pre-ramp baseline. Per ADR 0721-04. Recovery is manual (no auto-re-ramp) — operator inspects AE dashboard and re-writes the KV value to resume. Verified by unit test that simulates each threshold and asserts the rollback action.
- [ ] **AC-US3-09**: After 48 hours at `tier2-rollout-pct=100` with no auto-rollback triggered, a cleanup commit (Phase B Task 13) removes `PRIMARY_MODEL_SCOUT`, the bucket logic, and the `tier2-rollout-pct` KV branch from `tier2-scan.js`. Llama 4 Scout no longer appears in the codebase. Verified by `grep -r "llama-4-scout" crawl-worker/` returning zero matches and a unit test that asserts the chain is now an unconditional Qwen3 → Llama 3.3 70B → Gemini.

**Test Plan (per AC)**:
- AC-US3-01: Given the model chain, when inspected, then primary='@cf/qwen/qwen3-30b-a3b-fp8', fallback=Llama 3.3 70B, external=Gemini.
- AC-US3-02: Given `tier2-rollout-pct=0`, when scan runs, then Llama 4 Scout (legacy primary) is the first model called; given `tier2-rollout-pct=100`, then Qwen3-30B is the first model called.
- AC-US3-03: Given `submissionId='abc123'`, when bucket() is evaluated 1000 times, then the result is identical across all invocations.
- AC-US3-04: Given mocked invalid-JSON responses on all primary attempts, when scan runs, then exactly 2 retries occur with 250ms/750ms gaps before fallthrough.
- AC-US3-05: Given a malformed JSON response, when scan runs, then the Zod validator returns a typed error (not a thrown exception).
- AC-US3-06: Given Neuron consumption simulated past 50k in 24h, when scan runs, then Workers AI is skipped and Gemini is the only model called.
- AC-US3-07: Given a successful scan, when AE writes are inspected, then a `tier2_scan` event with all 9 required fields is captured.
- AC-US3-08: Given each of (a) error rate > 5%, (b) p95 > 40s, (c) FAIL-verdict 2× baseline simulated independently, when the rollback evaluator runs, then `tier2-rollout-pct=0` is written and an alert event is emitted in each case.
- AC-US3-09: Given the cleanup commit, when grepping the scanner directory, then zero matches for `llama-4-scout`; the chain has no rollout-bucket branching.

---

### US-004: AI Gateway exact-match caching (P1)
**Project**: vskill-platform

**As a** Platform Operator
**I want** identical content (same skill body, same scanner version, same system prompt version) to hit a 30-day cache instead of re-running a full LLM scan
**So that** effective cost on 600k scans/month drops from ~$148 (uncached Qwen3-30B) to ~$30–50 (≥60% cache hit rate after one week of warm traffic), and resubmissions of unchanged skills are sub-200ms

> Architecture lock: **ADR 0721-02** — cache key `sha256(body + SCANNER_VERSION + SYSTEM_PROMPT_VERSION)`, TTL 30 days, slug `tier2-scan-gateway` (default) read from env var `TIER2_AI_GATEWAY_SLUG`.

**Acceptance Criteria**:
- [ ] **AC-US4-01**: All Workers AI `fetch()` calls in `crawl-worker/lib/tier2-scan.js` (`callModel`, `callGeminiModel`, and any equivalent) route through the AI Gateway URL (`https://gateway.ai.cloudflare.com/v1/<accountId>/<gatewaySlug>/workers-ai/<model>`) and set `cf-aig-cache-key: sha256(body + SCANNER_VERSION + SYSTEM_PROMPT_VERSION)` and `cf-aig-cache-ttl: 2592000` (30 days in seconds). Per ADR 0721-02. Verified by unit test that captures outgoing request URL and headers.
- [ ] **AC-US4-02**: The AI Gateway slug is read from env var `TIER2_AI_GATEWAY_SLUG` (default value `tier2-scan-gateway`). On the crawl-worker (Hetzner-hosted) the slug lives in `crawl-worker/.env.vm{1,2,3}` files, never plaintext-committed. The Workers-side `wrangler.jsonc` adds an `ai_gateway` binding (reserved for future Workers-side migration). Verified by config inspection test that the env var is read and that `wrangler.jsonc` references the slug via binding.
- [ ] **AC-US4-03**: A second scan of identical skill content (same `body`, same `SCANNER_VERSION`, same `SYSTEM_PROMPT_VERSION`) yields a cache-hit response. The response carries observable cache-hit metadata (`cf-aig-cache-status: HIT` header from the gateway response) that is logged and emitted to Analytics Engine via the `cache_hit` field of the `tier2_scan_completed` event. Verified by integration test (Miniflare) that runs two scans and asserts the second is a HIT.
- [ ] **AC-US4-04**: Bumping **either** `SCANNER_VERSION` or `SYSTEM_PROMPT_VERSION` invalidates prior cache entries — a re-scan after either version bump is a cache MISS even on identical body content. Verified by two integration tests: one bumps `SCANNER_VERSION`, the other bumps `SYSTEM_PROMPT_VERSION`; both assert MISS on the second scan.
- [ ] **AC-US4-05**: Cache-hit responses end-to-end (including JSON parsing and verdict mapping) complete in p95 ≤ 200ms. Measured by a benchmark test that runs ≥20 cache-hit scans and reports the p95.
- [ ] **AC-US4-06**: Cache hit rate is observable on the AI Gateway dashboard and via the `tier2_scan` AE dataset (queryable by `cache_hit=true / total`). After the first week of post-deploy warm traffic, the hit rate is ≥60% (verified at closure, not at merge-time — closure gate may waive if traffic volume is insufficient with reason recorded).
- [ ] **AC-US4-07**: The cache key never contains raw skill content — only its sha256. Verified by unit test that asserts the outgoing `cf-aig-cache-key` header matches `/^[a-f0-9]{64}$/` regardless of content shape and contains no substrings of the body.
- [ ] **AC-US4-08**: A scanner startup health check probes the AI Gateway URL with a HEAD request; if the gateway returns 404 (slug doesn't exist) or any 5xx, the scanner logs a structured error and emits an alert event before processing any submissions. Verified by unit test that mocks 404 / 5xx responses and asserts alert-emit + refusal-to-process.

**Test Plan (per AC)**:
- AC-US4-01: Given a tier-2 scan, when the Workers AI fetch is captured, then the URL contains the gateway slug path and both `cf-aig-cache-key` and `cf-aig-cache-ttl: 2592000` headers are set.
- AC-US4-02: Given a config inspection, when env vars are read at scanner startup, then `TIER2_AI_GATEWAY_SLUG` resolves to a non-empty string and no plaintext slug literal appears in committed source.
- AC-US4-03: Given two identical scans, when the second runs, then the response is a cache HIT and the `tier2_scan` AE event has `cache_hit=true`.
- AC-US4-04: Given a `SCANNER_VERSION` bump (resp. `SYSTEM_PROMPT_VERSION` bump), when re-scanning identical body, then the response is a cache MISS.
- AC-US4-05: Given ≥20 cache-hit scans, when latencies are measured, then p95 ≤ 200ms.
- AC-US4-06: Given one week of warm traffic, when querying the `tier2_scan` AE dataset, then `sum(cache_hit=true) / count(*) >= 0.60`.
- AC-US4-07: Given any content shape, when the cache key is inspected, then it matches `/^[a-f0-9]{64}$/` and contains no plaintext substrings of the body.
- AC-US4-08: Given a mocked gateway 404 at startup, when the scanner boots, then it emits an alert event and refuses to process the next submission.

---

### US-005: Trust-tier label and SAST gate label clarification (P1)
**Project**: vskill-platform

**As a** Skill Author viewing my own skill page (and as a Security Reviewer reading any skill page)
**I want** the trust badge to honestly say "partially scanned" instead of "basic", and the SAST gate labels to read as scan-stage names instead of overloading the trust-ladder tier numbers
**So that** I understand `T2 PARTIAL` is a transient pre-LLM phase (not a stable end-state) and I do not confuse the SAST `Tier 1/2 PASS` labels with the trust-ladder `T1/T2/T3` levels

> Architecture lock: **ADR 0721-05** — TrustBadge label `T2 BASIC` → `T2 PARTIAL` with tooltip; SAST chips `Tier 1/2` → `Static Scan / Deep Scan`. UI-only; DB semantics unchanged.

**Acceptance Criteria**:
- [ ] **AC-US5-01**: In `src/app/components/TrustBadge.tsx` (lines 7-16, per ADR 0721-05), the `T2` label changes from `T2 BASIC` to `T2 PARTIAL`. Other labels (`T0 BLOCKED`, `T1 UNSCANNED`, `T3 VERIFIED`, `T4 CERTIFIED`) are unchanged. Verified by component snapshot test.
- [ ] **AC-US5-02**: The `T2 PARTIAL` badge shows a tooltip on hover/focus with the exact copy: `Pattern scan complete; deep LLM verification pending` (rendered via the HTML `title` attribute per ADR 0721-05). Verified by component test that asserts the tooltip text node.
- [ ] **AC-US5-03**: In `src/app/skills/[owner]/[repo]/[skill]/page.tsx` (lines ~362-363), the SAST gate labels rendered from `ExternalScanResult.tier` change at the JSX layer only: `Tier 1 PASS` → `Static Scan PASS`, `Tier 2 PASS` → `Deep Scan PASS`. (Same mapping for non-PASS verdicts: `Tier 1 FAIL` → `Static Scan FAIL`, etc.) Verified by component snapshot test.
- [ ] **AC-US5-04**: No data-layer change: `ExternalScanResult.tier` remains an integer (1 or 2), `ScanResult.tier=2` semantics are preserved, no Prisma migration is generated. Verified by `prisma migrate status` showing no new migrations and a schema-diff check showing zero changes.
- [ ] **AC-US5-05**: After backfill (US-001) completes for hyperframes, an E2E Playwright test loads `https://verified-skill.com/skills/heygen-com/hyperframes/hyperframes` and asserts: trust badge text is `T3 VERIFIED` (not `T2 BASIC`), and the SAST gate row shows `Static Scan PASS` and `Deep Scan PASS` (not `Tier 1 PASS` / `Tier 2 PASS`).
- [ ] **AC-US5-06**: No badge color change, no icon change, no layout reflow — text-only swap. Verified by visual-diff snapshot test that asserts pixel diff outside the text box is zero.

**Test Plan (per AC)**:
- AC-US5-01: Given a skill at `T2`, when `TrustBadge` renders, then the visible text is `T2 PARTIAL`.
- AC-US5-02: Given the `T2 PARTIAL` badge, when hovered/focused, then the tooltip text is exactly `Pattern scan complete; deep LLM verification pending`.
- AC-US5-03: Given a skill page with `ExternalScanResult` rows for tier 1 and 2 with verdict PASS, when the page renders, then the labels read `Static Scan PASS` and `Deep Scan PASS`.
- AC-US5-04: Given the schema after this increment, when `prisma migrate status` runs, then zero new migrations are reported.
- AC-US5-05: Given hyperframes post-backfill, when Playwright loads the public skill page, then trust badge = `T3 VERIFIED` and SAST gates = `Static Scan PASS` + `Deep Scan PASS`.
- AC-US5-06: Given before/after screenshots of the skill page, when visual-diffed, then non-text pixel diff = 0.

---

## Functional Requirements

### FR-001: Diagnostic artifact
The cliff-diagnosis report (`reports/cliff-diagnosis.md`) is a permanent artifact of this increment, not a throwaway. It is referenced from `tasks.md` and survives closure as the canonical record of why scans died on 2026-03-26. Useful for future post-mortems and for verifying the queue-starvation hypothesis is not re-introduced.

### FR-002: Idempotent backfill
The backfill script must be safe to re-run. Idempotency is enforced by the cutover-date check (`ScanResult.createdAt > '2026-04-25'`) — scans recorded after backfill begins are not re-processed. Operators may run the script multiple times without fear of duplicate writes or double-billing.

### FR-003: Atomic promotion
Promotion T2 → T3 happens inside the same Prisma `$transaction` that writes `ScanResult`. There is no observable intermediate state where the `ScanResult` row exists but `Skill.trustTier` is still `T2`. This eliminates dependency on the separate cron pattern (which is itself the subject of 0708/0713 outages).

### FR-004: Feature-flagged model rollout
The Qwen3-30B primary is gated behind a runtime KV flag `tier2-rollout-pct` (per ADR 0721-04, stored in `RATE_LIMIT_KV`). Rollout proceeds 10% → 25% → 50% → 100% over 48 hours, with deterministic per-`submissionId` cohort assignment via `sha256(submissionId).slice(0,8) % 100` so a single submission does not flap between models. Auto-rollback fires (sets KV to 0) on error rate >5%, p95 latency >40s, or FAIL-verdict rate >2× baseline over a 30-min window. Recovery is manual — no auto-re-ramp. After 48h at 100% with no rollback, a cleanup commit removes Llama 4 Scout and the rollout-bucket branching from the codebase.

### FR-005: AI Gateway caching wrapper
Cache key = `sha256(body + SCANNER_VERSION + SYSTEM_PROMPT_VERSION)` (per ADR 0721-02). TTL = 30 days. Slug = env var `TIER2_AI_GATEWAY_SLUG` (default `tier2-scan-gateway`). Implemented as headers on the existing `fetch()` calls plus a URL rewrite to the gateway endpoint `https://gateway.ai.cloudflare.com/v1/<accountId>/<gatewaySlug>/workers-ai/<model>`. A scanner startup health check probes the gateway URL; a 404 (slug doesn't exist) emits an alert and refuses to process submissions. The Workers-side `wrangler.jsonc` gains an `ai_gateway` binding reserved for future migration.

### FR-006: Hardened JSON parsing
Replace regex extraction (`text.match(/\{[\s\S]*\}/)`) with Workers AI `json_schema`-mode response + Zod validator. Parse failures return a typed error, not a thrown exception that discards the completion.

### FR-007: Observability
Every tier-2 scan emits a `tier2_scan_completed` event to Workers Analytics Engine (new dataset `tier2_scan`) with fields `submissionId`, `model_id`, `cache_hit`, `latency_ms`, `neurons_used`, `parse_retry_count`, `promotionApplied`, `trustTier`, `verdict`. Cost, latency, retry rate, and promotion outcome become queryable per-scan, not just per-day.

### FR-008: Cost kill-switch
50k Neurons/day rolling cap. On trip, Workers AI is bypassed and Gemini external becomes the sole model. Resets at next 24h boundary or via manual reset. Prevents runaway cost from a flood (e.g., malicious mass-submission).

### FR-009: UI label clarity
Two text-only swaps on user-facing pages: trust badge `T2 BASIC` → `T2 PARTIAL` (with new tooltip); SAST gate labels `Tier 1/2 PASS` → `Static Scan / Deep Scan PASS`. No data-layer change, no schema migration, no layout reflow.

---

## Non-Functional Requirements (NFRs)

### NFR-001: Latency SLO (Tier-2 scan)
- p50 ≤ **8 seconds**
- p95 ≤ **30 seconds**
- p99 ≤ **50 seconds**
- Hard timeout ceiling: **60 seconds** (scan aborts if exceeded)

Measured per-scan via the `tier2_scan_completed` AE event. Reportable on a daily/weekly window.

### NFR-002: Cache-hit latency
- Cache-hit responses (end-to-end including JSON parse + verdict mapping): p95 ≤ **200 ms**

### NFR-003: Cost SLO
- Effective unit cost ≤ **$0.10 / 1k scans** after one week of cache warming
- Target: **~$0.05 / 1k scans** (= ~$30/month at 600k scans/mo with ≥60% cache hit rate)
- Hard cap (kill-switch trips): **50,000 Neurons / day** rolling window → fail over to Gemini

### NFR-004: Cache hit rate
- ≥ **60%** after one week of warm traffic, measurable on AI Gateway dashboard and via the `tier2_scan` AE dataset

### NFR-005: Backfill rate
- ≤ **1,000 scans / hour** by default to spread Workers AI load and respect cache warming. Configurable via `--rate-limit` flag.

### NFR-006: Test coverage
- Coverage target **90%** (matches 0713)
- Unit (Vitest) + Integration (Miniflare) + E2E (Playwright) all required before `/sw:done`
- Strict TDD: every AC has a Test Plan block above; RED before GREEN

### NFR-007: Security
- AI Gateway slug stored as Cloudflare secret (env var `TIER2_AI_GATEWAY_SLUG`), never plaintext in `wrangler.jsonc`
- Backfill requires `--confirm` flag AND valid `INTERNAL_KEY` auth header; refuses to run without both
- Cache key = sha256 hash only (no raw content)
- `finalize-scan` route remains internal-only behind `INTERNAL_KEY`
- In-transaction promotion prevents partial-state attacks (no window where `ScanResult` exists but `Skill.trustTier` lags)

---

## Success Criteria

**Restoration (US-001, US-002)**:
- Diagnostic query `SELECT MAX("createdAt"), COUNT(*) FROM "ScanResult" WHERE tier=2 AND "createdAt" > now() - interval '24 hours'` returns non-zero count after backfill.
- `heygen-com/hyperframes/hyperframes` has at least one `ScanResult.tier=2` row and `Skill.trustTier='T3'` after backfill.
- Public page `https://verified-skill.com/skills/heygen-com/hyperframes/hyperframes` renders trust badge `T3 VERIFIED`.
- Zero observable cases of `ScanResult` written without corresponding `Skill.trustTier` update (or vice versa) — atomicity holds.

**Cost optimization (US-003, US-004)**:
- After one week post-deploy: AI Gateway dashboard cache hit rate ≥ 60%.
- Workers AI dashboard `model_id` filter shows Qwen3-30B as dominant (>80% of non-cached traffic), Llama 3.3 70B as thin tail (<10% fallback), Llama 4 Scout absent (0%).
- Effective unit cost per `tier2_scan` AE event aggregation ≤ $0.10 / 1k scans.
- Neuron-budget kill-switch verified by a synthetic flood test in staging (does not have to fire in production to be considered verified).

**UI clarity (US-005)**:
- E2E Playwright test for hyperframes page passes: badge = `T3 VERIFIED`, SAST gates = `Static Scan PASS` + `Deep Scan PASS`.
- Zero `T2 BASIC` strings remain in the rendered HTML of any skill page (sweep test).
- Zero schema migrations introduced.

**Process**:
- All 36 ACs marked `[x]` in `tasks.md`.
- ADR `0721-in-transaction-promotion.md` exists and is reviewed.
- Code-review report has zero critical/high/medium findings outstanding.
- `/sw:grill` report exists.
- Coverage ≥ 90% for changed files.

---

## Out of Scope

The following are explicitly deferred and **must not** be implemented in this increment:

- **Self-hosting the LLM on Hetzner** — researched in the plan file; verdict: 6×–30× more expensive than Cloudflare cached at our 600k-scans/mo volume. Full research preserved in `~/.claude/plans/jaunty-gliding-sunrise.md` for future revisit if reliability or vendor-independence becomes a goal.
- **Trust-score formula rework** — the `trust-score.ts:184-190` PASS-or-CONCERNS-promotes-T3 logic is preserved as-is. If stricter gating is wanted, that is a follow-up increment.
- **Adding or removing trust tiers** — the T0/T1/T2/T3/T4 ladder structure is unchanged.
- **Changing the SAST scanner itself** — Semgrep config, rule set, and `ExternalScanResult` schema are untouched. This increment changes UI labels only.
- **0712 scanner-outbox retrofit** — different scanner file (`src/lib/skill-update/scanner.ts`, not `crawl-worker/sources/submission-scanner.js`). Tracked in increment 0712 separately.
- **Replacing Llama 3.3 70B as fallback** — kept as-is for proven JSON adherence under load.
- **Migrating `cfAccountId` / `cfApiToken` away from per-VM `.env` files** — verification that they have not drifted is in scope (US-001 AC-US1-01); restructuring secret distribution is not.

---

## Dependencies

### Hard dependencies (blocking)
- **0713-queue-pipeline-restoration** — must ship first. Tier-2 scanner is downstream of the submission queue 0713 fixes; backfill cannot proceed until 0713 is live and the queue is draining cleanly. Diagnosis (US-001 AC-US1-01) may begin in parallel.

### Soft dependencies (informational)
- **0708-skill-update-push-pipeline** — the 2026-03-26 cliff coincides with the 0708 stats-cron freeze. Diagnosis findings should reference 0708 outage history.
- **0712-0708-followups-scanner-outbox-do-alarm-and-e2e** — different scanner file; outbox retrofit pattern may be reusable in a future increment but is not adopted here.
- **`reference_hetzner_vms.md`** (memory) — the 3 crawler VMs hold `cfAccountId` / `cfApiToken`; diagnosis must verify no drift across `crawl-worker/.env.vm{1,2,3}`.

### External services
- **Cloudflare Workers AI** — primary execution surface for Qwen3-30B and Llama 3.3 70B
- **Cloudflare AI Gateway** — exact-match cache wrapper around Workers AI fetch calls
- **Google Gemini 2.0 Flash** — external fallback when Workers AI primary + fallback both fail (or kill-switch trips)
- **Neon Postgres** (via Prisma) — `ScanResult`, `Skill`, `Submission`, `ExternalScanResult` tables
- **Workers Analytics Engine** — new dataset `tier2_scan` for per-scan telemetry

### Sync targets
- **GitHub**: `anton-abyzov/vskill-platform`
- **JIRA**: project `SWE2E`
- **ADO**: `EasyChamp/SpecWeaveSync`

---

## Definition of Done

- [ ] All 5 user stories complete with all ACs marked `[x]` in `tasks.md` (37 ACs total: 7 + 7 + 9 + 8 + 6)
- [ ] Diagnosis report `reports/cliff-diagnosis.md` produced with verdicts for all 4 root-cause checks
- [ ] Backfill script merged, dry-run verified, full backfill executed, hyperframes promoted to `T3 VERIFIED`
- [ ] All 5 ADRs (`0721-01` through `0721-05`) exist in `.specweave/docs/internal/architecture/adr/` and are referenced from the increment
- [ ] Qwen3-30B feature flag at `tier2-rollout-pct=100` for ≥48 hours with no auto-rollback triggered during the ramp
- [ ] Llama 4 Scout cleanup commit landed: zero matches for `llama-4-scout` under `crawl-worker/`; rollout-bucket branching removed
- [ ] AI Gateway cache hit rate ≥ 60% verified one week post-deploy (or waiver recorded with justification)
- [ ] All UI label changes visible on `https://verified-skill.com` and verified by Playwright E2E (`tests/e2e/tier2-restoration.spec.ts`)
- [ ] Unit test coverage ≥ 90% for changed files; Miniflare integration tests pass; Playwright E2E passes
- [ ] `sw:code-reviewer` report has zero critical/high/medium findings outstanding
- [ ] `/simplify` review pass complete
- [ ] `/sw:grill` report written
- [ ] `/sw:judge-llm` report written (or consent denied → waived)
- [ ] Sync to GitHub `anton-abyzov/vskill-platform`, JIRA `SWE2E`, ADO `EasyChamp/SpecWeaveSync`
- [ ] Increment closed via `/sw:done`
