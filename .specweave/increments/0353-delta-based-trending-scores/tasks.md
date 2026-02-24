# Tasks — 0353 Delta-Based Trending Scores

### T-001: Migration — add MetricsSnapshot model
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [ ] pending
**Test**: Given migration runs → When schema inspected → Then MetricsSnapshot table with index
- `prisma/schema.prisma` — new model: id, skillId, stars, forks, downloads, installs, capturedAt
- Index on (skillId, capturedAt DESC)

### T-002: Insert snapshots in enrichment batch
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [ ] pending
**Test**: Given enrichment updates skill → When metrics fetched → Then snapshot row created
- `src/lib/cron/enrichment.ts` — after metric update (in transaction), create snapshot

### T-003: Implement delta trending formula
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03, AC-US2-04, AC-US2-05 | **Status**: [ ] pending
**Test**: Given skill with 100 stars now, 80 seven days ago → When computed → Then score reflects +20
- New: `src/lib/cron/trending-score.ts` — `computeTrendingScore(current, historical)`
- Weights: stars x2.0, downloads x0.001, installs x1.0, recency bonus 0/5/10
- Clamp 0-100

### T-004: Replace enrichment formula with delta-based
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [ ] pending
**Test**: Given enrichment runs → When scores computed → Then use delta formula with snapshots
- `src/lib/cron/enrichment.ts:58-68` — query 7d/30d snapshots, compute deltas, update scores

### T-005: Add snapshot pruning
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [ ] pending
**Test**: Given snapshots older than 90d → When pruning runs → Then deleted
- `src/lib/cron/enrichment.ts` — prune at end of batch, configurable retention

### T-006: Update TrendingSkills UI
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [ ] pending
**Test**: Given trending data → When rendered → Then spark bar shows trendingScore7d
- `src/app/components/home/TrendingSkills.tsx:91-95` — use trendingScore7d, not githubStars

### T-007: Update skill detail trending display
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03 | **Status**: [ ] pending
**Test**: Given skill detail → When rendered → Then shows "7d Trend" label
- `src/app/skills/[name]/page.tsx:243` — rename "Trending" to "7d Trend"

### T-008: Handle non-GitHub skills gracefully
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02 | **Status**: [ ] pending
**Test**: Given GitLab skill → When trending computed → Then star delta = 0, no penalty
- `src/lib/cron/trending-score.ts` — 0 - 0 = 0, not negative
