---
increment: 0588-cleanup-single-repo-remnants
title: 'Stage 2: Deep cleanup of single-repo remnants'
type: refactor
priority: P1
status: completed
created: 2026-03-19T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Stage 2: Deep Cleanup of Single-Repo Remnants

## Problem Statement

Stage 1 (increment 0581) removed the primary single-repo code paths but a 4-agent code review uncovered residual references: the `'single'` variant in `GitHubSetupType`, dead helper functions in `prompt-consolidator.ts`, an entire unused migration directory, stale doc sections, and test mocks that reference removed init choices. These remnants confuse contributors, inflate bundle size, and create false positives in searches for single-repo logic.

## Goals

- Eliminate every remaining `'single'` code path from the runtime codebase
- Remove dead code that has zero production importers
- Align documentation and CLI output with the post-Stage-1 two-choice model
- Fix test mocks so they reflect current init option values

## User Stories

### US-001: Clean GitHubSetupType and issue-tracker flows
**Project**: specweave
**As a** contributor
**I want** the `GitHubSetupType` union and issue-tracker setup flows to have no `'single'` variant
**So that** the codebase has a single canonical path for repository configuration

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given `src/cli/commands/github-multi-repo.ts` is compiled, when inspecting the `GitHubSetupType` type, then it does not contain `'single'` as a member
- [x] **AC-US1-02**: Given `github-multi-repo.ts`, when searching for `configureSingleRepository`, then the function does not exist and the "Single repository" prompt choice maps to the multi-repo flow with count=1
- [x] **AC-US1-03**: Given `src/cli/commands/github.ts`, when searching for `case 'single'`, then no such case branch exists
- [x] **AC-US1-04**: Given any fallback assignment in the GitHub setup modules, when the fallback resolves, then it defaults to `'multiple'` (not `'single'`)

---

### US-002: Fix save command output
**Project**: specweave
**As a** user running `specweave save`
**I want** the output to say "Workspace (1 repository)" instead of "Single repository"
**So that** the CLI messaging is consistent with the new two-choice model

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given `src/cli/commands/save.ts`, when the save command formats output for a workspace with one repo, then the label reads "Workspace (1 repository)"
- [x] **AC-US2-02**: Given a user runs `specweave save` in a workspace with one child repo, when viewing stdout, then the string "Single repository" does not appear

---

### US-003: Update skill and doc files
**Project**: specweave
**As a** contributor reading project documentation
**I want** SKILL.md and the docs-site guides to reflect the current two-choice init prompt
**So that** onboarding docs do not reference removed single-repo flows

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given `plugins/specweave/skills/increment/SKILL.md`, when reading the file, then Step 0D (the resolve-structure block, approximately lines 121-142) does not exist and no "umbrella vs single-repo" framing remains
- [x] **AC-US3-02**: Given `docs-site/docs/guides/strategic-init.md`, when reading Phase 6, then it describes the current 2-choice prompt (not the removed 3-choice prompt)
- [x] **AC-US3-03**: Given `docs-site/docs/commands/save.md`, when reading the file, then the "Single Repo Mode" section has been replaced with content describing workspace mode

---

### US-004: Remove dead code
**Project**: specweave
**As a** contributor
**I want** unreachable functions and unused modules deleted
**So that** the codebase has no dead code from the old single-repo model

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given `src/core/repo-structure/prompt-consolidator.ts`, when searching for `getParentRepoBenefits`, `getRepoCountClarification`, or `formatArchitectureChoice`, then none of these functions exist
- [x] **AC-US4-02**: Given the project tree, when listing `src/core/migration/`, then the directory does not exist
- [x] **AC-US4-03**: Given `src/init/research/src/config/types.ts`, when inspecting the Zod enum for repo structure, then it contains only `['multi']`
- [x] **AC-US4-04**: Given `src/init/research/src/config/ConfigManager.ts`, when inspecting the default repo-structure value, then it is `'multi'`

---

### US-005: Fix stale test mocks
**Project**: specweave
**As a** contributor running the test suite
**I want** test mocks to use current init option values
**So that** tests validate real behavior instead of removed code paths

**Acceptance Criteria**:
- [x] **AC-US5-01**: Given `tests/unit/cli/commands/init-config-validation.test.ts`, when searching for `'existing'`, `'scratch'`, or `'multi-repo-deferred'`, then none appear and `'add-later'` is used instead
- [x] **AC-US5-02**: Given `tests/unit/cli/commands/init.test.ts`, when searching for `'existing'`, then it does not appear and `'add-later'` is used instead
- [x] **AC-US5-03**: Given `tests/unit/cli/commands/init-path-resolution.test.ts`, when searching for `'existing'`, then it does not appear and `'add-later'` is used instead
- [x] **AC-US5-04**: Given all test files are updated, when running `npx vitest run`, then the full test suite passes with zero failures

## Out of Scope

- New features or behavioral changes -- this is strictly a cleanup refactor
- Stage 3 findings (if any arise from this work, log them as a new increment)
- Updating third-party or community plugin references to single-repo
- Renaming the `multi` enum value to something else (it stays as-is)

## Non-Functional Requirements

- **Compatibility**: All existing tests pass after changes; no public API signatures change
- **Performance**: No runtime impact -- this is pure code deletion and string replacement
- **Security**: No security surface changes

## Edge Cases

- Files that import from `src/core/migration/` transitively: verify zero importers before deletion
- Zod enum narrowing from `['single', 'multi']` to `['multi']`: existing configs with `repoStructure: 'single'` would fail validation -- confirm Stage 1 already migrated all persisted configs
- SKILL.md line numbers may have shifted since the findings were recorded: use content matching, not line numbers

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| Migration directory has a hidden runtime importer | 0.1 | 7 | 0.7 | grep for all imports before deletion |
| Persisted configs still contain `'single'` | 0.1 | 6 | 0.6 | Stage 1 handled migration; verify with config schema tests |
| Doc line numbers drifted since findings | 0.3 | 2 | 0.6 | Match on content, not line numbers |

## Technical Notes

### Dependencies
- Increment 0581 (Stage 1) must be complete -- it removed the primary code paths this increment cleans up after

### Constraints
- Pure refactor: no behavioral changes allowed
- All changes target the `specweave` project (single-project increment)

## Success Metrics

- Zero occurrences of the string `'single'` in `GitHubSetupType` or Zod repo-structure enums
- `src/core/migration/` directory deleted with zero broken imports
- Full test suite green after all changes
- Zero grep hits for removed function names (`configureSingleRepository`, `getParentRepoBenefits`, `getRepoCountClarification`, `formatArchitectureChoice`)
