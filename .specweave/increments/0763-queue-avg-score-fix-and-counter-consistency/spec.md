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

## Out of scope

- Reconciling Skill-vs-Submission count divergence in labels. Different entities, real divergence (legacy imports). Flagged for product in `reports/findings.md`.
- Changing `QueueStats.avgScore` to nullable across all consumers — kept as `number` for cache compat. Empty-Skill-table edge case stays at `0` (acceptable, no live skills means no average).
- Adding an index on `ScanResult.score`. Out of scope; we no longer need it after switching the query source.
