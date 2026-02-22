---
increment: 0325-homepage-metrics-accuracy
title: "Architecture: Homepage Metrics Accuracy"
---

# Architecture Plan

## Overview

This plan organizes changes across three layers: **data utilities** (pure functions), **data layer** (data.ts / seed-data.ts), and **UI** (page.tsx). The approach is bottom-up: build and test pure utility functions first, then update the data layer, then update the homepage.

## Architecture Decisions

### AD-001: Pure Utility Functions for Metric Computation

All new metric logic lives in a single new file: `src/lib/metric-utils.ts`. This file contains pure functions with no side effects, making them trivially testable:

- `getUniqueRepoStats(skills)` -- groups by repoUrl, counts unique repos
- `getDeduplicatedStars(skills)` -- groups by repoUrl, takes max stars per repo
- `getFilteredNpmDownloads(skills)` -- sums only where npmPackage is truthy
- `categorizeSkill(name, description, labels)` -- keyword-based category assignment

**Rationale**: Separating metric computation from the data layer keeps `data.ts` focused on data access and makes the metric logic reusable (homepage, stats API, future dashboards).

### AD-002: Repo URL Normalization

Reuse `parseGitHubUrl()` from `popularity-fetcher.ts` for consistent URL normalization. Normalize to `owner/repo` string key for deduplication. For non-GitHub URLs, fall back to the raw URL as the key.

**Rationale**: The parser already handles edge cases (www prefix, .git suffix, trailing slashes). Using a consistent normalization key prevents repos from being double-counted due to URL variations.

### AD-003: Trust Score Defaults for Seed Data

Add `trustScore` and `trustTier` directly to seed data entries. Compute them offline using the trust score engine with conservative defaults:
- `tier1Verdict: "PASS"` (all seed skills passed scanning)
- `tier2Score`: use `certScore` value if available, else null
- `provenanceStatus: "unchecked"` for community, `"verified"` for vendor (Anthropic, OpenAI, Google)
- Other defaults: `isBlocked: false`, `unresolvedReportCount: 0`, `hasBlocklistHistory: false`

**Rationale**: Computing at build-time avoids runtime overhead. The trust score engine is deterministic, so we can compute once and embed in seed data.

### AD-004: Keyword-Based Categorization (No LLM)

Use a static keyword map for auto-categorization. Keywords are matched against `name`, `description`, and `labels` fields. First match wins; default is "development".

**Rationale**: Keyword matching is deterministic, fast, testable, and requires no API calls. Good enough for the current scale (~200 skills). LLM-based categorization can be a future enhancement.

### AD-005: Seed Data Cleanup Strategy

Clean up seed data in a single commit:
1. Set `npmDownloads: 0` for skills without `npmPackage`
2. Add `trustScore` and `trustTier` fields
3. Re-categorize skills using the new categorizer (review diff manually)

**Rationale**: Doing all seed data changes together makes the diff reviewable and ensures consistency.

## File Change Map

### New Files
| File | Purpose |
|------|---------|
| `src/lib/metric-utils.ts` | Pure functions: repo stats, stars dedup, npm filter, categorizer |
| `src/lib/__tests__/metric-utils.test.ts` | Tests for all metric utility functions |

### Modified Files
| File | Changes |
|------|---------|
| `src/lib/types.ts` | Expand `SkillCategory` union with new categories |
| `src/lib/seed-data.ts` | Clean up npmDownloads, add trustScore/trustTier, re-categorize |
| `src/app/page.tsx` | Use new metric functions, replace metric cards |
| `src/app/api/v1/admin/rebuild-index/route.ts` | Use `categorizeSkill()` instead of hardcoded "development" |
| `src/lib/submission-store.ts` | Use `categorizeSkill()` in publish flow (if category assignment happens there) |

### Unchanged Files
| File | Why Unchanged |
|------|---------------|
| `prisma/schema.prisma` | `category` is already a string field, no migration needed |
| `src/lib/trust/trust-score.ts` | Used as-is for computing seed data trust scores |
| `src/lib/popularity-fetcher.ts` | Reused as-is; `parseGitHubUrl()` exported for normalization |
| `src/lib/data.ts` | Data access unchanged; metric computation moves to `metric-utils.ts` |

## Dependency Graph

```
metric-utils.ts (new, pure)
    ├── uses parseGitHubUrl from popularity-fetcher.ts
    └── uses SkillCategory from types.ts

types.ts (modified)
    └── adds new SkillCategory values

seed-data.ts (modified)
    ├── uses metric-utils.ts categorizeSkill (during development, not runtime)
    └── adds trustScore/trustTier computed from trust-score.ts

page.tsx (modified)
    ├── imports from metric-utils.ts
    └── uses SkillData (unchanged interface, new optional fields populated)

rebuild-index/route.ts (modified)
    └── imports categorizeSkill from metric-utils.ts
```

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Metric totals drop dramatically (stars, npm) | Certain | Medium | Document the change clearly; the new values are more honest |
| Keyword categorizer misclassifies some skills | Medium | Low | Default to "development" on no match; review seed data diff manually |
| Trust score defaults differ from real computed values | Low | Low | Use same engine with conservative inputs; scores will update when real data flows in |
| Breaking change to /api/v1/stats | Low | Low | stats API currently doesn't expose install counts; check before deploying |

## Implementation Order

1. **Types** -- expand SkillCategory (AC-US5-01)
2. **metric-utils.ts** -- all pure functions + tests (AC-US1-07, AC-US3-01, AC-US5-03)
3. **Seed data cleanup** -- npmDownloads, trustScore, categories (AC-US2-03, AC-US5-06)
4. **Homepage UI** -- wire new functions (AC-US1-01 through AC-US1-06, AC-US2-01, AC-US3-02 through AC-US3-05, AC-US4-01 through AC-US4-04)
5. **Pipeline integration** -- rebuild-index + submission-store (AC-US5-04, AC-US5-05)
6. **Final verification** -- all tests pass, visual check
