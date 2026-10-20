# 0953 verified-skill.com hub pages and submissions API return 500

## Problem
Found during 0941 (October 19, 2026). Every request to `/claude-code-skills` and its 15 category hubs (all in the sitemap) returned HTTP 500 after 15s: the Worker log shows `DB query timed out after 15000ms [Skill.count]`. The hubs run live `Skill.count` and `groupBy(category)` over ~2M rows; `/skills` already moved those to the cron-computed facet snapshot in KV.

Every uncached `GET /api/v1/submissions` returned 500 after 30s: the deduplicating `DISTINCT ON ("repoUrl","skillName")` CTE sorts all 2.2M submissions and hits Postgres' statement timeout (57014), then the fallback calls `submission.count({ distinct })`, an argument Prisma's count does not accept. `(repoUrl, skillName)` is already unique (`Submission_repoUrl_skillName_key`), so the CTE removes nothing.

## Scope
In: hub page counts, the submission list query, one index for the hubs' category sort. Out: other slow queries.

## Acceptance Criteria
- [ ] AC-01: `/claude-code-skills` and every category hub render 200 in production with counts from the facet snapshot, never a live `Skill.count` or `groupBy`.
- [ ] AC-02: `GET /api/v1/submissions` (uncached, e.g. `?limit=2`) returns 200 with submissions and a total; the list never runs the full-table `DISTINCT ON` query and counts with a plain `where`.
- [ ] AC-04: Every `/claude-code-skills/<category>` hub in the sitemap answers in under 5s (it was 11-12s for productivity, against a 15s timeout), served by a `(category, trustScore DESC)` index.
- [ ] AC-03: Unit tests fail on the old code for both: hubs calling live counts, and the list calling `$queryRaw` or `count({ distinct })`.

## Approach
Hubs: replace `getSkillCategories()` and `getSkillCount()` with `loadCatalogCounts()` from `src/lib/skills-facets.ts`, as `/skills` does. Submissions: delete the raw `DISTINCT ON` path from `src/lib/queue/fetch-submission-list.ts` and count with `count({ where })`; the unique index guarantees one row per (repoUrl, skillName), and `dedupeSubmissions` still guards a page. Release with `npm run release`.

## Decisions
### Defaulted (change any before sw-do)
- D-01 Drop the DISTINCT ON query instead of indexing it: the unique index makes it a no-op, and any ordering other than (repoUrl, skillName) still needs a full sort (reversible).
- D-02 If the facet snapshot is missing, the hubs fall back to live counts, the same behaviour as `/skills` (reversible).
### Open
- If the legacy unique index is ever dropped (0861 phase B cutover), the plain count can overcount duplicates; revisit then.

## Tasks

### T-01 Hub counts from the facet snapshot and plain submission count
- AC: AC-01, AC-02, AC-03 | Files: vskill-platform/src/app/claude-code-skills/page.tsx, vskill-platform/src/app/claude-code-skills/[category]/page.tsx, vskill-platform/src/app/claude-code-skills/__tests__/hub-counts.test.tsx, vskill-platform/src/lib/queue/fetch-submission-list.ts, vskill-platform/src/lib/queue/__tests__/fetch-submission-list.test.ts | Test: cd repositories/anton-abyzov/vskill-platform && npx vitest run src/app/claude-code-skills src/lib/queue/__tests__/fetch-submission-list.test.ts

### T-02 Release and verify live
- AC: AC-01, AC-02 | Files: none (release) | Test: bash .specweave/increments/0953-verified-skillcom-hub-pages-and-submissions-api-return-500/reports/live-verify.sh

### T-03 Category trust-score index
- AC: AC-04 | Files: vskill-platform/prisma/schema.prisma, vskill-platform/prisma/migrations/20261020000000_skill_category_trust_index/migration.sql | Test: bash .specweave/increments/0953-verified-skillcom-hub-pages-and-submissions-api-return-500/reports/live-verify.sh

Verify and close 0953.
