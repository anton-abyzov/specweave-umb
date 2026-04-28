---
status: completed
---
# 0763 — Queue avg score fix + counter consistency audit

## Problem

`/queue` shows **AVG SCORE: 0.0** while displaying real counts (TOTAL 111,091, PUBLISHED 105,999). Live API confirms: `{"avgScore":0,"degraded":true,...}`.

Separately, the home page hardcodes `Search 100,000+ verified skills...` — actual `verifiedCount` is 115,343 (~15% stale).

## Root cause

**Avg score zero** — `src/lib/cron/queue-stats-refresh.ts:101-116`:

```sql
SELECT ROUND(AVG(score)) AS avg_score
FROM "ScanResult"
WHERE score > 0
```

- `ScanResult` has millions of rows, no index on `score` → full table scan.
- 5s timeout (line 108) is too short.
- Catch block (line 113-115) explicitly does NOT mark `p1Degraded` ("counts are the critical part"), and `avgScore` stays at the initialized `0` (line 56).
- UI `QueuePageClient.tsx:740-745` renders `0.0` instead of em-dash because the value is a real `0`, not `null`.

**Counter divergence** (audited, NOT changing semantics):
- Home `verifiedCount = 115,343` (Skill table, NOT isDeprecated, certTier IN VERIFIED/CERTIFIED)
- Queue `published = 105,999` (Submission table, state IN published-states)
- These tables measure different entities; ~10K diff is legacy Skills imported pre-submission system. Documented for product in `reports/findings.md`.

## User stories

### US-001: AVG SCORE reflects real registry data

**As a** queue dashboard viewer
**I want** the AVG SCORE card to show the real average certification score
**So that** I can see registry quality at a glance.

**Acceptance criteria**:
- [x] AC-US1-01: With ≥1 published skill, `/queue` AVG SCORE renders a positive integer in [1, 100], never `0.0` unless legitimately zero.
- [x] AC-US1-02: avg_score query targets `Skill.certScore`, not `ScanResult.score`, with budget ≤ 2s.
- [x] AC-US1-03: When avg_score query fails, the previous warm value is preserved (regression guard at queue-stats-refresh.ts:230 already handles this) — no spurious 0 overwrite.
- [x] AC-US1-04: API response from `/api/v1/submissions/stats` returns `avgScore` matching the home page's quality narrative (same source table).

### US-002: Search placeholder reflects real count

**As a** home page visitor
**I want** the search input placeholder to reflect the live verified-skill count
**So that** the number is consistent with the rest of the page.

**Acceptance criteria**:
- [x] AC-US2-01: HeroSearch placeholder reads `Search NNN,NNN+ verified skills...` where NNN,NNN is `verifiedCount` floored to nearest 1,000.
- [x] AC-US2-02: When `verifiedCount` is 0 / unavailable, falls back to `Search verified skills...` (no fake number).
- [x] AC-US2-03: When `verifiedCount < 1,000`, renders the raw count without thousand-separator (`Search 142+ verified skills...`).

## Reopened 2026-04-28 — true root cause was three-bug stack

The original 0763 was correct in *intent* but the avgScore-zero symptom in
production (`{"avgScore":0,"degraded":true,"totalSkillsAll":0}`) was actually
caused by THREE separate bugs that compounded, none of which the original
0763 surfaced:

1. **VM source has been a no-op since 0719.** `crawl-worker/sources/stats-
   compute.js` had a JSDoc literal `*/10` (meaning "every 10 minutes") in the
   second comment line — that string terminates the block comment at parse
   time, so the entire module raised `SyntaxError: Unexpected identifier
   'event'` on every dynamic import. The scheduler's catch block silently
   swallowed it, so the VM has *never* written queue stats and the entire
   2026-04 KV blob has been maintained solely by the CF watchdog.
2. **Wrong column name in the Skill query (0791-introduced).** The watchdog
   and `computeQueueStats` Phase 1b both queried
   `COUNT(*) FILTER (WHERE "status" IN ('VERIFIED', 'CERTIFIED'))` — but
   `Skill` has no `status` column; the field is `certTier`. Postgres throws
   `column "status" does not exist`, the catch block calls it "best-effort",
   and `watchdogVerifiedSkills` / `watchdogTotalSkillsAll` / `watchdogAvgScore`
   all stay null. Carry-forward then keeps the prior KV value, so once
   `avgScore = 0` is in the blob it propagates forever.
3. **VM payload, when it eventually works, would clobber CF-only fields.**
   Even after #1 and #2 are fixed, the VM POST to
   `/api/v1/internal/stats/queue` was a full overwrite — losing
   `rejectionBreakdown` (CF Phase 2-only) and the prior
   `avgProcessingTimeMs` (sourced from `QUEUE_METRICS_KV` which the VM can't
   read).

Why `verifiedSkills: 117562` shows in the live API despite #2: the read path
has an `enrichVerifiedSkills` cross-cache fallback that reads
`getHomeStats().verifiedCount` from the platform-stats blob (whose own
compute uses `certTier` correctly). There is no equivalent enrichment for
`avgScore` or `totalSkillsAll`, so they stay at the bad cached zero.

### US-003: Worker + VM Skill query uses the correct column

**As a** queue dashboard viewer
**I want** the AVG SCORE card to render real data
**So that** the value reflects the live registry quality.

**Acceptance criteria**:
- [x] AC-US3-A1: `src/lib/cron/queue-stats-refresh.ts` Phase 1b and the
  `ensureFreshStats` watchdog query `"certTier" IN ('VERIFIED', 'CERTIFIED')`
  (not `"status"`).
- [x] AC-US3-A2: After deploy, `curl https://verified-skill.com/api/v1/submissions/stats | jq '.avgScore, .totalSkillsAll'`
  returns positive integers and stays positive across two CF cron ticks.
  Verified 2026-04-28: 06:25 → avgScore=97 totalSkillsAll=117564;
  06:35 → avgScore=97 totalSkillsAll=117565.

### US-003B: VM-side queue stats source matches Worker

**As a** queue dashboard viewer
**I want** the AVG SCORE card to render real data even after the VM cron tick
**So that** the value does not flip back to 0 every 10 minutes.

**Acceptance criteria**:
- [x] AC-US3-01: `crawl-worker/sources/stats-compute.js` parses without
  syntax error (the `*/10` JSDoc bug is gone) and `computeQueueStats`
  queries `Skill.certScore` + `certTier` (not `ScanResult.score` / `status`).
- [x] AC-US3-02: The VM payload includes `verifiedSkills`,
  `totalSkillsAll`, `pendingReceived`, `publishedStrict`, `rejectedStrict`
  so a write does not clobber the fields the read path expects.
- [x] AC-US3-03: The route handler at `/api/v1/internal/stats/queue` merges
  the VM body over prior KV: fields the VM does not send
  (`rejectionBreakdown`, prior `avgProcessingTimeMs`) survive the VM tick.
  Five new tests in route.test.ts cover the merge cases.
- [x] AC-US3-04: After deploy, `curl https://verified-skill.com/api/v1/submissions/stats | jq '.avgScore, .totalSkillsAll'`
  returns positive integers within one tick (≤10 min) and stays positive
  across at least two ticks.

## Notes

- `stats-compute` is currently NOT in any VM's `ASSIGNED_SOURCES` (vm1=github-events+submission-scanner; vm2=github-graphql-check+sourcegraph+submission-scanner+vendor-org-discovery+sast-scanner; vm3=github-sharded+skills-sh+submission-scanner). The VM script fix ensures the source is *ready* to be scheduled but is currently dormant — the live fix is doing its work via the CF Worker code path. Enabling the VM source on a specific node is a separate operational decision (would offload the avg query off the Worker hot path) and out of scope for this hotfix.
- `submissionAvgScore` on the platform stats blob still reads 0 — that value comes from `computePlatformStats` in the same VM script (still uses `ScanResult.score`). It's a separate field on the home page and a separate field path from queue avgScore. Filing as out of scope; can be picked up in a follow-up if the home page surfaces it visibly.

## Out of scope

- Reconciling Skill-vs-Submission count divergence in labels. Different entities, real divergence (legacy imports). Flagged for product in `reports/findings.md`.
- Changing `QueueStats.avgScore` to nullable across all consumers — kept as `number` for cache compat. Empty-Skill-table edge case stays at `0` (acceptable, no live skills means no average).
- Adding an index on `ScanResult.score`. Out of scope; we no longer need it after switching the query source.
