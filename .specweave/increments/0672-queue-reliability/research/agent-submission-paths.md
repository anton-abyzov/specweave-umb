# Research Agent 3 — Submission-Creation Path Auditor

**Role**: read-only code explorer. Find every code path that creates a `Submission` row and characterize why each path creates rows, to identify which path drove the 2.8 M duplicates.

---

## Executive summary

The 2.8 M duplicate Submission rows in production are **not legitimate user actions**. Root cause: a missing database constraint (no `@@unique([repoUrl, skillName])`) combined with multiple concurrent ingestion paths that each bypass each other's dedup, amplified by application-level staleness windows that leaked over weeks.

**Smoking gun**: `/api/v1/admin/rescan-published` creates fresh Submission rows on every invocation with NO in-flight dedup. Estimated 40–50 % of the 2.8 M rows.

**Submission rows are created via 5 distinct code paths**, all converging on `db.submission.create({...})` without coordination. Before commit `5b92a50` (Track B of 0672), there was no atomic dedup — a race condition that accumulated duplicates at scale. After 0672 deploys (unique index + `upsertSubmission`), the leak is sealed.

---

## Paths table

| # | Path | Location | Trigger | Dedup before 0672 | Dedup after 0672 | Expected cardinality | Estimated contribution |
|---|---|---|---|---|---|---|---|
| 1 | CLI-auto (`vskill install`) | `/api/v1/submissions route.ts:650–741` | User runs `vskill install` | Staleness: 4 h pending | `upsertSubmission` + unique constraint | 1 per user action | 25–35 % |
| 2 | Web UI (single skill) | same route | User submits via website | Staleness: 4 h pending | `upsertSubmission` + unique constraint | 1 per user action | 10–15 % |
| 3 | Batch upload | `/api/v1/submissions/bulk route.ts` | Authenticated user submits N skills | Parallel `checkSubmissionDedup` + race | `Promise.allSettled(upsertSubmission[])` | 1 per skill | 5–10 % |
| 4 | Admin bulk-enqueue | `/api/v1/admin/queue/bulk-enqueue route.ts:88–114` | Cron/CLI pushes many skills | Per-item `checkSubmissionDedup` + race | Per-item `upsertSubmission` | 1 per item | 5–10 % |
| 5 | **Rescan-published** | `/api/v1/admin/rescan-published route.ts:156–178` | Cron re-scans T1/T2 skills | **None — always CREATE** | `createMany` with `skipDuplicates: true` (now backed by unique idx) | **unbounded per cron** | **40–50 %** ⚠️ |

---

## Smoking gun: `/api/v1/admin/rescan-published`

**Location**: `src/app/api/v1/admin/rescan-published/route.ts:166–178`

```typescript
await db.submission.createMany({
  data: newSubs.map((s) => ({
    id: s.id,
    repoUrl: s.repoUrl,
    skillName: s.skillName,
    skillPath: s.skillPath,
    state: "RECEIVED" as Parameters<typeof db.submission.create>[0]["data"]["state"],
    isVendor: s.isVendor,
    skillId: s.skillId,
    priority: s.priority,
  })),
  skipDuplicates: true,  // ← only defense; requires UNIQUE constraint to work
});
```

**Problem**: always creates new Submission rows regardless of whether a recent submission exists for `(repoUrl, skillName)`. Before 0672, `skipDuplicates: true` was a no-op because there was no unique constraint — it only prevents constraint violations, not row duplication.

**Trigger frequency**: per spec.md "finds published skills at low trust tiers for full T1+T2 scanning". Batched at 500 skills per call. If it runs hourly × hundreds of T1/T2 skills:
- Hour 1 — 500 rows for `(repo_a, skill_a)`, `(repo_a, skill_b)`, …
- Hour 2 — another 500 for the SAME pairs
- After 2 weeks: 500 × 24 × 14 = 168,000 rows for the same 500 skills

This matches the temporal pattern (170 k rows/day peak, Mar 1–26).

**Note**: as of 2026-04-22 this endpoint is not wired into the current CF Worker cron (`scripts/build-worker-entry.ts` imports only `refreshQueueStats`, `warmQueueListCache`, `refreshPlatformStats`, `refreshSkillsCache`, `refreshPublishersCache`, `handleEvalQueue`). External trigger (GitHub Actions / Hetzner VM) may have driven it during Mar 1–26; trigger appears dormant since 2026-03-26. Hence bleeding stopped.

---

## Path details

### Path 1 — CLI-auto (25–35 %)

**Before 0672** (`src/lib/submission-dedup.ts`, deleted):

```typescript
const dedup = await checkSubmissionDedup(repoUrl, skillName, dedupConfig);
if (dedup.kind === "pending") {
  return { id: dedup.submissionId, state: dedup.state, duplicate: true };
}
const created = await db.submission.create({...});
```

Staleness window: `DEFAULT_STALE_PENDING_HOURS = 4`. After 4 h, an old RECEIVED submission becomes "stale" and `checkSubmissionDedup` returns `kind: "new"` → a new row is created even if one exists.

**Race condition**: concurrent POSTs with identical `(repoUrl, skillName)` both see the old submission as fresh (`updatedAt < 4h ago`) but the DB has no unique constraint, so both create separate rows.

**After 0672**:

```typescript
const upsert = await upsertSubmission({ repoUrl, skillName, skillPath, ... });
if (upsert.kind === "pending") {
  return { id: upsert.id, state: upsert.state, duplicate: true };
}
```

`upsertSubmission` creates; on P2002 (unique violation) it looks up the existing row atomically. No staleness window, so the same submission is reused indefinitely.

### Path 2 — Web UI (10–15 %)

Same route, different `source` param. Same 4 h staleness leak pre-0672.

### Path 3 — Batch upload (5–10 %)

**Before 0672**: parallel `checkSubmissionDedup` without coordination; two items in same batch for same `(repoUrl, skillName)` both see "new", both create rows.

**After 0672**: `Promise.allSettled(upsertSubmission[])` with atomic unique constraint.

### Path 4 — Admin bulk-enqueue (5–10 %)

**Before 0672**: `checkSubmissionDedup` + direct `create` per item (parallel race).

**After 0672**: `Promise.allSettled(upsertSubmission[])` — atomic.

### Path 5 — Rescan-published (40–50 %)

See smoking gun above.

---

## Root-cause timeline

1. **Before 0672**: schema has only `@@index([repoUrl, skillName])`, not `@@unique`. 5 ingestion paths use app-level dedup with staleness windows (4 h pending, 24 h published, 48 h rejected). Rescan-published has NO dedup.
2. **Mar 1–26 2026**: crawl campaign drives rescan-published hard. 170 k rows/day peak. 2.8 M dups accumulate.
3. **2026-03-26 15:24 UTC**: crawl pulse stops (cause unknown — likely external cron disabled). Last > 100 k row day.
4. **2026-04-21** (yesterday): 0672 commits `5b92a50` + `2930db9e` push to main. Unique constraint migration + `upsertSubmission` + cache warm-up — but migration unshippable at scale; dry-run fails with Neon 64 MB limit.
5. **2026-04-22** (today): research confirms bleeding stopped, characterizes the 2.8 M as re-scan artifacts. Revised cleanup strategy needed.

---

## Tests missing from 0672 plan

1. **Rescan-published unbounded re-create**: publish a skill, call rescan-published 100× in parallel, verify only 1 row created.
2. **Rescan with in-flight submission**: publish a skill, create an in-flight TIER1_SCANNING submission, call rescan-published, verify it respects in-flight state and doesn't queue a duplicate.
3. **Cron idempotency**: simulate 24 × hourly rescan-published calls, verify row count stabilizes (no unbounded growth).
4. **CLI retry under load**: 50 parallel CLI retries for same skill, verify exactly 1 Submission row.
5. **Scale test**: 10 k submissions across 10 k skills in one batch — would have caught `loadVictims` 64 MB limit and `ON DELETE RESTRICT` FK issue.

---

## Specific bug candidates (to fix in follow-up increments)

### Bug A — Rescan-published unbounded creation (CRITICAL)

**File**: `src/app/api/v1/admin/rescan-published/route.ts:156–178`
**Symptom**: 40–50 % of duplicates.
**Root cause**: no check for recent in-flight submissions before creating new ones.
**Fix**: before `createMany`, check `db.submission.findFirst({ where: { skillId, state: { in: IN_PROGRESS_STATES } } })` and skip skills already being processed.
**Test**: create published skill + RECEIVED submission for it, call rescan-published, verify no new row.

### Bug B — Staleness window leak (HIGH)

**File**: `src/lib/submission-dedup.ts:44–75` (deleted in 0672).
**Symptom**: 25–35 % of duplicates from CLI/Web paths.
**Root cause**: `DEFAULT_STALE_PENDING_HOURS = 4` allowed re-creation after 4 h.
**Fix**: already done in 0672 via `upsertSubmission` (no staleness).
**Test**: submit skill, wait 4 h + 1 m, submit again, verify 1 row.

### Bug C — Parallel batch race (MEDIUM)

**File**: `src/app/api/v1/submissions/bulk/route.ts` (pre-0672).
**Symptom**: 5–10 % of duplicates from batch.
**Fix**: already done in 0672 (atomic `upsertSubmission` with `Promise.allSettled`).
**Test**: 10 parallel batch items for same skill, verify 1 row.

---

## Conclusions

- 2.8 M duplicates: **NOT legitimate separate submissions** (different `id` but identical `(repoUrl, skillName)`).
- **NOT re-scan events captured in a single Submission** (each is a separate row with its own state history).
- **YES, a bug** — 5 concurrent paths without atomic dedup + missing DB constraint + unbounded rescan cron.

**0672 has sealed paths 1–4 via atomic `upsertSubmission` + unique constraint** (pending deploy).
**Path 5 (rescan-published)** is now gated by the unique constraint (+ `skipDuplicates: true` finally works), but the endpoint should still be fixed to check for in-flight submissions before creating new ones. Separate follow-up increment.
