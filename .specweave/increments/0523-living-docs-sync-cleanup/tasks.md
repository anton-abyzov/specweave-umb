# Tasks: Living Docs Sync Cleanup: Bug Fixes and DRY Extraction

## Task Notation

- `[x]`: Completed
- `[ ]`: Not Started
- Tasks are ordered by execution sequence per plan.md

---

## US-001: Fix Cross-Reference Generation Using Unfiltered Groups

### T-001: Replace `groups` with `validGroups` in generateCrossReferences calls
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02
**Status**: [ ] Not Started
**Test**: Given a multi-project sync where `validGroups` contains 2 of 4 original groups → When `syncIncrement` runs the cross-project path → Then `generateCrossReferences()` receives only the 2 validated keys (not all 4), and FEATURE.md contains no links to filtered-out projects

**Implementation Details**:
- In `src/core/living-docs/living-docs-sync.ts` at line 321, replace `[...groups.keys()]` with `[...validGroups.keys()]`
- At line 365, replace `[...groups.keys()]` with `[...validGroups.keys()]` where `allTargetPaths` is derived
- No other changes in this task

**Test File**: `tests/unit/core/living-docs/living-docs-sync.test.ts`
- **TC-001**: Given `groups` has keys `[A, B, C, D]` and `validGroups` has keys `[A, B]`, when `generateCrossReferences` is called, then it receives `[A, B]` only
- **TC-002**: Given a filtered-out project key `C`, when FEATURE.md content is generated for project `A`, then `C` does not appear as a cross-reference link

**Dependencies**: None

---

## US-002: Remove Dead detectMultiProjectMode Method

### T-002: Delete the unused private `detectMultiProjectMode` method (~100 LOC)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02
**Status**: [ ] Not Started
**Test**: Given `living-docs-sync.ts` with the dead method present → When lines 1189-1288 are deleted → Then `grep -c 'detectMultiProjectMode' src/core/living-docs/living-docs-sync.ts` returns 0 and all existing tests still pass

**Implementation Details**:
- Delete lines 1189-1288 (the entire `private detectMultiProjectMode(...)` method body) from `src/core/living-docs/living-docs-sync.ts`
- Confirm zero callers: `grep -r 'detectMultiProjectMode' src/` should return no results after removal
- Run `npx vitest run` to confirm no regressions

**Test File**: `tests/unit/core/living-docs/living-docs-sync.test.ts` (existing suite, no new tests)
- **TC-001**: Given the method is removed, when the full test suite runs, then all tests pass with 0 failures
- **TC-002**: Given the source file after deletion, when searching for `detectMultiProjectMode`, then zero occurrences are found

**Dependencies**: T-001 (execute after to minimize line-number churn)

---

## US-003: Correct ADR Citation in ProjectResolutionService

### T-003: Fix ADR-0140 -> ADR-0195 in project-resolution.ts header comment
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01
**Status**: [ ] Not Started
**Test**: Given `src/core/project/project-resolution.ts` → When reading line 10 → Then the comment references "ADR-0195" not "ADR-0140"

**Implementation Details**:
- In `src/core/project/project-resolution.ts`, replace `ADR-0140` with `ADR-0195` in the module header comment (line 10)
- Single-character-sequence change; no logic affected

**Test File**: `tests/unit/core/project/project-resolution.test.ts` (existing suite, no new tests)
- **TC-001**: Given the file after the change, when searching for `ADR-0140`, then zero occurrences exist in `project-resolution.ts`
- **TC-002**: Given the file after the change, when reading the module header comment, then the string `ADR-0195` is present

**Dependencies**: None (isolated file, execute in parallel with T-001)

---

## US-004: Extract Duplicated SKIP_EXTERNAL_SYNC Parsing

### T-004: Hoist SKIP_EXTERNAL_SYNC parsing to top of syncIncrement
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02
**Status**: [ ] Not Started
**Test**: Given `SKIP_EXTERNAL_SYNC=true` in the environment → When `syncIncrement` is called in either cross-project or single-project mode → Then both paths observe `skipExternalSync === true` from the single hoisted const, and no duplicate parsing pattern exists in the file

**Implementation Details**:
- In `src/core/living-docs/living-docs-sync.ts`, add a single `const skipExternalSync = ...` declaration near line ~230 (after options validation, before the cross-project branch)
- Remove the duplicate declarations at lines 430-431 and 626-627, replacing both with references to the hoisted const
- Verify with `grep -c "\\['true', '1', 'yes'\\]" src/core/living-docs/living-docs-sync.ts` returns 1

**Test File**: `tests/unit/core/living-docs/living-docs-sync.test.ts`
- **TC-001**: Given `SKIP_EXTERNAL_SYNC=true`, when cross-project sync runs, then external sync is skipped
- **TC-002**: Given `SKIP_EXTERNAL_SYNC=1`, when single-project sync runs, then external sync is skipped
- **TC-003**: Given `SKIP_EXTERNAL_SYNC` unset, when either path runs, then external sync proceeds normally
- **TC-004**: Given the source file after the change, when counting the parsing pattern, then exactly 1 occurrence exists

**Dependencies**: T-001, T-003 (line numbers stabilized by prior tasks)

---

## US-005: Extract Duplicated Image Generation Block

### T-005: Extract image generation + TL;DR injection to private helper `generateAndInjectImage`
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03
**Status**: [ ] Not Started
**Test**: Given the extracted `generateAndInjectImage` private method → When called from the cross-project path with `crossProjectPath` or from the single-project path with `projectPath` → Then image markdown is injected after the TL;DR section in FEATURE.md content, image generation is skipped when `SPECWEAVE_SKIP_IMAGE_GEN=true`, and `generateLivingDocsImagesEnhanced` is called from exactly one place in the codebase

**Implementation Details**:
- Extract to a new private method on `LivingDocsSync`:
  ```ts
  private async generateAndInjectImage(
    featureFolderPath: string,
    featureFilePath: string,
    title: string,
    featureId: string,
    content: string,
    result: SyncResult
  ): Promise<string>
  ```
- Method encapsulates: `SPECWEAVE_SKIP_IMAGE_GEN` check, `DocContext` derivation, `generateLivingDocsImagesEnhanced()` call, TL;DR regex replacement, logging, and non-blocking error handling
- Returns modified content (or original if skipped/failed)
- Replace inline blocks at lines 333-358 and 507-538 with single-line calls to the helper
- Depends on T-005 (DRY 3) because dynamic `matter` imports in the same region will have been removed first

**Test File**: `tests/unit/core/living-docs/living-docs-sync.test.ts`
- **TC-001**: Given `SPECWEAVE_SKIP_IMAGE_GEN=true`, when `generateAndInjectImage` is called, then it returns the original content unchanged and does not call `generateLivingDocsImagesEnhanced`
- **TC-002**: Given a successful image generation returning `![img](url)`, when `generateAndInjectImage` runs, then the returned content contains the image markdown injected after the `## TL;DR` section
- **TC-003**: Given `generateLivingDocsImagesEnhanced` throws, when `generateAndInjectImage` runs, then the error is logged and original content is returned (non-blocking)
- **TC-004**: Given the source file after extraction, when searching for `generateLivingDocsImagesEnhanced` call sites, then exactly 1 call site exists (inside the helper)

**Dependencies**: T-004, T-006 (DRY 3 — static gray-matter import must land first to avoid touching same region twice)

---

## US-006: Consolidate Dynamic gray-matter Import to Static

### T-006: Replace two `await import('gray-matter')` calls with a static top-level import
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02
**Status**: [ ] Not Started
**Test**: Given `living-docs-sync.ts` with two dynamic `await import('gray-matter')` calls → When a static `import matter from 'gray-matter'` is added at the top and both dynamic patterns are replaced → Then `grep -c "await import('gray-matter')" src/core/living-docs/living-docs-sync.ts` returns 0 and the file has a static matter import

**Implementation Details**:
- Add `import matter from 'gray-matter';` near line 20 (with other static imports) in `src/core/living-docs/living-docs-sync.ts`
- At line 308 (cross-project path): remove `const matter = await import('gray-matter');` and replace `matter.default(...)` with `matter(...)`
- At line 496 (single-project path): same substitution
- Verify no circular dependency: `gray-matter` is a leaf npm dependency

**Test File**: `tests/unit/core/living-docs/living-docs-sync.test.ts` (existing suite, no new tests)
- **TC-001**: Given the file after change, when searching for `await import('gray-matter')`, then zero occurrences exist
- **TC-002**: Given the file after change, when checking imports, then a static `import matter from 'gray-matter'` line is present
- **TC-003**: Given the existing test suite, when run after this change, then all tests pass (behavior unchanged)

**Dependencies**: T-004 (execute before T-005/DRY 2 to stabilize the same region)

---

## Verification

### T-007: Run full test suite and confirm all grep invariants
**User Story**: US-001, US-002, US-004, US-005, US-006 | **Satisfies ACs**: AC-US2-02, AC-US4-01, AC-US5-01, AC-US6-02
**Status**: [ ] Not Started
**Test**: Given all prior tasks complete → When the full Vitest suite runs and grep checks execute → Then 0 test failures, 0 occurrences of `detectMultiProjectMode` in living-docs-sync.ts, 0 occurrences of `await import('gray-matter')`, 1 occurrence of the SKIP_EXTERNAL_SYNC parsing pattern, and 1 call site for `generateLivingDocsImagesEnhanced`

**Implementation Details**:
- `cd repositories/anton-abyzov/specweave && npx vitest run`
- `grep -c 'detectMultiProjectMode' src/core/living-docs/living-docs-sync.ts` → 0
- `grep -c "await import('gray-matter')" src/core/living-docs/living-docs-sync.ts` → 0
- `grep -c "SKIP_EXTERNAL_SYNC.*toLowerCase" src/core/living-docs/living-docs-sync.ts` → 1
- `grep -c 'generateLivingDocsImagesEnhanced' src/core/living-docs/living-docs-sync.ts` → 1 (inside helper only)

**Dependencies**: T-001, T-002, T-003, T-004, T-005, T-006
