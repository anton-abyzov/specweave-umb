# Tasks: Submission dedup cleanup at scale

**Increment**: 0673-submission-dedup-cleanup-at-scale
**Complexity**: Medium — batched DB migration is familiar territory; rescan-published fix is small.
**Tracks**: 3 (A: cleanup script + libs, B: rescan-published fix, C: Neon branch + deploy)
**Total tasks**: 20 (T-001..T-020)
**TDD enforcement**: STRICT (per CLAUDE.md) — RED before GREEN, every task.
**Target repo**: `repositories/anton-abyzov/vskill-platform/`

> **HANDOFF NOTE**: T-014..T-020 are **operational runbook tasks** executed across later Claude sessions.
> Each session should open `HANDOFF.md` at the increment root to confirm current state before running
> any operational step. T-016 produces DEPLOY_RUNBOOK.md; HANDOFF.md is kept in sync by the operator
> (team-lead writes the initial HANDOFF.md after this planning session).

> **SPEC DIVERGENCE NOTE**: AC-US3-01 specifies a DB-resident checkpoint table
> (`_migration_0673_checkpoint`). The Architect plan (plan.md §3.5) and ADR-0257 §3.5 specify a
> **filesystem JSON checkpoint** (`checkpoints/progress.json`) with strong rationale: filesystem
> checkpoints survive DB branch switches, PITR rollbacks, and connection drops — critical because this
> script runs against multiple Neon branches. The implementation follows plan.md + ADR-0257 (filesystem
> checkpoint). The spec's DB-table approach is noted but overridden by the architect decision. If the
> CTO prefers the DB table approach, update `scripts/migrations/lib/checkpoint.ts` and the integration
> tests accordingly — the API surface (`readCheckpoint` / `writeCheckpoint`) does not change.

---

## Estimation summary

| Track | Tasks | Type | Complexity |
|---|---|---|---|
| A — Cleanup script + libs | T-001..T-009 | Code (TDD) | Medium |
| B — Rescan-published fix | T-010..T-013 | Code (TDD) | Low |
| C — Neon branch + deploy | T-014..T-020 | Operational (runbook steps) | Medium |

---

## Track A — Revised cleanup script (US-002, US-003, US-005)

---

### T-001: RED — Unit tests for `computeSurvivorIds()` survivor-selection logic
**User Story**: US-003 | **AC**: AC-US3-01, AC-US1-01 | **Status**: [ ] pending
**Test Plan**: Given a fixture of `(repoUrl, skillName)` groups where one group has 1 PUBLISHED + 3 REJECTED rows (all different `updatedAt`), one group has 4 PUBLISHED rows (different `updatedAt`), and one group is a single-row "self-survivor" — When `computeSurvivorIds(rows)` is called — Then PUBLISHED wins over REJECTED in mixed groups; among same-state rows `updatedAt DESC` picks the survivor; the single-row group returns that row's ID as survivor with zero victim IDs.
**Files**:
- `repositories/anton-abyzov/vskill-platform/scripts/migrations/__tests__/0673-survivor-selection.test.ts`
**Notes**: Pure unit test — mock Neon with a small in-memory fixture. The SQL to test is the `DISTINCT ON (repoUrl, skillName) … ORDER BY … (CASE state WHEN 'PUBLISHED' THEN 0 ELSE 1 END), updatedAt DESC` query from ADR-0257 §3.1. Tests must FAIL (RED) before T-002 is started.

---

### T-002: GREEN — Implement `computeSurvivorIds` in the cleanup script module
**User Story**: US-003 | **AC**: AC-US3-01, AC-US1-01 | **Status**: [ ] pending
**Test Plan**: Given the RED tests from T-001 exist and fail — When `scripts/migrations/0673-cleanup-submission-dupes.ts` is created with the `computeSurvivorIds` function implementing the `DISTINCT ON` temp-table approach — Then all T-001 unit tests pass.
**Files**:
- `repositories/anton-abyzov/vskill-platform/scripts/migrations/0673-cleanup-submission-dupes.ts`
**Notes**: Create the TEMP TABLE `_0673_survivors` as per ADR-0257 §3.1. Export `computeSurvivorIds` for testability alongside the CLI `runCleanup(opts)` entrypoint. Script filename matches plan.md (hyphen convention: `0673-cleanup-submission-dupes.ts`).

---

### T-003: RED — Unit tests for `readCheckpoint()` / `writeCheckpoint()` in checkpoint lib
**User Story**: US-003 | **AC**: AC-US3-01, AC-US3-02 | **Status**: [ ] pending
**Test Plan**: Given a temp directory — When `writeCheckpoint(path, checkpoint)` writes state and `readCheckpoint(path)` reads it back — Then round-trip equality holds; When the checkpoint file does not exist, `readCheckpoint` returns `null` (fresh start); When the file contains malformed JSON, `readCheckpoint` throws an `Error` with a message containing the path; When the file is a partial write (simulate by truncating), recovery path restores `null` (fresh start, not a crash).
**Files**:
- `repositories/anton-abyzov/vskill-platform/scripts/migrations/__tests__/0673-checkpoint.test.ts`
**Notes**: Tests must FAIL (RED) before T-004 is started. Checkpoint schema from ADR-0257 §3.5: `{startedAt, updatedAt, lastBatchNumber, lastProcessedId, archivedGroupCount, deletedVictimCount, stopped}`. Filesystem-JSON approach (not DB table) — see divergence note at top.

---

### T-004: GREEN — Implement `scripts/migrations/lib/checkpoint.ts`
**User Story**: US-003 | **AC**: AC-US3-01, AC-US3-02 | **Status**: [ ] pending
**Test Plan**: Given the RED tests from T-003 exist and fail — When `lib/checkpoint.ts` is created with `readCheckpoint(path): Promise<Checkpoint | null>`, `writeCheckpoint(path, c): Promise<void>`, and exported `Checkpoint` type — Then all T-003 tests pass.
**Files**:
- `repositories/anton-abyzov/vskill-platform/scripts/migrations/lib/checkpoint.ts`
**Notes**: Atomic write pattern per ADR-0257 §3.5: write to `.tmp` file then rename. Export `Checkpoint` type for reuse by the cleanup script.

---

### T-005: RED — Integration tests for batched end-to-end cleanup (30 k group seed)
**User Story**: US-002, US-003 | **AC**: AC-US2-02, AC-US3-01, AC-US3-02, AC-US3-05 | **Status**: [ ] pending
**Test Plan**: Given a Neon test branch seeded with 30 k duplicate groups (variable victim count 1–50, plus 200 single-row groups; representative of the PUBLISHED/REJECTED distribution; `SubmissionStateEvent` rows present for each victim to exercise the RESTRICT FK) — When `runCleanup({ databaseUrl: BRANCH_URL, archivePath, checkpointPath })` is called — Then every `(repoUrl, skillName)` group has exactly 1 survivor; survivor state = PUBLISHED when at least 1 PUBLISHED row existed; survivor `updatedAt` = MAX among preferred-state rows; summary archive at `archivePath` contains one JSON line per group; archive file size is under 10 MB; re-running produces `deletedVictimCount: 0` (idempotent).
**Files**:
- `repositories/anton-abyzov/vskill-platform/scripts/migrations/__tests__/0673-cleanup.int.test.ts`
**Notes**: Real Neon branch required — not a mock. Seed script should be inline in the test file. Tests must FAIL before T-006 GREEN starts.

---

### T-006: GREEN — Implement full cleanup pipeline in `0673-cleanup-submission-dupes.ts`
**User Story**: US-002, US-003 | **AC**: AC-US2-02, AC-US3-01, AC-US3-02, AC-US3-04, AC-US3-05 | **Status**: [ ] pending
**Test Plan**: Given the RED integration tests from T-005 exist and fail — When the full pipeline is implemented (pre-flight quiescence check, survivor temp table, batch loop with FK-ordered deletes, checkpoint writes, archive writes, final verification query) — Then all T-005 integration tests pass.
**Files**:
- `repositories/anton-abyzov/vskill-platform/scripts/migrations/0673-cleanup-submission-dupes.ts`
**Notes**: Per-batch transaction pattern from ADR-0257 §3.4: `DELETE SubmissionStateEvent … ANY($ids)` then `DELETE Submission … ANY($ids)`. 100 ms pause between batches (`--batch-pause-ms` flag, default 100). Batch size via `--batch-size` flag (default 10 000). Pre-flight quiescence check: `SELECT COUNT(*) FROM "Submission" WHERE "createdAt" > NOW() - INTERVAL '48 hours'` — abort if non-zero.

---

### T-007: RED — Integration tests for resumability after SIGTERM mid-batch
**User Story**: US-003 | **AC**: AC-US3-02, AC-US3-03 | **Status**: [ ] pending
**Test Plan**: Given the same 30 k group seed from T-005 on a Neon test branch — When the cleanup process is spawned as a child process, killed via SIGTERM after batch 2 completes, then restarted with identical arguments — Then the final survivor count equals an uninterrupted control run (exact equality); no double-deletes occur; checkpoint resumes from `lastBatchNumber + 1`; When the script is run a third time on the already-clean DB, it logs `already clean: 0 batches to process` and exits with status 0.
**Files**:
- `repositories/anton-abyzov/vskill-platform/scripts/migrations/__tests__/0673-cleanup.resume.test.ts`
**Notes**: Covers AC-US3-02 (resume) and AC-US3-03 (no-op second run). Uses `child_process.spawn` + `process.kill(pid, 'SIGTERM')` mid-run. Tests must FAIL before T-008 GREEN starts.

---

### T-008: GREEN — Implement checkpoint-based resume and no-op idempotency
**User Story**: US-003 | **AC**: AC-US3-02, AC-US3-03 | **Status**: [ ] pending
**Test Plan**: Given T-007 RED tests exist and fail — When the resume logic is wired into `runCleanup` (read checkpoint on startup, skip batches with `batchNumber ≤ lastBatchNumber`, detect empty victim set and exit 0 with "already clean" log) — Then all T-007 tests pass.
**Files**:
- `repositories/anton-abyzov/vskill-platform/scripts/migrations/0673-cleanup-submission-dupes.ts`
**Notes**: The victim ID batch query must use `id > $lastProcessedId ORDER BY id LIMIT $batchSize` so resumption skips already-processed IDs deterministically without relying on batch numbers alone.

---

### T-009: REFACTOR — Extend `lib/archive.ts` with `GroupSummary` + prod-hostname guard unit test
**User Story**: US-002, US-003 | **AC**: AC-US2-05, AC-US3-05 | **Status**: [ ] pending
**Test Plan**: (a) Given the existing `lib/archive.ts` exports — When `GroupSummary` type and `writeGroupArchive(path, increment, groups)` are added — Then existing `VictimSnapshot` exports remain unchanged and their tests still pass; `writeGroupArchive` appends JSON lines (not a single JSON document) to the archive file per FR-003. (b) Given a cleanup script invoked with `DATABASE_URL` pointing to the prod hostname (`ep-polished-haze-aea6snnj-pooler.c-2.us-east-2.aws.neon.tech`) — When called without `--i-understand-this-is-prod` — Then the script exits with status 1 and logs a clear error message; When called with the flag on a non-prod branch URL — Then the script proceeds normally. Unit test at `scripts/migrations/__tests__/0673-prod-guard.test.ts` using stubbed `process.env.DATABASE_URL`.
**Files**:
- `repositories/anton-abyzov/vskill-platform/scripts/migrations/lib/archive.ts` (modify, additive)
- `repositories/anton-abyzov/vskill-platform/scripts/migrations/__tests__/0673-prod-guard.test.ts`
**Notes**: `GroupSummary` schema from ADR-0257 §3.3 and FR-003. Prod hostname guard is the `assertNeonHost` pattern from 0672 — copy (don't import) the logic into the cleanup script to avoid coupling. Archive file size assertion (`< 10 MB`) runs in the cleanup script's final step via `fs.stat`.

---

## Track B — Rescan-published in-flight dedup fix (US-004)

---

### T-010: RED — Unit tests for `rescan-published` in-flight skip filter
**User Story**: US-004 | **AC**: AC-US4-01, AC-US4-04, AC-US4-05 | **Status**: [ ] pending
**Test Plan**: Given a mocked Prisma client — When the endpoint receives a candidate skill set where (a) all skills have an in-flight `RECEIVED` submission → `createMany` is called with `data: []`; (b) mixed in-flight + eligible skills → only eligible are in `createMany.data`; (c) no in-flight submissions → behavior is identical to pre-change (skipDuplicates preserved); (d) a P2002 slips past the filter (simulate with mocked Prisma throwing P2002 on `createMany`) → error is swallowed because `skipDuplicates: true` prevents throwing — Then each scenario assertion passes and the response shape (`{ created, skipped, reason? }`) matches the pre-change contract.
**Files**:
- `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/rescan-published/__tests__/in-flight-dedup.test.ts`
**Notes**: Tests must FAIL before T-011 GREEN starts. Use `vi.hoisted()` + `vi.mock('@prisma/client')` per repo convention. Cover all four in-flight states: RECEIVED, TIER1_SCANNING, TIER2_SCANNING, AUTO_APPROVED.

---

### T-011: GREEN — Implement in-flight filter in `rescan-published/route.ts`
**User Story**: US-004 | **AC**: AC-US4-01, AC-US4-04, AC-US4-05 | **Status**: [ ] pending
**Test Plan**: Given T-010 RED tests exist and fail — When the pre-`createMany` filter step is inserted at `route.ts` around lines 156–178 — Then all T-010 unit tests pass and the existing test suite for this route remains green.
**Files**:
- `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/rescan-published/route.ts`
**Notes**: Exact implementation from plan.md §Phase 3: `findMany({ where: { skillId: { in: candidateSkillIds }, state: { in: IN_FLIGHT_STATES } }, select: { skillId: true } })` then filter the candidate set. Export `IN_FLIGHT_STATES` as a named constant (reuse existing `IN_PROGRESS_STATES` from route.ts:38 — check whether they are identical before deciding to add a separate export or alias). Keep `skipDuplicates: true` on `createMany`.

---

### T-012: RED — Integration test for in-flight skip (per state) + contract test
**User Story**: US-004 | **AC**: AC-US4-02, AC-US4-04 | **Status**: [ ] pending
**Test Plan**: Given a Neon test branch with a seeded published skill + one `RECEIVED` Submission — When the endpoint is called with that skill's id — Then `SELECT COUNT(*) FROM "Submission" WHERE "skillId" = $id` is unchanged (still 1) and the response is `{ created: 0, skipped: 1, reason: "in-flight" }`; Repeat for each of TIER1_SCANNING, TIER2_SCANNING, AUTO_APPROVED. Contract test asserts the JSON schema of the response is identical before and after the change.
**Files**:
- `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/rescan-published/__tests__/route.integration.test.ts`
- `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/rescan-published/__tests__/route.contract.test.ts`
**Notes**: Tests must FAIL before T-013 GREEN. Use a real Neon branch (not mock) for the integration test; the contract test can use HTTP fixtures (no DB needed).

---

### T-013: GREEN — Integration test for 20-parallel race; confirm test passes
**User Story**: US-004 | **AC**: AC-US4-02, AC-US4-03 | **Status**: [ ] pending
**Test Plan**: Given a Neon test branch with a seeded published skill and no prior in-flight Submission — When 20 parallel POSTs are fired via `Promise.all` to the endpoint for the same published skill — Then `SELECT COUNT(*) FROM "Submission" WHERE "skillId" = $id AND "createdAt" > $testStart` returns exactly 1 across all 20 responses; the filter + `skipDuplicates: true` + unique constraint together prevent double-inserts.
**Files**:
- `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/rescan-published/__tests__/route.parallel.test.ts`
**Notes**: If the parallel test flakes (race window not closed by filter alone), the `@@unique` index (applied in T-017) is the authoritative guard. Document any flakiness in a test comment and mark it as "bounded by unique index once 0672 migration is applied". Acceptance: ≥ 95 % of runs produce exactly 1 row.

---

## Track C — Neon branch + deploy (US-001, US-002, US-005)

> **These are operational tasks — not code tasks.** They are tracked here for session-hand-off
> visibility. `sw:do` should skip them during automated implementation. Execute them manually in
> dedicated sessions, consulting DEPLOY_RUNBOOK.md (T-016) for exact commands.

---

### T-014: [RUNBOOK STEP] Create Neon dry-run branch + capture connection string
**User Story**: US-002 | **AC**: AC-US2-01, AC-US2-04 | **Status**: [ ] pending
**Test Plan**: Given `neonctl` is authenticated (`neonctl me` returns a user) and the project ID is known — When `.specweave/increments/0673-submission-dedup-cleanup-at-scale/scripts/create-neon-branch.sh` is executed — Then a zero-copy branch named `0673-dryrun-<utc-timestamp>` is created in under 5 minutes, and the script prints the pooled and non-pooled connection strings to stdout; When `delete-neon-branch.sh <branch-name>` is run — Then the branch is deleted.
**Files**:
- `.specweave/increments/0673-submission-dedup-cleanup-at-scale/scripts/create-neon-branch.sh`
- `.specweave/increments/0673-submission-dedup-cleanup-at-scale/scripts/delete-neon-branch.sh`
**Notes**: Create these shell scripts as part of this task (they ARE code, unlike T-015/T-017+). The `create-neon-branch.sh` script falls back to the Neon REST API via `curl $NEON_API_KEY` if `neonctl` is absent (per AC-US2-01). The `delete-neon-branch.sh` script takes branch name as $1.

---

### T-015: [RUNBOOK STEP] Execute cleanup against Neon branch + validate survivor count
**User Story**: US-002 | **AC**: AC-US2-02, AC-US2-03 | **Status**: [ ] pending
**Test Plan**: Given the Neon branch from T-014 has `DATABASE_URL=$NEON_BRANCH_URL` — When `DATABASE_URL=$NEON_BRANCH_URL npx tsx scripts/migrations/0673-cleanup-submission-dupes.ts --dry-run` is run and then without `--dry-run` — Then the `Submission` row count drops to within ±5 % of 108,324 survivors; `SELECT COUNT(*) FROM (SELECT 1 FROM "Submission" GROUP BY "repoUrl", "skillName" HAVING COUNT(*) > 1) t` returns 0; `DATABASE_URL=$NEON_BRANCH_URL npx prisma migrate deploy` succeeds and `Submission_repoUrl_skillName_key` appears in `pg_indexes`.
**Files**: (none — operational step)
**Notes**: Manual runbook step. Run in a dedicated session. Verify the four validation SQL queries from plan.md §Phase 4. If survivor count is outside ±5 % tolerance, halt and investigate via the summary archive before proceeding to prod.

---

### T-016: Write DEPLOY_RUNBOOK.md (10 numbered steps + rollback tiers)
**User Story**: US-005 | **AC**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04, AC-US5-05 | **Status**: [ ] pending
**Test Plan**: Given spec.md AC-US5-01..AC-US5-05 define the required sections — When `DEPLOY_RUNBOOK.md` is written at `.specweave/increments/0673-submission-dedup-cleanup-at-scale/DEPLOY_RUNBOOK.md` — Then it contains exactly Steps 1–10 (Preconditions, Kill dashboard, Neon branch, Cleanup dry-run, Unique index on branch, Prod cleanup, Unique index on prod, Code deploy, Smoke tests, 24 h monitoring); Each step has the exact command, expected output, and "if this fails" subsection; A Rollback section covers the three scenarios from AC-US5-03; A "Do NOT do this" sidebar covers the four forbidden actions from AC-US5-04.
**Files**:
- `.specweave/increments/0673-submission-dedup-cleanup-at-scale/DEPLOY_RUNBOOK.md`
**Notes**: This task IS code work (writing a document). Execute it in the same session as T-014 or as a standalone task. This file REPLACES the 0672 runbook. After writing, update `HANDOFF.md` "current state" section to mark runbook available.

---

### T-017: [RUNBOOK STEP] Apply 0672 unique-index migration to Neon branch, then prod
**User Story**: US-001 | **AC**: AC-US1-02 | **Status**: [ ] pending
**Test Plan**: Given cleanup is complete on prod (T-018 done) — When `DATABASE_URL=$PROD_URL npx prisma migrate deploy` is run — Then `SELECT indexname FROM pg_indexes WHERE tablename='Submission' AND indexname='Submission_repoUrl_skillName_key'` returns 1 row with `indisunique=true`; no `P2002` errors are emitted during apply (confirms zero duplicates remain).
**Files**: (none — operational step)
**Notes**: Manual runbook step, later session. Pre-flight: `SELECT * FROM _prisma_migrations WHERE migration_name LIKE '%submission_unique%'` — if present and rolled back, use `prisma migrate resolve` (documented in DEPLOY_RUNBOOK.md Step 7). Apply branch first (T-015), then prod.

---

### T-018: [RUNBOOK STEP] Run cleanup against prod DB
**User Story**: US-001 | **AC**: AC-US1-01 | **Status**: [ ] pending
**Test Plan**: Given the Neon branch dry-run passed (T-015) and `--i-understand-this-is-prod` flag is available — When `DATABASE_URL=$PROD_URL npx tsx scripts/migrations/0673-cleanup-submission-dupes.ts --i-understand-this-is-prod` is run — Then after completion `SELECT COUNT(*) FROM "Submission"` returns a value between 102,907 and 113,740; duplicate-pair count query returns 0; archive file written to `backups/dedup-summary-0673.json` under 10 MB; checkpoint file written to `checkpoints/progress.json`.
**Files**: (none — operational step)
**Notes**: Manual runbook step, later session. Expected wall time ~45–90 min. If interrupted, resume with the same command — checkpoint handles it. If pre-flight quiescence check fails (non-zero inserts in last 48 h), abort and investigate before proceeding.

---

### T-019: [RUNBOOK STEP] Deploy 0672 code via `push-deploy.sh`
**User Story**: US-001 | **AC**: AC-US1-04 | **Status**: [ ] pending
**Test Plan**: Given 0672 code is on main (`5b92a50`) and the unique index is applied — When `./scripts/push-deploy.sh` is run — Then Cloudflare deploy succeeds and the hourly cache warm-up log shows `wrote=5 failed=0` within 1 h of deployment.
**Files**: (none — operational step)
**Notes**: Manual runbook step, later session. Run after T-017 (unique index applied). This unblocks the 0672 deploy that halted at dry-run.

---

### T-020: [RUNBOOK STEP] Smoke tests + 24 h monitoring
**User Story**: US-001 | **AC**: AC-US1-03, AC-US1-04 | **Status**: [ ] pending
**Test Plan**: Given 0672 code is deployed (T-019) — When `npx playwright test tests/e2e/queue-duplicates.spec.ts tests/e2e/queue-cold-load.spec.ts` is run against the deployed preview URL — Then both specs pass; `/queue?q=d` shows exactly one `obsidian-brain` row; `/queue` first-load renders within 1.5 s; Over 24 h, `SELECT COUNT(*) FROM "Submission" s JOIN "Submission" s2 ON s."repoUrl"=s2."repoUrl" AND s."skillName"=s2."skillName" AND s.id != s2.id` stays at 0; Zero new rows created by `rescan-published` (endpoint remains operationally disabled).
**Files**: (none — operational step)
**Notes**: Manual runbook step, later session. After 24 h passes clean, close 0672 and 0673.

---

## AC Coverage Matrix

| AC | Task(s) |
|---|---|
| AC-US1-01 | T-001, T-002, T-018 |
| AC-US1-02 | T-017 |
| AC-US1-03 | T-020 |
| AC-US1-04 | T-019, T-020 |
| AC-US2-01 | T-014 |
| AC-US2-02 | T-005, T-006, T-015 |
| AC-US2-03 | T-015 |
| AC-US2-04 | T-014 |
| AC-US2-05 | T-009 |
| AC-US3-01 | T-001, T-002, T-003, T-004 |
| AC-US3-02 | T-007, T-008 |
| AC-US3-03 | T-007, T-008 |
| AC-US3-04 | T-006 |
| AC-US3-05 | T-009 |
| AC-US4-01 | T-010, T-011 |
| AC-US4-02 | T-012 |
| AC-US4-03 | T-013 |
| AC-US4-04 | T-010, T-011, T-012 |
| AC-US4-05 | T-010, T-011 |
| AC-US5-01 | T-016 |
| AC-US5-02 | T-016 |
| AC-US5-03 | T-016 |
| AC-US5-04 | T-016 |
| AC-US5-05 | T-016, T-020 |
