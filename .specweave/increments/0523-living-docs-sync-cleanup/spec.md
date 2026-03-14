---
increment: 0523-living-docs-sync-cleanup
title: "Living Docs Sync Cleanup: Bug Fixes and DRY Extraction"
status: active
priority: P1
type: bug
created: 2026-03-14
---

# Living Docs Sync Cleanup: Bug Fixes and DRY Extraction

## Problem Statement

`living-docs-sync.ts` contains three bugs and three DRY violations identified during code review. Bug 1 causes cross-reference links to include filtered-out (invalid/placeholder) projects in FEATURE.md files. Bug 2 leaves ~100 lines of dead code. Bug 3 cites the wrong ADR. The DRY violations add maintenance burden through duplicated SKIP_EXTERNAL_SYNC parsing, duplicated image generation blocks, and inconsistent gray-matter imports.

## Goals

- Fix cross-reference generation to use only validated project groups
- Remove dead `detectMultiProjectMode` method (~100 LOC reduction)
- Correct ADR citation in ProjectResolutionService from ADR-0140 to ADR-0195
- Eliminate three DRY violations through extraction and consolidation
- Zero behavioral changes beyond the bug fixes

## User Stories

### US-001: Fix Cross-Reference Generation Using Unfiltered Groups
**Project**: specweave

**As a** SpecWeave user with a multi-project workspace
**I want** FEATURE.md cross-references to only link to validated projects
**So that** I do not see broken or misleading links to filtered-out placeholder projects

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a multi-project sync where `validGroups` contains 2 of 4 original groups, when `generateCrossReferences()` is called, then only the 2 validated project keys are passed (not all 4)
- [x] **AC-US1-02**: Given a project that was filtered out by the validation logic (lines 262-282), when FEATURE.md is generated for another project, then no cross-reference link to the filtered project appears

---

### US-002: Remove Dead detectMultiProjectMode Method
**Project**: specweave

**As a** SpecWeave maintainer
**I want** the unused `detectMultiProjectMode` private method removed from `living-docs-sync.ts`
**So that** the file is shorter and there is no confusion about which implementation is authoritative

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given the current codebase, when searching for `detectMultiProjectMode` in `living-docs-sync.ts`, then zero definitions or calls exist in that file
- [x] **AC-US2-02**: Given the removal, when existing tests are run, then all tests pass with no regressions

---

### US-003: Correct ADR Citation in ProjectResolutionService
**Project**: specweave

**As a** developer reading `project-resolution.ts`
**I want** the header comment to reference ADR-0195 (Remove Frontmatter Project Field)
**So that** I can find the correct architectural decision document

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given `src/core/project/project-resolution.ts`, when reading the module header comment, then it references "ADR-0195" instead of "ADR-0140"

---

### US-004: Extract Duplicated SKIP_EXTERNAL_SYNC Parsing
**Project**: specweave

**As a** SpecWeave maintainer
**I want** the SKIP_EXTERNAL_SYNC env var parsing to exist in one place
**So that** future changes to the parsing logic only need one update

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given `living-docs-sync.ts`, when searching for the SKIP_EXTERNAL_SYNC parsing pattern (`['true', '1', 'yes'].includes`), then it appears exactly once (extracted to a single check near the top of `syncIncrement`)
- [x] **AC-US4-02**: Given both the cross-project and single-project sync paths, when SKIP_EXTERNAL_SYNC is set to "true", then both paths skip external sync (behavior preserved)

---

### US-005: Extract Duplicated Image Generation Block
**Project**: specweave

**As a** SpecWeave maintainer
**I want** the image generation and TL;DR injection logic extracted to a private helper
**So that** the cross-project and single-project paths share one implementation

**Acceptance Criteria**:
- [x] **AC-US5-01**: Given `living-docs-sync.ts`, when searching for `generateLivingDocsImagesEnhanced`, then it is called from exactly one private helper method (not inline in two places)
- [x] **AC-US5-02**: Given SPECWEAVE_SKIP_IMAGE_GEN=true, when sync runs in either cross-project or single-project mode, then image generation is skipped (behavior preserved)
- [x] **AC-US5-03**: Given a successful image generation, when the helper runs, then the image markdown is injected after the TL;DR section in FEATURE.md content

---

### US-006: Consolidate Dynamic gray-matter Import to Static
**Project**: specweave

**As a** SpecWeave maintainer
**I want** `gray-matter` imported statically at the top of `living-docs-sync.ts`
**So that** the import style is consistent and there is no duplicated dynamic import

**Acceptance Criteria**:
- [x] **AC-US6-01**: Given `living-docs-sync.ts`, when checking imports, then `gray-matter` is imported via a static `import` statement at the top of the file
- [x] **AC-US6-02**: Given the file contents, when searching for `await import('gray-matter')`, then zero occurrences exist

## Out of Scope

- Refactoring beyond the identified bugs and DRY violations
- Changes to test files (only verify existing tests pass)
- Changes to any file outside `living-docs-sync.ts` and `project-resolution.ts`
- New features or configuration options
- External sync behavior changes

## Technical Notes

### Dependencies
- `gray-matter` (already a project dependency, changing from dynamic to static import)
- `src/utils/multi-project-detector.ts` (authoritative implementation of multi-project detection)
- `src/core/living-docs/sync-helpers/hierarchy-builder.ts` (another copy of detection logic, not touched in this increment)

### Constraints
- All changes must be behavior-preserving (except Bug 1 fix which corrects behavior)
- The extracted image generation helper must handle both `docContext` derivation patterns (cross-project uses `crossProjectPath`, single-project uses `projectPath`)

### Architecture Decisions
- Static import of `gray-matter` chosen over a single dynamic import because the module is always used (not conditionally loaded) and it matches the import style of other dependencies in the file

## Non-Functional Requirements

- **Performance**: No measurable impact; static import is equivalent to cached dynamic import
- **Compatibility**: No API surface changes; all changes are internal to the sync module
- **Security**: Bug 1 fix improves correctness by preventing references to invalid projects

## Edge Cases

- `validGroups` is empty: `generateCrossReferences` receives empty array, produces no cross-refs (correct behavior)
- Image generation helper called with path that has no TL;DR section: regex no-op, content unchanged (existing behavior preserved)
- gray-matter already used elsewhere via static import: no conflict, Node.js deduplicates

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| Static gray-matter import causes circular dependency | 0.1 | 3 | 0.3 | gray-matter is a leaf dependency with no SpecWeave imports |
| Extracted image helper misses subtle difference between cross-project and single-project paths | 0.2 | 4 | 0.8 | Parameterize helper to accept both path styles; verify with existing tests |
| Dead method removal breaks reflection/dynamic access | 0.05 | 5 | 0.25 | grep confirms zero callers; method is private |

## Success Metrics

- All existing tests pass after changes
- `living-docs-sync.ts` reduced by ~130 lines (100 dead method + 30 deduplicated)
- Zero occurrences of `await import('gray-matter')` in the file
- Cross-references only contain validated project keys
