---
increment: 0325-homepage-metrics-accuracy
title: "Tasks: Homepage Metrics Accuracy"
---

# Tasks

## Phase 1: Types & Pure Utility Functions

### T-001: Expand SkillCategory Type
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01 | **Status**: [x] completed
**Test**: Given the SkillCategory type -> When a skill uses "ai-ml" category -> Then TypeScript compiles without error

**Steps**:
1. Edit `src/lib/types.ts` to add new categories to the `SkillCategory` union: `"ai-ml"`, `"infrastructure"`, `"productivity"`, `"communication"`, `"finance"`, `"education"`, `"analytics"`
2. Verify no TypeScript errors in the build

**Files**: `src/lib/types.ts`

---

### T-002: Create getUniqueRepoStats() Utility
**User Story**: US-001 | **Satisfies ACs**: AC-US1-07 | **Status**: [x] completed
**Test**: Given 5 skills from 3 unique repos -> When getUniqueRepoStats() is called -> Then uniqueCount=3, topRepos has 3 entries sorted by skillCount desc

**Steps**:
1. RED: Write tests in `src/lib/__tests__/metric-utils.test.ts` for `getUniqueRepoStats()`:
   - 5 skills from 3 repos -> uniqueCount=3
   - Skills with same repo URL (different casing/trailing slash) -> correctly deduped
   - Empty array -> uniqueCount=0
   - topRepos sorted by skillCount descending
2. GREEN: Implement `getUniqueRepoStats(skills: SkillData[])` in `src/lib/metric-utils.ts`
   - Normalize repo URLs using `parseGitHubUrl()` for GitHub repos, raw URL for others
   - Group by normalized key, count skills per group
   - Return `{ uniqueCount, topRepos: Array<{ url, displayName, skillCount }> }`
3. REFACTOR: Extract URL normalization into a `normalizeRepoUrl()` helper

**Files**: `src/lib/metric-utils.ts`, `src/lib/__tests__/metric-utils.test.ts`

---

### T-003: Create getDeduplicatedStars() Utility
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-06 | **Status**: [x] completed
**Test**: Given 3 skills from repo A (stars: 100, 100, 100) and 2 skills from repo B (stars: 50, 50) -> When getDeduplicatedStars() is called -> Then totalStars=150, repoCount=2

**Steps**:
1. RED: Write tests for `getDeduplicatedStars()`:
   - Multiple skills same repo -> max stars taken once
   - Different repos -> stars summed correctly
   - Zero-star repos included in count but not in topRepos
   - topRepos sorted by stars descending
2. GREEN: Implement `getDeduplicatedStars(skills: SkillData[])` in `src/lib/metric-utils.ts`
   - Group by normalized repoUrl
   - Take `Math.max(...group.githubStars)` per repo
   - Return `{ totalStars, repoCount, topRepos: Array<{ url, displayName, stars }> }`
3. REFACTOR: Share normalization with `getUniqueRepoStats()`

**Files**: `src/lib/metric-utils.ts`, `src/lib/__tests__/metric-utils.test.ts`

---

### T-004: Create getFilteredNpmDownloads() Utility
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed
**Test**: Given 3 skills (1 with npmPackage="foo" and downloads=1000, 2 without npmPackage but downloads=500) -> When getFilteredNpmDownloads() is called -> Then total=1000, packages=[{name:"foo", downloads:1000}]

**Steps**:
1. RED: Write tests for `getFilteredNpmDownloads()`:
   - Only skills with npmPackage contribute
   - Skills with npmPackage but 0 downloads included in count
   - Return includes packageCount and topPackages
2. GREEN: Implement `getFilteredNpmDownloads(skills: SkillData[])` in `src/lib/metric-utils.ts`
   - Filter to skills where `npmPackage` is truthy
   - Sum `npmDownloads` from filtered set only
   - Return `{ totalDownloads, packageCount, topPackages: Array<{ name, displayName, downloads }> }`
3. REFACTOR: Clean up return type naming

**Files**: `src/lib/metric-utils.ts`, `src/lib/__tests__/metric-utils.test.ts`

---

### T-005: Create categorizeSkill() Function
**User Story**: US-005 | **Satisfies ACs**: AC-US5-03, AC-US5-07 | **Status**: [x] completed
**Test**: Given name="docker-compose-gen" description="Generates Docker Compose files" -> When categorizeSkill() is called -> Then returns "devops"

**Steps**:
1. RED: Write tests for `categorizeSkill()` with at least 10 representative cases:
   - "docker-compose-gen" + Docker description -> "devops"
   - "playwright-tests" + testing description -> "testing"
   - "secrets-detector" + security description -> "security"
   - "langchain-tools" + AI/ML description -> "ai-ml"
   - "tailwind-themes" + design description -> "design"
   - "storybook-gen" + documentation description -> "documentation" (or "design")
   - "eslint-config" + linting description -> "development"
   - "k8s-manifests" + Kubernetes description -> "infrastructure"
   - "marketing-analytics" + marketing description -> "marketing"
   - Unknown/generic skill -> "development" (default)
2. GREEN: Implement `categorizeSkill(name: string, description: string, labels: string[])` in `src/lib/metric-utils.ts`
   - Define keyword map: `Record<SkillCategory, string[]>` with keywords for each category
   - Score each category by keyword hit count
   - Return highest-scoring category, default to "development"
3. REFACTOR: Ensure keyword lists are comprehensive but not overlapping

**Files**: `src/lib/metric-utils.ts`, `src/lib/__tests__/metric-utils.test.ts`

---

## Phase 2: Seed Data Cleanup

### T-006: Clean npmDownloads in Seed Data
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03 | **Status**: [x] completed
**Test**: Given seed-data.ts -> When grep for skills with npmDownloads > 0 but no npmPackage -> Then count = 0

**Steps**:
1. Identify all seed data skills with `npmDownloads > 0` but no `npmPackage` field
2. Set their `npmDownloads: 0`
3. Verify only 6 skills retain non-zero npmDownloads (those with npmPackage)

**Files**: `src/lib/seed-data.ts`

---

### T-007: Add trustScore and trustTier to Seed Data
**User Story**: US-004 | **Satisfies ACs**: AC-US4-05 | **Status**: [x] completed
**Test**: Given seed-data.ts -> When all skills are checked -> Then every skill has trustScore (number) and trustTier (string)

**Steps**:
1. Create a one-time script or compute manually: for each seed skill, call `computeTrustScore()` with:
   - `isBlocked: false`
   - `tier1Verdict: "PASS"` (all seed skills are scanned)
   - `tier2Score: certScore` (if available)
   - `tier2Verdict: certScore >= 80 ? "PASS" : certScore >= 50 ? "CONCERNS" : null`
   - `provenanceStatus: "verified"` for Anthropic/OpenAI/Google vendors, `"unchecked"` for community
   - `skillAgeDays: 90` (conservative)
   - `installCount: 0` (since we're removing fabricated installs)
   - `unresolvedReportCount: 0`
   - `hasBlocklistHistory: false`
   - `humanReviewCompleted: false`
2. Add `trustScore` and `trustTier` to each skill object in seed-data.ts
3. Verify values are reasonable (vendor skills should score higher due to provenance)

**Files**: `src/lib/seed-data.ts`

---

### T-008: Re-categorize Seed Data Skills
**User Story**: US-005 | **Satisfies ACs**: AC-US5-06 | **Status**: [x] completed
**Test**: Given seed-data.ts after re-categorization -> When counting "development" category -> Then count < 25 (reduced from 31)

**Steps**:
1. Run `categorizeSkill()` against all 118 seed data skill names/descriptions
2. Compare with current categories; identify disagreements
3. Update categories where the auto-categorizer is more accurate
4. Manual review: ensure no obviously wrong re-categorizations
5. Update CATEGORY_LABELS in page.tsx to include new categories

**Files**: `src/lib/seed-data.ts`, `src/app/page.tsx`

---

## Phase 3: Homepage UI Updates

### T-009: Replace vskill Installs Metric Card with Unique Repos
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05 | **Status**: [x] completed
**Test**: Given the homepage renders -> When viewing the second metric card -> Then title="Unique Repos", value=unique repo count, chart shows top repos by skill count

**Steps**:
1. Import `getUniqueRepoStats` from `metric-utils.ts` in `page.tsx`
2. Call `getUniqueRepoStats(allSkills)` in the server component
3. Replace the "vskill Installs" MetricCard with "Unique Repos":
   - `title="Unique Repos"`
   - `value={uniqueRepos.uniqueCount}`
   - `subtitle="GitHub repositories"`
   - MiniBarChart: `items={uniqueRepos.topRepos.map(r => ({ label: r.displayName, value: r.skillCount, formattedValue: r.skillCount.toString() }))}`
4. Update hero inline stat: `{uniqueRepos.uniqueCount} repos`
5. Remove or update trending row "inst" column

**Files**: `src/app/page.tsx`

---

### T-010: Update NPM Downloads Metric Card
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-04 | **Status**: [x] completed
**Test**: Given the homepage renders -> When viewing NPM Downloads card -> Then total only includes skills with npmPackage, subtitle shows package count

**Steps**:
1. Import `getFilteredNpmDownloads` from `metric-utils.ts` in `page.tsx`
2. Replace `totalNpm` computation with `getFilteredNpmDownloads(allSkills)`
3. Update MetricCard:
   - `value={fmt(npmStats.totalDownloads)}`
   - `subtitle={`from ${npmStats.packageCount} packages`}`
   - MiniBarChart: use `npmStats.topPackages`
4. Remove old `topByNpm` computation

**Files**: `src/app/page.tsx`

---

### T-011: Update GitHub Stars Metric Card with Deduplication
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05 | **Status**: [x] completed
**Test**: Given the homepage renders -> When viewing GitHub Stars card -> Then total is deduplicated, chart shows repos not skills

**Steps**:
1. Import `getDeduplicatedStars` from `metric-utils.ts` in `page.tsx`
2. Replace `totalStars` computation with `getDeduplicatedStars(allSkills)`
3. Update MetricCard:
   - `value={fmt(starStats.totalStars)}`
   - `subtitle={`across ${starStats.repoCount} repos`}`
   - MiniBarChart: use `starStats.topRepos`
4. Update hero inline stat: `{fmt(starStats.totalStars)} stars`
5. Remove old `topByStars` computation

**Files**: `src/app/page.tsx`

---

### T-012: Replace certScore with trustScore on Dashboard
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04 | **Status**: [x] completed
**Test**: Given the homepage renders -> When viewing quality score card -> Then title="Avg Trust Score" and value is computed from trustScore

**Steps**:
1. Replace `avgCertScore` computation:
   - Filter skills that have `trustScore` defined and > 0
   - Compute average of `trustScore` values
2. Update MetricCard:
   - `title="Avg Trust Score"`
   - `value={Math.round(avgTrustScore).toString()}`
   - Keep subtitle with certified/verified counts
3. Update ScoreRing: `score={avgTrustScore}`

**Files**: `src/app/page.tsx`

---

### T-013: Update CATEGORY_LABELS for New Categories
**User Story**: US-005 | **Satisfies ACs**: AC-US5-02 | **Status**: [x] completed
**Test**: Given the homepage renders -> When categories include "ai-ml" -> Then the category pill shows "AI/ML"

**Steps**:
1. Add new entries to `CATEGORY_LABELS` in `page.tsx`:
   - `"ai-ml": "AI/ML"`
   - `"infrastructure": "Infra"`
   - `"productivity": "Productivity"`
   - `"communication": "Comms"`
   - `"finance": "Finance"`
   - `"education": "Education"`
   - `"analytics": "Analytics"`
2. Verify category pills render correctly

**Files**: `src/app/page.tsx`

---

## Phase 4: Pipeline Integration

### T-014: Use categorizeSkill() in Rebuild Index
**User Story**: US-005 | **Satisfies ACs**: AC-US5-04 | **Status**: [x] completed
**Test**: Given a discovered skill with name "docker-security-scan" -> When rebuild-index upserts it -> Then category is "security" (not "development")

**Steps**:
1. Import `categorizeSkill` from `@/lib/metric-utils` in `rebuild-index/route.ts`
2. Replace `category: "development"` with `category: categorizeSkill(skill.slug, skill.name, [])`
3. Write/update test to verify categorization is applied during upsert

**Files**: `src/app/api/v1/admin/rebuild-index/route.ts`

---

### T-015: Use categorizeSkill() in Submission Publish Flow
**User Story**: US-005 | **Satisfies ACs**: AC-US5-05 | **Status**: [x] completed
**Test**: Given a new skill submission with name "playwright-e2e-tests" -> When published -> Then skill category is "testing"

**Steps**:
1. Check `submission-store.ts` for where new Skill records are created
2. Import `categorizeSkill` and use it when setting the category field
3. Write/update test to verify categorization in publish flow

**Files**: `src/lib/submission-store.ts`

---

## Phase 5: Verification

### T-016: Integration Verification
**User Story**: ALL | **Satisfies ACs**: ALL | **Status**: [x] completed
**Test**: Given all changes are applied -> When running full test suite -> Then all tests pass with >80% coverage on new code

**Steps**:
1. Run `npm test` in vskill-platform
2. Verify all new tests pass
3. Verify no regression in existing tests
4. Run TypeScript check: `npx tsc --noEmit`
5. Verify build: `npm run build` (or at minimum `next build` dry run)
6. Manual spot check: review homepage metric values for reasonableness

**Files**: N/A (verification only)

---

## Phase 6: Seed Data Real Metrics (US-006)

### T-017: Write Seed Data Accuracy Tests + Update GitHub Metrics
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-03, AC-US6-04, AC-US6-05, AC-US6-06, AC-US6-07, AC-US6-08, AC-US6-09, AC-US6-10, AC-US6-11, AC-US6-12 | **Status**: [x] completed
**Test**: Given seed-data.ts -> When all skills sharing `anthropics/skills` repoUrl are checked -> Then all 16 have `githubStars: 73059` and `githubForks: 7481`

**Steps**:
1. RED: Write `src/lib/__tests__/seed-data-accuracy.test.ts`:
   - All skills in same repo have identical `githubStars` and `githubForks`
   - Each repo group matches expected real values
   - Fictional repos have `githubStars: 0`, `githubForks: 0`
   - All `vskillInstalls` are `0`
2. GREEN: Update `src/lib/seed-data.ts` with real values for all 118 skills
3. REFACTOR: Verify no test regressions

**Files**: `src/lib/seed-data.ts`, `src/lib/__tests__/seed-data-accuracy.test.ts`

---

### T-018: Update NPM Downloads and Fix specweave Version
**User Story**: US-006 | **Satisfies ACs**: AC-US6-02, AC-US6-13 | **Status**: [x] completed
**Test**: Given seed-data.ts -> When specweave skill is checked -> Then `npmDownloads: 20002` and `currentVersion: "1.0.313"`

**Steps**:
1. RED: Add tests for real npm download values for all 6 packages
2. GREEN: Update the 6 skills with `npmPackage` to real download counts:
   - @playwright/test: 77283441
   - @sentry/node: 56521189
   - eslint: 351651881
   - prisma: 33664102
   - specweave: 20002
   - langchain: 7062262
3. Fix specweave `currentVersion: "1.0.313"`

**Files**: `src/lib/seed-data.ts`, `src/lib/__tests__/seed-data-accuracy.test.ts`

---

## Phase 7: Remove vskillInstalls from UI (US-007)

### T-019: Remove Installs StatCard from Skill Detail Page
**User Story**: US-007 | **Satisfies ACs**: AC-US7-01 | **Status**: [x] completed
**Test**: Given a skill detail page renders -> When viewing Popularity section -> Then no "Installs" StatCard appears

**Steps**:
1. Remove the "Installs" StatCard from `src/app/skills/[name]/page.tsx`
2. Keep Stars, Forks, NPM Downloads, Trending

**Files**: `src/app/skills/[name]/page.tsx`

---

### T-020: Replace Installs with Trust in VerifiedSkillsTab
**User Story**: US-007 | **Satisfies ACs**: AC-US7-02, AC-US7-03 | **Status**: [x] completed
**Test**: Given VerifiedSkillsTab renders -> When viewing table -> Then column header says "Trust" not "Installs"

**Steps**:
1. RED: Update test — table header "Trust" not "Installs", sort by trust
2. GREEN: Edit `src/app/trust/VerifiedSkillsTab.tsx`:
   - Replace "Installs" column header with "Trust"
   - Replace cell value from `vskillInstalls` to `trustScore`
   - Replace sort option from "installs" to "trust"

**Files**: `src/app/trust/VerifiedSkillsTab.tsx`, `src/app/trust/__tests__/VerifiedSkillsTab.test.tsx`

---

### T-021: Integration Verification (Phase 6-7)
**User Story**: ALL (US-006, US-007) | **Satisfies ACs**: ALL | **Status**: [x] completed
**Test**: Given all changes applied -> When running full test suite -> Then all tests pass

**Steps**:
1. Run `npm test` in vskill-platform
2. Run `npx tsc --noEmit`
3. Spot-check: `/skills/specweave` shows Stars=69, Forks=7, no "Installs"
4. Spot-check: `/trust` table shows "Trust" column

**Files**: N/A (verification only)
