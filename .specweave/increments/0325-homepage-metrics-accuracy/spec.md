---
increment: 0325-homepage-metrics-accuracy
title: >-
  Fix homepage metrics accuracy: unique repos, real npm, stars dedup, trust
  score, categories
type: feature
priority: P1
status: completed
created: 2026-02-22T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 80
---

# Feature: Homepage Metrics Accuracy

## Overview

The vskill-platform homepage dashboard displays five metrics that are currently inaccurate or misleading:

1. **"vskill Installs"** -- fabricated numbers (no real install tracking exists). Replace with "Unique Repos" to show how many distinct GitHub repositories contain skills.
2. **"NPM Downloads"** -- 89 of 118 seed skills have non-zero `npmDownloads` but only 6 have a real `npmPackage` set. The total is inflated by ~15x. Only skills with a valid `npmPackage` field should contribute to the NPM downloads metric.
3. **"GitHub Stars"** -- 118 skills share only 29 unique repos (e.g., 32 skills from `openai/skills`, 16 from `anthropics/skills`). Stars are counted per-skill, causing massive duplication. Deduplicate by repo URL so each repo's stars are counted once.
4. **"Avg Quality Score"** -- labeled "Avg Quality Score" and uses `certScore` (0-100 scan tier score). Replace with the existing `trustScore` (0-100 composite trust score) which factors in scan results, provenance, community signals, and blocklist status -- a more meaningful quality indicator.
5. **Categories** -- only 8 categories exist, all community/discovered skills default to "development". Add new categories and implement keyword-based auto-categorization during the publish pipeline.

### Current State (measured from seed-data.ts)

| Metric | Current Value | Problem |
|--------|--------------|---------|
| GitHub Stars | ~380k (sum across 118 skills) | 29 unique repos, stars counted 118 times |
| vskill Installs | ~200k | Fabricated -- no install tracking exists |
| NPM Downloads | ~1.5M (89 skills with values) | Only 6 skills have real npm packages |
| Avg Quality Score | ~85 (certScore average) | Uses scan score, not composite trust |
| Categories | 8 | All discovered skills get "development" |

## User Stories

### US-001: Replace vskill Installs with Unique Repos Metric (P1)
**Project**: vskill-platform

**As a** visitor viewing the homepage dashboard
**I want** the "vskill Installs" metric card to show "Unique Repos" instead
**So that** I see an honest, verifiable metric showing the breadth of the skill ecosystem

**Acceptance Criteria**:
- [x] **AC-US1-01**: The second metric card title changes from "vskill Installs" to "Unique Repos"
- [x] **AC-US1-02**: The value shows the count of distinct `repoUrl` values across all skills (deduped)
- [x] **AC-US1-03**: The subtitle changes from "platform installs" to "GitHub repositories"
- [x] **AC-US1-04**: The MiniBarChart shows top repos by skill count (most skills per repo) instead of top by installs
- [x] **AC-US1-05**: The hero inline stat changes from `{fmt(totalInstalls)} installs` to `{uniqueRepos} repos`
- [x] **AC-US1-06**: Trending row "inst" column changes to show the repo's total skill count or is removed
- [x] **AC-US1-07**: A helper function `getUniqueRepoCount(skills)` is added to the data layer with tests

---

### US-002: NPM Downloads Only for Real Packages (P1)
**Project**: vskill-platform

**As a** visitor viewing the NPM Downloads metric
**I want** only skills with a valid `npmPackage` field to contribute to the total
**So that** the download count reflects real npm registry data, not fabricated numbers

**Acceptance Criteria**:
- [x] **AC-US2-01**: `totalNpm` on the homepage is computed as `allSkills.filter(s => s.npmPackage).reduce(...)` -- only skills with `npmPackage` set contribute
- [x] **AC-US2-02**: The MiniBarChart for NPM Downloads only shows skills that have a `npmPackage` field
- [x] **AC-US2-03**: Seed data skills without `npmPackage` have their `npmDownloads` set to `0` (data cleanup)
- [x] **AC-US2-04**: The subtitle shows "from N packages" (where N = count of skills with `npmPackage`)
- [x] **AC-US2-05**: The `enrichSkillWithMetrics()` function skips npm fetching when `npmPackage` is absent (already the case -- verify with test)

---

### US-003: GitHub Stars Deduplication by Repo URL (P1)
**Project**: vskill-platform

**As a** visitor viewing the GitHub Stars metric
**I want** stars to be counted once per unique repository, not once per skill
**So that** the total reflects actual GitHub star counts without inflation

**Acceptance Criteria**:
- [x] **AC-US3-01**: A helper function `getDeduplicatedStars(skills)` returns `{ totalStars, repoCount, topRepos }` by grouping skills by `repoUrl` and taking the max stars per repo
- [x] **AC-US3-02**: The homepage "GitHub Stars" metric card uses the deduplicated total
- [x] **AC-US3-03**: The MiniBarChart shows top repos (not skills) by star count, with the repo display name as `owner/repo`
- [x] **AC-US3-04**: The hero inline stat `{fmt(totalStars)} stars` uses the deduplicated value
- [x] **AC-US3-05**: The MetricCard subtitle shows "across N repos" (not "across N skills")
- [x] **AC-US3-06**: The deduplication uses the max `githubStars` value among all skills sharing a `repoUrl` (since the repo's star count should be the same for all skills in it)

---

### US-004: Trust Score Instead of certScore on Dashboard (P2)
**Project**: vskill-platform

**As a** visitor viewing the quality score metric
**I want** the dashboard to show the composite trust score instead of the raw scan score
**So that** I see a more meaningful quality indicator that factors in provenance, community signals, and security history

**Acceptance Criteria**:
- [x] **AC-US4-01**: The fourth metric card title changes from "Avg Quality Score" to "Avg Trust Score"
- [x] **AC-US4-02**: The value is computed from `trustScore` (or computed via `computeTrustScore()` for seed data) instead of `certScore`
- [x] **AC-US4-03**: The ScoreRing component renders the trust score average
- [x] **AC-US4-04**: The subtitle still shows certified/verified counts
- [x] **AC-US4-05**: For seed-data skills that lack `trustScore`, compute it using `computeTrustScore()` with reasonable defaults (tier1=PASS, provenance=unchecked, etc.)

---

### US-005: Expand Categories with Auto-Categorization (P2)
**Project**: vskill-platform

**As a** platform maintainer
**I want** more skill categories and automatic categorization based on skill content
**So that** discovered skills get meaningful categories instead of all defaulting to "development"

**Acceptance Criteria**:
- [x] **AC-US5-01**: The `SkillCategory` type is expanded with new categories: `"ai-ml"`, `"infrastructure"`, `"productivity"`, `"communication"`, `"finance"`, `"education"`, `"analytics"`
- [x] **AC-US5-02**: `CATEGORY_LABELS` on the homepage maps all new categories to display labels
- [x] **AC-US5-03**: A `categorizeSkill(name: string, description: string, labels: string[]): SkillCategory` function is created that assigns categories based on keyword matching
- [x] **AC-US5-04**: The rebuild-index route (`/api/v1/admin/rebuild-index`) uses `categorizeSkill()` instead of hardcoding `"development"`
- [x] **AC-US5-05**: The publish pipeline in `submission-store.ts` uses `categorizeSkill()` when creating new skills
- [x] **AC-US5-06**: Existing seed data skills are re-reviewed: any miscategorized skills are corrected
- [x] **AC-US5-07**: The keyword mapping is tested with at least 10 representative skill names/descriptions

---

### US-006: Update Seed Data with Real GitHub/NPM Metrics (P1)
**Project**: vskill-platform

**As a** visitor viewing individual skill pages
**I want** to see real GitHub stars, forks, npm downloads, and version numbers
**So that** per-skill metrics reflect verifiable reality instead of fabricated values

**Acceptance Criteria**:
- [x] **AC-US6-01**: All skills sharing a `repoUrl` show the same `githubStars` and `githubForks` values (the real repo values)
- [x] **AC-US6-02**: `specweave` skill shows `githubStars: 69`, `githubForks: 7`, `npmDownloads: 20002`, `currentVersion: "1.0.313"`
- [x] **AC-US6-03**: `anthropics/skills` group (16 skills) shows `githubStars: 73059`, `githubForks: 7481`
- [x] **AC-US6-04**: `openai/skills` group (32 skills) shows `githubStars: 9280`, `githubForks: 518`
- [x] **AC-US6-05**: `google-gemini/gemini-cli` group shows `githubStars: 95246`, `githubForks: 11474`
- [x] **AC-US6-06**: `google-gemini/gemini-skills` group shows `githubStars: 1766`, `githubForks: 115`
- [x] **AC-US6-07**: `google-labs-code/stitch-skills` group shows `githubStars: 1873`, `githubForks: 213`
- [x] **AC-US6-08**: `google-labs-code/jules-skills` group shows `githubStars: 7`, `githubForks: 1`
- [x] **AC-US6-09**: `firebase/agent-skills` group shows `githubStars: 123`, `githubForks: 2`
- [x] **AC-US6-10**: `coreyhaines31/marketingskills` group shows `githubStars: 8701`, `githubForks: 1135`
- [x] **AC-US6-11**: Community skills from fictional repos (e.g., `devops-community/skill-*`) have `githubStars: 0`, `githubForks: 0`
- [x] **AC-US6-12**: All `vskillInstalls` values in seed data are set to `0`
- [x] **AC-US6-13**: NPM downloads for the 6 real packages use actual npm registry values

---

### US-007: Remove Fabricated vskillInstalls from Skill Detail Pages (P1)
**Project**: vskill-platform

**As a** visitor viewing a skill detail page or the verified skills table
**I want** to no longer see fabricated install counts
**So that** per-skill metrics are trustworthy and consistent with the homepage (which already shows "Unique Repos")

**Acceptance Criteria**:
- [x] **AC-US7-01**: The skill detail page (`/skills/[name]/page.tsx`) Popularity section no longer shows the "Installs" StatCard
- [x] **AC-US7-02**: The VerifiedSkillsTab table replaces the "Installs" column with "Trust" column showing `trustScore`
- [x] **AC-US7-03**: The VerifiedSkillsTab sort option "Installs" is replaced with "Trust" (sorting by `trustScore`)

## Functional Requirements

### FR-001: Unique Repos Computation
Create a `getUniqueRepoStats(skills: SkillData[])` function that:
- Groups skills by normalized `repoUrl` (trim trailing slashes, lowercase)
- Returns `{ uniqueCount: number, topRepos: Array<{ url: string, displayName: string, skillCount: number }> }`
- Used by the homepage for the "Unique Repos" metric card

### FR-002: Stars Deduplication
Create a `getDeduplicatedStars(skills: SkillData[])` function that:
- Groups skills by normalized `repoUrl`
- For each repo group, takes `Math.max(...group.map(s => s.githubStars))` as the repo's star count
- Returns `{ totalStars: number, repoCount: number, topRepos: Array<{ url: string, displayName: string, stars: number }> }`

### FR-003: NPM Downloads Filtering
Modify `totalNpm` computation to only sum `npmDownloads` where `npmPackage` is truthy. Clean up seed data to set `npmDownloads: 0` for skills without `npmPackage`.

### FR-004: Trust Score Integration
Seed data skills currently have `certScore` but most lack `trustScore`. Two options:
- **Option A (preferred)**: Add `trustScore` to seed data with computed values
- **Option B**: Compute trust scores at runtime using `computeTrustScore()` with defaults

### FR-005: Auto-Categorization Engine
Create a keyword-based categorizer: `categorizeSkill(name, description, labels) -> SkillCategory`
- Match against a keyword map (e.g., "docker" -> "devops", "test" -> "testing", "security" -> "security")
- Default to "development" if no keywords match (preserves current behavior for truly generic skills)
- Applied during publish (submission-store) and rebuild-index

## Technical Notes

### Seed Data Changes
- Set `npmDownloads: 0` for 83 skills that lack `npmPackage`
- Add `trustScore` and `trustTier` fields to seed data entries (or compute at runtime)
- Review and correct any miscategorized skills after expanding the category list

### Migration Path
- Prisma schema already has `trustTier` and `trustScore` on the Skill model -- no migration needed
- New categories are string enum values -- add to the `SkillCategory` TypeScript type only (Prisma column is `String`)
- No database migration required (category is a string field, not a Prisma enum)

### Breaking Changes
- The homepage "vskill Installs" metric disappears; downstream API consumers relying on `/api/v1/stats` returning `totalInstalls` should be checked
- NPM download totals will drop significantly (from ~1.5M to real values from ~6 packages)
- GitHub star totals will drop (from ~380k duplicated to ~60k deduplicated)

## Success Criteria

- All homepage metrics reflect real, verifiable data
- GitHub stars are deduplicated -- no repo counted more than once
- NPM downloads only count packages that exist on npm
- "Unique Repos" replaces the fabricated "vskill Installs" metric
- Trust score provides a richer quality indicator than raw scan score
- New categories reduce the "development" bucket from 31 to under 20
- All changes have >80% test coverage

## Out of Scope

- Implementing actual vskill install tracking (separate future increment)
- Changing the trust score computation algorithm itself
- Redesigning the dashboard layout or adding new metric cards
- Real-time npm/GitHub API calls on the homepage (live metrics are behind `ENABLE_LIVE_METRICS` flag)
- Database migration for Prisma enum changes (category is already a string)

## Dependencies

- Trust score engine exists at `src/lib/trust/trust-score.ts` (computeTrustScore, deriveTrustTier)
- Repository model exists in Prisma schema with owner/name unique constraint
- `parseGitHubUrl()` exists in `src/lib/popularity-fetcher.ts` for URL normalization
- Seed data at `src/lib/seed-data.ts` (118 skills, 29 unique repos)
