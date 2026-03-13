# Tasks: specweave get — Bulk Cloning

## Summary

| Category | Count |
|----------|-------|
| Total tasks | 10 |
| Completed | 10 |
| Remaining | 0 |

---

### T-001: Export fetchGitHubRepos (RED prerequisite)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed
**Test**: Given `import { fetchGitHubRepos } from '../init/github-repo-cloning.js'` → When compiled → Then no TS error
**File**: `src/cli/helpers/init/github-repo-cloning.ts`

---

### T-002: bulk-get.ts — unit tests (RED)
**User Story**: US-001–US-004 | **Satisfies ACs**: AC-US1-01, AC-US1-05, AC-US2-01, AC-US2-02, AC-US3-01–03, AC-US4-01–03 | **Status**: [x] completed
**Test**: Given various source strings + options → When `parseBulkSource()` runs → Then correct org/pattern or null returned; Given mocked fetchGitHubRepos → When `buildBulkRepoList()` runs → Then correct filtered repo array; Given env/cli states → When `getAuthToken()` runs → Then token or error
**File**: `tests/unit/cli/helpers/get/bulk-get.test.ts`

---

### T-003: bulk-get.ts — implementation (GREEN)
**User Story**: US-001–US-004 | **Satisfies ACs**: AC-US1-01, AC-US1-05, AC-US2-01, AC-US2-02, AC-US3-01–03, AC-US4-01–03 | **Status**: [x] completed
**Test**: All T-002 tests pass
**File**: `src/cli/helpers/get/bulk-get.ts`

---

### T-004: get command bulk path — unit tests (RED)
**User Story**: US-001, US-005 | **Satisfies ACs**: AC-US1-03, AC-US1-04, AC-US5-01, AC-US5-02 | **Status**: [x] completed
**Test**: Given mocked parseBulkSource returning bulk result → When `getCommand()` runs → Then `launchCloneJob` called, not `cloneRepo`; Given null from parseBulkSource → Then existing single-repo path runs unchanged
**File**: `tests/unit/cli/commands/get-bulk.test.ts`

---

### T-005: get.ts — implement bulk path (GREEN)
**User Story**: US-001, US-005 | **Satisfies ACs**: AC-US1-03, AC-US1-04, AC-US5-01, AC-US5-02 | **Status**: [x] completed
**Test**: All T-004 tests pass
**File**: `src/cli/commands/get.ts`

---

### T-006: bin/specweave.js — add bulk CLI options
**User Story**: US-002, US-003 | **Satisfies ACs**: AC-US2-01, AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x] completed
**Test**: `specweave get --help` shows `--all`, `--pattern`, `--limit`, `--no-archived`, `--no-forks`
**File**: `bin/specweave.js`

---

### T-007: Update sw:get SKILL.md with bulk examples
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test**: SKILL.md includes bulk trigger examples and commands
**File**: `plugins/specweave/skills/get/SKILL.md`

---

### T-008: npm run build
**User Story**: all | **Satisfies ACs**: all | **Status**: [x] completed
**Test**: `npm run build` exits 0, no TS errors
**File**: `dist/`

---

### T-009: npx vitest run — all tests pass
**User Story**: all | **Satisfies ACs**: all | **Status**: [x] completed
**Test**: All existing tests + new tests pass, no regressions
**File**: test suite

---

### T-010: npm version patch + publish + git push
**User Story**: all | **Satisfies ACs**: all | **Status**: [x] completed
**Test**: `npm show specweave version` shows new patch version
**File**: package.json, npm registry
