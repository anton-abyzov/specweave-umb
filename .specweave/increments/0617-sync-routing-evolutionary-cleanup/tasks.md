---
increment: 0617-sync-routing-evolutionary-cleanup
title: "Sync Routing Evolutionary Cleanup"
generated: 2026-03-19
test_mode: TDD
coverage_target: 90
---

# Tasks: Sync Routing Evolutionary Cleanup

## Implementation Order: C1 → C3 → C4 → C2

---

## US-SPE-001: Auto-Populate Project Field During Increment Creation

### T-001: [TDD RED] Write failing tests for `detectProjectFromCwd` utility
**User Story**: US-SPE-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Status**: [x] completed
**Test**: Given a test suite with no implementation, when `detectProjectFromCwd` is imported and called with umbrella config + cwd variants, then ALL assertions fail (red phase confirmed)
- Test: cwd inside child repo path → returns childRepo.id
- Test: cwd at umbrella root → returns umbrella.projectName
- Test: umbrella.enabled false/absent → returns undefined
- Test: cwd inside disabled child repo → returns childRepo.id (disabled ≠ no-id)
- Test: deeply nested cwd (e.g., `.../specweave/src/sync/`) → still matches correct childRepo

### T-002: [TDD GREEN] Implement `detectProjectFromCwd` in `template-creator.ts`
**User Story**: US-SPE-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Status**: [x] completed
**Test**: Given the failing tests from T-001, when `detectProjectFromCwd(config, cwd)` is added to `template-creator.ts` using `path.resolve` for cross-platform comparison and longest-prefix matching for overlapping repos, then all T-001 tests pass (green phase)

### T-003: [TDD RED] Write failing tests for `project` field injection into metadata.json
**User Story**: US-SPE-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02
**Status**: [x] completed
**Test**: Given `createIncrementTemplates()` called with an umbrella config and cwd inside a child repo, when the resulting `metadata.json` content is inspected, then it contains `"project": "<childRepo.id>"` — test fails before implementation

### T-004: [TDD GREEN] Inject `project` field in `createIncrementTemplates()`
**User Story**: US-SPE-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Status**: [x] completed
**Test**: Given the failing tests from T-003, when `template-creator.ts` is updated to call `detectProjectFromCwd` after building the metadata object (before `fs.writeFileSync`) and conditionally sets `metadata.project`, then all T-003 tests pass — and increments created without umbrella config have no `project` field

### T-005: [TDD GREEN] Integration test — Phase 1 resolver activates with auto-set project
**User Story**: US-SPE-001 | **Satisfies ACs**: AC-US1-05
**Status**: [x] completed
**Test**: Given an increment with `metadata.json.project = "specweave"` and a config with `childRepos[].id = "specweave"`, when `resolveSyncTarget("specweave", config)` is called, then it returns the child repo's specific sync targets (NOT the global fallback) — verified by checking resolver Phase 1 match path in unit test

---

## US-SPE-003: Auto-Prefix User Story IDs

### T-006: [TDD RED] Write failing tests for prefixed US-ID generation
**User Story**: US-SPE-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Status**: [x] completed
**Test**: Given the current `us-id-generator.ts` with no prefix support, when tests assert `formatUsId(1, 'internal', 'SPE')` returns `"US-SPE-001"`, `formatUsId(1, 'internal', undefined)` returns `"US-001"`, and `getNextUsId(['US-SPE-001', 'US-SPE-002'], 'internal', 'SPE')` returns `"US-SPE-003"`, then ALL assertions fail (red phase)

### T-007: [TDD GREEN] Extend `formatUsId`, `parseUsId`, `getNextUsId` for prefix support
**User Story**: US-SPE-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Status**: [x] completed
**Test**: Given the failing tests from T-006, when `us-id-generator.ts` is updated with prefix-aware `formatUsId(num, origin, prefix?)`, updated `parseUsId` regex `/^US-(?:([A-Za-z]{2,6})-)?(\d+)(E)?$/`, and `getNextUsId` accepting optional prefix with prefix-filtered counting, then all T-006 tests pass — AND existing tests with old `US-001` format still pass (no regression)

### T-008: [TDD RED] Write failing tests for prefixed story header parsing in `spec-parser.ts`
**User Story**: US-SPE-003 | **Satisfies ACs**: AC-US3-01, AC-US3-05
**Status**: [x] completed
**Test**: Given a spec.md string with headers `### US-SPE-001: My Story` and `### US-001: Old Story`, when `spec-parser.ts` parses the file, then it correctly extracts BOTH story IDs — test fails before regex update

### T-009: [TDD GREEN] Update `spec-parser.ts` regex to parse prefixed story headers
**User Story**: US-SPE-003 | **Satisfies ACs**: AC-US3-01, AC-US3-05
**Status**: [x] completed
**Test**: Given the failing tests from T-008, when the story-header regex in `spec-parser.ts:217` is updated from `/^###?\s+(US-\d{3,}E?):\s*(.+)$/` to `/^###?\s+(US-(?:[A-Za-z]{2,6}-)?\d{3,}E?):\s*(.+)$/`, then both prefixed and non-prefixed story headers parse correctly

### T-010: [TDD RED+GREEN] Integration test — story-router prefix extraction + Phase 3 fallback
**User Story**: US-SPE-003 | **Satisfies ACs**: AC-US3-04, AC-US3-05
**Status**: [x] completed
**Test**: Given `story-router.ts` receives `US-SPE-001`, when extracting the prefix, then it matches `childRepos[].prefix === "SPE"` and returns correct repo routing; AND given old-format `US-001`, when processed, then Phase 3 global fallback handles it without error (no regression)

---

## US-SPE-004: Add Project Validation to `sw:validate`

### T-011: [TDD RED] Write failing tests for `METADATA_MISSING_PROJECT` warning
**User Story**: US-SPE-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02
**Status**: [x] completed
**Test**: Given `three-file-validator.ts` with no project field checks, when tests assert:
- umbrella + childRepos.length > 1 + no `metadata.project` → emits WARNING with code `METADATA_MISSING_PROJECT`
- no umbrella (single repo) + no `metadata.project` → emits NO warning,
then BOTH assertions fail (red phase)

### T-012: [TDD GREEN] Implement `METADATA_MISSING_PROJECT` validation
**User Story**: US-SPE-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02
**Status**: [x] completed
**Test**: Given the failing tests from T-011, when `three-file-validator.ts` is updated with `METADATA_MISSING_PROJECT` added to `ValidationErrorCode` and a rule that fires only when `umbrella.enabled && childRepos.length > 1 && !metadata.project`, then all T-011 tests pass — single-repo setups produce no warning

### T-013: [TDD RED+GREEN] Implement `METADATA_UNKNOWN_PROJECT` validation
**User Story**: US-SPE-004 | **Satisfies ACs**: AC-US4-03
**Status**: [x] completed
**Test**: Given an increment with `metadata.project = "unknown-repo"` and a config where no childRepo.id or umbrella.projectName matches, when `sw:validate` runs, then it emits a WARNING with code `METADATA_UNKNOWN_PROJECT` and message including the unrecognized project name — write test first (red), then implement (green) in same task

---

## US-SPE-002: Simplify Sync-Setup Wizard

### T-014: [TDD RED] Write failing tests for umbrella auto-detection guard in wizard
**User Story**: US-SPE-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02
**Status**: [x] completed
**Test**: Given the current wizard with no umbrella guard, when tests assert:
- `promptStructure()` with `umbrella.enabled: true` → does NOT call `getArchitecturePrompt()` and auto-selects `'github-parent'`
- `promptStructure()` without umbrella config → DOES call `getArchitecturePrompt()`,
then BOTH assertions fail (red phase)

### T-015: [TDD GREEN] Implement umbrella skip guard in `repo-structure-manager.ts`
**User Story**: US-SPE-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02
**Status**: [x] completed
**Test**: Given the failing tests from T-014, when `repo-structure-manager.ts` is updated to check `config.umbrella?.enabled` before calling the architecture prompt — auto-setting `architecture = 'github-parent'` and filtering `activeChildRepos` — then all T-014 tests pass, AND a non-umbrella project still reaches the architecture question (backward-compatible)

### T-016: [TDD RED+GREEN] Rate-limit fallback and detected-repo display
**User Story**: US-SPE-002 | **Satisfies ACs**: AC-US2-03, AC-US2-04
**Status**: [x] completed
**Test**: Given the GitHub API returns HTTP 403 during repo detection, when the wizard runs in umbrella mode, then it falls back to `config.umbrella.childRepos` without throwing or hanging; AND when auto-detection succeeds, the setup summary displays `"Detected N active child repos: <names>"` — write failing tests first, then implement fallback + display logic in `github-multi-repo.ts`

### T-017: End-to-end wizard integration test in umbrella mode
**User Story**: US-SPE-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03, AC-US2-04
**Status**: [x] completed
**Test**: Given a full wizard run mocked against an umbrella config with 2 active child repos, when the wizard executes from start to completion, then: architecture question is never presented, setup summary shows "Detected 2 active child repos: specweave, vskill", and wizard completes without error — verified via integration test against the real wizard flow
