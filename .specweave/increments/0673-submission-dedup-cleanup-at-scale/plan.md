# Implementation Plan: Submission Dedup Cleanup at Scale

> **Status**: drafted in parallel with spec.md — this plan binds the revised 0672 strategy discovered by the production-scale research on 2026-04-22. See `research/` (symlinked to 0672 research) and ADR-0257 for context.
>
> **Target repo**: `repositories/anton-abyzov/vskill-platform/`
>
> **Core constraints**: (1) Neon 64 MB per-response limit; (2) `SubmissionStateEvent.submissionId ON DELETE RESTRICT`; (3) 2,825,767 victim rows (99 % PUBLISHED, bleeding stopped since 2026-03-26); (4) ~4.2 M orphan-able `ScanResult` rows, ~5.5 k `EvalRun` rows (both `ON DELETE SET NULL`, left as-is); (5) 0672 unique index migration SQL already exists at `prisma/migrations/20260421100000_submission_unique_repo_skill/migration.sql` — will apply AFTER cleanup.

## Overview

Ship a resumable, batched cleanup script that collapses 2.8 M duplicate `Submission` rows down to ~108 k survivors (one per `(repoUrl, skillName)` group, `state=PUBLISHED` preferred, `updatedAt DESC` tiebreak), then apply the pre-existing 0672 unique-index migration. Simultaneously seal the one remaining leak source (`/api/v1/admin/rescan-published`'s in-flight race) with a belt-and-suspenders check. Rollout is Neon-branch-first — we never touch prod until the script has been observed passing against a live branch of real prod data.

## Architecture

### Components

- **`scripts/migrations/0673-cleanup-submission-dupes.ts`** (new) — CLI migration script. Resumable, ID-range batched, summary-only archive. Reuses 0672's Neon-host guard pattern and `lib/archive.ts`'s file-write discipline (replacing `VictimSnapshot[]` with `GroupSummary[]`).
- **`scripts/migrations/lib/checkpoint.ts`** (new) — small read/write helper for `checkpoints/progress.json`. Pure fs, no DB dependency.
- **`scripts/migrations/lib/archive.ts`** (modify, additive) — add `GroupSummary` type + `writeGroupArchive()` function alongside the existing `VictimSnapshot` types. Existing 0672 exports preserved.
- **`src/app/api/v1/admin/rescan-published/route.ts`** (modify) — add an explicit pre-`createMany` in-flight check on the already-filtered candidate set. The existing `submissions: { none: { state: { in: IN_PROGRESS_STATES } } }` filter at line 97 is a necessary-but-not-sufficient guard (it doesn't close the read-to-write race); the new check is belt-and-suspenders.
- **`src/app/api/v1/admin/rescan-published/__tests__/in-flight-dedup.test.ts`** (new) — Vitest unit test, mocked Prisma, asserts: (a) skills with an already-in-flight submission are filtered out, (b) the double-check at route.ts actually runs, (c) `skipDuplicates: true` is retained.
- **`scripts/migrations/__tests__/0673-survivor-selection.test.ts`** (new) — Vitest unit, mocked Neon, pure-SQL survivor-rule correctness (PUBLISHED-preference, updatedAt tiebreak).
- **`scripts/migrations/__tests__/0673-cleanup.int.test.ts`** (new) — Vitest integration against a Neon branch. Seeds representative dup data (100 k+ rows mimicking prod distribution); asserts end-state.
- **`DEPLOY_RUNBOOK.md`** (new, in increment dir) — step-by-step deploy doc (US-005 deliverable).
- **ADR-0257** (new, already written) — large-table backfill pattern.

### Data Model

No schema changes in this increment. The 0672 schema (with `@@unique([repoUrl, skillName])` at `prisma/schema.prisma:200`) is the target end-state. The cleanup precedes `prisma migrate deploy` for the pre-existing 20260421100000 migration.

Runtime helpers:
- `_0673_survivors` — session-scoped Postgres TEMP TABLE. Columns: `id TEXT PRIMARY KEY, repoUrl TEXT, skillName TEXT`. Indexed on `id` for fast `NOT IN` anti-join.
- `checkpoints/progress.json` — filesystem checkpoint. Schema in ADR-0257 §3.5.

### API Contracts

No new endpoints. Modified endpoint stays on its current contract:
- `POST /api/v1/admin/rescan-published` — body unchanged; response unchanged; behavior change is **invisible at the wire** (filters out more skills, never produces more rows than before).

## Technology Stack

- **Language/Runtime**: TypeScript, Node 20, executed via `tsx`. Matches existing `scripts/migrations/*.ts` convention.
- **DB driver**: `@neondatabase/serverless` (`neon()` for simple queries, `neon().transaction([...])` for per-batch atomicity). Matches 0672.
- **Tests**: Vitest with `vi.hoisted()` + `vi.mock('@prisma/client')` for unit; Neon branch for integration. Matches repo convention.
- **Neon branching CLI**: `npx neonctl branches create|delete` (no global install needed). Alternative: Neon REST API `https://console.neon.tech/api/v2/projects/{id}/branches` — use only if `neonctl` auth is unreliable from CI.

**Architecture Decisions** (see ADR-0257 for full rationale):
- **Survivor rule**: `(CASE state WHEN 'PUBLISHED' THEN 0 ELSE 1 END), updatedAt DESC` — chosen to match the 99 % PUBLISHED reality + preserve latest state-machine position. Alternative `MAX(createdAt)` rejected because it would pick a REJECTED survivor for 2 groups that have both PUBLISHED and REJECTED rows.
- **Uniqueness key**: `(repoUrl, skillName)` — matches `upsertSubmission` shipped in 0672; alternatives (`+skillPath`, `+state`) considered and rejected in research §Revised uniqueness key.
- **Checkpoint storage**: filesystem JSON, not DB table — survives DB branch switches and PITR. ADR-0257 §3.5.
- **Concurrency safety**: **Option B** from the brief — pre-flight quiescence check (zero INSERTs in the last 48 h), no table-level lock. Accepts the theoretical risk of a concurrent write during cleanup; mitigated by running on a branch first and by the observed 26-day write drought. ADR-0257 §3.6.
- **Archive strategy**: summary-only (~9 MB) — no per-row dump. Rollback path is Neon PITR branch. ADR-0257 §3.3.
- **ADR scope**: **new ADR-0257**, not an amendment to 0256. 0256 concerns the Tier-2 LLM runtime (Cloudflare vs GCP); 0257 concerns a reusable migration pattern. Mixing them would muddy both.

## Implementation Phases

### Phase 1 — Planning (this session)
- Write spec.md (PM, parallel), plan.md (this file), tasks.md (Planner, after spec).
- ADR-0257 drafted and committed.

### Phase 2 — Script + checkpoint lib (next session)
- `scripts/migrations/lib/checkpoint.ts` with `readCheckpoint(path): Promise<Checkpoint | null>`, `writeCheckpoint(path, c): Promise<void>`, and `Checkpoint` type exported.
- `scripts/migrations/lib/archive.ts` extended with `GroupSummary` type and `writeGroupArchive(path, increment, groups)` function. Leaves existing `VictimSnapshot` exports intact.
- `scripts/migrations/0673-cleanup-submission-dupes.ts` implemented. Exports `runCleanup(opts)` + CLI entry.
- Unit tests: `scripts/migrations/__tests__/0673-survivor-selection.test.ts` (pure SQL correctness via mocked Neon) — covers AC-US1-01 / AC-US1-02 survivor rules.
- Can parallelize with Phase 3.

### Phase 3 — Rescan-published fix + tests (next session, parallel with Phase 2)
- Modify `src/app/api/v1/admin/rescan-published/route.ts` around lines 156–178. Insert between the Phase 1 skill fetch and the `createMany`:
  ```ts
  // Belt-and-suspenders: closes the read-to-write race window between
  // skillWhere's `submissions: { none: ... }` filter and createMany. The
  // schema-level @@unique([repoUrl, skillName]) is the hard guarantee; this
  // check just avoids generating predictable P2002s under hourly cron load.
  const candidateSkillIds = skills.map((s) => s.id);
  const inFlight = await db.submission.findMany({
    where: {
      skillId: { in: candidateSkillIds },
      state: { in: IN_FLIGHT_STATES },
    },
    select: { skillId: true },
  });
  const inFlightIds = new Set(inFlight.map((s) => s.skillId));
  const filteredSkills = skills.filter((s) => !inFlightIds.has(s.id));
  // …then continue with filteredSkills instead of skills.
  ```
- `IN_FLIGHT_STATES`: reuse the existing `IN_PROGRESS_STATES` constant at route.ts:38. No separate constant needed.
- Keep `skipDuplicates: true` on `createMany`. The `@@unique` index is now the authoritative guard.
- Tests: `src/app/api/v1/admin/rescan-published/__tests__/in-flight-dedup.test.ts`. Mocked Prisma. Scenarios:
  1. All candidate skills have in-flight submissions → `createMany` called with `data: []` (or early-return with `created: 0`).
  2. Mixed in-flight + eligible → only eligible are in `createMany.data`.
  3. No in-flight → unchanged behavior from current.
  4. P2002 leak test: simulate concurrent write slipping past the check → assert the `createMany({ skipDuplicates: true })` swallows it without throwing.

### Phase 4 — Neon branch test (Step 4 of deploy)
- Create branch: `npx neonctl branches create --name 0673-cleanup-test --parent main`.
- Point `DATABASE_URL_TEST` at branch's pooled URL (Neon returns a different hostname; our `assertNeonHost` still passes because it's `*.neon.tech`).
- Run `DATABASE_URL=$DATABASE_URL_TEST npx tsx scripts/migrations/0673-cleanup-submission-dupes.ts --dry-run` → expect `deletedVictimCount: 0, wouldDelete: ~2825767, wouldArchive: ~91159`.
- Run without `--dry-run` → expect `deletedVictimCount: ~2825767, archivedGroupCount: ~91159`.
- Run `DATABASE_URL=$DATABASE_URL_TEST npx prisma migrate deploy` → applies 0672's unique-index migration; expect success (no duplicate-key error).
- Validation queries on branch:
  ```sql
  -- 0 rows expected
  SELECT COUNT(*) FROM "Submission" s JOIN "Submission" s2
    ON s."repoUrl"=s2."repoUrl" AND s."skillName"=s2."skillName" AND s.id != s2.id;
  -- ~108,324 expected
  SELECT COUNT(*) FROM "Submission";
  -- Should have 1 row with @@unique index
  SELECT indexname FROM pg_indexes WHERE tablename='Submission' AND indexname LIKE '%repoUrl%';
  -- Survivor state distribution — ~99% PUBLISHED expected
  SELECT state, COUNT(*) FROM "Submission" GROUP BY state;
  -- No orphan FKs — ScanResult rows with dangling submissionId (should be 0; ON DELETE SET NULL handles this)
  SELECT COUNT(*) FROM "ScanResult" sr
  WHERE sr."submissionId" IS NOT NULL
    AND NOT EXISTS (SELECT 1 FROM "Submission" s WHERE s.id = sr."submissionId");
  ```
- Branch kept for 24 h then deleted (`neonctl branches delete`) once prod cleanup passes smoke.

### Phase 5 — Prod cleanup + unique index (Step 5 of deploy)
- Sanity re-run: `SELECT COUNT(*) FROM "Submission" WHERE "createdAt" > NOW() - INTERVAL '48 hours';` must be 0. Abort otherwise.
- `DATABASE_URL=$PROD_DATABASE_URL npx tsx scripts/migrations/0673-cleanup-submission-dupes.ts --dry-run` → counts sanity check vs branch run.
- `DATABASE_URL=$PROD_DATABASE_URL npx tsx scripts/migrations/0673-cleanup-submission-dupes.ts` → full run. Expected wall time ~45–90 min at ~30 k rows/min.
- On completion: commit `.specweave/increments/0673-.../backups/dedup-summary-0673.json` + `checkpoints/progress.json` (final state).
- `DATABASE_URL=$PROD_DATABASE_URL npx prisma migrate deploy` → applies unique index.

### Phase 6 — Code deploy + smoke (Step 6)
- `./scripts/push-deploy.sh` (existing 0672 pattern) pushes the rescan-published fix to Cloudflare.
- Smoke: `POST /api/v1/admin/rescan-published` with `{"dryRun": true, "limit": 5}` → expect `totalMatching > 0` and no duplicates created in a subsequent non-dry run.
- Bug 1 / bug 2 from 0672 still fixed (they depend on cleanup + unique index, both now in place).

### Phase 7 — 24 h monitoring + closure (Step 7)
- Hourly check for 24 h: `SELECT COUNT(*) FROM "Submission" s JOIN "Submission" s2 ON s."repoUrl"=s2."repoUrl" AND s."skillName"=s2."skillName" AND s.id != s2.id;` must stay at 0.
- Check Cloudflare logs for P2002s leaking into HTTP responses from `upsertSubmission` or `rescan-published` → should be 0.
- If both checks hold, close increment.

## Testing Strategy

### Unit (Vitest)
- **Survivor selection**: mock Neon with a small in-memory fixture; call the query; assert the `DISTINCT ON` behavior produces the expected survivor. Edge cases: all-PUBLISHED group, all-REJECTED group, mixed group with same `updatedAt`, single-row "group" (survivor = self, no victims).
- **Checkpoint lib**: read/write round-trip, absence handling (file not found → null), corruption handling (invalid JSON → throws with actionable message).
- **Archive helper**: `GroupSummary` schema shape, deterministic output order (sorted by `repoUrl, skillName`).
- **In-flight dedup** (rescan-published): 4 scenarios listed in Phase 3.

### Integration (Vitest, Neon branch)
- Seed branch with a representative dup pattern: 1000 groups × variable victim count (1 to 5000), plus 200 single-row groups. Total ~150 k rows.
- Run `runCleanup({ databaseUrl: $BRANCH, archivePath, checkpointPath })`.
- Post-conditions:
  - Every group has exactly 1 survivor.
  - Survivor state = PUBLISHED when at least 1 PUBLISHED victim existed in the group.
  - Survivor `updatedAt` = MAX among preferred-state candidates.
  - Archive file contains one summary per group; counts match.
  - Re-running is idempotent — second invocation: `deletedVictimCount: 0, archivedGroupCount: 0` (already clean).
  - Checkpoint persistence: kill the process mid-run (simulate SIGTERM); rerun; assert resume from correct `lastProcessedId`.
- Scale regression (US-002 related): 100 k+ row seed; assert no Neon 64 MB errors and total wall time < 5 min.

### E2E (Playwright)
- Reuse 0672's `tests/e2e/queue-duplicates.spec.ts`. Runs post-deploy on prod URL:
  - `/queue?q=d` renders ≤ 1 `obsidian-brain` row.
  - `/queue` first-load returns non-empty list (bug 1).
  - Hourly cron log (`queue list warmup`) has `wrote=5 failed=0`.

### Manual verification
- After Phase 5 prod cleanup: pull `/queue?q=d` in browser; visual inspection of known multi-submitter repos (e.g., `404kidwiz/claude-supercode-skills`) shows 1 row.
- After Phase 6 deploy: `POST /api/v1/admin/rescan-published` with dryRun; run real rescan cycle; verify row count stable over 6 h.

## Technical Challenges

### Challenge 1 — Neon 64 MB response limit
**Solution**: ID-range batching of 10 k rows per query (ADR-0257 §3.2). Temp-table survivor snapshot keeps per-batch response size under 400 KB. Never aggregate victim rows via `row_to_json` on the full table.
**Risk mitigation**: Phase 4 Neon-branch dry-run catches any accidental non-batched query before prod touches data.

### Challenge 2 — `SubmissionStateEvent ON DELETE RESTRICT`
**Solution**: explicit two-statement per-batch transaction — delete `SubmissionStateEvent` children first, then `Submission` parents (ADR-0257 §3.4). `ScanResult` and `EvalRun` are `ON DELETE SET NULL`, no explicit cleanup needed.
**Risk mitigation**: integration test asserts post-state that every surviving `Submission` still has its state events; deleted victims' `SubmissionStateEvent` rows are gone (count drops from ~8.98 M to ~326 k — 1 per survivor avg).

### Challenge 3 — Concurrent writes during 1–2 h cleanup
**Solution**: pre-flight quiescence check (48 h look-back, abort if non-zero). Relies on the observed fact that Submission inserts stopped 2026-03-26.
**Risk mitigation**: if a new Submission lands mid-cleanup, the `@@unique` index (applied post-cleanup) will catch it; the worst case is one orphan duplicate requiring a follow-up single-row cleanup. If 48 h look-back fails the pre-flight, we investigate the source before attempting cleanup.

### Challenge 4 — Rollback
**Solution**: Neon PITR branch is the authoritative rollback. Before Phase 5, branch creation is logged as a step in DEPLOY_RUNBOOK.md — that branch IS the rollback path for 24 h.
**Risk mitigation**: ADR-0257 §3.3 codifies "rollback via branch, not via archive replay". Summary archive is for audit, not restoration.

### Challenge 5 — Resumability under crash
**Solution**: filesystem checkpoint per batch. Restart with same args resumes from `lastProcessedId`.
**Risk mitigation**: integration test simulates crash mid-run.

### Challenge 6 — Race between rescan filter and createMany
**Solution**: belt-and-suspenders in-flight check immediately before `createMany` (Phase 3). Combined with `@@unique` index, this closes the leak deterministically.
**Risk mitigation**: rescan-published has historically been the 40–50 % leak source; even with the current Prisma-level filter, an hourly cron concurrent with a CLI submission could slip a duplicate through without the belt-and-suspenders. Tests cover the race explicitly.

## File Manifest

### Create (8 files)
- `repositories/anton-abyzov/vskill-platform/scripts/migrations/0673-cleanup-submission-dupes.ts` — cleanup CLI.
- `repositories/anton-abyzov/vskill-platform/scripts/migrations/lib/checkpoint.ts` — checkpoint fs helper.
- `repositories/anton-abyzov/vskill-platform/scripts/migrations/__tests__/0673-survivor-selection.test.ts` — unit.
- `repositories/anton-abyzov/vskill-platform/scripts/migrations/__tests__/0673-cleanup.int.test.ts` — integration.
- `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/rescan-published/__tests__/in-flight-dedup.test.ts` — unit.
- `.specweave/increments/0673-submission-dedup-cleanup-at-scale/DEPLOY_RUNBOOK.md` — deploy doc (US-005 deliverable).
- `.specweave/increments/0673-submission-dedup-cleanup-at-scale/backups/dedup-summary-0673.json` — produced by the run (gitignored during authoring, committed post-run).
- `.specweave/docs/internal/architecture/adr/0257-large-table-backfill-pattern.md` — ADR (already written).

### Modify (2 files)
- `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/rescan-published/route.ts` — insert pre-`createMany` in-flight check (Phase 3).
- `repositories/anton-abyzov/vskill-platform/scripts/migrations/lib/archive.ts` — additive: `GroupSummary` type + `writeGroupArchive()` function. Keeps all existing exports.

### Reuse (3 artifacts, no modification)
- `repositories/anton-abyzov/vskill-platform/prisma/migrations/20260421100000_submission_unique_repo_skill/migration.sql` — applied AFTER cleanup.
- `repositories/anton-abyzov/vskill-platform/src/lib/submission/upsert.ts` — `upsertSubmission` stays as-is; it's the write-side pattern that the cleanup makes safe to keep.
- `scripts/migrations/0672-collapse-submission-dupes.ts` — referenced for the Neon-host guard (`assertNeonHost`) pattern. Copied (not imported) to avoid coupling.

### Delete (0 files)
- None. The 0672 script is kept as a reference implementation for the < 10 k-row pattern (see ADR-0257 §4 "Negative / trade-offs").

## Risk Register

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R-01 | Concurrent write slips in during cleanup, creates new duplicate post-cleanup | Low (26-day idle baseline) | Medium | Pre-flight 48 h look-back; unique index applied immediately after cleanup catches any new dup via P2002; branch-first testing |
| R-02 | Neon HTTP response exceeds 64 MB on an unexpected path | Low (ID-range batching + temp table) | High | Integration test at 100 k+ rows; branch dry-run before prod |
| R-03 | FK delete order wrong → `RESTRICT` error mid-cleanup | Low (explicit two-statement pattern) | High | Integration test asserts post-state; per-batch transaction rolls back cleanly on error |
| R-04 | Cleanup runs partially, checkpoint corrupts, can't resume | Very low | Medium | `writeCheckpoint` writes atomically via `fs.writeFile(tmp); fs.rename(tmp,final)`; corruption → manual restart from `lastProcessedId` in last commit |
| R-05 | `rescan-published` fix has a new bug, creates duplicates elsewhere | Low | Medium | Unit tests cover all 4 scenarios; deploy after cleanup so unique index is the ultimate guard |
| R-06 | Wall-time exceeds 2 h, deploy window slips | Low | Low | 10 k-batch × ~1 s each = ~50 min baseline; budget 2 h; no customer impact (live traffic unaffected) |
| R-07 | Neon branch can't be created (API outage, quota) | Very low | Medium | Fall back to manual PITR timestamp note in DEPLOY_RUNBOOK; prod run remains safe because the cleanup is idempotent and the archive preserves a group-level audit |
| R-08 | `@@unique` index creation fails post-cleanup (leftover duplicate) | Low | High | Final verification SQL asserts 0 duplicates before `prisma migrate deploy`; if assertion fails, re-run cleanup (idempotent) |
| R-09 | `prisma migrate deploy` skips the 20260421100000 migration because it's already in `_prisma_migrations` | Low | Medium | Pre-flight: `SELECT * FROM _prisma_migrations WHERE migration_name LIKE '%submission_unique%';` — if present and rolled-back, use `prisma migrate resolve` to mark rolled-back; document in runbook |
| R-10 | ScanResult orphan rows (~4.2 M with `submissionId=NULL` post-cleanup) create UI/query regressions | Low | Low | Already validated by research (FK is `ON DELETE SET NULL`; rows remain queryable). Accept as-is; no UI surface queries them by-submissionId |

## Dependencies

- **Blocks**: 0672's deploy is unblocked by this increment (the unique index migration needs cleanup to land first).
- **Blocked by**: nothing — spec/plan/tasks land today, implementation next session.
- **External**: Neon branching API must be reachable; Cloudflare deploy pipeline (`./scripts/push-deploy.sh`) must be healthy.
- **Resource**: CTO sign-off on the Option B quiescence approach (no `LOCK TABLE`). If declined, switch to Option A locked variant — additional ~2 h of read-blocked traffic, no code changes needed in the script itself (just flip a flag).

## Success criteria (mirrors spec.md)

- `SELECT COUNT(*) FROM "Submission"` drops from 2,933,783 → ~108,324 (±100 rows for in-flight writes that land during the final hour, covered by the `@@unique` index).
- Duplicate-pair count query returns 0 after cleanup.
- `@@unique([repoUrl, skillName])` index exists on `Submission` (`Submission_repoUrl_skillName_key`).
- `/queue` first-load returns non-empty (bug 1 resolved).
- `/queue?q=d` returns ≤ 1 row per `obsidian-brain` entry (bug 2 resolved).
- `rescan-published` over 6 h of hourly cron creates no new duplicates for skills already in-flight.
- Cleanup is resumable (verified by integration test + manual SIGTERM drill on branch).
- Summary archive under 10 MB; committed to `.specweave/increments/0673-.../backups/`.
