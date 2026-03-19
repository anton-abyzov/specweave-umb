---
increment: 0589-cli-complete-improvements
title: CLI Complete Command Improvements
type: bug
priority: P1
status: completed
created: 2026-03-19T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: CLI Complete Command Improvements

## Overview

Three improvements to the `specweave complete` CLI command: short-ID resolution (accept `0573` instead of requiring the full slug), batch mode (accept multiple IDs in one invocation), and graceful degradation when the AC coverage validator encounters a task-parser error.

## User Stories

### US-001: Short-ID Resolution for Complete Command (P0)
**Project**: specweave

**As a** SpecWeave CLI user
**I want** to run `specweave complete 0573` without typing the full slug
**So that** I can complete increments faster without looking up exact folder names

**Acceptance Criteria**:
- [x] **AC-US1-01**: `specweave complete 0573` resolves to `0573-fix-sw-specweave-corruption` when that is the only matching prefix
- [x] **AC-US1-02**: Full slugs (`specweave complete 0573-fix-sw-specweave-corruption`) continue to work unchanged
- [x] **AC-US1-03**: If the short ID matches zero increments, a clear error is shown with the searched prefix
- [x] **AC-US1-04**: If the short ID matches multiple increments (ambiguous), all matches are listed and the command fails
- [x] **AC-US1-05**: The resolver is a shared utility function reusable by other commands (extracted from `evaluate-completion.ts`)

---

### US-002: Batch Mode for Complete Command (P0)
**Project**: specweave

**As a** SpecWeave CLI user
**I want** to run `specweave complete 0573 0562 0571` to complete multiple increments at once
**So that** I can batch-close related work without repeating the command

**Acceptance Criteria**:
- [x] **AC-US2-01**: `specweave complete 0573 0562 0571` processes all three IDs sequentially
- [x] **AC-US2-02**: One failure does NOT stop processing of remaining IDs; all IDs are attempted
- [x] **AC-US2-03**: Exit code is non-zero if ANY ID fails; zero only when all succeed
- [x] **AC-US2-04**: Each ID goes through short-ID resolution before processing
- [x] **AC-US2-05**: A summary is printed at the end showing which IDs succeeded and which failed

---

### US-003: AC Coverage Validator Graceful Parse Error Handling (P1)
**Project**: specweave

**As a** SpecWeave CLI user
**I want** completion to succeed with a warning when the task parser cannot parse tasks.md
**So that** malformed task files do not block closure of otherwise-valid increments

**Acceptance Criteria**:
- [x] **AC-US3-01**: When `parseTasksWithUSLinks()` throws a parse error inside `validateACCoverage()`, it degrades to a warning ("AC coverage validation skipped due to parse error") instead of blocking
- [x] **AC-US3-02**: The bug at `completion-validator.ts:400` is fixed — `parseTasksWithUSLinks()` is called with `tasksPath` (file path) instead of `tasksContent` (file content string)
- [x] **AC-US3-03**: When tasks.md parses successfully and violations are found, those violations still block completion as before (no behavioral regression)
- [x] **AC-US3-04**: The warning includes the parse error message for debuggability

## Functional Requirements

### FR-001: Shared `resolveIncrementId()` Utility
Extract the existing `resolveIncrementId()` from `src/cli/commands/evaluate-completion.ts:59-76` into a shared utility at `src/utils/resolve-increment-id.ts`. The function:
1. Checks for exact match in `.specweave/increments/`
2. Falls back to prefix match
3. Returns the full slug, or null if no match
4. Handles ambiguous matches (multiple prefixes) by returning all matches for the caller to report

The original in `evaluate-completion.ts` should be replaced with an import of the shared utility.

### FR-002: Variadic Complete Command
Change the Commander.js registration from `complete <increment-id>` to `complete <increment-id> [more-ids...]` following the same pattern as the `archive` command (`bin/specweave.js:419`). The handler:
1. Collects all IDs into an array (first required + rest variadic)
2. Resolves each via `resolveIncrementId()`
3. Calls `completeIncrement()` for each resolved ID
4. Collects successes and failures
5. Prints summary and exits with appropriate code

### FR-003: Fix `validateACCoverage` Call Site
At `completion-validator.ts:400`, `parseTasksWithUSLinks(tasksContent)` is called with file **content** but the function expects a file **path** (it calls `readFileSync` internally at `task-parser.ts:95`). Fix by passing `tasksPath` instead of `tasksContent`. The existing try/catch at lines 107-140 already handles errors correctly — the fix is just the wrong argument.

## Success Criteria

- All three improvements work independently (no coupling between them)
- Existing tests pass; new unit tests for resolver and batch mode
- No regressions in single-ID completion flow
- `evaluate-completion.ts` uses the shared resolver (DRY)

## Out of Scope

- Short-ID resolution for other commands beyond complete and evaluate-completion (future work — the utility is reusable)
- Interactive disambiguation when short-ID is ambiguous (just fail with a list)
- Parallel batch processing (sequential is sufficient)

## Dependencies

- Commander.js variadic argument support (already used by `archive` command)
- Existing `resolveIncrementId()` implementation in `evaluate-completion.ts`
