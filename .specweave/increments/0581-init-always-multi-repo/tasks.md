---
increment: 0581-init-always-multi-repo
title: "Simplify init to always use repositories/owner/repo structure"
generated: 2026-03-18
test_mode: TDD
---

# Tasks: Simplify Init to Always-Multi Repository

## US-004: Config and Type Simplification

> Types are cleaned first -- all other phases depend on correct foundation types (Phase 1).

---

### T-001: Remove `-single`/`-multirepo` suffixes from `RepositoryHosting` in `src/cli/helpers/init/types.ts`
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01
**Status**: [x] Completed
**Test Plan**: Given `src/cli/helpers/init/types.ts` after this change → When the `RepositoryHosting` type is inspected → Then it contains exactly `'github' | 'bitbucket' | 'ado' | 'local' | 'other'` with no `-single` or `-multirepo` suffix variants

---

### T-002: Remove `-single`/`-multirepo` suffixes from `RepositoryHosting` in `src/cli/helpers/issue-tracker/types.ts`
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02
**Status**: [x] Completed
**Test Plan**: Given `src/cli/helpers/issue-tracker/types.ts` after this change → When the `RepositoryHosting` type is inspected → Then it contains no values with `-single` or `-multirepo` suffixes and matches the values in `init/types.ts`

---

### T-003: Update consumer files that pattern-match on `RepositoryHosting` suffix values
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02
**Status**: [x] Completed
**Test Plan**: Given `src/cli/commands/sync-setup.ts` and `src/cli/helpers/issue-tracker/github-multi-repo.ts` after this change → When `npx vitest run` is executed → Then no TypeScript errors reference removed suffix variants and all existing tests pass

---

### T-004: Remove `'single'` from `RepoArchitecture` type in `repo-structure-manager.ts`
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03
**Status**: [x] Completed
**Test Plan**: Given `src/core/repo-structure/repo-structure-manager.ts` after this change → When the `RepoArchitecture` type is inspected → Then its union contains only `'multi-repo' | 'monorepo' | 'parent'` with no `'single'` value

---

### T-005: Remove `'single'` from `SetupArchitecture` type in `setup-state-manager.ts`
**User Story**: US-004 | **Satisfies ACs**: AC-US4-04
**Status**: [x] Completed
**Test Plan**: Given `src/core/repo-structure/setup-state-manager.ts` after this change → When the `SetupArchitecture` type is inspected → Then its union contains only `'multi-repo' | 'parent' | 'monorepo'` with no `'single'` value

---

### T-006: Delete `single-project-migrator.ts` and remove its import and call from `config-manager.ts`
**User Story**: US-004 | **Satisfies ACs**: AC-US4-05
**Status**: [x] Completed
**Test Plan**: Given `src/core/config/` after this change → When the directory is examined → Then `single-project-migrator.ts` does not exist; and given `src/core/config/config-manager.ts` → When inspected → Then no import of `single-project-migrator` and no call to `detectAndMigrateSingleProject` remain

---

### T-007: Remove `multiProject.enabled` write and `isMultiRepo` declaration from `init.ts`
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-03
**Status**: [x] Completed
**Test Plan**: Given `src/cli/commands/init.ts` after this change → When the file is inspected → Then no `let isMultiRepo` declaration and no `multiProject.enabled` assignment exist; and given running `npx vitest run` → Then all init-related tests pass

---

### T-008: Write unit tests for type simplification (TDD red phase before T-001 through T-007)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04
**Status**: [x] Completed
**Test Plan**: Given new unit tests asserting the simplified type shapes (no suffix variants, no `'single'` in architecture types) → When `npx vitest run` is executed before the type changes → Then these tests fail (red); and after T-001 through T-007 → Then the same tests pass (green)

---

### T-009: Run `npx vitest run` after Phase 1 -- assert zero failures
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05
**Status**: [x] Completed
**Test Plan**: Given the codebase after T-001 through T-008 → When `npx vitest run` is executed → Then the test suite reports 0 failures and 0 skipped tests related to changed type files

---

## US-001: Simplified Init Flow

> Depends on US-004 types being clean first (Phase 1 complete before Phase 2).

---

### T-010: Write failing tests for simplified init flow (TDD red phase)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Status**: [x] Completed
**Test Plan**: Given new/updated tests in `tests/unit/cli/commands/init-multirepo.test.ts` asserting: no 4-way prompt, 2-choice prompt, `repositories/` always created, banner shows "Workspace", next steps show "specweave get" only → When `npx vitest run` is executed before implementation → Then these tests fail (red)

---

### T-011: Simplify `ProjectSetupChoice` to 2 choices and replace the 4-way prompt in `repo-connect.ts`
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02
**Status**: [x] Completed
**Test Plan**: Given `src/cli/helpers/init/repo-connect.ts` after this change → When the `promptProjectSetup` function is called in a test simulating the prompt → Then only two options are rendered: "Connect repositories" and "Add later via specweave get", with no "existing" or "scratch" choices present

---

### T-012: Make `repositories/` directory creation unconditional in `init.ts`
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03
**Status**: [x] Completed
**Test Plan**: Given a test that invokes the init flow with any setup choice (including "add-later" and CI mode) → When init completes → Then a `repositories/` directory exists at the workspace root in all code paths

---

### T-013: Make umbrella config write unconditional in `init.ts` (always `umbrella.enabled: true`)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03
**Status**: [x] Completed
**Test Plan**: Given a test that runs init with zero repositories provided → When init completes and config is read → Then `config.umbrella.enabled` is `true` and `config.umbrella.childRepos` is an empty array, with no `multiProject.enabled` key written

---

### T-014: Update summary banner to show "Workspace (N repositories)" instead of "Single repository"
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04
**Status**: [x] Completed
**Test Plan**: Given `src/cli/helpers/init/summary-banner.ts` after this change → When the banner is rendered with zero or more discovered repos → Then the output contains "Workspace (0 repositories)" or "Workspace (N repositories)" and never contains the string "Single repository"

---

### T-015: Update next-steps to always show `specweave get` and never show `migrate-to-umbrella`
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05
**Status**: [x] Completed
**Test Plan**: Given `src/cli/helpers/init/next-steps.ts` after this change → When next steps are rendered for any init completion → Then the output includes `specweave get` and does not contain the string `migrate-to-umbrella` in any code path

---

### T-016: Remove `isMultiRepo` from `NextStepsContext` type and remove `context.isUmbrella` branching
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05
**Status**: [x] Completed
**Test Plan**: Given `src/cli/helpers/init/types.ts` after this change → When the `NextStepsContext` interface is inspected → Then it does not contain an `isMultiRepo` field; and given `npx tsc --noEmit` → Then no TypeScript errors occur

---

### T-017: Remove optional sync-setup chain from `init.ts` (post-scaffold block lines 455-467)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01
**Status**: [x] Completed
**Test Plan**: Given `src/cli/commands/init.ts` after this change → When the post-scaffold block is inspected → Then no optional sync-setup invocation block exists; and given `npx vitest run` → Then init unit tests pass

---

### T-018: Rewrite `tests/unit/cli/commands/init-multirepo.test.ts` for unified flow (green phase)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Status**: [x] Completed
**Test Plan**: Given `tests/unit/cli/commands/init-multirepo.test.ts` rewritten for unified flow → When `npx vitest run` is executed after T-011 through T-017 → Then all assertions pass: no 4-way prompt, "repositories/" always created, banner shows "Workspace", next steps include "specweave get" only, and zero skipped tests

---

### T-019: Update `tests/unit/cli/helpers/init/repo-connect.test.ts` for 2-choice prompt
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02
**Status**: [x] Completed
**Test Plan**: Given `tests/unit/cli/helpers/init/repo-connect.test.ts` updated → When `npx vitest run` is executed → Then tests assert only "clone-repos" and "add-later" choices exist, old "existing" and "scratch" choice assertions are removed, and all tests pass

---

### T-020: Update `tests/unit/cli/helpers/init/summary-banner.test.ts` to remove "Single repository" assertions
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04
**Status**: [x] Completed
**Test Plan**: Given `tests/unit/cli/helpers/init/summary-banner.test.ts` updated → When `npx vitest run` is executed → Then no test asserts the presence of "Single repository" text, all banner tests assert "Workspace" format, and all tests pass

---

## US-002: Remove migrate-to-umbrella Command

> Depends on Phase 1 types. Independent of Phase 2 init rewrite.

---

### T-021: Delete `src/cli/commands/migrate-to-umbrella.ts`
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01
**Status**: [x] Completed
**Test Plan**: Given the codebase after this change → When `ls src/cli/commands/` is examined → Then `migrate-to-umbrella.ts` does not exist; and given `npx vitest run` → Then no test import of the deleted file causes a failure

---

### T-022: Replace `migrate-to-umbrella` registration in `bin/specweave.js` with deprecation stub
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-03
**Status**: [x] Completed
**Test Plan**: Given `bin/specweave.js` after this change → When `specweave migrate-to-umbrella` is invoked → Then the CLI prints "This command has been removed. Use `specweave get` to add repositories." and exits with code 0; and given inspecting `bin/specweave.js` → Then no `require('./src/cli/commands/migrate-to-umbrella')` line exists

---

### T-023: Verify `consolidation-engine.ts` and `spec-project-mapper.ts` are preserved
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04
**Status**: [x] Completed
**Test Plan**: Given the codebase after all migrate-to-umbrella removal changes → When `src/consolidation/` is examined → Then both `consolidation-engine.ts` and `spec-project-mapper.ts` exist and `npx vitest run` shows no import errors for those files

---

### T-024: Delete `tests/unit/cli/commands/migrate-to-umbrella.test.ts`
**User Story**: US-002 | **Satisfies ACs**: AC-US6-02
**Status**: [x] Completed
**Test Plan**: Given the test suite after this deletion → When `tests/unit/cli/commands/` is examined → Then `migrate-to-umbrella.test.ts` does not exist; and given `npx vitest run` → Then no broken import or missing-file error occurs

---

## US-003: Remove resolve-structure Command

---

### T-025: Delete `src/cli/commands/resolve-structure.ts`
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01
**Status**: [x] Completed
**Test Plan**: Given the codebase after this change → When `ls src/cli/commands/` is examined → Then `resolve-structure.ts` does not exist; and given `npx vitest run` → Then no test import of the deleted file causes a failure

---

### T-026: Replace `resolve-structure` registration in `bin/specweave.js` with deprecation stub
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02
**Status**: [x] Completed
**Test Plan**: Given `bin/specweave.js` after this change → When `specweave resolve-structure` is invoked → Then the CLI prints "This command has been removed. All workspaces now use the repositories/ structure." and exits with code 0; and given inspecting `bin/specweave.js` → Then no `require('./src/cli/commands/resolve-structure')` line exists

---

## US-006: Test Updates

---

### T-027: Write test asserting init config never contains `multiProject.enabled`
**User Story**: US-006 | **Satisfies ACs**: AC-US6-03
**Status**: [x] Completed
**Test Plan**: Given a test in `tests/unit/cli/commands/init-multirepo.test.ts` that runs the full init flow → When init completes and the resulting config is parsed → Then the config object has no `multiProject` key and `config.umbrella.enabled` is `true`

---

### T-028: Write test asserting `specweave get <url>` clones into `repositories/owner/repo`
**User Story**: US-006 | **Satisfies ACs**: AC-US6-04
**Status**: [x] Completed
**Test Plan**: Given a test workspace initialized with the new unified flow → When `specweave get https://github.com/owner/repo` is simulated → Then the clone target path resolves to `repositories/owner/repo` relative to the workspace root

---

## US-005: Documentation Updates

> Depends on all Phase 1-3 code changes being complete. Run grep sweep first.

---

### T-029: Grep sweep for outdated terminology across all doc files
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04, AC-US5-05
**Status**: [x] Completed
**Test Plan**: Given a grep sweep for `single.repo|multi.repo|isMultiRepo|migrate-to-umbrella|resolve-structure|single vs multi|4-way|promptProjectSetup` across `docs-site/`, `templates/`, and `CLAUDE.md` → When the sweep completes → Then a hit list is produced and every hit is addressed in T-030 through T-033

---

### T-030: Update `CLAUDE.md` in specweave repo -- remove single/multi distinction from "Multi-repo" section
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01
**Status**: [x] Completed
**Test Plan**: Given `CLAUDE.md` in the specweave repo after this change → When the file is inspected → Then the "Multi-repo" section describes a single unified workspace model with no single/multi distinction and no reference to `migrate-to-umbrella`

---

### T-031: Rename "Multi-Repo Structure" to "Repository Structure" in `templates/AGENTS.md.template`
**User Story**: US-005 | **Satisfies ACs**: AC-US5-02
**Status**: [x] Completed
**Test Plan**: Given `templates/AGENTS.md.template` after this change → When the file is inspected → Then the section formerly titled "Multi-Repo Structure" is titled "Repository Structure" and no single/multi distinction text remains

---

### T-032: Rewrite `docs-site/docs/guides/multi-project-setup.md` for unified workspace model
**User Story**: US-005 | **Satisfies ACs**: AC-US5-03
**Status**: [x] Completed
**Test Plan**: Given `docs-site/docs/guides/multi-project-setup.md` after this change → When inspected → Then it describes the unified `repositories/` structure for all workspace sizes, contains no migration instructions, and does not use "single repo mode" or "multi-repo mode"

---

### T-033: Remove `migrate-to-umbrella` from `docs-site/docs/guides/command-reference-by-priority.md`
**User Story**: US-005 | **Satisfies ACs**: AC-US5-04
**Status**: [x] Completed
**Test Plan**: Given `docs-site/docs/guides/command-reference-by-priority.md` after this change → When the file is searched for "migrate-to-umbrella" → Then zero matches are found

---

### T-034: Update `docs-site/docs/getting-started/installation.md` to match new init prompt sequence
**User Story**: US-005 | **Satisfies ACs**: AC-US5-05
**Status**: [x] Completed
**Test Plan**: Given `docs-site/docs/getting-started/installation.md` after this change → When the init flow description is inspected → Then it describes a 2-choice prompt ("Connect repositories" or "Add later"), mentions `repositories/` is always created, and contains no reference to the 4-way setup question

---

### T-035: Sweep remaining docs-site files for outdated single/multi terminology and update
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-03, AC-US5-04, AC-US5-05
**Status**: [x] Completed
**Test Plan**: Given all docs-site files not covered by T-032 through T-034 → When a final grep sweep for outdated terms runs → Then zero matches for `migrate-to-umbrella`, `resolve-structure`, `isMultiRepo`, `-single`, `-multirepo` suffix variants remain across all documentation files

---

## Verification Gates

### T-036: Run `npx tsc --noEmit` after all Phase 1-3 code changes -- assert zero TypeScript errors
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05
**Status**: [x] Completed
**Test Plan**: Given the codebase after all Phase 1-3 changes → When `npx tsc --noEmit` is run in the specweave repo → Then the compiler reports zero errors, confirming all type references to removed values have been updated

---

### T-037: Run full `npx vitest run` after Phase 2+3 -- assert zero failures and 90% coverage target
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-04
**Status**: [x] Completed
**Test Plan**: Given the codebase after T-010 through T-028 → When `npx vitest run` is executed → Then all tests pass, no test file imports a deleted module, zero tests are skipped, and coverage for changed files meets the 90% target
