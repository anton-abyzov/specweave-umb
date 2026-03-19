---
increment: 0588-cleanup-single-repo-remnants
title: "Stage 2: Deep cleanup of single-repo remnants"
type: refactor
---

# Tasks: Stage 2 -- Deep Cleanup of Single-Repo Remnants

All groups (A–E) are independent and can execute in parallel.

---

## US-001: Clean GitHubSetupType and issue-tracker flows

### T-001: Remove `'single'` from GitHubSetupType and prompt choices
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-03
**Status**: [x] Completed
**Test**: Given `github-multi-repo.ts` is compiled → When inspecting `GitHubSetupType` and the `select()` choices array → Then `'single'` does not appear as a union member or prompt option

### T-002: Delete `configureSingleRepository()` and fix its call sites
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-04
**Status**: [x] Completed
**Test**: Given `github-multi-repo.ts` and `github.ts` are saved → When grepping `src/` for `configureSingleRepository` and `case 'single'` → Then zero matches are returned and the fallback `setupType` resolves to `'multiple'`

---

## US-002: Fix save command output

### T-003: Update mode label in `save.ts`
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02
**Status**: [x] Completed
**Test**: Given `save.ts` is modified → When `specweave save` runs in a workspace with one child repo → Then stdout contains `"Workspace (1 repository)"` and does not contain the string `"Single repository"`

---

## US-003: Update SKILL.md and doc files

### T-004: Remove resolve-structure block from SKILL.md
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01
**Status**: [x] Completed
**Test**: Given `plugins/specweave/skills/increment/SKILL.md` is saved → When grepping for `resolve-structure` and `DEFERRED` → Then zero matches are found in the file

### T-005: Update strategic-init.md Phase 6 and save.md docs
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-03
**Status**: [x] Completed
**Test**: Given both doc files are updated → When reading `strategic-init.md` Phase 6 and `save.md` → Then neither file contains `"Single repository"` or a `"Single Repo Mode"` heading, and Phase 6 describes a 2-choice prompt

---

## US-004: Remove dead code

### T-006: Delete deprecated functions from `prompt-consolidator.ts`
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01
**Status**: [x] Completed
**Test**: Given `prompt-consolidator.ts` is saved and its test file updated → When grepping `src/` for `getParentRepoBenefits`, `getRepoCountClarification`, `formatArchitectureChoice` → Then zero matches are found

### T-007: Delete `src/core/migration/` directory and its test files
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02
**Status**: [x] Completed
**Test**: Given all 4 source files and 7 test files under `src/core/migration/` are deleted → When listing the directory and grepping `src/` for `core/migration` imports → Then the directory does not exist and no broken imports remain

### T-008: Narrow Zod enum and update ConfigManager default
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03, AC-US4-04
**Status**: [x] Completed
**Test**: Given `types.ts` and `ConfigManager.ts` are saved → When inspecting the Zod enum and the default config → Then the enum contains only `['multi']` and the default `type` is `'multi'`

---

## US-005: Fix stale test mocks

### T-009: Fix init test mocks (`init.test.ts`, `init-config-validation.test.ts`, `init-path-resolution.test.ts`)
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03
**Status**: [x] Completed
**Test**: Given all three init test files are updated → When grepping them for `'existing'`, `'scratch'`, `'multi-repo-deferred'` → Then zero matches are found and `'add-later'` / `'clone-repos'` are used instead

### T-010: Fix GitHub test mocks (`github-multi-repo.test.ts`, `github.test.ts`, `github-repo-reuse.test.ts`)
**User Story**: US-005 | **Satisfies ACs**: AC-US5-04
**Status**: [x] Completed
**Test**: Given all three GitHub test files are updated → When grepping them for `setupType.*'single'` → Then zero matches are found

### T-011: Run full test suite and verify zero grep hits
**User Story**: US-005 | **Satisfies ACs**: AC-US5-04
**Status**: [x] Completed
**Test**: Given all changes from T-001 through T-010 are applied → When running `npx vitest run` and `npx tsc --noEmit` → Then the full suite passes with zero failures and zero type errors
