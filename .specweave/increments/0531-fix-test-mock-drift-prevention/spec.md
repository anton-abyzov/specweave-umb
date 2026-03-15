---
increment: 0531-fix-test-mock-drift-prevention
title: Fix test mock drift with shared npm constants
type: bug
priority: P1
status: completed
created: 2026-03-15T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Fix Test Mock Drift with Shared npm Constants

## Problem Statement

PR #1572 auto-fix bot missed TC-UH-02 because the test mock strings for `installation-health-checker` lack the `--registry https://registry.npmjs.org` flag that production code includes. The root cause is that npm command strings are hardcoded independently in both production code and test mocks, so changes to one silently leave the other stale. This fragile pattern affects 15+ test files across the codebase.

## Goals

- Fix TC-UH-02 by correcting the mock command strings to include `--registry` flag
- Eliminate the class of bugs where test mocks drift from production command strings
- Follow existing patterns (`src/utils/pricing-constants.ts`) for shared constants

## User Stories

### US-001: Fix TC-UH-02 Registry Flag in Test Mocks (P0)
**Project**: specweave

**As a** SpecWeave developer
**I want** TC-UH-02 test mocks to include the `--registry https://registry.npmjs.org` flag
**So that** the test accurately validates the production npm install command

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given the `installation-health-checker.test.ts` file, when TC-UH-02 constructs a mock npm install command, then the command string includes `--registry https://registry.npmjs.org`
- [x] **AC-US1-02**: Given the corrected TC-UH-02 test, when the test suite runs, then TC-UH-02 passes without modifying production behavior

---

### US-002: Shared npm Constants Module (P0)
**Project**: specweave

**As a** SpecWeave developer
**I want** a shared `src/constants/npm-constants.ts` module exporting the registry URL and command-building helpers
**So that** production code and test mocks reference a single source of truth

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given the new module `src/constants/npm-constants.ts`, when imported, then it exports `NPM_REGISTRY_URL` with value `https://registry.npmjs.org`
- [x] **AC-US2-02**: Given the new module, when imported, then it exports a `npmRegistryFlag()` helper that returns `--registry https://registry.npmjs.org`
- [x] **AC-US2-03**: Given the module file, when inspected, then its structure follows the same pattern as `src/utils/pricing-constants.ts`

---

### US-003: Migrate Production Code to Shared Constants (P0)
**Project**: specweave

**As a** SpecWeave developer
**I want** all production files that hardcode the npm registry URL to import from `npm-constants.ts`
**So that** future registry URL changes propagate automatically

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given `src/core/doctor/checkers/installation-health-checker.ts`, when the npm install command is built, then it uses the imported constant instead of a hardcoded registry string
- [x] **AC-US3-02**: Given `src/cli/commands/update.ts`, when the npm update command is built, then it uses the imported constant
- [x] **AC-US3-03**: Given `src/utils/docs-preview/package-installer.ts`, when the npm install command is built, then it uses the imported constant
- [x] **AC-US3-04**: Given `src/core/fabric/discovery/npm-provider.ts`, when the registry URL is referenced, then it uses the imported constant
- [x] **AC-US3-05**: Given all 4 production files after migration, when the test suite runs, then all existing tests pass with no behavior change

---

### US-004: Migrate Test Mocks to Shared Constants (P1)
**Project**: specweave

**As a** SpecWeave developer
**I want** test files that mock npm commands to import command strings from `npm-constants.ts`
**So that** test mocks cannot silently drift from production code

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given `installation-health-checker.test.ts`, when mock command strings are constructed, then they import and use constants from `npm-constants.ts`
- [x] **AC-US4-02**: Given `update.test.ts`, when mock command strings are constructed, then they import and use constants from `npm-constants.ts`
- [x] **AC-US4-03**: Given `update-robustness.test.ts`, when mock command strings are constructed, then they import and use constants from `npm-constants.ts`
- [x] **AC-US4-04**: Given all migrated test files, when the full test suite runs, then all tests pass

## Out of Scope

- Migrating the remaining 12+ test files that use similar hardcoded patterns (future increment)
- Adding a CI lint rule to detect new hardcoded registry URLs (future increment)
- Changing the actual registry URL value
- Refactoring other hardcoded command strings beyond npm registry

## Non-Functional Requirements

- **Compatibility**: Module must use ESM with `.js` import extensions per project convention (`--moduleResolution nodenext`)
- **Maintainability**: Single constant definition referenced everywhere, zero duplication of the registry URL string

## Edge Cases

- Import path extensions: All imports must use `.js` extension for ESM compatibility
- Re-export patterns: If any barrel exports exist, ensure the new module integrates correctly

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| Missed hardcoded occurrence | 0.3 | 3 | 0.9 | grep codebase for `registry.npmjs.org` before marking complete |
| Import path wrong for ESM | 0.2 | 2 | 0.4 | Follow existing `.js` extension pattern, run tests |

## Technical Notes

- Target repo: `repositories/anton-abyzov/specweave/`
- Key production files: `installation-health-checker.ts` (line 527), `update.ts` (line 843), `package-installer.ts` (line 66), `npm-provider.ts` (line 11)
- Key test files: `installation-health-checker.test.ts`, `update.test.ts`, `update-robustness.test.ts`
- Existing pattern to follow: `src/utils/pricing-constants.ts`
- TDD mode is active: write tests for the new constants module first

## Success Metrics

- TC-UH-02 passes with correct registry flag assertion
- Zero hardcoded `registry.npmjs.org` strings remain in the 4 production files and 3 test files
- Full test suite passes with no regressions
