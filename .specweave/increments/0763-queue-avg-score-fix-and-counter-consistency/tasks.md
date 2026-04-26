# 0763 — Tasks

## T-001: Switch queue avg_score query to Skill.certScore
**User Story**: US-001 | **AC**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [x] completed
**Test Plan**: Given a `Skill` table with mixed certScore values (NULL, 0, positive), when the cron's Phase 1b query runs, then it returns the rounded average of positive certScore values, in <2s, never `0` if at least one positive value exists.

## T-002: Add `verifiedCount` prop + `formatSearchPlaceholder` to HeroSearch
**User Story**: US-002 | **AC**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Test Plan**: Given verifiedCount=115343, formatSearchPlaceholder returns `"Search 115,000+ verified skills..."`. Given verifiedCount=undefined or 0, returns `"Search verified skills..."`. Given verifiedCount=42, returns `"Search 42+ verified skills..."`.

## T-003: Wire `stats.verifiedCount` from page.tsx into `<HeroSearch>`
**User Story**: US-002 | **AC**: AC-US2-01 | **Status**: [x] completed
**Test Plan**: Given the home page renders with `getHomeStats()` returning `{verifiedCount: 115343, ...}`, when `<HeroSearch>` is rendered as a child, then the `<input>` `placeholder` attribute reads `Search 115,000+ verified skills...`.

## T-004: Add HeroSearch unit tests for the three placeholder branches
**User Story**: US-002 | **AC**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Test Plan**: Vitest + RTL render with each `verifiedCount` value, assert `screen.getByPlaceholderText` matches expected string.

## T-005: Document Skill-vs-Submission counter divergence
**User Story**: US-001 | **AC**: AC-US1-04 | **Status**: [x] completed
**Test Plan**: Deliverable is a markdown report at `reports/findings.md` listing every numeric counter on home + queue + their data sources, plus the recommendation about labels. No automated test (documentation artifact).
