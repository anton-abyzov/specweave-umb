# Tasks: Extensible Skills Standard Formalization

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), sonnet (medium), opus (complex)

---

## Phase 1: Foundation (Types + Detector)

### US-001: Extensibility Tier Model

#### T-001: Add ExtensibilityTier type to types.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-04 | **Status**: [x] completed

**Description**: Add the `ExtensibilityTier` type union and extend `SkillData` and `SkillFilters` with tier-related fields.

**Implementation Details**:
- Add `export type ExtensibilityTier = 'E0' | 'E1' | 'E2' | 'E3' | 'E4';` to `src/lib/types.ts`
- Add `extensibilityTier?: ExtensibilityTier` to `SkillData` interface
- Add `portability?: Record<string, string[]>` to `SkillData` interface
- Update `SkillFilters.extensible` from `boolean` to `boolean | ExtensibilityTier` for backward compat
- Keep existing `extensible?: boolean` field on `SkillData`

**Test Plan**:
- **File**: `src/lib/__tests__/types.test.ts`
- **Tests**:
  - **TC-001**: ExtensibilityTier type accepts all valid values (E0-E4)
    - Given the type definition
    - When assigning each valid tier string
    - Then TypeScript compiles without error (compile-time check, verified by build)

**Dependencies**: None
**Model**: haiku

---

#### T-002: Extend ExtensibilityResult with tier and portability
**User Story**: US-001, US-003 | **Satisfies ACs**: AC-US1-01, AC-US3-01 | **Status**: [x] completed

**Description**: Update the `ExtensibilityResult` and `ExtensionPoint` interfaces in the detector module.

**Implementation Details**:
- Add `tier: ExtensibilityTier` to `ExtensibilityResult`
- Add `portability: Record<string, string[]>` to `ExtensibilityResult`
- Update the return type of `detectExtensibility` to include `tier` and `portability`
- Ensure backward compat: `extensible` remains derived from `tier !== 'E0'`

**Test Plan**:
- **File**: `src/lib/scanner/__tests__/extensibility-detector.test.ts`
- **Tests**:
  - **TC-002**: detectExtensibility returns tier field
    - Given a plain skill with no signals
    - When calling detectExtensibility
    - Then result.tier equals 'E0' and result.extensible equals false
  - **TC-003**: detectExtensibility returns portability field
    - Given an extensible skill
    - When calling detectExtensibility
    - Then result.portability is an object with mechanism-to-agent-slug mappings

**Dependencies**: T-001
**Model**: sonnet

---

### US-002: Enhanced Detector with DCI Block Detection

#### T-003: Implement DCI block detection in detector
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03 | **Status**: [x] completed

**Description**: Add regex-based DCI shell block detection to `detectExtensibility`. DCI blocks use the pattern `` !`...` `` at the start of a line (not inside fenced code blocks).

**Implementation Details**:
- Add a pre-processing step to strip fenced code blocks (` ``` `) from the content before signal scanning
- Add a DCI_PATTERNS array with regexes:
  - `` /^!`[^`]+skill-memories[^`]+`/m `` for skill-memories DCI
  - `` /^!`[^`]+`/m `` for generic DCI blocks
- If skill-memories DCI + reflect/auto-learn reference found -> E4
- If skill-memories DCI found -> E3
- DCI without skill-memories -> still E3 (custom DCI)

**Test Plan**:
- **File**: `src/lib/scanner/__tests__/extensibility-detector.test.ts`
- **Tests**:
  - **TC-004**: Detects DCI block with skill-memories reference as E3
    - Given SKILL.md with `!` backtick block containing "skill-memories"
    - When calling detectExtensibility
    - Then result.tier equals 'E3'
  - **TC-005**: Detects DCI block + reflect reference as E4
    - Given SKILL.md with DCI block + "reflect" or "auto-learn" keyword
    - When calling detectExtensibility
    - Then result.tier equals 'E4'
  - **TC-006**: Does not match DCI patterns inside fenced code blocks
    - Given SKILL.md with a DCI-like pattern inside triple-backtick code block
    - When calling detectExtensibility
    - Then the DCI pattern is not detected (tier remains based on other signals)
  - **TC-007**: Keyword-only skill remains E1
    - Given SKILL.md with "custom templates" but no DCI block
    - When calling detectExtensibility
    - Then result.tier equals 'E1'

**Dependencies**: T-002
**Model**: opus

---

#### T-004: Implement frontmatter extensibility parsing
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [x] completed

**Description**: Parse YAML frontmatter for an `extensibility:` key to detect E2-level declaration.

**Implementation Details**:
- Extract YAML frontmatter block (between `---` delimiters) from SKILL.md content
- Parse for `extensibility:` key presence (simple regex, no full YAML parser needed)
- If found, classify as E2 (unless DCI signals bump it higher)
- Frontmatter format: `extensibility: { tier: "E2", points: ["template", "config"] }`

**Test Plan**:
- **File**: `src/lib/scanner/__tests__/extensibility-detector.test.ts`
- **Tests**:
  - **TC-008**: Detects frontmatter extensibility declaration as E2
    - Given SKILL.md with `extensibility:` in YAML frontmatter
    - When calling detectExtensibility
    - Then result.tier equals 'E2'
  - **TC-009**: Frontmatter + DCI results in higher tier (E3)
    - Given SKILL.md with both frontmatter extensibility and DCI block
    - When calling detectExtensibility
    - Then result.tier equals 'E3' (DCI wins)

**Dependencies**: T-002
**Model**: sonnet

---

#### T-005: Implement tier determination logic (highest wins)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03, AC-US2-05 | **Status**: [x] completed

**Description**: Implement the tier resolution logic that selects the highest detected tier.

**Implementation Details**:
- Define tier priority: E4 > E3 > E2 > E1 > E0
- After all signal checks, return the highest tier found
- Ensure `extensible` boolean is derived: `tier !== 'E0'`
- Ensure `extensionPoints` array is populated from all detection methods

**Test Plan**:
- **File**: `src/lib/scanner/__tests__/extensibility-detector.test.ts`
- **Tests**:
  - **TC-010**: All tier transitions tested
    - Given 5 sample SKILL.md contents (one per tier)
    - When calling detectExtensibility on each
    - Then each returns the correct tier (E0, E1, E2, E3, E4)
  - **TC-011**: Keyword + DCI combined returns E3 (not E1)
    - Given SKILL.md with both keyword signals and DCI block
    - When calling detectExtensibility
    - Then result.tier equals 'E3'

**Dependencies**: T-003, T-004
**Model**: sonnet

---

### US-003: Portability Matrix

#### T-006: Implement portability mapping in detector
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x] completed

**Description**: Map each detected extensibility mechanism to compatible agent slugs.

**Implementation Details**:
- Define portability constants:
  - `DCI -> ["claude-code"]` (only agent executing shell in SKILL.md)
  - `frontmatter -> ["claude-code", "cursor", "github-copilot", "windsurf", "aider"]` (agents reading YAML frontmatter)
  - `keyword -> ["*"]` (universal, informational only)
- Build portability map based on which mechanisms were detected
- Return as `Record<string, string[]>` on `ExtensibilityResult`

**Test Plan**:
- **File**: `src/lib/scanner/__tests__/extensibility-detector.test.ts`
- **Tests**:
  - **TC-012**: DCI-detected skill maps to claude-code only
    - Given SKILL.md with DCI block
    - When calling detectExtensibility
    - Then result.portability["DCI"] equals ["claude-code"]
  - **TC-013**: Keyword-detected skill maps to universal
    - Given SKILL.md with keyword signals only
    - When calling detectExtensibility
    - Then result.portability["keyword"] equals ["*"]
  - **TC-014**: Multiple mechanisms produce combined portability map
    - Given SKILL.md with DCI + keyword signals
    - When calling detectExtensibility
    - Then result.portability has both "DCI" and "keyword" keys

**Dependencies**: T-005
**Model**: sonnet

---

## Phase 2: Integration (API + UI + Seed Data)

### US-006: Seed Data Migration

#### T-007: Update seed data with extensibilityTier field [P]
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-04 | **Status**: [x] completed

**Description**: Add `extensibilityTier` to all 89 skills in seed-data.ts.

**Implementation Details**:
- Skills with `extensible: true` and keyword-only detection -> `extensibilityTier: 'E1'`
- SpecWeave skill (has DCI + reflect) -> `extensibilityTier: 'E4'`
- Skills with `extensible: false` or undefined -> `extensibilityTier: 'E0'` (or omit, defaulting to E0)
- Keep `extensible: boolean` field as-is for backward compat

**Test Plan**:
- **File**: `src/lib/__tests__/data.test.ts`
- **Tests**:
  - **TC-015**: All extensible skills have extensibilityTier set
    - Given the seed data
    - When filtering skills with extensible: true
    - Then all have extensibilityTier >= 'E1'
  - **TC-016**: Non-extensible skills default to E0
    - Given the seed data
    - When filtering skills without extensible: true
    - Then extensibilityTier is undefined or 'E0'

**Dependencies**: T-001
**Model**: haiku

---

### US-004: Platform Statistics

#### T-008: Extend /api/v1/stats with extensibility breakdown
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01 | **Status**: [x] completed

**Description**: Add extensibility tier counts to the stats endpoint response.

**Implementation Details**:
- In `src/app/api/v1/stats/route.ts`, after fetching all skills, compute tier distribution
- Group by `extensibilityTier` (default to 'E0' if undefined)
- Add `extensibility: { total, e0, e1, e2, e3, e4 }` to response JSON
- Add helper function `getExtensibilityStats(skills: SkillData[])` in `data.ts`

**Test Plan**:
- **File**: `src/app/api/v1/stats/__tests__/route.test.ts` (new)
- **Tests**:
  - **TC-017**: Stats endpoint includes extensibility object
    - Given skills with mixed extensibility tiers
    - When calling GET /api/v1/stats
    - Then response contains extensibility.total, extensibility.e0-e4
  - **TC-018**: Extensibility counts sum to totalSkills
    - Given the stats response
    - When summing e0+e1+e2+e3+e4
    - Then equals totalSkills

**Dependencies**: T-007
**Model**: sonnet

---

#### T-009: Update data layer for tier-aware filtering
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03 | **Status**: [x] completed

**Description**: Update `getSkills` in `data.ts` to support tier-based extensibility filtering.

**Implementation Details**:
- Update `SkillFilters.extensible` type to `boolean | ExtensibilityTier`
- When `extensible === true` -> filter to `tier >= E1` (backward compat)
- When `extensible` is an `ExtensibilityTier` string -> filter to skills with tier >= that value
- Add `getExtensibilityStats` helper function

**Test Plan**:
- **File**: `src/lib/__tests__/data.test.ts`
- **Tests**:
  - **TC-019**: getSkills with extensible=true returns all extensible skills (backward compat)
    - Given skills with various tiers
    - When calling getSkills({ extensible: true })
    - Then returns all skills with tier >= E1
  - **TC-020**: getSkills with extensible='E3' returns E3+ skills only
    - Given skills with E1, E2, E3, E4 tiers
    - When calling getSkills({ extensible: 'E3' })
    - Then returns only E3 and E4 skills

**Dependencies**: T-007
**Model**: sonnet

---

#### T-010: Update /skills page with tier-aware filtering [P]
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02, AC-US4-03 | **Status**: [x] completed

**Description**: Replace the boolean extensible filter on the skills page with a tier-aware dropdown/pills.

**Implementation Details**:
- Replace `isExtFilter` boolean with `extTier` that can be `'true'` (backward compat) or `'E1'`-`'E4'`
- Show tier distribution count next to each tier option
- Keep "Extensible" as a toggle that maps to `?ext=true` (any extensible)
- Add tier pills: E1, E2, E3, E4 for granular filtering
- Update `buildUrl` and query param handling

**Test Plan**:
- Manual visual verification (server component, not unit-testable for UI)
- Verify `?ext=true` still works (backward compat)
- Verify `?ext=E3` filters correctly

**Dependencies**: T-009
**Model**: sonnet

---

#### T-011: Update skill detail page with tier badge and portability [P]
**User Story**: US-003, US-001 | **Satisfies ACs**: AC-US3-04, AC-US1-01 | **Status**: [x] completed

**Description**: Show extensibility tier badge and portability matrix on the skill detail page.

**Implementation Details**:
- Replace "EXTENSIBLE" pill with tier-specific badge (e.g., "E3 DCI-VERIFIED")
- In the Extension Points section, add portability info showing which agents support each mechanism
- Add tier explanation tooltip
- Color-code tiers: E1=gray, E2=blue, E3=teal, E4=green

**Test Plan**:
- Manual visual verification (server component)
- Verify tier badge renders correctly for each tier level

**Dependencies**: T-007, T-006
**Model**: sonnet

---

## Phase 3: Documentation

### US-005: Documentation Restructure

#### T-012: Split extensible-skills.md into standard and guide
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02 | **Status**: [x] completed

**Description**: Restructure the extensible skills documentation into two documents.

**Implementation Details**:
- Create `extensible-skills-standard.md` (formal standard):
  - E0-E4 tier definitions with RFC language (MUST/SHOULD/MAY)
  - DCI specification (syntax, execution model, graceful degradation)
  - Frontmatter schema specification
  - Portability matrix (mechanism vs agent compatibility)
  - Conformance requirements
- Rename/rewrite `extensible-skills.md` to `extensible-skills-guide.md` (implementation guide):
  - Getting Started (for Claude Code users, for SpecWeave users)
  - Real-world examples
  - FAQ
  - Troubleshooting
- Keep backward-compat redirect from old URL if possible

**Test Plan**:
- Verify all internal links resolve
- Verify sidebar renders correctly
- Verify no broken cross-references

**Dependencies**: None (can start in parallel with Phase 1)
**Model**: opus

---

#### T-013: Update index and sidebar for new doc structure
**User Story**: US-005 | **Satisfies ACs**: AC-US5-03 | **Status**: [x] completed

**Description**: Update the extensible skills index page and Docusaurus sidebar configuration.

**Implementation Details**:
- Update `docs/skills/extensible/index.md` with new document links
- Update `sidebars.ts` if needed for new file names
- Ensure sidebar ordering: Standard -> Guide -> Deep Dive -> Self-Improving -> Development Guidelines

**Test Plan**:
- Build docs site and verify sidebar navigation
- Verify all links on index page work

**Dependencies**: T-012
**Model**: haiku

---

#### T-014: Update vskill-platform UI links to new doc URLs
**User Story**: US-005 | **Satisfies ACs**: AC-US5-04 | **Status**: [x] completed

**Description**: Update all links in the vskill-platform codebase that point to the extensible skills documentation.

**Implementation Details**:
- Search for `extensible-skills` URL references in vskill-platform src/
- Update links to point to new `extensible-skills-standard` or `extensible-skills-guide` as appropriate
- The skill detail page tooltip link should point to the standard
- The "Learn more" links should point to the guide

**Test Plan**:
- Grep for old URLs and verify zero matches after update
- Verify links render correctly on skill detail page

**Dependencies**: T-012
**Model**: haiku

---

## Phase 4: Verification

#### T-015: End-to-end verification
**User Story**: All | **Satisfies ACs**: All | **Status**: [x] completed

**Description**: Verify the complete feature across both repos.

**Implementation Details**:
- Run full test suite in vskill-platform
- Build docs site and verify no broken links
- Verify `/api/v1/stats` includes extensibility breakdown
- Verify `/skills?ext=true` backward compat
- Verify `/skills?ext=E3` tier filtering
- Verify skill detail page shows tier badge + portability
- Verify seed data has correct tier assignments

**Test Plan**:
- `npm test` in vskill-platform
- `npm run build` in docs-site
- Manual API endpoint verification
- Manual UI spot-check

**Dependencies**: T-008, T-009, T-010, T-011, T-013, T-014
**Model**: opus
