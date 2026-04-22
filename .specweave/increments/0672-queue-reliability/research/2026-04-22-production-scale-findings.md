# Production Scale Findings — 2026-04-22

> **Status**: Deploy of 0672 HALTED during dry-run. The migration is unshippable as designed against actual prod data. This document captures what we learned, what changed, and what the revised path looks like.
>
> **Trigger**: Running `scripts/migrations/0672-collapse-submission-dupes.ts --dry-run` against prod Neon failed with a Neon `HTTP 507: response is too large (max 67108864 bytes)` error — `loadVictims()` tries to load all victims + their FK children in one query, and the response exceeds Neon's 64 MB serverless limit.

## Headline

- **Spec expected**: 6–20 duplicate Submission rows (sampled from the visible `/queue?q=d` page, which paginates at 50).
- **Reality measured**: **2,825,767 victim rows** — 96.3% of the 2,933,783-row `Submission` table.
- **Sampling error**: the spec's "6–7 obsidian-brain duplicates" came from a 50-row UI page. Real scale was only discoverable via a `COUNT(*)` on the DB.
- **No active bleeding**: last `Submission` row created `2026-04-17 07:16:15 UTC`. Zero rows in the last 24 h. 25 rows total since `2026-03-26 15:24 UTC`. The 2.8 M backlog is historical — not growing.

## Production snapshot (2026-04-22 UTC)

| Metric | Value |
|---|---|
| Total `Submission` rows | 2,933,783 |
| `(repoUrl, skillName)` groups with COUNT > 1 | 91,159 |
| Victim rows (to be collapsed) | 2,825,767 |
| Unique rows (no duplicates) | 16,857 |
| State = PUBLISHED | 2,911,321 (99.23 %) |
| State = REJECTED | 21,022 |
| State = DEQUEUED | 1,309 |
| `contentHashAtScan` NULL on every row | 100 % |
| `submitterEmail` NULL | 100 % |
| `userId` NULL | 99.99 % |
| `repositoryId` NULL | 99.99 % |
| `skillId` NULL | 0.76 % |
| Rows in `SubmissionStateEvent` | 8,976,455 |
| Rows in `ScanResult` | 4,380,746 |
| Rows in `SubmissionJob` | 0 |
| Rows in `EmailNotification` | 0 |
| Rows in `EvalRun` | 5,458 |
| Rows in `SkillVersion` | 62 (sparsely populated; orphaned from top submitters) |

## What a "duplicate" actually is here

Three parallel research agents (data analyst on prod Neon + code reader for versioning + code reader for creation paths) converged on:

1. **Not version history.** `contentHashAtScan` is NULL on 100 % of rows — there is no version signal in `Submission` today. The `SkillVersion` table is the proper home for versions (`@@unique([skillId, version])`, content-hash driven bumps in `publishSkill`), but it's only 62 rows, unrelated to the heavy submitters.
2. **Not distinct user submissions.** 99.23 % of rows are terminal-state PUBLISHED duplicates; `userId` and `submitterEmail` are NULL everywhere, meaning these weren't interactive user actions.
3. **Crawl-pulse re-scans.** Temporal pattern shows ~99 % of rows land between 2026-03-01 and 2026-03-26, peaking at 170 k/day. Per-day submissions-to-unique-groups ratio is 2.5–7 × — a cron that re-scanned every repo/skill 2–7 times a day for 25 days.
4. **Source of the bleed: `/api/v1/admin/rescan-published`** — creates fresh Submission rows via `createMany({ skipDuplicates: true })` with **no in-flight dedup check** and **no unique constraint backing `skipDuplicates`** (which is thus a no-op). Estimated 40–50 % of the 2.8 M rows.
5. **Secondary sources** (before 0672): CLI-auto 4 h staleness leak (~25–35 %), Web UI 4 h leak (~10–15 %), batch/bulk parallel races (~5–10 %).
6. **Bleeding stopped ~2026-03-26 15:24 UTC.** No code change visible in the diff; likely cron disabled manually or crawler campaign ended. Whatever caused it, Submission writes trickled to < 1/day.

## Versioning model (ground truth from `prisma/schema.prisma` + `publish.ts`)

- `Skill.name` is globally unique (`schema.prisma:216`). One skill, one canonical row.
- `SkillVersion` is keyed `@@unique([skillId, version])` (`schema.prisma:378`). Per-version `contentHash` (SHA-256 of SKILL.md) + `gitSha`.
- Version bumps are **content-diff-driven**, not frontmatter or tag-driven: `publishSkill` compares `scan.contentHash` against `latestVersion.contentHash` — if different → patch bump (1.0.0 → 1.0.1), if same → update cert tier in place (`publish.ts:221–238`).
- `Submission` is a **processing receipt**, not a version artifact. At most one active Submission per `(repoUrl, skillName)` is the intended cardinality.
- **The 0672 choice of `@@unique([repoUrl, skillName])` is correct.** It does not conflict with versioning — versions live in `SkillVersion`, one Submission row can walk through many versions via successive scans.

## Why the original migration is not shippable

1. **Neon 64 MB query limit.** `loadVictims` in `scripts/migrations/0672-collapse-submission-dupes.ts` does `SELECT row_to_json(v) FROM "Submission" v JOIN survivors ...` with no `LIMIT`. At 2.8 M rows × ~1–5 KB per row, the response is 3–14 GB — fails instantly.
2. **JSON archive blow-up.** The archive at `backups/dedup-collapse-0672.json` was intended to hold every victim + its FK children (state events, scan results, etc.) for rollback. At 2.8 M victims × 5 child tables (~3 rows each on average), the archive would be 10–100 GB — not serializable, not committable to git.
3. **FK constraint gotcha.** `SubmissionStateEvent.submissionId → Submission` is `ON DELETE RESTRICT` (not CASCADE). The original collapse script's final step — `DELETE FROM "Submission" WHERE id IN (...victims)` — would fail immediately on any victim with state events (all of them). The CRITICAL fix in sw-closer moved `writeArchive()` before the transaction but did not fix this. Needs an explicit `DELETE FROM "SubmissionStateEvent"` first.
4. **Survivor rule too coarse.** Original rule was `MAX(createdAt)`; doesn't prefer PUBLISHED over REJECTED. A REJECTED survivor would mean the skill appears rejected in the UI even though 431 PUBLISHED rows existed.

## Revised uniqueness key

**Recommendation: keep `(repoUrl, skillName)`.** Alternatives considered:

| Candidate | Unique groups | Victims | Verdict |
|---|---|---|---|
| `(repoUrl, skillName)` | 108,324 | 2,825,459 | **CHOSEN** — aligns with `upsertSubmission` shipped in Track B |
| `(repoUrl, skillName, skillPath)` | 115,710 | 2,818,073 | Saves 7 k rows; requires Track B code change; not worth re-testing |
| `(repoUrl, skillName, skillPath, state)` | 121,787 | 2,811,996 | State transitions belong in `SubmissionStateEvent`, not row dupes |
| `(skillId)` | 106,935 | ~2,802,000 | 22,391 rows have NULL `skillId`; not viable as sole key |

## Revised survivor rule

```sql
ORDER BY
  (CASE state WHEN 'PUBLISHED' THEN 0 ELSE 1 END),  -- prefer PUBLISHED
  updatedAt DESC                                       -- then most recent
LIMIT 1
```

Rationale: PUBLISHED represents the steady-state outcome for 99 % of groups. REJECTED-only survivors for the few groups where REJECTED is the only state. Most-recent `updatedAt` preserves the latest state-machine position.

## Revised cleanup strategy (DB-side, batched, no JSON archive)

1. **Summary-only archive** (~9 MB total):
   - For each of 91,159 groups: `{repoUrl, skillName, survivorId, victimCount, stateDistribution}` stored as JSON in `backups/`.
   - Individual victim rows are NOT preserved. Rationale: 99 % PUBLISHED with all meaningful columns NULL — no information to lose.

2. **Batched SQL deletion** per (repoUrl, skillName) group or by victim-ID chunks of 10 k:
   ```
   -- Step 1: delete state events (ON DELETE RESTRICT requires this)
   DELETE FROM "SubmissionStateEvent" WHERE "submissionId" = ANY($victim_ids);
   -- Step 2: delete victims (ScanResult/EvalRun auto-SET NULL their FKs)
   DELETE FROM "Submission" WHERE id = ANY($victim_ids);
   ```
   ~282 batches of 10 k, or finer-grained for safety. Each batch in its own transaction. Idempotent + resumable (can restart on failure).

3. **Apply unique index migration** (the existing 0672 SQL — drops the index and adds `@@unique([repoUrl, skillName])`).

4. **Deploy 0672 code** (`upsertSubmission`, cache warm-up) via `./scripts/push-deploy.sh`.

5. **Post-deploy verification**:
   - `/queue` renders rows on first load (bug 1 fixed).
   - `/queue?q=d` shows ≤ 1 `obsidian-brain` row (bug 2 fixed).
   - Hourly cron logs `queue list warmup: wrote=5 failed=0`.
   - No P2002 leaking into HTTP responses.

## Orphaned data decisions

- **ScanResult.submissionId**: FK is `ON DELETE SET NULL`. After cleanup, ~4.2 M `ScanResult` rows will have `submissionId = NULL`. These remain queryable standalone. Accept as-is — they encode scan verdicts that have independent value.
- **EvalRun.submissionId**: same `ON DELETE SET NULL`. 5,458 rows affected. Accept as-is.
- **SubmissionJob / EmailNotification**: 0 rows globally. No-op.

## Gap analysis — what 0672's test plan missed

1. **No rescan-published test.** The 40–50 % bleed source has no test for "hourly call creates only 1 row per skill". Needed as part of revised cleanup.
2. **No scale test.** 20-parallel-upsert covered race within a single submission; no test for "10 k submissions across 10 k skills under load". Would have caught neither the `loadVictims` 64 MB limit nor the `ON DELETE RESTRICT` FK issue.
3. **No real-data dry-run.** Tests seed 3 victim groups into a blank Neon branch; they never hit prod-scale data. Hence the spec assumed 6–20 victims.
4. **No archive size budget.** No assertion that `backups/dedup-collapse-0672.json` stays under (e.g.) 10 MB. Would have caught the JSON blow-up.

These gaps should be closed in 0673's test plan.

## Decisions pending user approval

1. Create `0673-submission-dedup-cleanup-at-scale` as a new increment to carry the revised strategy, or amend 0672 post-hoc? (0672 is already closed with commits `5b92a50` + `2930db9e` — cleaner to do 0673.)
2. Execute cleanup against production directly (bleeding has stopped; safe window) or branch a Neon DB first to test the revised script?
3. Orphan the 4.2 M `ScanResult` rows (default, per FK `SET NULL`), or delete them alongside their Submissions?

## References

- [spec.md](../spec.md) — original ACs based on the 20-dupe assumption
- [plan.md](../plan.md) — original migration design
- [tasks.md](../tasks.md) — T-001..T-008 (Track A) authored the broken migration
- [DEPLOY_RUNBOOK.md](../DEPLOY_RUNBOOK.md) — obsolete; assumes the broken migration will work
- `reports/code-review-report.json` — caught 2 CRITICAL bugs in the migration but missed the scale issue
- Research agent reports:
  - [agent-data-analyst.md](./agent-data-analyst.md)
  - [agent-versioning-model.md](./agent-versioning-model.md)
  - [agent-submission-paths.md](./agent-submission-paths.md)
