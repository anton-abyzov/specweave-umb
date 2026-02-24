# 0353 — Delta-Based Trending Scores

## Problem

The current trending formula (`githubStars * 0.01 + npmDownloads * 0.0001 + vskillInstalls * 0.5`) uses absolute cumulative values, making it a popularity score, not a trending score. A stagnant repo with 10k stars always outranks a viral repo with 100 stars gained this week. No historical snapshots exist to compute deltas. The 7d and 30d scores differ by only 25% in weights (meaningless). The UI shows raw GitHub stars in the "Trending" section, and non-GitHub skills are permanently penalized.

## User Stories

### US-001: Store historical metric snapshots

As a platform operator, I want periodic snapshots of skill metrics so delta-based trending can be computed.

**Acceptance Criteria:**
- [ ] AC-US1-01: `MetricsSnapshot` model exists with id, skillId, githubStars, githubForks, npmDownloads, vskillInstalls, capturedAt
- [ ] AC-US1-02: Index on (skillId, capturedAt DESC) for fast delta queries
- [ ] AC-US1-03: Enrichment batch inserts snapshot row for each updated skill
- [ ] AC-US1-04: Snapshots older than 90 days are pruned (configurable)

### US-002: Compute delta-based trending scores

As a user, I want trending to reflect actual momentum — skills gaining popularity fastest, not just the most popular.

**Acceptance Criteria:**
- [ ] AC-US2-01: 7d score = weighted sum of deltas: (current - 7d_ago) for stars, downloads, installs
- [ ] AC-US2-02: 30d score uses 30-day-old snapshot for comparison
- [ ] AC-US2-03: Missing snapshot → score 0 (new skill, no momentum data yet)
- [ ] AC-US2-04: Negative deltas contribute 0 (score cannot go below 0)
- [ ] AC-US2-05: Scores clamped to 0-100

### US-003: Update trending UI

As a user, I want the trending display to show trending scores and meaningful momentum, not raw star counts.

**Acceptance Criteria:**
- [ ] AC-US3-01: TrendingSkills spark bar shows trendingScore7d, not githubStars
- [ ] AC-US3-02: MomentumArrow shows real acceleration (7d vs 30d delta scores)
- [ ] AC-US3-03: Skill detail shows "7d Trend" label instead of "Trending"

### US-004: Fair treatment for non-GitHub skills

As a skill author hosting on GitLab, I want my skill to be fairly ranked by available metrics.

**Acceptance Criteria:**
- [ ] AC-US4-01: Missing GitHub data = 0 delta contribution, not penalty
- [ ] AC-US4-02: npm downloads and vskill installs still contribute normally

## Out of Scope

- Certification tier fixes (handled in 0352)
- Data freshness/reliability fixes (handled in 0354)
- Trust score formula changes

## Dependencies

- **Depends on 0354**: Snapshot insertion needs 0354's refactored enrichment (transaction wrapping, metrics-can-decrease fix)
- Delta-based trending requires reliable, decrementable metrics from 0354

## Risks

- **Cold start**: New skills score 0 until 7+ days of snapshots accumulate. Acceptable — honest and simple.
- **Table growth**: ~100 skills x 24 snapshots/day x 90 days = ~216k rows. Manageable with compound index.
- **Formula tuning**: Initial weights (stars x2.0, downloads x0.001, installs x1.0) need empirical adjustment.
