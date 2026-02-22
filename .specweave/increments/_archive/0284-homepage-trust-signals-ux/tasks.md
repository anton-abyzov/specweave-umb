# Tasks: Homepage trust signals and UX clarity improvements

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## Phase 1: Homepage Changes

### US-001: Scanner Attribution on Security Banner

#### T-001: Add scanner attribution to security callout banner

**Description**: Add "Powered by vskill scanner -- 52 patterns" attribution text inside the security callout `<a>` element on the homepage.

**References**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04

**Implementation Details**:
- In `src/app/page.tsx`, inside the security callout `<a>` element
- Added inline attribution after the Snyk source reference: "Powered by vskill scanner -- 52 patterns"
- Style: inherits `fontSize: "0.625rem"` from parent span, uses `fontFamily: mono, color: "var(--text-faint)"`
- Text: "Powered by vskill scanner" (no Snyk reference for scanning attribution)
- Pattern count already correct at 52 (updated from 38 in a prior increment)

**Test Plan**:
- **TC-001**: Security banner scanner attribution
  - Given homepage is loaded
  - When viewing the security callout banner
  - Then "Powered by vskill scanner" text is visible
  - And pattern count shows "52"
  - And Snyk reference is only for source citation, not scanner attribution

**Dependencies**: None
**Status**: [x] Completed

---

### US-002: Disambiguate Verified Count

#### T-002: Change hero headline text

**Description**: Replace "{totalSkills} verified skills" with "{totalSkills} security-scanned skills" to avoid terminology collision with the VERIFIED tier badge.

**References**: AC-US2-01

**Implementation Details**:
- In `src/app/page.tsx`, line 120
- Already changed to `{totalSkills} security-scanned skills` in a prior update

**Test Plan**:
- **TC-002**: Hero headline text
  - Given homepage is loaded
  - When viewing the hero section
  - Then headline says "{N} security-scanned skills"
  - And the word "verified" does NOT appear in the hero headline

**Dependencies**: None
**Status**: [x] Completed

---

#### T-003: Clarify inline stats tier labels [P]

**Description**: Make inline stat labels unambiguous by using tier badge colors and explicit phrasing.

**References**: AC-US2-02

**Implementation Details**:
- In `src/app/page.tsx`, lines 190-195
- Stats already show "certified" and "verified" with different colors (amber and green)
- No change needed since hero (T-002) no longer uses "verified" as total descriptor
- The tier labels are now unambiguous in context

**Test Plan**:
- **TC-003**: Inline stats clarity
  - Given homepage is loaded
  - When viewing the stats bar
  - Then "certified" count appears with amber color
  - And "verified" count appears with green color
  - And these clearly refer to tier counts, not the total

**Dependencies**: T-002
**Status**: [x] Completed

---

## Phase 2: Skill Detail Page

### US-003: Skill Detail Page Usability

#### T-004: Add NPM downloads stat card [P]

**Description**: Add an NPM downloads StatCard to the Popularity section on the skill detail page. Only render when `npmDownloads > 0`.

**References**: AC-US3-01, AC-US3-04

**Implementation Details**:
- In `src/app/skills/[name]/page.tsx`, after the Installs StatCard
- Already implemented: `{skill.npmDownloads > 0 && <StatCard value={formatNumber(skill.npmDownloads)} label="NPM" />}`
- StatCard component already exists in the same file
- Conditional rendering ensures zero-value stats are hidden

**Test Plan**:
- **TC-004**: NPM downloads stat card
  - Given a skill with npmDownloads > 0
  - When viewing the skill detail page
  - Then an "NPM" stat card appears in the Popularity section
  - And the value is formatted correctly (e.g., "12.5k")

- **TC-005**: NPM downloads hidden when zero
  - Given a skill with npmDownloads = 0
  - When viewing the skill detail page
  - Then no "NPM" stat card appears

**Dependencies**: None
**Status**: [x] Completed

---

#### T-005: Add "Last Updated" meta row [P]

**Description**: Add a "Last Updated" row to the meta section showing `skill.updatedAt` formatted as a readable date.

**References**: AC-US3-02

**Implementation Details**:
- In `src/app/skills/[name]/page.tsx`, in the meta section after the Repository row
- Already implemented: `{skill.updatedAt && <MetaRow label="Last Updated" value={formatDate(skill.updatedAt)} />}`
- `formatDate` function already exists in the file
- Conditionally rendered only when `updatedAt` is present

**Test Plan**:
- **TC-006**: Last Updated meta row
  - Given a skill detail page
  - When viewing the meta section
  - Then "Last Updated" row appears with a formatted date

**Dependencies**: None
**Status**: [x] Completed

---

#### T-006: Fix pattern count in security section

**Description**: Normalize pattern count references across the codebase. The count was previously 37, then updated to 38, and is now 52 (matching current `patterns.ts`).

**References**: AC-US3-03

**Implementation Details**:
- All UI-facing pattern counts already show 52:
  - `src/app/page.tsx`: "52 vulnerability patterns scanned" and "52 patterns"
  - `src/app/skills/[name]/page.tsx`: "52 checks"
  - `src/app/skills/[name]/security/page.tsx`: "52 built-in patterns" and "52 checks"
- Updated test mock data from `patternsChecked: 37` to `patternsChecked: 52` in:
  - `src/lib/queue/__tests__/process-submission.test.ts` (4 occurrences)
  - `src/app/api/v1/admin/scan-external/__tests__/route.test.ts` (3 occurrences)

**Test Plan**:
- **TC-007**: Pattern count consistency
  - Given any page referencing pattern counts
  - When viewing the security-related text
  - Then the pattern count shows "52" everywhere

**Dependencies**: None
**Status**: [x] Completed

---

## Phase 3: Verification

- [x] [T-007] haiku - Visual verification of all changes across homepage, skill detail, and security pages
- [x] [T-008] haiku - Verify no "37" pattern count references remain in the codebase
