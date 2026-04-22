---
increment: 0672-queue-reliability
title: Queue Reliability — Dedup + Cache Warm-up + Tier-2 ADR
type: bug
priority: P1
status: completed
created: 2026-04-21T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Queue Reliability — Dedup + Cache Warm-up + Tier-2 ADR

## Overview

Fix two user-visible production bugs on [verified-skill.com/queue](https://verified-skill.com/queue):

1. **Empty default render** — `/queue` with no query params shows a blank flash / "No submissions" state on first load. Root cause is an SSR cache miss in `src/app/queue/data.ts:95` combined with lazy-only cache writes in `src/app/api/v1/submissions/route.ts:375`; cold Workers, Neon circuit-breaker trips, and the 60 s TTL leave the KV cache empty during low-traffic windows.
2. **Duplicate rows** — `obsidian-brain` (from `anton-abyzov/vskill`) appears 7+ times on `/queue?q=d`. The `Submission` model in `prisma/schema.prisma:200` carries only `@@index([repoUrl, skillName])` — **no `@@unique` constraint**. App-level dedup in `src/lib/submission-dedup.ts:72` leaks via staleness windows (4 h / 24 h / 48 h), batch-parallel races between concurrent inserts, fail-open on Prisma errors, and multiple ingestion paths (`cli-auto`, web, crawler `submission-scanner`) that each bypass each other.

Fix both by: (a) adding `@@unique([repoUrl, skillName])` plus a collapse-duplicates migration; (b) replacing the multi-branch dedup with an `upsertSubmission` + P2002-catch pattern; (c) populating the KV list cache via an hourly cron warm-up.

In the same increment, produce **ADR only** evaluating Tier-2 LLM scoring runtime choice (stay on Cloudflare Workers AI vs. move to GCP spot VMs). Actual migration is deferred to follow-up increment `0673` if the ADR recommends it.

## Background (production bugs)

**Infra baseline**: Next.js 15 + OpenNext on Cloudflare Workers (`verified-skill-com`); Neon Postgres via Prisma + Neon serverless adapter; 7 CF KV namespaces; `submission-processing` CF Queue; Hetzner VMs running `crawl-worker/server.js` pushing to `/api/v1/webhooks/scan-results`. 10 GCP crawl VMs are stopped since the March cost cleanup; no GCP VMs are currently serving traffic.

**Bug 1 reproducer**: open https://verified-skill.com/queue in an incognito window after a low-traffic period. SSR returns no rows; client-side fetch then populates the list a moment later, producing a visible "No submissions yet" flash.

**Bug 2 reproducer**: open https://verified-skill.com/queue?q=d. The `obsidian-brain` skill appears multiple times (7+ rows observed as of 2026-04-21). The underlying DB rows have distinct `id` values but identical `(repoUrl, skillName)` tuples.

**Scope guardrails (pre-approved)**:
- Tier-2 LLM runtime migration is **out of scope** — this increment produces the ADR only.
- Duplicate-row collapse uses **hard delete** of older rows (keep newest per `(repoUrl, skillName)`), with FK children (`SubmissionStateEvent`, `ScanResult`, `SubmissionJob`, `EmailNotification`, `EvalRun`) re-pointed to the survivor. Archived rows are written to `backups/dedup-collapse-0672.json` for rollback.
- Public `/api/v1/submissions` request schema is **not changed** — CLI pollers continue to send the same payload and receive `{ id, state, duplicate: true }` on known-skill re-submission.

## User Stories

### US-001: Queue renders immediately on first load (P1)
**Project**: vskill-platform

**As an** ops visitor
**I want** to see the queue's active submissions immediately on first load of `/queue` with no query params
**So that** I don't see a blank flash or "No submissions" state before the real data appears.

**Acceptance Criteria**:
- [x] **AC-US1-01**: GET `/queue` with no query params and a cold KV cache renders ≥ 50 active submission rows within p95 < 1.5 s. Measured via Playwright run against a freshly deployed preview worker.
- [x] **AC-US1-02**: After any successful hourly cron run, the following KV keys in the `submissions-cache` namespace are populated with non-empty JSON payloads: `submissions:list:active:::processingOrder:asc:50:0`, `submissions:list:published:::updatedAt:desc:50:0`, `submissions:list:rejected:::updatedAt:desc:50:0`, `submissions:list:blocked:::updatedAt:desc:50:0`, `submissions:list:onHold:::updatedAt:desc:50:0`. Corresponding `submissions:latest:<filter>` fallback keys are also populated.
- [x] **AC-US1-03**: The SSR cache read in `src/app/queue/data.ts` hits on the warmed key when the hourly cron has run within the last 90 minutes — the function returns a non-null result with ≥ 1 row (integration assertion against a wrangler-dev environment with a pre-populated KV).
- [x] **AC-US1-04**: `LIST_CACHE_TTL` is raised from 60 s to 5400 s (90 min), leaving a 30 min buffer past the hourly cron. The change is committed as part of the cache-warm-up task; wrangler env does not override it below 5400 s.

---

### US-002: Queue shows at most one row per skill (P1)
**Project**: vskill-platform

**As an** ops visitor
**I want** the queue to show at most one row per `(repoUrl, skillName)` combination
**So that** I can scan the list without visible duplicates and trust the counts.

**Acceptance Criteria**:
- [x] **AC-US2-01**: The Prisma schema at `repositories/anton-abyzov/vskill-platform/prisma/schema.prisma:200` adds `@@unique([repoUrl, skillName])` to the `Submission` model and drops the now-redundant `@@index([repoUrl, skillName])`. `npx prisma migrate deploy` succeeds end-to-end against a Neon branch seeded with duplicated fixtures, after the collapse step has run.
- [x] **AC-US2-02**: The collapse-duplicates script at `scripts/migrations/0672-collapse-submission-dupes.ts` keeps the newest row per `(repoUrl, skillName)` (max `createdAt` wins); re-points `SubmissionStateEvent.submissionId`, `ScanResult.submissionId`, `SubmissionJob.submissionId`, `EmailNotification.submissionId`, and `EvalRun.submissionId` from victim rows to the survivor; archives each deleted row plus its children (full JSON snapshot) to `.specweave/increments/0672-queue-reliability/backups/dedup-collapse-0672.json`; and runs entirely inside a single Prisma transaction so partial FK re-points cannot occur.
- [x] **AC-US2-03**: The collapse script is **idempotent**: a second invocation against the same (post-collapse) DB performs zero deletions, re-points zero children, and writes an archive entry of `{ "deleted": 0 }`.
- [x] **AC-US2-04**: After migration deploys to production, GET `/queue?q=<any prefix>` shows exactly one row for any given `(repoUrl, skillName)` combination. Playwright asserts this for the `obsidian-brain` / `anton-abyzov/vskill` case specifically.
- [x] **AC-US2-05**: A rollback script at `scripts/migrations/0672-restore-submission-dupes.ts` can read the archive JSON and recreate deleted rows + children. Exercised on a Neon branch post-collapse — row count and FK targets match the pre-collapse snapshot.

---

### US-003: CLI re-submission stays idempotent (P1)
**Project**: vskill-platform

**As a** CLI user running `vskill install`
**I want** a re-submission of an already-known skill to return the existing submission id idempotently with HTTP 200
**So that** my CLI keeps polling the same record without producing duplicate rows or surfacing P2002 errors.

**Acceptance Criteria**:
- [x] **AC-US3-01**: `src/lib/submission-dedup.ts::checkSubmissionDedup` and its staleness constants (`DEFAULT_STALE_PENDING_HOURS`, etc.) are deleted. A new `src/lib/submission-store.ts::upsertSubmission(input)` returns `{ id, created: boolean, state, verifiedSkill? }` — on `create()` success it reports `created: true`; on a P2002 unique-violation it looks up the existing row via `findUniqueOrThrow({ where: { repoUrl_skillName: … } })` and returns `created: false` with the existing record.
- [x] **AC-US3-02**: Concurrent-insert unit test — 20 parallel `upsertSubmission` calls with identical `(repoUrl, skillName)` produce **exactly 1** row in the DB and **all 20** calls return the same `id`. Test runs against a real Neon test branch (not a mock) per CLAUDE.md guidance.
- [x] **AC-US3-03**: HTTP contract preserved — `POST /api/v1/submissions` for a known `(repoUrl, skillName)` returns HTTP **200** with JSON body `{ id: string, state: string, duplicate: true }`. For a known-published skill, it returns `{ skillId, skillName, alreadyVerified: true }`. For an admin-blocked skill, it returns `{ blocked: true, submissionId }`. All three response shapes verified by contract tests against `vitest` HTTP fixtures.
- [x] **AC-US3-04**: P2002 errors do **not** leak Prisma internals to the public API. The error handler catches `e.code === "P2002"` on the unique constraint, maps it to the existing-row lookup path, and never propagates the Prisma error object to the HTTP response.
- [x] **AC-US3-05**: The existing `src/app/api/v1/submissions/route.ts` call sites at approx. lines 582, 668–679, and 778 are updated to use `upsertSubmission` instead of `checkSubmissionDedup(...) + db.submission.create(...)`. No remaining caller imports from `submission-dedup.ts`.

---

### US-004: ADR for Tier-2 LLM runtime choice (P2)
**Project**: vskill-platform

**As the** maintainer (CTO)
**I want** an ADR documenting the Tier-2 LLM scoring runtime choice with concrete cost and latency numbers
**So that** I can decide whether to stay on Cloudflare Workers AI or migrate to GCP spot VMs.

**Acceptance Criteria**:
- [x] **AC-US4-01**: An ADR file exists at `.specweave/docs/internal/architecture/adr/ADR-00XX-tier2-runtime.md` (XX = next sequential ADR number at the time of writing) containing all of:
  - **Baseline metrics** from the last 30 days: Cloudflare Workers AI neuron usage, $ cost (pulled from CF analytics API), p50/p95/p99 scan latency (pulled from Neon or KV log aggregation), Llama→Gemini fallback rate.
  - **Option A — Keep**: stay on CF Workers AI + Llama 4 Scout primary, Llama 3.3 + Gemini fallback. Pros/cons written out explicitly.
  - **Option B — Move**: 1–2 GCP spot `e2-small` instances in `us-central1-a` (reuse existing project `vskill-crawlers`), Gemini 2.0 Flash via Google GenAI SDK as primary. Pros/cons + projected monthly cost.
  - **Option C — Hybrid**: CF Workers AI fast-path + GCP Gemini for low-confidence cases. Documented but not recommended.
  - **Recommendation**: explicit go/no-go on Option B with migration rationale.
- [x] **AC-US4-02**: The ADR contains **no secret API keys, credentials, or auth tokens** in its text. Numbers and cost figures are present but any key references use placeholder names (e.g. `GOOGLE_API_KEY`, never the actual key value). Confirmed by grep for known key prefixes in the PR review.
- [x] **AC-US4-03**: The ADR is linked from `.specweave/docs/internal/architecture/adr/README.md` (or equivalent ADR index) and referenced from this increment's `plan.md`.

## Functional Requirements

### FR-001: `upsertSubmission` is the single write path for new submissions

All ingestion sources (`cli-auto`, web UI submit endpoint, crawler `submission-scanner`) route through `src/lib/submission-store.ts::upsertSubmission`. No caller constructs a `db.submission.create({...})` directly on the path for "known skill? create or reuse." Direct `create` is allowed only for genuinely new, first-time submissions where the caller has independently confirmed uniqueness.

### FR-002: Hourly cron warms KV list cache for all filter states

`src/lib/cron/queue-list-warmup.ts` is invoked from the hourly scheduled handler in `.open-next/worker-with-queues.js` alongside the existing `refreshQueueStats`. For each filter ∈ {`active`, `published`, `rejected`, `blocked`, `onHold`} it calls a shared `fetchSubmissionList({ filter, sort, dir, limit: 50, offset: 0 })` helper (extracted from the HTTP route and cron so both code paths match exactly) and writes results to both `submissions:list:<filter>:::<sort>:<dir>:50:0` and `submissions:latest:<filter>`.

### FR-003: Migration runs inside a transaction with admin-only creds

The collapse step and the unique-index step run inside `prisma migrate deploy` and require the same deploy-time Postgres credentials used by `push-deploy.sh`. No public API or developer tool triggers the migration. The collapse script refuses to run if `DATABASE_URL` points at a non-Neon host (defence against accidental local-DB corruption).

### FR-004: Rollback is possible for 30 days

`backups/dedup-collapse-0672.json` is committed to git (file size expected < 1 MB). A sibling restore script can recreate deleted rows + children. Rollback SLA: within 30 days of migration deploy, the restore script can be run against the production DB and produce row-level parity with the pre-collapse snapshot.

## Success Criteria

- `/queue` cold-load p95 < 1.5 s (Playwright, measured against deployed preview).
- Zero duplicate `(repoUrl, skillName)` rows in `Submission` table post-migration (SQL assertion: `SELECT COUNT(*) FROM submission GROUP BY repo_url, skill_name HAVING COUNT(*) > 1` returns zero rows).
- Zero P2002 errors surfaced to public `/api/v1/submissions` response bodies over a 7-day observation window post-deploy.
- `obsidian-brain` and all other skills appear at most once per `(repoUrl, skillName)` in production `/queue` within 1 hour of migration deploy.
- ADR reviewed by maintainer and merged to `.specweave/docs/internal/architecture/adr/`.

## Non-Goals / Out of Scope

- **Tier-2 LLM runtime migration itself** — the ADR is the deliverable; actual migration to GCP spot VMs is increment `0673` if the ADR recommends it.
- **Refactoring the broader queue consumer logic** beyond replacing the dedup branch. The queue consumer state machine, retry semantics, Tier-1/Tier-2 scan orchestration, and webhook handlers are unchanged.
- **Changing the `/api/v1/submissions` request schema**. Request body shape is preserved; only the server-side dedup implementation changes, and response bodies retain backwards-compatible fields (`duplicate: true`, `alreadyVerified: true`, `blocked: true`).
- **UI changes to `/queue`** beyond the functional consequence that duplicate rows disappear. No layout, sort-control, or filter-UI work.
- **Retroactive de-duplication of other FK-related data** (e.g. redundant `EvalRun` rows that survived collapse). Collapse re-points children to the survivor but does not then dedupe the children themselves.
- **Admin "force rescan" endpoint**. Staleness-based re-scan semantics used to be implicit in `checkSubmissionDedup`; explicit admin re-scan is a separate concern handled elsewhere and not part of this increment.

## Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Collapse migration corrupts FK relationships on a victim row | Low | High | Single Prisma transaction wraps collapse + index step; any error rolls back all changes; archive JSON enables restore. |
| Concurrent scan-pipeline writes during migration hit the old schema | Medium | Medium | Document a short maintenance window (or take a brief write-lock) during deploy; existing circuit-breaker limits Neon write concurrency. |
| Prisma transient error during collapse leaves partial state | Low | High | Prisma transactions auto-rollback on throw; restore script covers catastrophic failure; idempotent re-run is safe. |
| Archive JSON grows beyond reasonable git-committable size | Low | Low | ~7-ish duplicates per observed skill × a few hundred skills → expected < 1 MB; if > 5 MB, store in CF R2 instead of git. |
| KV cache warm-up doubles Neon query load hourly | Low | Low | 5 filter × 1 query each = 5 queries/hr, well below Neon free-tier limits; query uses existing indexed paths. |
| P2002 catch masks a real data issue (e.g., corrupted repoUrl) | Low | Medium | `upsertSubmission` logs P2002 occurrences (without leaking to HTTP) so they are observable in CF logs; threshold-based alert recommended but out of scope. |
| ADR authoring blocked by missing CF analytics access | Low | Low | Analytics data is already accessible via existing CF API token used for deploys; ADR author reuses it. |
| Rollback script deploys to wrong DB (dev vs prod) | Low | High | Restore script refuses to run unless `--i-understand-this-is-prod` flag is passed and `DATABASE_URL` host matches expected Neon hostname. |

## Dependencies

**None external.** This increment is standalone within `vskill-platform`. It does not block on, nor is it blocked by, any other active increment.

Relevant in-flight increments (for awareness only, not dependencies):
- `0657-dark-theme-semantic-tokens` (31/32 tasks, nearly closed) — unrelated.
- `0670-skill-builder-universal` (3/35 tasks, early) — unrelated.

## Test Strategy

Per CLAUDE.md strict TDD enforcement, every task writes failing tests first (RED) before implementation (GREEN), then refactors (REFACTOR). Tests hit real infrastructure (Neon test branch, real KV in wrangler dev) per project policy — no Prisma or KV mocks for integration tests.

| Test area | Type | Stack | Location |
|---|---|---|---|
| `upsertSubmission` P2002 handling | Unit | Vitest + Prisma mock for error branch only | `src/lib/submission-store.test.ts` |
| `upsertSubmission` 20-parallel race | Integration | Vitest + real Neon test branch | `src/lib/submission-store.integration.test.ts` |
| Cache warm-up writes all 5 filter keys | Integration | Vitest + real KV via wrangler dev | `src/lib/cron/queue-list-warmup.integration.test.ts` |
| SSR `data.ts` reads warmed key | Integration | Vitest + OpenNext adapter, real KV | `src/app/queue/data.integration.test.ts` |
| Collapse-duplicates idempotency | Integration | Vitest + Neon branch with seeded duplicates | `scripts/migrations/0672-collapse-submission-dupes.test.ts` |
| Restore script round-trip | Integration | Vitest + Neon branch post-collapse | `scripts/migrations/0672-restore-submission-dupes.test.ts` |
| `/queue` cold-load renders 50 rows < 1.5 s | E2E | Playwright | `e2e/queue-cold-load.spec.ts` |
| `/queue?q=d` single `obsidian-brain` row | E2E | Playwright | `e2e/queue-no-duplicates.spec.ts` |
| `/api/v1/submissions` contract preservation | Contract | Vitest HTTP fixtures | `src/app/api/v1/submissions/route.contract.test.ts` |
| ADR presence + content structure | Lint | markdown-lint + grep for required headings | `.specweave/docs/internal/architecture/adr/` |

**Coverage targets**: unit 95 %, integration 90 %, E2E 100 % of ACs (all four ACs covered by at least one E2E or integration assertion).

**Closure gates** (per CLAUDE.md Testing Pipeline):
- `sw:code-reviewer` must write `code-review-report.json` with zero critical/high/medium findings.
- `/simplify` runs after code-review.
- `/sw:grill` writes `grill-report.json`.
- `/sw:judge-llm` writes `judge-llm-report.json` (WAIVED if consent denied).
- `/sw:validate` 130+ rule checks pass.
- E2E `npx playwright test` passes.

## Edge Cases

Documented here so the architect and planner can encode them into plan.md and tasks.md:

1. **Prisma transient error during collapse** → transaction rollback; no partial FK re-point; script safe to re-run.
2. **Partial FK re-point** → atomicity required; entire collapse step runs inside a single Prisma transaction.
3. **Concurrent scan-pipeline writes during migration** → take a short write-lock window or schedule during low-traffic maintenance window; document in rollout steps.
4. **P2002 on non-`(repoUrl, skillName)` constraint** → only the `repoUrl_skillName` unique violation maps to the existing-row lookup; other P2002 codes re-throw.
5. **Cron runs before collapse deploys** → warm-up writes are harmless (just populate KV with current, possibly duplicated data); after collapse deploy, next hourly cron cleans up.
6. **CF Workers AI outage during scan pipeline** → unrelated to this increment; existing Gemini fallback handles it.
7. **Archive JSON corrupted or missing before restore** → restore script refuses to run without a valid archive; script validates JSON schema on read.
