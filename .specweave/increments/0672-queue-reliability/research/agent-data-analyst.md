# Research Agent 1 — Data Analyst

**Role**: read-only analyst querying prod Neon to characterize what the 2.8 M "duplicate" Submission rows actually are. Find out: duplicates, or version history?

**Ran against**: production Neon DB (`ep-polished-haze-aea6snnj-pooler.c-2.us-east-2.aws.neon.tech`), 2026-04-22.

---

## Headline

**The 2.8 M "victims" are real re-scan duplicates, not version history.** There is no version signal anywhere in the Submission table (`contentHashAtScan` is NULL on 100 % of rows; `SkillVersion` table has 62 rows total and is orphaned from the top 10 most-submitted skills). Rows differ only on identity columns (`id`, `createdAt`, `updatedAt`) and occasionally on `skillPath` / `skillId`.

## 1. What varies within a dup group

Sample group: `https://github.com/zhaobohao/workspace // 数据库` — 433 rows, spanning 25 days (Mar 2–26, 2026).

| Column | Distinct values | Notes |
|---|---|---|
| `id` (PK) | 433 | All unique (obviously) |
| `createdAt` | 433 | Each crawl makes a new row |
| `updatedAt` | 433 | Tracks state transitions |
| `state` | 2 | 432 PUBLISHED, 1 REJECTED |
| `skillPath` | 2 | Two file locations inside repo |
| `skillId` | 2 + 425 NULL | FK churn — skillId gets reassigned and orphaned |
| `contentHashAtScan` | 0 (all NULL) | **Column never populated** |
| `submitterEmail` | 0 (all NULL) | Never populated |
| `userId` | 0 (all NULL) | Never populated |
| `repositoryId` | 0 (all NULL) | Never populated |
| `provenanceStatus` | 0 (all NULL) | Never populated |
| `provenanceVerified` | 1 | Always the default |
| `priority` | 1 | Always the default |
| `isVendor`, `vendorOrg` | 1 / 0 | Not meaningful |

Across the top-100 largest groups: avg 2.57 distinct `skillPath`, 271 rows. All 100 have `contentHashAtScan = NULL` on every row. Same result for a random 200 of small (2–5 row) groups.

## 2. Global NULL / ghost counts

| Column | NULL count | % |
|---|---|---|
| `contentHashAtScan` | 2,933,783 | **100 %** |
| `submitterEmail` | 2,933,783 | 100 % |
| `userId` | 2,933,561 | 99.99 % |
| `repositoryId` | 2,933,482 | 99.99 % |
| `skillId` | 22,391 | 0.76 % |
| `skillId` NULL AND state=PUBLISHED ("ghost published") | 3,169 | — |

## 3. State distribution (global)

```
PUBLISHED:   2,911,321  (99.23 %)
REJECTED:       21,022
DEQUEUED:        1,309
EXPANDED:           77
BLOCKED:            52
TIER1_FAILED:        2
```

Terminal-state PUBLISHED dominates — not workflow history, not retry loops.

## 4. Temporal pattern

- Data spans **Feb 24 → Apr 17 2026** (36 distinct days), but ~99 % of rows land between **Mar 1 and Mar 26** (25-day crawl campaign).
- Daily submission counts peak at **170 k/day** in mid-March.
- Per-day ratio submissions : unique `(repoUrl, skillName)` groups = **2.5–7 ×** — each skill re-submitted 2–7 times per day.
- Consistent with a cron job re-scanning every repo/skill daily.
- Verdict: a **crawl pulse**, not version history. If it were version history, we'd see distinct `contentHashAtScan` values at boundaries.

## 5. Skill / SkillVersion relationship

- `SkillVersion` table exists but holds only **62 rows** total.
- Top 10 Skills by Submission count (e.g., 4,920 submissions for `404kidwiz/claude-supercode-skills`) have **zero** SkillVersion rows.
- Conclusion: version tracking infrastructure exists as a stub but isn't wired to the heavy submitters. Submission rows are not "capturing version history" — they aren't.

## 6. FK child fan-out (blast radius of delete)

| Child table | Row count | FK semantic | Avg per Submission |
|---|---|---|---|
| `SubmissionStateEvent` | 8,976,455 | ON DELETE **RESTRICT** | ~3.06 (max 129) |
| `ScanResult` | 4,380,746 | ON DELETE SET NULL | ~1.5 |
| `EmailNotification` | 0 | ON DELETE RESTRICT | 0 |
| `SubmissionJob` | 0 | ON DELETE RESTRICT | 0 |
| `EvalRun` | 5,458 | ON DELETE SET NULL | ~0 |

**Critical gotcha**: `SubmissionStateEvent` is `ON DELETE RESTRICT`. A naive `DELETE FROM "Submission"` will fail immediately. State events must be deleted first (or cascaded manually).

## 7. Indices / constraints audit

```
Submission_pkey                         UNIQUE ON (id) — the only unique index
Submission_skillName_idx                non-unique
Submission_createdAt_idx                non-unique
Submission_state_idx                    non-unique
Submission_userId_idx                   non-unique
Submission_repositoryId_idx             non-unique
Submission_repoUrl_skillName_idx        non-unique  ← key for our work
Submission_repositoryId_skillName_idx   non-unique
Submission_state_priority_createdAt_idx non-unique
Submission_state_updatedAt_idx          non-unique
```

**No unique constraint exists anywhere except the PK.** Root cause of the dedup failure.

## 8. Candidate uniqueness key matrix

Total rows = 2,933,783. Victim = rows to remove under that key.

| Candidate | Unique groups | Victims | Pros | Cons |
|---|---|---|---|---|
| `(repoUrl, skillName)` | 108,324 | **2,825,459** | Matches existing plan / `upsertSubmission` | Collapses 2 `skillPath` variants into 1 row (~7 k groups affected) |
| `(repoUrl, skillName, skillPath)` | 115,710 | **2,818,073** | Preserves path variation | Saves only 7 k rows vs first option (noise) |
| `(repoUrl, skillName, skillPath, state)` | 121,787 | 2,811,996 | PUBLISHED + REJECTED twins separate | Adds noise — state transitions belong in `SubmissionStateEvent` |
| `(repoUrl, skillPath)` | 109,539 | ~2,824,244 | Path-first model | Breaks if `skillName` ever matters (renames) |
| `(skillId)` (non-NULL only) | 106,935 | ~2,802,000 | Aligns with Skill identity | 22 k rows have NULL skillId |

**Recommended**: `(repoUrl, skillName, skillPath)` — preserves path variation, collapses re-scans. Saves 7 k legitimate rows. If aggressive: add `state` to keep REJECTED twins separate.

## 9. What I don't know (honest gaps)

1. **Survivor rule** — MAX(createdAt) vs state-aware (PUBLISHED first). Not picked; affects which state events need re-parenting vs deleting.
2. **Other FK tables** — only checked the 5 known children. Schema should be cross-referenced for anything I missed.
3. **ScanResult orphan semantics** — `ON DELETE SET NULL` leaves orphaned ScanResult rows. Queryable standalone? Effectively garbage? Need app code inspection.
4. **Why is `contentHashAtScan` NULL everywhere?** — Scan pipeline clearly ran (4.38 M ScanResult rows). Could the hash be on ScanResult instead? Worth checking before concluding "no version signal."
5. **The 3,169 ghost PUBLISHED** (`skillId=NULL`) — orphaned Skill rows, or never created? Affects whether they're safe to archive.
6. **The 1 REJECTED out of 432 PUBLISHED** — spurious test data, or real moderation? Affects whether state=REJECTED rows deserve preservation.
7. **Neon 64 MB limit** — I used aggregates + `LIMIT` everywhere. No deep per-row inspection of large groups.

## 10. Bottom-line recommendation

- Uniqueness key: `(repoUrl, skillName, skillPath)`; victim ≈ 2.82 M.
- Survivor rule: `ORDER BY (state='PUBLISHED') DESC, updatedAt DESC LIMIT 1`.
- Handle `SubmissionStateEvent ON DELETE RESTRICT` explicitly — delete state events first.
- Add a real unique index after cleanup to prevent recurrence.
- Ignore `contentHashAtScan` — carries zero signal today. If versioning becomes real, `SkillVersion` is the right home.
