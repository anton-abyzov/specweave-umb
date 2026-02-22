---
increment: 0296-strip-prefix-rollout-fixes
title: "Fix slug mismatch bugs from 0292 strip-prefix rollout"
type: bug
priority: P1
status: planned
created: 2026-02-21
structure: user-stories
test_mode: TDD
coverage_target: 80
---

# Bug Fix: Slug mismatch bugs from 0292 strip-prefix rollout

## Overview

Increment 0292 changed `makeSlug()` to strip the org/repo prefix from skill slugs, but four integration sites were not updated to use `makeSlug()` or handle the new clean slugs correctly:

1. **Submit page inline regex** -- `src/app/submit/[id]/page.tsx` computes slugs with `data.skillName.toLowerCase().replace(...)` instead of calling `makeSlug()`. This produces a different slug than what was stored in KV during publishing, causing broken "View published skill" links and failed security API fetches.

2. **Missing `encodeURIComponent`** -- The homepage trending section (`src/app/page.tsx` line 217) and the SearchPalette skill links (`src/app/components/SearchPalette.tsx` line 108) build `/skills/${skill.name}` URLs without encoding. Skill names with special characters (e.g. `@scope/name`) break routing.

3. **`getSkillCategories` ignores KV** -- `getSkillCategories()` in `src/lib/data.ts` only iterates seed-data skills. Published skills from KV (which are `category: "development"` by default) are not counted, making the "development" category undercount on the homepage.

4. **Published skills hardcoded `trendingScore=0`** -- In `getSkills()` in `src/lib/data.ts` (lines 85-86), KV-published skills have `trendingScore7d: 0` and `trendingScore30d: 0`, making them permanently invisible in the "Trending" section since the default sort is `trendingScore7d desc`.

## User Stories

### US-001: Consistent Slug Computation on Submit Page (P1)
**Project**: vskill-platform

**As a** skill author who just published a skill
**I want** the "View published skill" link on the submission status page to point to the correct URL
**So that** I can verify my published skill page without manually guessing the URL

**Acceptance Criteria**:
- [x] **AC-US1-01**: The submit status page (`/submit/[id]`) imports and calls `makeSlug()` from `submission-store.ts` instead of using inline regex to compute the skill slug
- [x] **AC-US1-02**: The `ExternalScanStatus` component uses the same `makeSlug()` call for the security API URL and the security report link
- [x] **AC-US1-03**: Unit test confirms the slug on the submit page matches the slug stored in KV after `publishSkill()` runs

---

### US-002: URL-Safe Skill Links (P2)
**Project**: vskill-platform

**As a** user browsing skills on the homepage or using the search palette
**I want** skill links to work even when skill names contain special characters
**So that** clicking a trending skill or search result always navigates to the correct page

**Acceptance Criteria**:
- [x] **AC-US2-01**: Homepage trending skill links use `encodeURIComponent(skill.name)` in the href
- [x] **AC-US2-02**: SearchPalette skill result links use `encodeURIComponent(r.name)` in the href

---

### US-003: Accurate Category Counts Including KV Skills (P2)
**Project**: vskill-platform

**As a** user viewing the "Skills by Category" chart on the homepage
**I want** the category counts to include community-published skills from KV
**So that** the development category count reflects the actual number of skills

**Acceptance Criteria**:
- [x] **AC-US3-01**: `getSkillCategories()` merges published KV skills into category counts (using each skill's category, defaulting to "development")
- [x] **AC-US3-02**: Seed-data skills that overlap with KV-published slugs are not double-counted
- [x] **AC-US3-03**: When KV is unavailable (build time), the function falls back gracefully to seed-data-only counts

---

### US-004: Baseline Trending Scores for Published Skills (P2)
**Project**: vskill-platform

**As a** platform user browsing the trending section
**I want** newly published community skills to have a non-zero baseline trending score
**So that** they appear in trending lists instead of being permanently buried at the bottom

**Acceptance Criteria**:
- [x] **AC-US4-01**: KV-published skills in `getSkills()` receive a baseline `trendingScore7d` value (e.g., 1) instead of hardcoded 0
- [x] **AC-US4-02**: KV-published skills in `getSkillByName()` also receive the same baseline score
- [x] **AC-US4-03**: Skills enriched with live metrics (`ENABLE_LIVE_METRICS=true`) override the baseline with real values

## Functional Requirements

### FR-001: Single Source of Truth for Slug Computation
All code that computes a skill slug MUST call `makeSlug()` from `submission-store.ts`. No inline regex duplication is allowed.

### FR-002: URL Encoding for Dynamic Skill Names
Any URL constructed with a skill name or slug that may contain special characters MUST use `encodeURIComponent()`.

### FR-003: Category Aggregation Across Data Sources
`getSkillCategories()` must merge seed-data and KV-published skills, deduplicating by slug/name.

### FR-004: Baseline Trending Score
Published skills from KV must have a small positive baseline trending score to ensure they appear in sorted trending lists.

## Success Criteria

- "View published skill" link on `/submit/[id]` navigates to the correct skill page for any skill name
- All trending/search links work for skill names with special characters
- Category counts on homepage match `getSkills()` total per category
- Newly published KV skills appear in the trending section
- All existing tests pass, new tests cover each fix

## Out of Scope

- Changing the KV data model or stored skill records
- Adding real trending score computation from GitHub/npm activity for published skills
- Changing seed-data skill categories or trending scores
- Modifying the publish pipeline itself

## Dependencies

- Increment 0292 (strip-prefix rollout) -- the root cause of these bugs
- `makeSlug()` export from `submission-store.ts`
- Cloudflare KV for published skills data
