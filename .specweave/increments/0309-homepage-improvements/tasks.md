# Tasks: Homepage Improvements

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## Phase 1: CLI Command Examples (US-001)

### T-001: Replace generic vskill placeholder with real install/find examples
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [ ] not started

**Description**: In `src/app/page.tsx`, replace the `$ npx vskill ...` code element with two concrete CLI examples showing `vskill install` and `vskill find` commands using real skill repo/names from seed data.

**Implementation Details**:
- Replace the single `<code>` element (lines 137-143) with two examples:
  - `$ npx vskill install anthropics/skills`
  - `$ npx vskill find security`
- Keep the `or bunx / pnpx / yarn dlx` hint below
- Use monospace font, same styling as current element
- Ensure examples fit within the hero layout on mobile

**Test Plan**:
- **File**: `src/app/__tests__/page.test.tsx` (or verify manually)
- **Tests**:
  - **TC-001**: Homepage renders install command example
    - Given the homepage renders
    - When inspecting the hero section
    - Then a code element containing `vskill install` is visible
  - **TC-002**: Homepage renders find command example
    - Given the homepage renders
    - When inspecting the hero section
    - Then a code element containing `vskill find` is visible

**Dependencies**: None
**Model Hint**: haiku

---

## Phase 2: Category Chart Data Fix (US-002)

### T-002: Write failing test for getSkillCategories with DB skills (TDD RED)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-04 | **Status**: [ ] not started

**Description**: Write a test that verifies `getSkillCategories()` includes counts from DB-published skills (not just seed data). This test should fail initially because the current implementation may not properly aggregate.

**Implementation Details**:
- Add test in `src/lib/__tests__/data-prisma.test.ts`
- Mock Prisma `db.skill.groupBy()` to return extra categories with counts
- Assert that returned counts include both seed + DB counts
- Assert total across all categories equals seed count + DB count

**Test Plan**:
- **File**: `src/lib/__tests__/data-prisma.test.ts`
- **Tests**:
  - **TC-003**: getSkillCategories merges seed + DB category counts
    - Given Prisma returns 50 extra "development" skills and 20 extra "security" skills
    - When getSkillCategories() is called
    - Then development count = seed development count + 50
    - And security count = seed security count + 20
  - **TC-004**: getSkillCategories sum matches getSkills total
    - Given Prisma returns consistent data for both getSkills and getSkillCategories
    - When both functions are called
    - Then sum of category counts equals total skills length

**Dependencies**: None
**Model Hint**: sonnet

---

### T-003: Fix getSkillCategories to properly merge DB counts (TDD GREEN)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [ ] not started

**Description**: Ensure `getSkillCategories()` in `src/lib/data.ts` properly merges Prisma DB category counts with seed data counts so the category chart matches the total skills count.

**Implementation Details**:
- Review current implementation (lines 333-372) - it already attempts DB merge
- Verify the `groupBy` query excludes seed skills by name (it does: `where: { name: { notIn: seedNames } }`)
- Ensure the KV fallback path also properly aggregates
- Make T-002 test pass

**Test Plan**: T-002 tests should now pass

**Dependencies**: T-002
**Model Hint**: sonnet

---

### T-004: Verify KV fallback still works for getSkillCategories
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03 | **Status**: [ ] not started

**Description**: Ensure when Prisma is unavailable, `getSkillCategories()` falls back to KV and still includes community skill counts.

**Implementation Details**:
- Add/verify test in `src/lib/__tests__/data.test.ts` for KV fallback
- Mock Prisma to throw, mock KV to return published skills
- Assert category counts include KV-published skills

**Test Plan**:
- **File**: `src/lib/__tests__/data.test.ts`
- **Tests**:
  - **TC-005**: getSkillCategories falls back to KV when Prisma unavailable
    - Given Prisma throws an error
    - And KV returns 10 published skills
    - When getSkillCategories() is called
    - Then development count includes 10 KV-published skills

**Dependencies**: T-003
**Model Hint**: haiku

---

## Phase 3: Trending Score Documentation (US-003)

### T-005: Add JSDoc to trendingScore fields in SkillData interface [P]
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-03 | **Status**: [ ] not started

**Description**: Document the trendingScore scale and methodology in the `SkillData` interface in `src/lib/types.ts`.

**Implementation Details**:
- Add JSDoc to `trendingScore7d` field explaining:
  - Scale: 0-100 (higher = more trending)
  - Represents weighted combination of star velocity, install growth, and commit recency over 7 days
  - Used for default sort order on homepage and skills listing
- Add JSDoc to `trendingScore30d` field explaining:
  - Same scale as 7d but over 30-day window
  - Used as baseline for momentum calculation (7d - 30d = momentum delta)
  - MomentumArrow displays the delta between 7d and 30d

**Test Plan**: N/A (documentation only - type file)

**Dependencies**: None
**Model Hint**: haiku

---

### T-006: Add scale documentation comment to seed-data.ts [P]
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-03 | **Status**: [ ] not started

**Description**: Add a comment block near the top of `src/lib/seed-data.ts` documenting the trending score scale and explaining how momentum deltas are computed.

**Implementation Details**:
- Add a comment block after the imports explaining:
  - trendingScore range: 0-100
  - trendingScore7d: recent 7-day momentum (higher = more active recently)
  - trendingScore30d: 30-day baseline
  - Delta (7d - 30d) drives MomentumArrow component: positive = accelerating, negative = decelerating
  - Seed data values are illustrative and representative of relative popularity

**Test Plan**: N/A (comment only)

**Dependencies**: None
**Model Hint**: haiku

---

### T-007: Adjust top trending skill score deltas for meaningful momentum display
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-04 | **Status**: [ ] not started

**Description**: Review and adjust the trendingScore7d and trendingScore30d values in seed data so that the top 8 trending skills (those shown on the homepage) have visually meaningful momentum deltas.

**Implementation Details**:
- Current state: top 8 skills by trendingScore7d have deltas of 1.4 to 3.5 pts
- MomentumArrow threshold: delta > 1 shows up arrow, delta < -1 shows down arrow
- Adjust top 3-4 skills to have 7d scores that are 5-12 pts higher than 30d (strong upward momentum)
- Keep 1-2 skills with flat momentum (delta ~0) for contrast
- Keep 1-2 skills with slight negative momentum for variety
- Ensure scores remain within 0-100 range and maintain relative ordering

**Test Plan**:
- **File**: `src/lib/__tests__/seed-data-trending.test.ts` (new)
- **Tests**:
  - **TC-006**: Top 8 trending skills have at least 3 with delta > 5
    - Given the seed data sorted by trendingScore7d desc
    - When taking the top 8
    - Then at least 3 have (trendingScore7d - trendingScore30d) > 5
  - **TC-007**: All trendingScore values are within 0-100
    - Given all skills in seed data
    - When checking trendingScore7d and trendingScore30d
    - Then all values are >= 0 and <= 100
  - **TC-008**: trendingScore7d and trendingScore30d are both present for every skill
    - Given all skills in seed data
    - When checking each skill
    - Then both trendingScore7d and trendingScore30d are defined and are numbers

**Dependencies**: T-005 (for scale documentation context)
**Model Hint**: sonnet

---

## Phase 4: Verification

### T-008: Run full test suite and verify all ACs
**User Story**: All | **Satisfies ACs**: All | **Status**: [ ] not started

**Description**: Run the complete test suite, verify homepage renders correctly, and check all acceptance criteria.

**Implementation Details**:
- Run `npm test` in vskill-platform
- Verify homepage renders with CLI examples
- Verify category chart matches total skills count
- Verify trending section shows meaningful momentum arrows
- Mark all ACs as complete in spec.md

**Test Plan**: Full test suite execution

**Dependencies**: T-001, T-003, T-004, T-007
**Model Hint**: haiku
