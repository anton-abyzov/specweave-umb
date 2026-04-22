# 0673 Hand-off — Session Log

> **Purpose**: this document is the single source of truth for where we are in the 0673 cleanup effort. Every session (potentially on a different Claude account) reads this first, does the next step, and updates this document before stopping.
>
> **Rule**: each step ends with "current state" + "next step" + "to resume, say ..." updated here. Do not leave it stale.

---

## Current state (2026-04-22 UTC) — after Step 1

### What landed in this session
- **0673 increment created** at `.specweave/increments/0673-submission-dedup-cleanup-at-scale/`
- **spec.md**: 5 user stories (US-001..US-005), 24 ACs, 12 risks, 13 test-strategy rows, 12 edge cases, 9 non-goals, 4 FRs. All stories tagged `**Project**: vskill-platform`.
- **plan.md**: batched cleanup algorithm, Option B concurrency (48 h quiescence pre-flight), filesystem-JSON checkpoints, `neonctl` branch strategy, file manifest (8 create, 2 modify, 3 reuse, 0 delete), 10 risks (R-01..R-10), phased rollout.
- **ADR-0257** at `.specweave/docs/internal/architecture/adr/0257-large-table-backfill-pattern.md` — new ADR for the reusable large-table backfill pattern (separate from ADR-0256 which is Tier-2 LLM runtime).
- **tasks.md**: 20 tasks, 3 tracks (A cleanup 9, B rescan fix 4, C runbook+deploy 7). All 24 ACs cited. RED → GREEN → REFACTOR ordering per track.
- **External sync**: JIRA Epic [SWE2E-846](https://antonabyzov.atlassian.net/browse/SWE2E-846), ADO Feature [#1685](https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/1685), 5 ADO User Stories #1686–#1690.

### What did NOT land
- Any code changes in `repositories/anton-abyzov/vskill-platform/` — this session was planning only
- `scripts/migrations/0673-cleanup.ts` — does not exist yet (Step 2)
- Any rescan-published edits — untouched (Step 3)
- Any Neon branch — not created yet (Step 4)
- No production DB touches — Submission table unchanged (verified before and after session)

### Key spec/plan divergence to remember
**Checkpoint storage: filesystem JSON, not a DB table.** spec.md (AC-US3-01) mentioned a `_migration_0673_checkpoint` DB table; plan.md + ADR-0257 §3.5 override this to a filesystem JSON at `checkpoints/progress.json` because filesystem checkpoints survive Neon branch switches, PITR rollbacks, and connection drops. The external API (`readCheckpoint`/`writeCheckpoint`) is the same either way — implementation can be flipped in one file (`lib/checkpoint.ts`) if you change your mind. Tasks.md follows the plan/ADR (filesystem).

### 0672 state (unchanged)
- Commit `5b92a50` on `main` (vskill-platform) — **NOT deployed** to Cloudflare Workers.
- Migration SQL `20260421100000_submission_unique_repo_skill` exists in git but **NOT applied** to prod Neon.
- `upsertSubmission` + cache warm-up code is committed. Safe because:
  - It doesn't run until `push-deploy.sh` executes (Step 6 of this sequence).
  - Without the unique index, the `create` call inside `upsertSubmission` would succeed and never trigger P2002, meaning no dedup. That's why we MUST run the cleanup + unique index BEFORE deploying the code — otherwise dedup would silently be disabled.

### Production DB snapshot (verified 2026-04-22)
- Total `Submission`: 2,933,783
- Duplicate victims under `(repoUrl, skillName)`: 2,825,767
- Survivors (expected post-cleanup): ~108,324
- Last row created: 2026-04-17 07:16:15 UTC (6 days ago; bleed stopped since 2026-03-26)
- `SubmissionStateEvent`: 8,976,455 rows (FK ON DELETE RESTRICT — must delete these first in each batch)
- `ScanResult`: 4,380,746 rows (FK ON DELETE SET NULL — auto-nulls on victim delete)

### Git state
- Umbrella `main`: latest `5266faf8 0672: store prod-scale findings and research agent reports`
- vskill-platform `main`: latest `5b92a50 0672: dedup via upsert + cache warm-up + unique index`
- 0673 files committed in next commit after this HANDOFF.md is written.

---

## Next step — Step 2

**Goal**: implement the revised batched cleanup script + tests following tasks.md Track A (T-001..T-009) in strict TDD.

**Expected deliverables**:
- `repositories/anton-abyzov/vskill-platform/scripts/migrations/0673-cleanup.ts` (core script)
- `repositories/anton-abyzov/vskill-platform/scripts/migrations/lib/survivor.ts`
- `repositories/anton-abyzov/vskill-platform/scripts/migrations/lib/checkpoint.ts`
- Test files: `scripts/migrations/__tests__/0673-{cleanup,survivor,checkpoint}.test.ts`
- Integration test: `scripts/migrations/__tests__/0673-cleanup.int.test.ts` (skipped without `DATABASE_URL_TEST`)

**Do NOT touch**:
- Production Neon (only the integration test — and only when `DATABASE_URL_TEST` is set to a Neon *branch* URL, never prod)
- `src/app/api/v1/admin/rescan-published/route.ts` — that's Step 3, separate track
- 0672's files (schema, upsertSubmission, cache warm-up) — already correct

**Runtime estimate**: ~30–60 min of implementation work.

**Verification before closing Step 2**:
- `npx vitest run scripts/migrations/__tests__/0673-*.test.ts` → all unit tests pass
- `npx tsx scripts/migrations/0673-cleanup.ts --help` → prints usage
- `npx tsx scripts/migrations/0673-cleanup.ts --dry-run` with `DATABASE_URL_TEST` unset → exits cleanly without DB access

**Commit** as:
```
0673: batched cleanup script + tests (TDD Track A)
```
Then push to `main` on the vskill-platform child repo.

**Update THIS HANDOFF.md** when done — move Step 2 to "Current state" and set Step 3 as "Next step".

---

## To resume in a new Claude session

Say exactly:

> Continue 0673 from Step 2. Read `.specweave/increments/0673-submission-dedup-cleanup-at-scale/HANDOFF.md` + `tasks.md` (Track A, T-001..T-009) + `plan.md` (§§ cleanup algorithm, checkpoint) + `spec.md` (US-002, US-003). Implement the cleanup script with strict TDD. Do NOT touch prod; do NOT run migrations; do NOT deploy.

The session should:
1. Read this file + tasks.md Track A + plan.md cleanup sections
2. Execute T-001..T-009 in RED→GREEN→REFACTOR order
3. Commit as `0673: batched cleanup script + tests (TDD Track A)` and push
4. Update HANDOFF.md with new "Current state" + "Next step = Step 3" and commit+push

---

## Rollback

Nothing to roll back as of this HANDOFF. No production data touched since the dry-run halt. If the plan itself is wrong, abort by setting `0673/metadata.json.status = "abandoned"` and opening an incident-response increment.

---

## Session log

| Date (UTC) | Session | Step | Outcome |
|---|---|---|---|
| 2026-04-22 | anton.abyzov@gmail.com | 1 (planning) | Spec/plan/tasks committed; sync done; HANDOFF.md written |
| — | — | 2 (cleanup script + tests) | pending |
| — | — | 3 (rescan-published in-flight dedup fix) | pending |
| — | — | 4 (Neon branch dry-run) | pending |
| — | — | 5 (prod cleanup + unique index) | pending |
| — | — | 6 (push-deploy.sh code deploy) | pending |
| — | — | 7 (smoke tests + 24 h monitor + close 0672/0673) | pending |
