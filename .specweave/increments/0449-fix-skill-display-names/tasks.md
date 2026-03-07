---
increment: 0449-fix-skill-display-names
title: "Fix skill display names after hierarchical URL migration"
by_user_story:
  US-001:
    tasks: [T-001, T-002, T-003, T-004, T-005, T-006]
    status: completed
  US-002:
    tasks: [T-007, T-008, T-009]
    status: completed
total_tasks: 9
completed_tasks: 9
---

# Tasks: Fix Skill Display Names After Hierarchical URL Migration

## User Story: US-001 - Platform Display Fix

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Tasks**: 6 total, 0 completed
**Project**: vskill-platform

---

### T-001: Add slug fields to platform type definitions

**User Story**: US-001
**Satisfies ACs**: AC-US1-01
**Status**: [x] completed

**Test Plan**:
- **Given** the four type definitions in vskill-platform (`SkillData`, `SearchIndexEntry`, `SearchResult`, `TrendingSkillEntry`)
- **When** the TypeScript compiler checks the types
- **Then** each includes `ownerSlug?: string`, `repoSlug?: string`, `skillSlug?: string` and the project compiles without errors

**Test Cases**:
1. **Unit**: `src/lib/__tests__/types.test.ts`
   - typeDefinitionsIncludeSlugFields(): TypeScript structural check that an object with slug fields satisfies each interface
   - **Coverage Target**: 90%

**Implementation**:
1. In `src/lib/types.ts` add `ownerSlug?: string; repoSlug?: string; skillSlug?: string` to `SkillData`
2. In `src/lib/search-index.ts` add same three fields to `SearchIndexEntry`
3. In `src/lib/search.ts` add same three fields to `SearchResult`
4. In `src/lib/stats-compute.ts` add same three fields to `TrendingSkillEntry`
5. Run `npx tsc --noEmit` to confirm no compile errors
6. Run `npx vitest run` to confirm no regressions

---

### T-002: Propagate slug fields through data mappers and search index builder

**User Story**: US-001
**Satisfies ACs**: AC-US1-02
**Status**: [x] completed

**Test Plan**:
- **Given** a Prisma `Skill` row with populated `ownerSlug`, `repoSlug`, `skillSlug` columns
- **When** `mapDbSkillToSkillData()` processes the row
- **Then** the returned `SkillData` contains the correct slug values

**Test Cases**:
1. **Unit**: `src/lib/__tests__/data.test.ts`
   - mapDbSkillToSkillDataIncludesSlugFields(): mock Prisma row with slug values, assert output SkillData has them
   - mapDbSkillToSkillDataHandlesNullSlugs(): mock row with NULL slugs, assert output has undefined fields
   - **Coverage Target**: 90%

2. **Unit**: `src/lib/__tests__/search-index.test.ts`
   - buildSearchIndexEntryIncludesSlugFields(): assert SearchIndexEntry written to KV contains slug fields
   - **Coverage Target**: 85%

3. **Unit**: `src/lib/__tests__/search.test.ts`
   - searchResultIncludesSlugFields(): assert SearchResult from edge path copies slug fields from SearchIndexEntry
   - searchSkillsPostgresIncludesSlugFields(): assert raw SQL SELECT includes ownerSlug, repoSlug, skillSlug
   - **Coverage Target**: 85%

4. **Unit**: `src/lib/__tests__/stats-compute.test.ts`
   - trendingSkillEntryIncludesSlugFields(): assert Prisma select for trending includes slug columns
   - **Coverage Target**: 85%

**Implementation**:
1. In `src/lib/data.ts` `mapDbSkillToSkillData()`: add `ownerSlug: s.ownerSlug ?? undefined, repoSlug: s.repoSlug ?? undefined, skillSlug: s.skillSlug ?? undefined`
2. In `src/lib/search-index.ts` `buildSearchIndex()`: add slug columns to DB `select` clause; include in `SearchIndexEntry` object
3. In `src/lib/search.ts` edge path (`searchSkillsEdge()`): copy slug fields from `SearchIndexEntry` to `SearchResult`
4. In `src/lib/search.ts` Postgres path: add `"ownerSlug"`, `"repoSlug"`, `"skillSlug"` to raw SQL SELECT; update `SkillSearchRow` type
5. In `src/lib/stats-compute.ts`: add `ownerSlug: true, repoSlug: true, skillSlug: true` to Prisma `select` in both `computeFullStats()` and `computeMinimalStats()` trending queries
6. Run `npx vitest run` - all tests must pass

---

### T-003: Fix SearchPalette to display skillSlug as primary name

**User Story**: US-001
**Satisfies ACs**: AC-US1-03
**Status**: [x] completed

**Test Plan**:
- **Given** search results that include `ownerSlug`, `repoSlug`, `skillSlug` fields
- **When** `SearchPalette` renders a result with `skillSlug = "news-digest"`, `ownerSlug = "dailydotdev"`, `repoSlug = "daily"`
- **Then** the label shows `"news-digest"` as primary text and `"dailydotdev/daily"` as secondary context with no owner duplication

**Test Cases**:
1. **Unit**: `src/app/components/__tests__/SearchPalette.test.tsx`
   - searchPaletteShowsSkillSlugAsLabel(): render with slug fields, assert label text equals skillSlug
   - searchPaletteFallsBackToName(): render without slug fields, assert label uses name (no duplication)
   - searchPaletteShowsOwnerRepoContext(): render with slug fields, assert secondary context is `ownerSlug/repoSlug`
   - **Coverage Target**: 90%

**Implementation**:
1. In `src/app/components/SearchPalette.tsx` around line 344, change result mapping:
   - `label: r.skillSlug ?? r.name` as primary name
   - secondary context: `r.ownerSlug && r.repoSlug ? \`${r.ownerSlug}/${r.repoSlug}\` : r.author`
2. Ensure the rendered `<CommandItem>` uses the label correctly (check existing JSX structure)
3. Run `npx vitest run`

---

### T-004: Fix TrendingSkills to display skillSlug with ownerSlug prefix

**User Story**: US-001
**Satisfies ACs**: AC-US1-04
**Status**: [x] completed

**Test Plan**:
- **Given** a trending skill with `ownerSlug = "dailydotdev"`, `skillSlug = "news-digest"`, `author = "dailydotdev"`, `name = "dailydotdev/daily/news-digest"`
- **When** the `TrendingSkills` component renders
- **Then** the display shows `"dailydotdev/"` as the faint prefix and `"news-digest"` as the bold name (not `"dailydotdev/dailydotdev/daily/news-digest"`)

**Test Cases**:
1. **Unit**: `src/app/components/home/__tests__/TrendingSkills.test.tsx`
   - trendingSkillShowsSkillSlugAsBoldName(): render with slug fields, assert bold element text equals skillSlug
   - trendingSkillShowsOwnerSlugAsPrefix(): render with slug fields, assert faint prefix is ownerSlug
   - trendingSkillFallsBackToName(): render without slug fields, assert displays name (no duplication)
   - **Coverage Target**: 90%

**Implementation**:
1. In `src/app/components/home/TrendingSkills.tsx` around lines 48-49:
   - faint prefix: `{skill.ownerSlug ?? skill.author}/`
   - bold name: `{skill.skillSlug ?? skill.name}`
2. Run `npx vitest run`

---

### T-005: Fix skills browse page to pass skillSlug to PublisherLink

**User Story**: US-001
**Satisfies ACs**: AC-US1-05
**Status**: [x] completed

**Test Plan**:
- **Given** a skill with `skillSlug = "news-digest"` and `name = "dailydotdev/daily/news-digest"`
- **When** the skills browse page renders the `PublisherLink` component for that skill
- **Then** `PublisherLink` receives `skillSlug` as the `skillName` prop (not the full hierarchical name)

**Test Cases**:
1. **Unit**: `src/app/skills/__tests__/page.test.tsx`
   - skillsPagePassesSkillSlugToPublisherLink(): render skills list, assert PublisherLink receives skillSlug as skillName prop
   - skillsPageFallsBackToNameWhenNoSlug(): render skill without slugs, assert PublisherLink receives name
   - **Coverage Target**: 85%

**Implementation**:
1. In `src/app/skills/page.tsx` around line 265, change the prop:
   - Before: `<PublisherLink author={skill.author} skillName={skill.name} />`
   - After: `<PublisherLink author={skill.author} skillName={skill.skillSlug ?? skill.name} />`
2. Confirm `PublisherLink.tsx` itself needs no changes (it already renders `author / skillName` correctly)
3. Run `npx vitest run`

---

### T-006: Write backfill script for NULL slug fields and document index rebuild

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02
**Status**: [x] completed

**Test Plan**:
- **Given** a production DB with some `Skill` rows having NULL `ownerSlug`, `repoSlug`, `skillSlug`
- **When** the backfill script runs
- **Then** all NULL slug fields are populated using `extractOwner()`, `extractRepoName()`, `deriveSkillSlug()` from `slug.ts`

**Test Cases**:
1. **Unit**: `scripts/__tests__/backfill-slugs.test.ts`
   - backfillDerivedSlugsFromName(): mock skill with NULL slugs and hierarchical name, assert correct slug values derived
   - backfillSkipsSkillsWithExistingSlugs(): mock skill with existing slugs, assert no update issued
   - **Coverage Target**: 85%

**Implementation**:
1. Create `repositories/anton-abyzov/vskill-platform/scripts/backfill-slugs.ts`:
   - Query all skills where `ownerSlug IS NULL OR repoSlug IS NULL OR skillSlug IS NULL`
   - For each: derive slugs using `extractOwner(name)`, `extractRepoName(name)`, `deriveSkillSlug(name)` from `src/lib/slug.ts`
   - Update the DB row with derived values
   - Log count of updated rows
2. Add header comment documenting how to trigger KV index rebuild after deploy (call the cron endpoint)
3. Run `npx vitest run` for the backfill script tests

---

## User Story: US-002 - CLI Display Fix

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Tasks**: 3 total, 0 completed
**Project**: vskill

---

### T-007: Add slug fields to CLI SkillSearchResult type

**User Story**: US-002
**Satisfies ACs**: AC-US2-01
**Status**: [x] completed

**Test Plan**:
- **Given** the `SkillSearchResult` interface in `src/api/client.ts`
- **When** the TypeScript compiler checks the type
- **Then** it includes `ownerSlug?: string`, `repoSlug?: string`, `skillSlug?: string` optional fields

**Test Cases**:
1. **Unit**: `src/api/__tests__/client.test.ts`
   - skillSearchResultTypeIncludesSlugFields(): TypeScript structural check that an object with slug fields satisfies `SkillSearchResult`
   - **Coverage Target**: 85%

**Implementation**:
1. In `repositories/anton-abyzov/vskill/src/api/client.ts`, add to `SkillSearchResult`:
   ```ts
   ownerSlug?: string;
   repoSlug?: string;
   skillSlug?: string;
   ```
2. Run `npx vitest run` in the vskill repo directory

---

### T-008: Fix CLI formatSkillId to use slug fields without duplication

**User Story**: US-002
**Satisfies ACs**: AC-US2-02
**Status**: [x] completed

**Test Plan**:
- **Given** a `SkillSearchResult` with `ownerSlug = "dailydotdev"`, `repoSlug = "daily"`, `skillSlug = "news-digest"`
- **When** `formatSkillId()` formats the result
- **Then** it returns `"dailydotdev/daily@news-digest"` with no duplication

**Test Cases**:
1. **Unit**: `src/commands/__tests__/find.test.ts`
   - formatSkillIdWithSlugFields(): slug fields present → returns `ownerSlug/repoSlug@skillSlug`
   - formatSkillIdPartialSlugFields(): only skillSlug present → parses name for owner/repo prefix
   - formatSkillIdLegacyFlatName(): legacy flat name with no slashes → returns name as-is
   - **Coverage Target**: 95%

**Implementation**:
1. In `repositories/anton-abyzov/vskill/src/commands/find.ts`, rewrite `formatSkillId()`:
   - If `skill.skillSlug` is present: return `${skill.ownerSlug ?? extractOwner(skill.name)}/${skill.repoSlug ?? extractRepoName(skill.name)}@${skill.skillSlug}`
   - Else if `skill.name` has 3+ segments: return `${parts[0]}/${parts[1]}@${parts[parts.length - 1]}`
   - Else: return `skill.name` unchanged
2. Remove old `extractBaseRepo(repoUrl)` usage from label building if it was the source of duplication
3. Run `npx vitest run` in the vskill repo directory

---

### T-009: Verify CLI graceful fallback for missing slug fields

**User Story**: US-002
**Satisfies ACs**: AC-US2-03
**Status**: [x] completed

**Test Plan**:
- **Given** a skill API response that has a hierarchical `name` but no `ownerSlug`, `repoSlug`, or `skillSlug` fields (old API response format)
- **When** `formatSkillId()` renders the label
- **Then** it parses `name` into segments and displays without duplication (returns `"dailydotdev/daily@news-digest"` not `"dailydotdev/daily@dailydotdev/daily/news-digest"`)

**Test Cases**:
1. **Unit**: `src/commands/__tests__/find.test.ts`
   - formatSkillIdFallbackParsesHierarchicalName(): `name = "dailydotdev/daily/news-digest"`, no slug fields → `"dailydotdev/daily@news-digest"`
   - formatSkillIdFallbackHandlesTwoSegments(): `name = "owner/skill"`, no slug fields → `"owner/skill"` (no @ added)
   - formatSkillIdFallbackHandlesSingleSegment(): `name = "simple-skill"`, no slug fields → `"simple-skill"`
   - **Coverage Target**: 95%

**Implementation**:
1. Confirm the fallback logic in `formatSkillId()` written in T-008 covers all edge cases (no additional code changes expected)
2. Add the three edge-case tests to `src/commands/__tests__/find.test.ts`
3. Run `npx vitest run` in the vskill repo directory - all fallback tests must pass
