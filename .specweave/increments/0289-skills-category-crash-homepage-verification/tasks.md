# Tasks: Fix skills category crash and improve homepage verification section

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## Phase 1: Fix Skills Page Crash

### US-001: Fix Skills Page Server Component Crash (P1)

#### T-001: Replace onClick handler with anchor tag in skills page

**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05 | **Status**: [x] completed

**Description**: Replace the `<span onClick={...}>` pattern on line 299 of `src/app/skills/page.tsx` with a standard `<a href={...} target="_blank" rel="noopener noreferrer">` element. The `onClick` handler prevents the default link behavior and opens the URL in a new tab -- an `<a>` tag with `target="_blank"` achieves the same result without JavaScript.

**Implementation Details**:
- Remove the `<span>` with `onClick` handler (lines 298-304)
- Replace with `<a href={skill.repoUrl} target="_blank" rel="noopener noreferrer">`
- Keep existing styling (color: #0D9488, cursor: pointer, etc.)
- Add `e.stopPropagation()` equivalent via CSS or by wrapping correctly so the parent `<a>` link doesn't interfere

**Test Plan**:
- **File**: `src/app/skills/__tests__/page.test.tsx` (or verify via build + dev server)
- **Tests**:
  - **TC-001**: Skills page renders without onClick handlers
    - Given the /skills page Server Component
    - When rendered with skills that have repoUrl
    - Then no onClick event handler exists in the output
    - And repo URLs render as `<a>` tags with target="_blank"
  - **TC-002**: Skills page returns HTTP 200
    - Given the dev server is running
    - When GET /skills is requested
    - Then HTTP 200 is returned
  - **TC-003**: Category filter works
    - Given the dev server is running
    - When GET /skills?category=development is requested
    - Then HTTP 200 is returned with filtered skills

**Dependencies**: None
**Status**: [x] Completed

---

## Phase 2: Homepage Verification Section

### US-002: Improve Homepage Verification Section Design (P2)

#### T-002: Redesign homepage verification section

**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04 | **Status**: [x] completed

**Description**: Replace the TreeList-based "How verification works" section in `src/app/page.tsx` (lines 355-363) with a more visually distinct three-tier layout. Each tier (Scanned, Verified, Certified) should have visual differentiation, a brief method description, and the section should link to /trust.

**Implementation Details**:
- Remove TreeList import and usage for the verification section
- Create inline layout with three tier cards/rows
- Use existing CSS variables and terminal aesthetic
- Each tier shows: name, verification method, visual indicator
- Add "View trust details >>" link to /trust page
- Keep existing grid layout with the "Works with" section

**Test Plan**:
- **File**: Visual verification + build test
- **Tests**:
  - **TC-004**: Verification section renders three tiers
    - Given the homepage
    - When rendered
    - Then three verification tiers are visible (Scanned, Verified, Certified)
  - **TC-005**: Trust page link exists
    - Given the homepage verification section
    - When rendered
    - Then a link to /trust is present
  - **TC-006**: Existing design system used
    - Given the verification section markup
    - When inspected
    - Then CSS variables (--font-geist-mono, --text, --border, etc.) are used

**Dependencies**: None
**Status**: [x] Completed

---

## Phase 3: Verification

#### T-003: Build and runtime verification

**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US1-05, AC-US2-04 | **Status**: [x] completed

**Description**: Run `next build`, start dev server, and verify both the /skills page and homepage render correctly.

**Test Plan**:
- **TC-007**: next build succeeds
  - Given the codebase with changes applied
  - When `npx next build` is run
  - Then exit code is 0
- **TC-008**: /skills page loads in dev mode
  - Given the dev server is running
  - When /skills is accessed
  - Then HTTP 200 is returned
- **TC-009**: All existing tests pass
  - Given the codebase with changes applied
  - When `npx vitest run` is executed
  - Then all tests pass (excluding pre-existing failures)

**Dependencies**: T-001, T-002
**Status**: [x] Completed
