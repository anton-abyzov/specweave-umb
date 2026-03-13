# Tasks: specweave get CLI command

## Summary

| Category | Count |
|----------|-------|
| Total tasks | 13 |
| Completed | 12 |
| Remaining | 1 |

---

### T-001: Source Parser — unit tests (RED)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05 | **Status**: [x] completed
**Test**: Given `owner/repo`, HTTPS, SSH, local path, and non-GitHub URL inputs → When `parseSource()` runs → Then correct `ParsedSource` discriminated union is returned for each case
**File**: `tests/unit/cli/helpers/get/source-parser.test.ts`

---

### T-002: Source Parser — implementation (GREEN)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05 | **Status**: [x] completed
**Test**: All T-001 tests pass (17/17)
**File**: `src/cli/helpers/get/source-parser.ts`

Fixes applied:
- `os.homedir()` instead of `process.env.HOME` for tilde expansion
- Greedy regex fixed: `([^/?#]+?)` prevents nested URL subpaths bleeding into repo name
- Shorthand check moved before `fs.existsSync` fallback to prevent `owner/repo` misidentified as local

---

### T-003: Clone Helper — unit tests (RED)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03, AC-US2-04, AC-US2-05 | **Status**: [x] completed
**Test**: Given mocked `execFileNoThrow` → When `cloneRepo()` is called with existing dir / new dir / auth failure / branch option → Then correct `CloneResult` is returned and git args are correct
**File**: `tests/unit/cli/helpers/get/clone-repo.test.ts`

---

### T-004: Clone Helper — implementation (GREEN)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03, AC-US2-04, AC-US2-05 | **Status**: [x] completed
**Test**: All T-003 tests pass (11/11)
**File**: `src/cli/helpers/get/clone-repo.ts`

Fixes applied:
- Early check: targetDir exists but no `.git` → clear error instead of obscure clone failure
- `mkdir` wrapped in try/catch with user-friendly error message

---

### T-005: Register Helper — unit tests (RED)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05 | **Status**: [x] completed
**Test**: Given mocked `persistUmbrellaConfig` and fs → When `registerRepo()` is called → Then config.json gets correct entry, prefix defaults to 3-char uppercase, role is set, duplicate is detected
**File**: `tests/unit/cli/helpers/get/register-repo.test.ts`

---

### T-006: Register Helper — implementation (GREEN)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05 | **Status**: [x] completed
**Test**: All T-005 tests pass (7/7)
**File**: `src/cli/helpers/get/register-repo.ts`

---

### T-007: Get Command — unit tests (RED)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05 | **Status**: [x] completed
**Test**: Given mocked helpers + config → When `getCommand()` is called with various option combinations → Then correct helpers are called in order, `--no-init` skips init, `--yes` skips prompts, local path skips clone
**File**: `tests/unit/cli/commands/get.test.ts`

---

### T-008: Get Command — implementation (GREEN)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05 | **Status**: [x] completed
**Test**: All T-007 tests pass (11/11)
**File**: `src/cli/commands/get.ts`

Fixes applied:
- `return` after every `process.exit(1)` to prevent execution continuing in mocked environments
- Empty owner fallback: `_unknown` dir for generic git URLs with no detected org
- Local path `relPath` normalized with `.replace(/\\/g, '/')` for Windows parity

---

### T-009: Register command in bin/specweave.js
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01 | **Status**: [x] completed
**Test**: `specweave get --help` shows command with all options ✓
**File**: `bin/specweave.js`

---

### T-010: sw:get Skill — SKILL.md
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03 | **Status**: [x] completed
**Test**: SKILL.md has triggers: "add repo", "clone repo", "add github repo to umbrella", etc. Negative: "add a feature", "add a task", etc.
**File**: `plugins/specweave/skills/get/SKILL.md`

---

### T-011: Run full test suite
**User Story**: US-001–US-004 | **Satisfies ACs**: all | **Status**: [x] completed
**Test**: 46 new tests pass, no regressions in full suite
**File**: test suite

---

### T-012: Build and verify CLI
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01 | **Status**: [x] completed
**Test**: `npm run build` succeeds → `specweave get --help` shows command ✓
**File**: built dist/

---

### T-013: Refactor pass (/simplify)
**User Story**: US-001–US-005 | **Satisfies ACs**: all | **Status**: [ ] pending
**Test**: `/simplify` review — no duplication, no dead code, all edge cases handled
**Notes**: Run after all tests pass; clean up any temporary scaffolding
