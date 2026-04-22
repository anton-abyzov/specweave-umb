---
increment: 0673-submission-dedup-cleanup-at-scale
title: "Submission dedup cleanup at scale"
type: bug
priority: P1
status: planned
created: 2026-04-22
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Submission dedup cleanup at scale

## Overview

Deploying 0672 yesterday halted at the dry-run because the production `Submission` table holds 2,825,767 duplicate rows under `(repoUrl, skillName)` — 96.3 % of the entire 2,933,783-row table — and the 0672 collapse script (`scripts/migrations/0672-collapse-submission-dupes.ts::loadVictims`) cannot handle that scale (Neon serverless imposes a 64 MB response limit; the naive victim query would return 3–14 GB). This increment ships a batched, checkpointed, idempotent DB-side cleanup plus fixes the latent `/api/v1/admin/rescan-published` endpoint bug (`rescan-published/route.ts:156–178`) that produced an estimated 40–50 % of the duplicates, unblocking the 0672 deploy.

The cleanup also resolves a second blocker the 0672 script missed: `SubmissionStateEvent.submissionId` carries an `ON DELETE RESTRICT` FK (not `CASCADE`), so 8,976,455 state events must be deleted before their parent Submissions in each batch. Survivor selection is state-aware: prefer `PUBLISHED` over `REJECTED`, then most recent `updatedAt`. No Prisma schema change is required — 0672's `@@unique([repoUrl, skillName])` is design-correct (confirmed by the versioning-model research agent) and will be applied cleanly post-cleanup.

## Background (production context)

**Bleeding has stopped.** Last Submission row created `2026-04-17 07:16:15 UTC`; zero rows in the last 24 h; only 25 rows total since `2026-03-26 15:24 UTC`. The 2.8 M backlog is historical — a crawl-pulse re-scan campaign, not active traffic — so the cleanup runs against a stable table.

**Production snapshot (2026-04-22 UTC)**, measured directly against prod Neon (`ep-polished-haze-aea6snnj-pooler.c-2.us-east-2.aws.neon.tech`):

| Metric | Value |
|---|---|
| Total `Submission` rows | 2,933,783 |
| `(repoUrl, skillName)` groups with COUNT > 1 | 91,159 |
| Victim rows (to be collapsed) | 2,825,767 |
| Expected survivor count | ~108,324 (±5 %) |
| State = PUBLISHED | 2,911,321 (99.23 %) |
| `contentHashAtScan` NULL | 100 % |
| `submitterEmail` NULL | 100 % |
| `userId` NULL | 99.99 % |
| `skillId` NULL | 0.76 % (22,391 rows) |
| Ghost PUBLISHED (`skillId=NULL AND state=PUBLISHED`) | 3,169 |
| `SubmissionStateEvent` rows | 8,976,455 |
| `ScanResult` rows | 4,380,746 |
| `SubmissionJob` / `EmailNotification` | 0 / 0 |
| `EvalRun` rows | 5,458 |

**Smoking gun**: `/api/v1/admin/rescan-published` (`repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/rescan-published/route.ts:156–178`) calls `db.submission.createMany({ ..., skipDuplicates: true })` with no in-flight dedup check. Before 0672, `skipDuplicates: true` was a no-op because there was no unique constraint — so the endpoint accumulated ~40–50 % of the 2.8 M rows between 2026-03-01 and 2026-03-26. The cron that drove it appears dormant since 2026-03-26, but the endpoint is still a latent bug: it will re-bleed if re-enabled, and the "in-flight skill" race it exposes (concurrent rescans double-inserting) is independent of the unique constraint.

**Scope guardrails (pre-approved)**:
- No change to 0672's Prisma schema — `@@unique([repoUrl, skillName])` stays exactly as shipped in commit `5b92a50`.
- No change to `upsertSubmission` or the hourly cache warm-up — both already on main.
- No change to `SkillVersion` or the versioning flow — `SkillVersion` remains the version home (`@@unique([skillId, version])`, content-hash driven bumps); `Submission` is a processing receipt, not a version artifact.
- **Summary-only archive**: per-group summary (`{repoUrl, skillName, survivorId, victimCount, stateDistribution}`) written to `backups/dedup-summary-0673.json` (~9 MB). Individual victim rows are NOT preserved — 99 % are PUBLISHED with every informative column NULL, so there is no information to lose.
- `ScanResult` and `EvalRun` orphans (~4.2 M / ~5 k rows) are left in place via `ON DELETE SET NULL`; they encode scan verdicts with independent value.

## User Stories

### US-001: Queue shows at most one row per skill at prod scale (P1)
**Project**: vskill-platform

**As an** ops visitor on `https://verified-skill.com/queue`,
**I want** the queue to show at most one row per `(repoUrl, skillName)` after the cleanup and 0672 deploy land,
**So that** the queue is trustworthy and matches the cardinality the UI assumes.

**Acceptance Criteria**:
- [ ] **AC-US1-01**: `SELECT COUNT(*) FROM "Submission"` drops from 2,933,783 to between 102,907 and 113,740 (expected ~108,324, ±5 % tolerance) after cleanup completes on prod; remaining `(repoUrl, skillName)` groups with `COUNT(*) > 1` returns zero rows.
- [ ] **AC-US1-02**: `npx prisma migrate deploy` (applying 0672's unique index migration at `repositories/anton-abyzov/vskill-platform/prisma/migrations/*_add_submission_unique_repo_skill_name/`) succeeds cleanly against the post-cleanup prod DB without manual intervention. `Submission_repoUrl_skillName_key` shows in `pg_indexes` with `indisunique=true`.
- [ ] **AC-US1-03**: The Playwright spec at `repositories/anton-abyzov/vskill-platform/tests/e2e/queue-duplicates.spec.ts` (shipped with 0672) passes against the deployed preview URL post-cleanup — specifically, `/queue?q=d` returns exactly one `obsidian-brain` row from `anton-abyzov/vskill`.
- [ ] **AC-US1-04**: Within 1 h of cleanup completion the hourly cache warm-up (`refreshQueueListCache` in the CF Worker cron) logs `wrote=5 failed=0`, confirming the post-cleanup state is cacheable.

---

### US-002: Dry-run against a Neon branch before touching prod (P1)
**Project**: vskill-platform

**As the** operator running the cleanup,
**I want** to dry-run the entire cleanup + index-apply flow against a zero-copy Neon branch before touching the production DB,
**So that** the production window is reserved for the proven path and a bad script never reaches prod.

**Acceptance Criteria**:
- [ ] **AC-US2-01**: A one-shot script at `.specweave/increments/0673-submission-dedup-cleanup-at-scale/scripts/create-neon-branch.sh` creates a zero-copy Neon branch named `0673-dryrun-<utc-timestamp>` from the current prod branch in under 5 minutes using `neonctl branches create --parent main --name 0673-dryrun-$(date -u +%Y%m%d-%H%M%S)` (or the Neon API equivalent when `neonctl` is absent); the script prints the branch's pooled and non-pooled connection strings to stdout and nothing else.
- [ ] **AC-US2-02**: Running `scripts/migrations/0673-cleanup.ts --target $NEON_BRANCH_URL` against that branch reduces its `Submission` row count from ~2.9 M to within ±5 % of 108,324 survivors, with zero rows in `(repoUrl, skillName)` groups with `COUNT(*) > 1`, and writes the checkpoint rows described in US-003.
- [ ] **AC-US2-03**: `npx prisma migrate deploy` against the branch succeeds after cleanup — the unique index applies cleanly, confirming the prod deploy will apply cleanly too.
- [ ] **AC-US2-04**: A `scripts/delete-neon-branch.sh` script deletes the dry-run branch in one command (`neonctl branches delete 0673-dryrun-<timestamp>`), serving as the branch-based rollback path. The runbook (US-005) documents that branch deletion is zero-risk (no prod data is ever touched during dry-run).
- [ ] **AC-US2-05**: The cleanup script refuses to run against a hostname that looks like the prod pooler (`ep-polished-haze-aea6snnj-pooler.c-2.us-east-2.aws.neon.tech`) without an explicit `--i-understand-this-is-prod` flag; without the flag, it exits with a non-zero status and a clear error message. Integration test covers both paths (flag present → proceeds on a non-prod branch; flag absent → exits 1).

---

### US-003: Cleanup is idempotent and resumable (P1)
**Project**: vskill-platform

**As the** operator running a 1–2 h batched DB operation,
**I want** the cleanup script to be idempotent and resumable,
**So that** a killed process, flaky Neon connection, or hand-off between Claude sessions never produces double-deletes, lost batches, or inconsistent state.

**Acceptance Criteria**:
- [ ] **AC-US3-01**: Checkpoint state is persisted to a DB table `_migration_0673_checkpoint` with columns `(batchNumber INT PRIMARY KEY, lastProcessedId TEXT NOT NULL, victimsDeleted INT NOT NULL, stateEventsDeleted INT NOT NULL, startedAt TIMESTAMPTZ NOT NULL DEFAULT NOW(), finishedAt TIMESTAMPTZ)`. On startup the script reads `MAX(batchNumber)` and resumes from the next batch, never re-processing IDs already in the table. The table is created automatically on first run if absent (`CREATE TABLE IF NOT EXISTS`).
- [ ] **AC-US3-02**: Killing the process mid-batch (e.g., `SIGTERM` between batch 147 and 148) and restarting produces the same final state as an uninterrupted run. Verified by an integration test at `repositories/anton-abyzov/vskill-platform/scripts/migrations/0673-cleanup.resume.test.ts` that seeds 30 k victim groups into a Neon test branch, kills the process after batch 2, restarts, and asserts the final survivor count matches an uninterrupted control run (exact equality; not a tolerance check).
- [ ] **AC-US3-03**: A second end-to-end run of the completed cleanup script against an already-clean DB is a no-op: zero rows deleted, zero state events deleted, zero checkpoint rows inserted, and the script logs `already clean: 0 batches to process` before exiting with status 0. Unit test at `repositories/anton-abyzov/vskill-platform/scripts/migrations/0673-cleanup.idempotent.test.ts` asserts this against a post-cleanup seeded fixture.
- [ ] **AC-US3-04**: The cleanup runs inside an `ISOLATION LEVEL REPEATABLE READ` transaction per batch, and the pre-batch survivor-ID identification step uses `LOCK TABLE "Submission" IN EXCLUSIVE MODE` for the duration of a batch to block concurrent inserts (belt-and-suspenders against rescan-published being re-enabled during the run). The runbook still forbids re-enabling the rescan endpoint during cleanup.
- [ ] **AC-US3-05**: The summary archive at `.specweave/increments/0673-submission-dedup-cleanup-at-scale/backups/dedup-summary-0673.json` is appended batch-by-batch as a JSON Lines file (not a single JSON document) so partial runs don't corrupt the archive; file size stays under 10 MB (asserted by the cleanup script's final step: `fs.stat(archivePath).size < 10 * 1024 * 1024`).

---

### US-004: `rescan-published` never double-inserts for in-flight skills (P1)
**Project**: vskill-platform

**As the** operator (and as a defense against this bug recurring),
**I want** `/api/v1/admin/rescan-published` to skip skills that already have an in-flight Submission,
**So that** even if the unique constraint is dropped in the future, the endpoint cannot re-create the 2.8 M-row disaster on its own.

**Acceptance Criteria**:
- [ ] **AC-US4-01**: Before `db.submission.createMany(...)` at `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/rescan-published/route.ts:166`, a new filter step removes from the candidate set any `skillId` that has at least one `Submission` row with `state ∈ {RECEIVED, TIER1_SCANNING, TIER2_SCANNING, AUTO_APPROVED}`. The candidate set after filtering is what `createMany` receives. The filter query uses `findMany({ where: { skillId: { in: ids }, state: { in: IN_FLIGHT_STATES } }, select: { skillId: true } })`.
- [ ] **AC-US4-02**: Integration test at `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/rescan-published/route.integration.test.ts` — seed a published skill plus a `RECEIVED` Submission row for it, call the endpoint with that skill's id, assert the endpoint returns `{ created: 0, skipped: 1, reason: "in-flight" }` and `SELECT COUNT(*) FROM "Submission" WHERE "skillId" = $id` is unchanged (still 1). Repeat for each of the four in-flight states.
- [ ] **AC-US4-03**: Integration test for concurrency — fire 20 parallel POSTs to the endpoint for the same published skill (no prior in-flight Submission); assert that `SELECT COUNT(*) FROM "Submission" WHERE "skillId" = $id AND "createdAt" > $testStart` returns **exactly 1** row across all 20 responses. This confirms the filter + `skipDuplicates: true` + unique constraint are together race-safe.
- [ ] **AC-US4-04**: The existing `skipDuplicates: true` on `createMany` is preserved (belt-and-suspenders). The HTTP response shape (`{ created, skipped, reason? }` or whatever the current shape is — contract test pins it) is unchanged for existing clients; only the numbers differ. Contract test at `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/rescan-published/route.contract.test.ts` asserts the pre-change and post-change response JSON schema match.
- [ ] **AC-US4-05**: No schema changes, no new env vars, no new dependencies — fix is purely a 5–15 line filter step inside the existing route handler.

---

### US-005: Replacement deploy runbook for 0672 (P1)
**Project**: vskill-platform

**As the** operator handing the deploy off between Claude sessions or teammates,
**I want** a self-contained DEPLOY_RUNBOOK.md with numbered, idempotent steps and a rollback section,
**So that** any session can pick up exactly where the previous one stopped without re-reading the whole increment.

**Acceptance Criteria**:
- [ ] **AC-US5-01**: A file exists at `.specweave/increments/0673-submission-dedup-cleanup-at-scale/DEPLOY_RUNBOOK.md` with at least these sections, each resumable standalone:
  - **Step 1** — Preconditions (0672 commit `5b92a50` on main, `DATABASE_URL` verified-prod, `wrangler` auth, `neonctl` auth).
  - **Step 2** — Kill the `specweave dashboard` and any GitHub poller before heavy DB ops (per user's documented preference).
  - **Step 3** — Create Neon dry-run branch via `scripts/create-neon-branch.sh`; capture `$NEON_BRANCH_URL`.
  - **Step 4** — Run cleanup against the branch: `DATABASE_URL=$NEON_BRANCH_URL tsx scripts/migrations/0673-cleanup.ts`; verify survivor count 108 k ±5 %.
  - **Step 5** — Apply 0672 unique index against the branch: `DATABASE_URL=$NEON_BRANCH_URL npx prisma migrate deploy`; verify `Submission_repoUrl_skillName_key` exists.
  - **Step 6** — Prod cleanup: `DATABASE_URL=$PROD_URL tsx scripts/migrations/0673-cleanup.ts --i-understand-this-is-prod`.
  - **Step 7** — Apply unique index on prod: `DATABASE_URL=$PROD_URL npx prisma migrate deploy`.
  - **Step 8** — Deploy 0672 code: `./scripts/push-deploy.sh` (wraps `wrangler deploy`).
  - **Step 9** — Smoke tests: curl `/api/v1/submissions?limit=5`, open `/queue` + `/queue?q=d`, run `npx playwright test tests/e2e/queue-duplicates.spec.ts tests/e2e/queue-cold-load.spec.ts`.
  - **Step 10** — 24 h monitoring; close 0672 and 0673.
- [ ] **AC-US5-02**: Each step contains the exact command to run, the expected output or exit status, and a "if this fails" subsection. Example: Step 6 fails mid-batch → "restart with the same command; checkpoint table resumes from the last completed batch (see US-003 AC-US3-01)."
- [ ] **AC-US5-03**: A **Rollback** section at the bottom covers three scenarios:
  - **During Step 3–5 (Neon branch only)**: run `scripts/delete-neon-branch.sh`; no prod impact.
  - **During Step 6 (prod cleanup partway)**: stop the process; checkpoint table records last completed batch; the DB is in a consistent partial state (older survivors remain intact) and can be finished later. The runbook explicitly states no restore is needed at this stage because the archive is summary-only and the cleanup is forward-only; the DB is internally consistent regardless of where it stops.
  - **After Step 7 (unique index applied, code not deployed)**: no rollback needed — the constraint matches the data; the `upsertSubmission` code on main will work. Revert only if a data bug is discovered: `DROP INDEX CONCURRENTLY "Submission_repoUrl_skillName_key"` and the DB is back to the post-cleanup state.
- [ ] **AC-US5-04**: The runbook includes a "Do NOT do this" sidebar: never re-enable `/api/v1/admin/rescan-published` until 0673 closes (US-004 ships the fix); never run cleanup and `rescan-published` cron simultaneously; never run cleanup without the `--i-understand-this-is-prod` flag against the prod URL.
- [ ] **AC-US5-05**: `.specweave/increments/0673-submission-dedup-cleanup-at-scale/HANDOFF.md` is kept in sync with runbook progress — each session updates "current state" + "next step" after making progress, so a new session can resume without re-reading the runbook top-to-bottom.

## Functional Requirements

### FR-001: Cleanup script lives at `scripts/migrations/0673-cleanup.ts`

The cleanup script is TypeScript (matching the 0672 convention), runs via `tsx`, imports Prisma + `pg` (for `COPY`-style bulk ops where Prisma is inefficient), and exposes a single CLI entry point. It reads `DATABASE_URL` from env, refuses to run against the prod hostname without `--i-understand-this-is-prod`, creates the checkpoint table if missing, and exits 0 on success (including no-op idempotent re-runs).

### FR-002: Batch size is 10,000 victim IDs per transaction

Each transaction deletes matching `SubmissionStateEvent` rows first (`DELETE FROM "SubmissionStateEvent" WHERE "submissionId" = ANY($victim_ids)`), then `Submission` rows (`DELETE FROM "Submission" WHERE id = ANY($victim_ids)`). `ScanResult.submissionId` and `EvalRun.submissionId` auto-null via `ON DELETE SET NULL`. A pause of 100 ms between batches avoids overwhelming Neon's connection pool. The batch size and pause are CLI flags (`--batch-size`, `--batch-pause-ms`) with the defaults above.

### FR-003: Summary archive is JSON Lines at `backups/dedup-summary-0673.json`

Per batch, the script appends JSON lines of the form `{"batchNumber": N, "groups": [{"repoUrl": "...", "skillName": "...", "survivorId": "...", "victimCount": 430, "stateDistribution": {"PUBLISHED": 429, "REJECTED": 1}}, ...]}`. The archive is not committed to git (`.specweave/increments/*/backups/` is expected to stay local or sync to R2 for files > 5 MB per 0672's precedent) but is produced during dry-run and prod runs for audit.

### FR-004: `rescan-published` filter is in-flight-first

The new filter step in `src/app/api/v1/admin/rescan-published/route.ts` runs before `createMany`, uses an indexed query on `(skillId, state)`, and never deletes or modifies existing rows — it only narrows the candidate list for the subsequent `createMany`. The set of in-flight states is exported as a named constant `IN_FLIGHT_STATES = ['RECEIVED', 'TIER1_SCANNING', 'TIER2_SCANNING', 'AUTO_APPROVED']` for reuse and testability.

## Success Criteria

- `SELECT COUNT(*) FROM "Submission"` returns a value between 102,907 and 113,740 within 1 h of the prod cleanup finishing.
- `SELECT COUNT(*) FROM (SELECT 1 FROM "Submission" GROUP BY "repoUrl", "skillName" HAVING COUNT(*) > 1) t` returns 0.
- `Submission_repoUrl_skillName_key` exists in `pg_indexes` with `indisunique=true`.
- `tests/e2e/queue-duplicates.spec.ts` and `tests/e2e/queue-cold-load.spec.ts` pass against the deployed preview worker.
- `/api/v1/admin/rescan-published` integration and contract tests pass; parallel-20 test produces exactly 1 new row.
- `DEPLOY_RUNBOOK.md` + `HANDOFF.md` exist and are kept current through the sequence.
- Zero rows created in `Submission` via `rescan-published` in a 24 h observation window post-deploy (endpoint remains operationally disabled; metric is just "background hygiene check").

## Non-Goals / Out of Scope

- **Changes to 0672's `upsertSubmission`** (`src/lib/submission/upsert.ts`) or cache warm-up (`src/lib/cron/queue-list-warmup.ts`) — both already shipped in commit `5b92a50` and confirmed correct.
- **Changes to Prisma schema** (`prisma/schema.prisma`) — `@@unique([repoUrl, skillName])` on `Submission` stays exactly as shipped by 0672; no new fields, no new models, no migration authoring for schema deltas.
- **Changes to `SkillVersion` or the versioning flow** — confirmed design-correct by the versioning-model research agent. `Submission` is a processing receipt, not a version artifact. `SkillVersion` keyed `@@unique([skillId, version])` with content-hash driven bumps stays as-is.
- **Instrumenting `contentHashAtScan` on new submissions** — 100 % NULL in prod today is a separate tracked follow-up (not this increment). Does not affect cleanup correctness; the column is never read by the cleanup.
- **Deleting orphan `ScanResult` / `EvalRun` rows** — ~4.2 M `ScanResult` rows will end with `submissionId = NULL` after cleanup (via `ON DELETE SET NULL`); same for 5,458 `EvalRun` rows. They encode scan verdicts with independent value and are left in place.
- **Fixing the hidden GPT-4o-mini spend (~$299/mo) surfaced during 0672 planning** — separate decision after CTO reviews ADR-0256; tracked as candidate 0674.
- **Refactoring the broader queue consumer, scan pipeline, or webhook handlers** — no code touched outside `scripts/migrations/0673-cleanup.ts`, `src/app/api/v1/admin/rescan-published/route.ts`, and the two 0673 test files (plus their integration counterparts).
- **UI / UX work** — no layout, filter, or sort changes on `/queue`. The visible fix (no duplicate rows) is a consequence of the cleanup; nothing rendering changes.
- **Automated re-enabling of `rescan-published`** — endpoint stays operationally disabled; 0673 only ensures that *if* it gets re-enabled, it cannot re-cause the disaster.

## Dependencies

- **0672 commit `5b92a50` on main** — confirmed via `git log --oneline` 2026-04-22. Provides `@@unique([repoUrl, skillName])` in schema, `upsertSubmission`, and cache warm-up. 0673's unique-index apply step depends on 0672's migration SQL being on main.
- **Neon API access with branching enabled** — confirmed supported on current Neon plan (zero-copy branches). Used for US-002 dry-run.
- **`wrangler` auth** — confirmed earlier in this session. Used for Step 8 of the runbook (deploy code).
- **`neonctl` CLI** — preferred for branch creation; if absent, the script falls back to the Neon API via `curl` with `NEON_API_KEY` env. Both documented in the runbook.

**Relevant in-flight increments (awareness only, not dependencies)**:
- `0657-dark-theme-semantic-tokens` — closed.
- `0670-skill-builder-universal` — early planning; unrelated.
- `0672-queue-reliability` — closed but undeployed; 0673 unblocks its deploy.

## Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Prod cleanup runs longer than the 1–2 h estimate | Medium | Medium | Batch size is a CLI flag (`--batch-size`, default 10 k); operator can reduce mid-run by killing + restarting (idempotent + resumable per US-003). Runbook includes a "pause between batches" lever (`--batch-pause-ms`). |
| Neon branch fails to spin up or connection string invalid | Low | Medium | `neonctl` has a documented SLA; runbook includes the raw Neon API equivalent as a fallback. Branch creation is reversible (delete branch if corrupted). |
| FK re-point / delete bug despite tests passing | Low | High | Integration test against a real seeded Neon branch (not a mock); sample survivor/victim counts verified before proceeding to prod; AC-US2-02 dry-run reproduces prod scale before the prod cleanup runs. |
| Process killed mid-batch leaves DB in an inconsistent partial state | Low | Medium | Checkpoint table + per-batch transactions ensure the DB is always internally consistent between batches; the cleanup is forward-only, so a partial run leaves older survivors + in-progress data still intact. Resume logic verified by AC-US3-02. |
| Rescan-published re-enabled mid-cleanup creates new victims | Low | High | Runbook's "Do NOT do this" sidebar explicitly forbids it; `LOCK TABLE EXCLUSIVE` inside each batch blocks concurrent inserts as a defensive measure. Endpoint is also dormant since 2026-03-26 with no plans to re-enable until 0673 closes. |
| Survivor count ±5 % tolerance is exceeded | Low | Low | If cleanup produces <102,907 or >113,740 survivors, the script halts before applying the unique index and the operator re-reads the summary archive to understand the delta. Dry-run catches this before prod. |
| 8.4 M `SubmissionStateEvent` deletes overwhelm Neon write capacity | Medium | Medium | 10 k batch size with 100 ms pause = ~840 batches × 100 ms = ~84 s of pause time over a 1–2 h run; Neon compute tier handles this easily (observed in prior schema migrations). Fallback: halve batch size. |
| Living-docs sync (JIRA/ADO) fails with GitHub 404 or API error | Low | Low | Cosmetic per 0657 and 0672 closure — non-blocking for the deploy. Documented in the runbook's "known warnings" section. |
| A group has survivor with NULL `skillId` but victims with non-NULL `skillId` | Low | Low | Cleanup preserves survivor's `skillId` as-is; does NOT promote victim's `skillId` to survivor. Rationale: `skillId` is a FK to `Skill` and is populated by `publishSkill` — it's a downstream signal, not authoritative for Submission identity. 3,169 ghost PUBLISHED rows stay ghost PUBLISHED. |
| 2 distinct `skillPath` values for same `(repoUrl, skillName)` collapsed into one | Low | Low | Accepted; alternative key `(repoUrl, skillName, skillPath)` saves only 7 k rows (noise at 2.8 M scale) and would require changing 0672's `upsertSubmission` — too costly to re-ship. |
| DATABASE_URL echoed to logs leaks creds | Low | High | Cleanup script uses `process.env.DATABASE_URL` but never logs its value; startup log prints only the hostname (e.g., `ep-polished-haze-aea6snnj-pooler`); integration test asserts the connection string is not present in captured stdout. |
| Cleanup + unique-index step desynced (cleanup succeeds but index fails) | Low | Medium | Two separate commands in the runbook, each idempotent; if index apply fails, operator re-runs cleanup (no-op) then retries index. Prisma migrate is itself idempotent via `_prisma_migrations` table. |

## Test Strategy

Per CLAUDE.md strict TDD — every task writes failing tests first (RED), then implementation (GREEN), then refactor (REFACTOR). Tests hit real infrastructure (Neon test branch, not mocks) per project policy.

| Test area | Type | Stack | Location |
|---|---|---|---|
| `computeSurvivorIds()` picks PUBLISHED over REJECTED, then max `updatedAt` | Unit | Vitest | `repositories/anton-abyzov/vskill-platform/scripts/migrations/0673-cleanup.survivor.test.ts` |
| Checkpoint table read/resume logic | Unit | Vitest + Prisma in-memory spy | `repositories/anton-abyzov/vskill-platform/scripts/migrations/0673-cleanup.checkpoint.test.ts` |
| Batched cleanup end-to-end (seeded 30 k groups) | Integration | Vitest + real Neon test branch | `repositories/anton-abyzov/vskill-platform/scripts/migrations/0673-cleanup.integration.test.ts` |
| Resume after SIGTERM mid-batch | Integration | Vitest + Neon branch + child-process kill | `repositories/anton-abyzov/vskill-platform/scripts/migrations/0673-cleanup.resume.test.ts` |
| Idempotent no-op on second run | Integration | Vitest + post-cleanup seeded branch | `repositories/anton-abyzov/vskill-platform/scripts/migrations/0673-cleanup.idempotent.test.ts` |
| Prod-hostname guard refuses without flag | Unit | Vitest + stubbed `process.env` | `repositories/anton-abyzov/vskill-platform/scripts/migrations/0673-cleanup.prod-guard.test.ts` |
| `rescan-published` in-flight skip | Integration | Vitest + real Neon branch seeded with in-flight submission | `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/rescan-published/route.integration.test.ts` |
| `rescan-published` 20-parallel race | Integration | Vitest + Neon branch + `Promise.all` of 20 | `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/rescan-published/route.parallel.test.ts` |
| `rescan-published` HTTP response shape unchanged | Contract | Vitest HTTP fixtures | `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/rescan-published/route.contract.test.ts` |
| `/queue?q=d` single `obsidian-brain` row post-deploy | E2E | Playwright (from 0672, stays) | `repositories/anton-abyzov/vskill-platform/tests/e2e/queue-duplicates.spec.ts` |
| `/queue` cold-load renders 50 rows < 1.5 s post-deploy | E2E | Playwright (from 0672, stays) | `repositories/anton-abyzov/vskill-platform/tests/e2e/queue-cold-load.spec.ts` |
| Neon branch create + delete round-trip | Manual | Runbook Step 3 + Step 10 rollback | `.specweave/increments/0673-submission-dedup-cleanup-at-scale/DEPLOY_RUNBOOK.md` |
| Prod dry-run against Neon branch (survivor count + index apply) | Manual | Runbook Steps 3–5 | `.specweave/increments/0673-submission-dedup-cleanup-at-scale/DEPLOY_RUNBOOK.md` |

**Coverage targets**: unit 95 %, integration 90 %, E2E 100 % of AC scenarios that involve user-facing behavior (US-001 AC-US1-03, AC-US1-04). Operator-facing ACs (US-002, US-003, US-005) are covered by integration tests + manual runbook steps.

**Closure gates** (per CLAUDE.md Testing Pipeline):
- `sw:code-reviewer` writes `reports/code-review-report.json` — zero critical/high/medium findings required.
- `/simplify` runs after code-review.
- `/sw:grill` writes `reports/grill-report.json`.
- `/sw:judge-llm` writes `reports/judge-llm-report.json` (WAIVED if consent denied).
- `/sw:validate` 130+ rule checks pass.
- E2E `npx playwright test` passes against the deployed preview.

## Edge Cases

Encoded for architect and planner to operationalize in plan.md and tasks.md:

1. **Survivor has NULL `skillId` but a victim in the same group has non-NULL `skillId`** — survivor's `skillId` stays NULL. `skillId` is a downstream FK populated by `publishSkill`, not authoritative for Submission identity. Ghost PUBLISHED rows stay ghost PUBLISHED. (22,391 rows total, 3,169 of which are `skillId=NULL AND state=PUBLISHED`.)
2. **Group has 2 distinct `skillPath` values** — collapsed into one survivor (the state/updatedAt winner's `skillPath`). Alternative key `(repoUrl, skillName, skillPath)` was considered and rejected (saves 7 k rows; requires re-shipping 0672).
3. **Concurrent write lands mid-cleanup** — blocked by `LOCK TABLE "Submission" IN EXCLUSIVE MODE` inside each batch transaction. Rescan-published is also operationally disabled; runbook reinforces.
4. **Process killed mid-batch** — checkpoint table records only completed batches (`finishedAt IS NOT NULL`); resume skips to the next unfinished batch. No double-deletes because each batch's victim IDs are deterministic (derived from the survivor set, which is a temp table rebuilt at resume time).
5. **Second end-to-end run of completed cleanup** — script detects empty victim set on the first survivor scan, writes no checkpoints, logs `already clean`, exits 0.
6. **Neon 64 MB response limit** — avoided by batched queries (each `SELECT` returns ≤ 10 k IDs; each `DELETE` acts on ≤ 10 k rows). The 0672 script's fatal flaw was a single unbounded `SELECT row_to_json(v) JOIN survivors` query; 0673 never issues an unbounded query.
7. **`ON DELETE RESTRICT` on `SubmissionStateEvent.submissionId`** — handled explicitly by deleting state events in each batch before their parent Submissions. `ScanResult` and `EvalRun` use `ON DELETE SET NULL` and orphan safely.
8. **Unique-index apply fails after successful cleanup** — re-run cleanup (no-op), then retry `prisma migrate deploy`. Prisma's `_prisma_migrations` table handles idempotency.
9. **Rollback during Step 6 prod cleanup** — stop the process; DB is in consistent partial state; no restore needed because the archive is summary-only and cleanup is forward-only. Resume later or abandon (the partial cleanup still reduces row count toward the target without creating duplicates).
10. **Neon branch deletion fails or branch leaks** — low-risk; Neon branches are cheap (zero-copy) and auto-expire after 7 days of inactivity on most plans. Runbook notes manual cleanup via `neonctl branches list` if needed.
11. **`rescan-published` 20-parallel race with zero prior in-flight row** — the filter step sees no in-flight row in all 20 calls, so all 20 pass through to `createMany`. `skipDuplicates: true` + unique constraint ensures exactly 1 row is created; the other 19 are silently skipped by Postgres. Test AC-US4-03 asserts this.
12. **`rescan-published` filter runs but the found in-flight submission transitions out mid-call** — acceptable: a skill that was in-flight at filter time might have published 10 ms later. Worst case: the endpoint skips a skill that is now free, which the next cron run picks up. Strictly safer than the current behavior.
