# Tasks: Multi-Package-Manager Documentation Update

## Task Notation

- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed

---

## Phase 1: vskill-platform (verified-skill.com)

### T-001: Update Homepage Hero Install Snippet
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] Completed
**Test**: Given the homepage loads -> When a user views the hero section -> Then they see install commands for npm, bun, pnpm, and yarn

**File**: `repositories/anton-abyzov/vskill-platform/src/app/page.tsx`
**Details**:
- Replace the `$ npm install -g vskill` inline code element (lines 164-170) with a compact multi-line code block showing:
  ```
  $ npx vskill ...          # or bunx / pnpx / yarn dlx
  ```
  Or a stacked format showing all four runners.

---

### T-002: Vary AnimatedTerminal Scenarios Across Runners [P]
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] Completed
**Test**: Given the AnimatedTerminal component renders -> When it cycles through scenarios -> Then different package runners are shown (not just npx for all three)

**File**: `repositories/anton-abyzov/vskill-platform/src/app/components/AnimatedTerminal.tsx`
**Details**:
- Scenario "init": keep `npx vskill init`
- Scenario "add": change to `bunx vskill install anthropics/frontend-design`
- Scenario "scan": change to `pnpx vskill scan ./SKILL.md`

---

### T-003: Update Skill Detail Page Install Section [P]
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] Completed
**Test**: Given a user views a skill detail page -> When they see the Install section -> Then all four package runners are shown

**File**: `repositories/anton-abyzov/vskill-platform/src/app/skills/[name]/page.tsx`
**Details**:
- Replace single `installCmd` string with multi-line format showing npx, bunx, pnpx, yarn dlx
- Ensure the TerminalBlock renders all four lines

---

## Phase 2: specweave docs-site (spec-weave.com)

### T-004: Update Docs-Site Homepage CTA Install Snippet [P]
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] Completed
**Test**: Given the docs-site homepage loads -> When a user scrolls to CTA section -> Then they see install commands for all four package managers

**File**: `repositories/anton-abyzov/specweave/docs-site/src/pages/index.tsx`
**Details**:
- Replace `npm install -g specweave && specweave init .` code element with multi-runner format

---

### T-005: Update Quick Start Guide Installation [P]
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [x] Completed
**Test**: Given a user reads the Quick Start guide -> When they reach the Installation section -> Then they see commands for npm, bun, pnpm, and yarn

**File**: `repositories/anton-abyzov/specweave/docs-site/docs/quick-start.md`
**Details**:
- Add bun/pnpm/yarn alternatives alongside `npm install -g specweave`

---

### T-006: Update Installation Guide Methods [P]
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03 | **Status**: [x] Completed
**Test**: Given a user reads the Installation guide -> When they view Method 1 and Method 2 -> Then each method shows all four package manager equivalents

**File**: `repositories/anton-abyzov/specweave/docs-site/docs/guides/getting-started/installation.md`
**Details**:
- Method 1 (Global Install): add `bun add -g`, `pnpm add -g`, `yarn global add` equivalents
- Method 2 (npx): add `bunx`, `pnpx`, `yarn dlx` equivalents
- Update upgrade section similarly
- Update the bottom "Install now" line

---

### T-007: Update Verified Skills Doc CLI Section [P]
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04 | **Status**: [x] Completed
**Test**: Given a user reads verified-skills.md -> When they see the vskill CLI section -> Then all four runners are shown

**File**: `repositories/anton-abyzov/specweave/docs-site/docs/skills/verified/verified-skills.md`
**Details**:
- Update the `### npx vskill CLI` section title and code blocks to show bunx/pnpx/yarn dlx alternatives

---

### T-008: Update Skills Index Page Reference [P]
**User Story**: US-002 | **Satisfies ACs**: AC-US2-05 | **Status**: [x] Completed
**Test**: Given a user reads skills/index.md -> When they see the npx vskill reference -> Then alternative runners are mentioned

**File**: `repositories/anton-abyzov/specweave/docs-site/docs/skills/index.md`
**Details**:
- Update the `npx vskill` reference to mention bunx/pnpx/yarn dlx

---

## Phase 3: vskill CLI README

### T-009: Update vskill README Top Code Block [P]
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [x] Completed
**Test**: Given a user views the vskill README on GitHub -> When they see the top code block -> Then they see npx and alternative runners

**File**: `repositories/anton-abyzov/vskill/README.md`
**Details**:
- Add comment-annotated alternatives (bunx, pnpx, yarn dlx) to the top three example commands

---

### T-010: Update vskill README Commands Section [P]
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02 | **Status**: [x] Completed
**Test**: Given a user reads the Commands section of vskill README -> When they see the command examples -> Then a note about alternative runners is included

**File**: `repositories/anton-abyzov/vskill/README.md`
**Details**:
- Add a note below the Commands code block: "Replace `vskill` with `npx vskill`, `bunx vskill`, `pnpx vskill`, or `yarn dlx vskill` if not installed globally."

---

## Phase 4: Verification

### T-011: Final Review of All Changes
**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: All | **Status**: [x] Completed
**Test**: Given all changes are made -> When reviewing all modified files -> Then no npm-only snippets remain in user-facing pages and format is consistent across repos

**Details**:
- Grep for remaining npm-only install patterns across all three repos
- Verify consistent format across all snippets
