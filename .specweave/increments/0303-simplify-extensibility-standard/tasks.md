# Tasks: Simplify Extensible Skills Standard — 3 Clear Categories

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed

## Phase 1: Core Type and Detector (US-001)

### T-001: Change ExtensibilityTier type definition

**Description**: Replace the 5-value union type with 3-value union in `types.ts`. Remove `portability` from `ExtensibilityResult` interface and `SkillData`.

**AC**: AC-US1-01, AC-US1-06

**Implementation Details**:
- Change `ExtensibilityTier` from `"E0" | "E1" | "E2" | "E3" | "E4"` to `"extensible" | "semi-extensible" | "not-extensible"`
- Remove `portability?: Record<string, string[]>` from `SkillData` interface
- Remove `portability` from `ExtensibilityResult` interface in `extensibility-detector.ts`
- Fix any TypeScript compilation errors across codebase

**Test Plan**:
- **TC-001**: TypeScript compiles with no errors after type change
  - Given the type is changed
  - When `npx tsc --noEmit` runs
  - Then zero type errors

**Dependencies**: None
**Status**: [ ] Not Started

---

### T-002: Rewrite extensibility-detector.ts

**Description**: Simplify detection logic to 3 categories. Remove frontmatter detection and portability matrix.

**AC**: AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06, AC-US1-07, AC-US1-10

**Implementation Details**:
- Remove `detectFrontmatterExtensibility()` function
- Remove `PORTABILITY_*` constants
- Remove `TIER_ORDER` array
- Simplify `detectExtensibility()`: DCI + skill-memories → `extensible`, keyword signals → `semi-extensible`, nothing → `not-extensible`
- Keep fenced code block stripping (still needed for accurate DCI detection)
- Keep `extensible: boolean` derived as `tier !== "not-extensible"`
- DCI blocks WITHOUT skill-memories reference → `semi-extensible` (not standard mechanism)

**Test Plan**:
- **TC-002**: DCI block with skill-memories → `extensible`
  - Given a SKILL.md with `!`s="test"; for d in .specweave/skill-memories...``
  - When `detectExtensibility()` is called
  - Then result.tier === "extensible" and result.extensible === true
- **TC-003**: Keyword signals only → `semi-extensible`
  - Given a SKILL.md mentioning "custom templates"
  - When `detectExtensibility()` is called
  - Then result.tier === "semi-extensible" and result.extensible === true
- **TC-004**: No signals → `not-extensible`
  - Given a plain SKILL.md with no extension signals
  - When `detectExtensibility()` is called
  - Then result.tier === "not-extensible" and result.extensible === false
- **TC-005**: DCI inside fenced code blocks → ignored
  - Given DCI patterns inside ``` blocks
  - When `detectExtensibility()` is called
  - Then tier is NOT `extensible`

**Dependencies**: T-001
**Status**: [ ] Not Started

---

### T-003: Rewrite extensibility-detector tests

**Description**: Rewrite `extensibility-detector.test.ts` for the 3-tier model. Cover all categories, edge cases, and backward compat.

**AC**: AC-US1-08

**Implementation Details**:
- Test `not-extensible`: plain text, empty input
- Test `semi-extensible`: template keywords, hook keywords, config keywords, plugin keywords, context keywords, multiple extension points
- Test `extensible`: DCI block with skill-memories, DCI + keywords combined
- Test edge cases: fenced code block stripping, DCI without skill-memories → semi-extensible, empty string
- Test backward compat: `extensible` boolean derivation
- Remove all E0/E1/E2/E3/E4 references from tests

**Test Plan**:
- **TC-006**: All tests pass with `npx vitest run extensibility-detector`

**Dependencies**: T-002
**Status**: [ ] Not Started

---

### T-004: Update data.ts stats and filtering

**Description**: Update `getExtensibilityStats()` to return 3-category counts. Update tier filtering logic.

**AC**: AC-US1-09

**Implementation Details**:
- Change stats from `{ e0, e1, e2, e3, e4 }` to `{ extensible, semiExtensible, notExtensible }`
- Update any filtering that references E0-E4 tier values
- Update `SkillFilters` type if it references `ExtensibilityTier`

**Test Plan**:
- **TC-007**: Stats return correct 3-category counts
  - Given seed data with known classifications
  - When `getExtensibilityStats()` is called
  - Then counts match expected values for extensible, semi-extensible, not-extensible

**Dependencies**: T-001
**Status**: [ ] Not Started

---

## Phase 2: Seed Data and UI (US-002)

### T-005: Reclassify seed data

**Description**: Update all 21 extensible skills in `seed-data.ts` to use new tier values.

**AC**: AC-US2-01, AC-US2-02

**Implementation Details**:
- 20 former-E1 skills → `semi-extensible` (keep existing extension points)
- 1 former-E4 skill (specweave) → `extensible`
- All other skills: `extensibilityTier` changes from `"E0"` to `"not-extensible"` (or remove if not set)

**Test Plan**:
- **TC-008**: No TypeScript errors in seed-data.ts after reclassification
- **TC-009**: Seed data contains exactly 1 `extensible`, 20 `semi-extensible` skills

**Dependencies**: T-001
**Status**: [ ] Not Started

---

### T-006: Update skills list page filter UI

**Description**: Replace E0-E4 sub-filters with 3 category pills on the skills list page.

**AC**: AC-US2-03, AC-US2-05, AC-US2-06

**Implementation Details**:
- Update filter buttons/pills from E1-E4 to Extensible / Semi-Extensible / Not Extensible
- `ext=true` URL param → show both extensible + semi-extensible
- `ext=extensible` → show only extensible
- `ext=semi-extensible` → show only semi-extensible
- Update filter badge colors

**Test Plan**:
- **TC-010**: Filter pills render with correct labels
- **TC-011**: `ext=true` returns union of extensible + semi-extensible skills

**Dependencies**: T-004, T-005
**Status**: [ ] Not Started

---

### T-007: Update skill detail page tier display

**Description**: Show new tier label with appropriate styling on the skill detail page.

**AC**: AC-US2-04

**Implementation Details**:
- Replace E0-E4 badge with tier-specific badge
- Colors: green for `extensible`, yellow/amber for `semi-extensible`, gray for `not-extensible`
- Update any tooltip text explaining what the tier means

**Test Plan**:
- **TC-012**: Detail page renders correct tier badge for each category

**Dependencies**: T-005
**Status**: [ ] Not Started

---

## Phase 3: Documentation (US-003)

### T-008: Rewrite extensible-skills-standard.md

**Description**: Rewrite the formal standard to define 3 categories instead of 5 tiers.

**AC**: AC-US3-01, AC-US3-04, AC-US3-06

**Implementation Details**:
- Replace tier model section with 3 categories (Extensible, Semi-Extensible, Not Extensible)
- Remove Section 3 (Frontmatter Schema) entirely
- Remove Section 4 (Agent Portability Matrix) entirely
- Keep Section 2 (DCI specification) — the mechanism hasn't changed
- Update detection algorithm to describe 3-tier logic
- Add note that Reflect is orthogonal to classification
- Update conformance requirements

**Dependencies**: T-002 (detector logic must be finalized first)
**Status**: [ ] Not Started

---

### T-009: Simplify extensible-skills-guide.md

**Description**: Remove over-engineered content from the implementation guide.

**AC**: AC-US3-02, AC-US3-05

**Implementation Details**:
- Replace 5-tier table with 3-category table
- Remove frontmatter schema example
- Remove portability matrix references
- Keep architecture section (DCI blocks, cascading lookup, skill memories format)
- Keep getting started section
- Keep FAQ section (update tier references)

**Dependencies**: T-008
**Status**: [ ] Not Started

---

### T-010: Update extensible-skills.md landing page

**Description**: Update the hub page quick reference table.

**AC**: AC-US3-03

**Implementation Details**:
- Replace E0-E4 quick reference table with 3-category table
- Update links to standard and guide

**Dependencies**: T-008
**Status**: [ ] Not Started
