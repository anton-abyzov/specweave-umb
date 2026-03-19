---
increment: 0582-fix-duplicate-increment-creation
title: "Fix Duplicate Increment Creation Bugs"
status: active
---

# Tasks: Fix Duplicate Increment Creation Bugs

## US-003: ID Scanner Includes _backlog/ (AD-1)

### T-001: [RED] Write failing tests for getDirsToScan() and _backlog inclusion
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Status**: [x] completed
**Test**: Given `RECOGNIZED_LIFECYCLE_FOLDERS` contains `_backlog` and an increment in `_backlog/`, when `getDirsToScan()` is called, then it returns entries for all lifecycle folders including `_backlog`, and `getNextIncrementNumber()` returns an ID greater than the backlog increment

### T-002: [GREEN] Implement getDirsToScan() private static helper
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02
**Status**: [x] completed
**Test**: Given `RECOGNIZED_LIFECYCLE_FOLDERS = ['_archive', '_abandoned', '_paused', '_backlog']`, when `getDirsToScan(incrementsDir)` is called, then the returned array includes `{ path: incrementsDir, label: 'active' }` plus one entry per lifecycle folder

### T-003: [GREEN] Refactor 4 callers to use getDirsToScan()
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-03
**Status**: [x] completed
**Test**: Given increments 0001-0003 active and 0004 in `_backlog/`, when `getNextIncrementNumber()` is called after refactoring all 4 callers (`incrementNumberExists`, `getAllIncrementNumbers`, `scanAllIncrementDirectories`, `findDuplicates`), then the output is `0005`

---

## US-006: Re-enable Increment Name Duplicate Guard (AD-6)

### T-004: [RED] Write failing tests for findNameDuplicates()
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03
**Status**: [x] completed
**Test**: Given increment `0010-user-auth` exists as active, when `findNameDuplicates('user-auth', projectRoot)` is called, then it returns `['0010-user-auth']`; given `0010-user-auth` is in `_archive/`, then it returns `[]`

### T-005: [GREEN] Implement findNameDuplicates() static method on IncrementNumberManager
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-03
**Status**: [x] completed
**Test**: Given active + `_backlog` directories scanned (archived/abandoned excluded by default), when `findNameDuplicates(name, projectRoot)` runs, then only active and `_backlog` slugs are checked for name collision

### T-006: [GREEN] Integrate findNameDuplicates warning into template-creator.ts
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02
**Status**: [x] completed
**Test**: Given `createIncrementTemplates()` is called with a name matching an existing active increment, when the function executes, then `console.warn()` is emitted with the duplicate list and the operation still proceeds (non-blocking)

---

## US-001: next-id Respects Explicit Project Root (AD-2)

### T-007: [RED] Write failing tests for --project-root option on next-id
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Status**: [x] completed
**Test**: Given a project at `/tmp/project-a` with increments 0001-0003 and cwd at `/tmp/project-b`, when `next-id --project-root /tmp/project-a` is called, then the output is `0004`; when `--project-root` points to a dir without `.specweave/config.json`, then exit code is 1

### T-008: [GREEN] Implement --project-root option in next-id CLI command
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Status**: [x] completed
**Test**: Given `--project-root` is provided with a valid SpecWeave project path, when `next-id` runs, then `resolveEffectiveRoot` is bypassed and the provided path is used directly; when `--project-root` is absent, existing cwd-based behavior is unchanged

---

## US-002: Init Creates config.json Before increments/ (AD-3)

### T-009: [RED] Write failing integration test for init config.json ordering
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] completed
**Test**: Given a fresh directory with a sibling project at `../other-project` having increments 0001-0005, when `specweave init --quick` runs in the current directory, then `.specweave/config.json` exists on disk before `.specweave/increments/` is created, and `next-id` returns `0001`

### T-010: [GREEN] Fix init.ts to write minimal config.json before createDirectoryStructure()
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] completed
**Test**: Given `specweave init` is interrupted after config.json is written but before increments/ is created, when `specweave init` is re-run, then it detects the partial init and completes without error (reinit safety)

---

## US-004: Atomic ID Reservation (AD-4)

### T-011: [RED] Write failing tests for --auto-id atomic reservation and concurrency
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03
**Status**: [x] completed
**Test**: Given two concurrent `create-increment --auto-id` calls, when both execute simultaneously, then each receives a unique ID with no collision; given `mkdirSync` throws `EEXIST`, when retrying up to 10 times, then a fresh unique ID is generated

### T-012: [GREEN] Add --auto-id and --name options to create-increment CLI
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02, AC-US4-03
**Status**: [x] completed
**Test**: Given `create-increment --auto-id --name feature --title "Feature"` is called without `--id`, when the command runs, then it internally calls `getNextIncrementNumber()` and creates the directory in a single atomic operation

### T-013: [GREEN] Implement atomic creation path with retry logic in template-creator.ts
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02
**Status**: [x] completed
**Test**: Given three parallel `create-increment --auto-id` calls with max 10 retry attempts, when all three race to claim the next ID, then all three succeed with sequential unique IDs and no `EEXIST` propagates to the caller

---

## US-005: Portable Increment SKILL.md (AD-5)

### T-014: [GREEN] Update SKILL.md Step 4 for adapter portability
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03
**Status**: [x] completed
**Test**: Given the updated SKILL.md, when parsed by a non-Claude AI tool, then the default path contains only `specweave create-increment --auto-id` CLI commands with no `TeamCreate`, `Agent()`, `SendMessage`, or `EnterPlanMode` references; Claude Code-specific delegation is in a clearly demarcated optional section
