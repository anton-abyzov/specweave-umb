# Tasks: External Issue Import

## Phase 1: Suffix System

### T-001: Update increment-utils.ts regex patterns
**References**: AC-US3-01, AC-US3-05
**Status**: [x] Completed

Update 6 regex patterns from `E?` to `[GJAE]?`:
- `getAllIncrementNumbers()` line 290
- `incrementNumberExists()` line 190
- `scanAllIncrementDirectories()` line 370
- `extractNumber()` line 647
- `findDuplicates()` line 698
- `isExternalIncrement()` line 626

### T-002: Add getNextPlatformIncrementNumber() method
**References**: AC-US3-04
**Status**: [x] Completed

New method using SUFFIX_MAP from sync/types.ts.

### T-003: Update generateIncrementId() for platformSuffix
**References**: AC-US3-02, AC-US3-03
**Status**: [x] Completed

Add `platformSuffix?: PlatformSuffix` to options, use instead of 'E' when provided.

## Phase 2: Template Creator

### T-004: Add externalSource to CreateTemplateOptions
**References**: AC-US1-05, AC-US1-06
**Status**: [x] Completed

### T-005: Add generateExternalSpecContent() and generateExternalTasksContent()
**References**: AC-US1-06
**Status**: [x] Completed

## Phase 3: Duplicate Detection

### T-006: Create increment-external-ref-detector.ts
**References**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] Completed

### T-007: Implement external_ref and origin in metadata.json
**References**: AC-US2-04
**Status**: [x] Completed

## Phase 4: Import Bridge

### T-008: Create import-to-increment.ts
**References**: AC-US1-02, AC-US1-03, AC-US1-04
**Status**: [x] Completed

## Phase 5: Skill

### T-009: Create /sw:import SKILL.md
**References**: AC-US1-01
**Status**: [x] Completed

## Phase 6: Tests

### T-010: Write unit tests for suffix system
**References**: AC-US3-01 through AC-US3-05
**Status**: [x] Completed

### T-011: Write unit tests for import-to-increment
**References**: AC-US2-01 through AC-US2-04
**Status**: [x] Completed
