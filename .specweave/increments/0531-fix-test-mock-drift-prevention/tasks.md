# Tasks: Fix Test Mock Drift with Shared npm Constants

## Task Notation

- `[ ]`: Not started
- `[x]`: Completed

---

## US-002: Shared npm Constants Module

### T-001: Write failing tests for npm-constants module (TDD Red)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] Completed
**Test**: Given `src/utils/npm-constants.ts` does not yet exist → When the test file `tests/unit/utils/npm-constants.test.ts` is run → Then it fails with "cannot find module" or missing-export errors for `NPM_REGISTRY_URL` and `npmRegistryFlag()`

---

### T-002: Create npm-constants module (TDD Green)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] Completed
**Test**: Given `src/utils/npm-constants.ts` exports `NPM_REGISTRY_URL` and `npmRegistryFlag()` following the `pricing-constants.ts` pattern → When `tests/unit/utils/npm-constants.test.ts` runs → Then `NPM_REGISTRY_URL === "https://registry.npmjs.org"` and `npmRegistryFlag() === "--registry https://registry.npmjs.org"` both pass

---

## US-001: Fix TC-UH-02 Registry Flag in Test Mocks

### T-003: Fix mock command string in installation-health-checker.test.ts (TC-UH-02)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02
**Status**: [x] Completed
**Test**: Given TC-UH-02 in `tests/unit/core/doctor/checkers/installation-health-checker.test.ts` → When the mock npm install command is corrected to include `--registry https://registry.npmjs.org` → Then TC-UH-02 passes and no other test in that file regresses

---

## US-003: Migrate Production Code to Shared Constants

### T-004: Migrate installation-health-checker.ts to npm-constants
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-05
**Status**: [x] Completed
**Test**: Given `src/core/doctor/checkers/installation-health-checker.ts` imports `npmRegistryFlag` from `../../utils/npm-constants.js` and line 527 uses it → When the test suite runs → Then all installation-health-checker tests pass and no literal `registry.npmjs.org` string remains in that production file

---

### T-005: Migrate update.ts to npm-constants
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-05
**Status**: [x] Completed
**Test**: Given `src/cli/commands/update.ts` imports `npmRegistryFlag` from `../../utils/npm-constants.js` and line 843 uses it → When the test suite runs → Then all update command tests pass and no literal `registry.npmjs.org` string remains in that file

---

### T-006: Migrate package-installer.ts to npm-constants
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03, AC-US3-05
**Status**: [x] Completed
**Test**: Given `src/utils/docs-preview/package-installer.ts` imports `NPM_REGISTRY_URL` from `../npm-constants.js` and line 66 uses `` `--registry=${NPM_REGISTRY_URL}` `` → When the test suite runs → Then all package-installer tests pass and no literal `registry.npmjs.org` string remains in that file

---

### T-007: Migrate npm-provider.ts to npm-constants
**User Story**: US-003 | **Satisfies ACs**: AC-US3-04, AC-US3-05
**Status**: [x] Completed
**Test**: Given `src/core/fabric/discovery/npm-provider.ts` imports `NPM_REGISTRY_URL` from `npm-constants.js` and line 11 constructs the search URL using the constant → When the test suite runs → Then all npm-provider tests pass and no literal `registry.npmjs.org` string remains in that file

---

## US-004: Migrate Test Mocks to Shared Constants

### T-008: Migrate installation-health-checker.test.ts mocks to npm-constants
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-04
**Status**: [x] Completed
**Test**: Given `tests/unit/core/doctor/checkers/installation-health-checker.test.ts` imports `npmRegistryFlag` from `npm-constants.js` and uses it in mock command construction → When `grep "registry.npmjs.org"` is run on that file → Then zero literal matches are found and all tests in the file pass

---

### T-009: Migrate update.test.ts mocks to npm-constants
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02, AC-US4-04
**Status**: [x] Completed
**Test**: Given `tests/unit/cli/commands/update.test.ts` imports `npmRegistryFlag` from `npm-constants.js` and uses it for mock and expect strings → When `grep "registry.npmjs.org"` is run on that file → Then zero literal matches are found and all tests in the file pass

---

### T-010: Migrate update-robustness.test.ts mocks to npm-constants
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03, AC-US4-04
**Status**: [x] Completed
**Test**: Given `tests/unit/cli/commands/update-robustness.test.ts` imports `npmRegistryFlag` from `npm-constants.js` and uses it in assertion strings → When `grep "registry.npmjs.org"` is run on that file → Then zero literal matches are found and all tests in the file pass

---

### T-011: Final completeness check and full suite regression
**User Story**: US-003, US-004 | **Satisfies ACs**: AC-US3-05, AC-US4-04
**Status**: [x] Completed
**Test**: Given all 4 production files and 3 test files have been migrated → When `grep -r "registry.npmjs.org"` is run across all 7 migrated files → Then it returns zero matches and `npx vitest run` exits with no failures
