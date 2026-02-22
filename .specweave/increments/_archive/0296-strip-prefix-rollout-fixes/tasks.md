# Tasks: Fix slug mismatch bugs from 0292 strip-prefix rollout

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), sonnet (moderate), opus (complex)

## Phase 1: Extract Shared Slug Utility

### T-001: Extract makeSlug to shared slug.ts module
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed

**Description**: Create `src/lib/slug.ts` with the `makeSlug()` function extracted from `submission-store.ts`. Update `submission-store.ts` to re-import from `slug.ts`. This makes `makeSlug` safely importable from client components.

**Implementation Details**:
1. Create `src/lib/slug.ts` exporting `makeSlug(repoUrl: string, skillName: string): string`
2. Move the `REPO_URL_RE` regex to `slug.ts` as well (exported, used by `resolveSlug` in submission-store)
3. In `submission-store.ts`, replace local `makeSlug` and `REPO_URL_RE` with imports from `./slug.js`
4. Ensure all existing `makeSlug` callers in `submission-store.ts` still work (resolveSlug, migrateSkillSlugs)

**Test Plan**:
- **File**: `src/lib/__tests__/slug.test.ts`
- **Tests**:
  - **TC-001**: makeSlug strips non-alphanumeric characters
    - Given skillName "sw-frontend"
    - When makeSlug("", "sw-frontend") is called
    - Then it returns "sw-frontend"
  - **TC-002**: makeSlug strips leading/trailing hyphens
    - Given skillName "@scope/my-skill"
    - When makeSlug("", "@scope/my-skill") is called
    - Then it returns "scope-my-skill" (no leading hyphen)
  - **TC-003**: makeSlug lowercases
    - Given skillName "My-Awesome-Skill"
    - When makeSlug("", "My-Awesome-Skill") is called
    - Then it returns "my-awesome-skill"
  - **TC-004**: makeSlug ignores repoUrl (clean slug only)
    - Given repoUrl "https://github.com/org/repo" and skillName "test"
    - When makeSlug is called
    - Then it returns "test" (no org/repo prefix)

**Dependencies**: None
**Model hint**: sonnet

---

## Phase 2: Fix Submit Page Slug Mismatch (US-001)

### T-002: Replace inline regex with makeSlug on submit page
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed

**Description**: In `src/app/submit/[id]/page.tsx`, replace two instances of inline regex slug computation with `makeSlug()` from `@/lib/slug`.

**Implementation Details**:
1. Add import: `import { makeSlug } from "@/lib/slug";`
2. Line 401 (published link): Replace `data.skillName.toLowerCase().replace(/[^a-z0-9]+/g, '-')` with `makeSlug("", data.skillName)`
3. Line 420 (`ExternalScanStatus` component): Replace `skillName.toLowerCase().replace(/[^a-z0-9]+/g, "-")` with `makeSlug("", skillName)`
4. Remove the now-unused `const slug = ...` line inside `ExternalScanStatus` and use `makeSlug` directly or assign to const

**Test Plan**:
- **File**: `src/app/submit/__tests__/slug-consistency.test.ts`
- **Tests**:
  - **TC-005**: Published skill link uses makeSlug output
    - Given a submission with skillName "@scope/my-tool"
    - When the "View published skill" href is computed
    - Then it equals `/skills/${makeSlug("", "@scope/my-tool")}`
  - **TC-006**: ExternalScanStatus security API URL uses makeSlug
    - Given skillName "@scope/my-tool"
    - When the security API is fetched
    - Then the URL path contains `encodeURIComponent(makeSlug("", "@scope/my-tool"))`

**Dependencies**: T-001
**Model hint**: sonnet

---

## Phase 3: Fix URL Encoding (US-002)

### T-003: [P] Add encodeURIComponent to homepage trending links
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] completed

**Description**: In `src/app/page.tsx`, wrap `skill.name` with `encodeURIComponent()` in the trending skill link href.

**Implementation Details**:
1. Line 217: Change `href={`/skills/${skill.name}`}` to `href={`/skills/${encodeURIComponent(skill.name)}`}`

**Test Plan**:
- Manual verification: Trending links for skills with special characters navigate correctly
- Regression: Existing clean slug links still work (encodeURIComponent is no-op for clean strings)

**Dependencies**: None
**Model hint**: haiku

---

### T-004: [P] Add encodeURIComponent to SearchPalette links
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [x] completed

**Description**: In `src/app/components/SearchPalette.tsx`, wrap `r.name` with `encodeURIComponent()` in skill result href.

**Implementation Details**:
1. Line 108: Change `href: `/skills/${r.name}`` to `href: `/skills/${encodeURIComponent(r.name)}`

**Test Plan**:
- Manual verification: Search result clicks for skills with special characters navigate correctly

**Dependencies**: None
**Model hint**: haiku

---

## Phase 4: Fix Category Counts (US-003)

### T-005: Include KV-published skills in getSkillCategories
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x] completed

**Description**: Update `getSkillCategories()` in `src/lib/data.ts` to include KV-published skills in category counts.

**Implementation Details**:
1. After the seed-data loop, call `getCachedPublishedSkills()` inside a try/catch
2. Create a set of seed-data names for dedup: `const seedNames = new Set(skills.map(s => s.name))`
3. For each published skill not in seed-data, increment the "development" category count (default category for published skills)
4. Wrap the KV read in try/catch so build-time failures fall back gracefully

**Test Plan**:
- **File**: `src/lib/__tests__/data.test.ts` (extend existing)
- **Tests**:
  - **TC-007**: getSkillCategories includes KV-published skills
    - Given 2 seed-data skills (1 development, 1 security) and 3 KV-published skills
    - When getSkillCategories() is called
    - Then development count = 1 + 3 = 4, security count = 1
  - **TC-008**: getSkillCategories deduplicates seed + KV
    - Given a seed skill named "sw-frontend" and a KV skill with slug "sw-frontend"
    - When getSkillCategories() is called
    - Then "sw-frontend" is counted only once
  - **TC-009**: getSkillCategories falls back when KV unavailable
    - Given KV throws an error
    - When getSkillCategories() is called
    - Then it returns seed-data-only counts without throwing

**Dependencies**: None
**Model hint**: sonnet

---

## Phase 5: Fix Trending Score (US-004)

### T-006: Set baseline trending score for KV-published skills
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03 | **Status**: [x] completed

**Description**: In `src/lib/data.ts`, change hardcoded `trendingScore7d: 0` and `trendingScore30d: 0` to `1` for KV-published skills in both `getSkills()` and `getSkillByName()`.

**Implementation Details**:
1. `getSkills()` lines 85-86: Change `trendingScore7d: 0` to `trendingScore7d: 1`, `trendingScore30d: 0` to `trendingScore30d: 1`
2. `getSkillByName()` lines 204-205: Same change
3. When `ENABLE_LIVE_METRICS=true`, the `enrichSkillWithMetrics()` call will override these baselines with real data

**Test Plan**:
- **File**: `src/lib/__tests__/data.test.ts` (extend existing)
- **Tests**:
  - **TC-010**: getSkills returns non-zero trending score for published skills
    - Given a KV-published skill
    - When getSkills({ sortBy: "trendingScore7d", sortDir: "desc" }) is called
    - Then the published skill has trendingScore7d >= 1
  - **TC-011**: getSkillByName returns non-zero trending score for published skill
    - Given a KV-published skill with slug "my-tool"
    - When getSkillByName("my-tool") is called
    - Then the result has trendingScore7d >= 1

**Dependencies**: None
**Model hint**: sonnet

---

## Phase 6: Verification

### T-007: Run full test suite and verify all ACs
**User Story**: All | **Satisfies ACs**: All | **Status**: [x] completed

**Description**: Run `npm test` in vskill-platform to verify all existing and new tests pass. Manually verify the four fixes are working correctly.

**Implementation Details**:
1. Run `npm test` -- all tests must pass
2. Run `npm run build` -- build must succeed
3. Verify no TypeScript errors
4. Check all AC-IDs from spec.md are satisfied

**Dependencies**: T-001, T-002, T-003, T-004, T-005, T-006
**Model hint**: haiku
