# Tasks: Extensible Skills Filter -- Full-Stack UX

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), sonnet (medium), opus (complex)

## Phase 1: Backend

### US-002: Extensible Toggle Filter (P1)

#### T-001: Add extensible field to SkillFilters type
**User Story**: US-002 | **Satisfies ACs**: AC-US2-06 | **Status**: [x] completed
**Description**: Add `extensible?: boolean` to the `SkillFilters` interface in `src/lib/types.ts`.
**Implementation Details**:
- Add `extensible?: boolean` field after `sortDir` in the `SkillFilters` interface
**Test**: Given SkillFilters type -> When extensible field is set -> Then TypeScript compiles without errors
**Dependencies**: None
**Model**: haiku

---

#### T-002: Add extensible filter logic to getSkills()
**User Story**: US-002 | **Satisfies ACs**: AC-US2-07 | **Status**: [x] completed
**Description**: Add extensible filtering in `getSkills()` in `src/lib/data.ts`, after existing filters.
**Implementation Details**:
- After the `search` filter block, add: `if (filters?.extensible) { result = result.filter(s => s.extensible === true); }`
**Test Plan**:
- **File**: `src/lib/__tests__/data.test.ts`
- **Tests**:
  - **TC-001**: filters by extensible when extensible=true
    - Given mock skills with mixed extensible values
    - When getSkills({ extensible: true }) is called
    - Then only skills with extensible=true are returned
  - **TC-002**: does not filter when extensible is undefined
    - Given mock skills with mixed extensible values
    - When getSkills() is called without extensible filter
    - Then all skills are returned
  - **TC-003**: combines extensible filter with category filter
    - Given mock skills with mixed extensible and category values
    - When getSkills({ extensible: true, category: 'development' }) is called
    - Then only extensible development skills are returned
**Dependencies**: T-001
**Model**: sonnet

---

#### T-003: Add extensible param to /api/v1/skills route
**User Story**: US-002 | **Satisfies ACs**: AC-US2-08 | **Status**: [x] completed
**Description**: Accept `extensible` query param in the skills API route and pass to `getSkills()`.
**Implementation Details**:
- Read `extensible` from `searchParams.get("extensible")`
- If value is `"true"`, pass `extensible: true` to `getSkills()`
- Invalid values (anything besides "true") are ignored (treated as no filter)
**Test Plan**:
- **File**: `src/app/api/v1/skills/__tests__/route.test.ts` (or inline in existing test)
- **Tests**:
  - **TC-004**: passes extensible=true to getSkills when param is "true"
    - Given request with ?extensible=true
    - When GET handler processes it
    - Then getSkills is called with extensible: true
  - **TC-005**: ignores extensible param when not "true"
    - Given request with ?extensible=false or no param
    - When GET handler processes it
    - Then getSkills is called without extensible filter
**Dependencies**: T-001, T-002
**Model**: sonnet

---

## Phase 2: Frontend

### US-001: EXT Badge on Skill Cards (P1)

#### T-004: Add EXT pill badge to skill cards
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [x] completed
**Description**: Add a teal "EXT" pill badge in the skill card top row (name/author line) for extensible skills.
**Implementation Details**:
- In `src/app/skills/page.tsx`, inside each skill card's top row div
- After the author span, add: `{skill.extensible && <span style={extBadgeStyle}>EXT</span>}`
- Style: teal background (#0D9488 10% opacity), teal border, teal text, uppercase, monospace, small font
- Badge is unconditional on filter state (always shown for extensible skills)
**Test**: Visual verification -- extensible skills show "EXT" badge, non-extensible do not
**Dependencies**: None (frontend-only, data already has extensible field)
**Model**: sonnet

---

### US-002: Extensible Toggle Filter (P1, frontend)

#### T-005: Add extensible toggle button to filter bar
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05 | **Status**: [x] completed
**Description**: Add a toggle button in the Sort+Tier row that filters to extensible skills.
**Implementation Details**:
- In `src/app/skills/page.tsx`:
  - Read `ext` from search params (new param)
  - Add `ext` to the `base` object for URL building
  - Compute `extensibleCount` from `allSkills.filter(s => s.extensible).length`
  - Pass `extensible: isExtFilter ? true : undefined` to `getSkills()` call
  - Add toggle button after the Tier filter group:
    - Inactive: standard border, teal text "Extensible N"
    - Active: teal background (#0D9488), white text
    - Link toggles `?ext=true` on/off
  - Update `buildUrl` to handle `ext` param (strip when "all" or falsy)
**Test**: Visual verification -- toggle filters list, count is correct, URL updates
**Dependencies**: T-001, T-002
**Model**: opus

---

### US-003: Extension Point Types in Metrics Row (P2)

#### T-006: Show extension point types in metrics row when filter active
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04 | **Status**: [x] completed
**Description**: When the extensible filter is active, append de-duplicated extension point types to each card's metrics row.
**Implementation Details**:
- In `src/app/skills/page.tsx`, in the metrics row div of each skill card:
  - If `isExtFilter && skill.extensible && skill.extensionPoints`:
    - Compute unique types: `[...new Set(skill.extensionPoints.map(ep => ep.type))]`
    - Render each type as a teal-colored span
  - When ext filter is NOT active, do not render extension point types
**Test**: Visual verification -- types shown only when ext=true filter active
**Dependencies**: T-005
**Model**: sonnet

---

## Phase 3: Verification

#### T-007: End-to-end verification
**User Story**: All | **Satisfies ACs**: All | **Status**: [x] completed
**Description**: Verify all acceptance criteria pass, run test suite, check for regressions.
**Implementation Details**:
- Run `vitest` in vskill-platform to confirm all tests pass
- Verify catalog page renders correctly with and without ext filter
- Verify combined filters (category + ext, tier + ext, search + ext) work correctly
- Verify EXT badge always visible on extensible skills
- Verify extension point types only shown when ext=true
**Test**: All unit tests pass, all ACs verified
**Dependencies**: T-001 through T-006
**Model**: sonnet
