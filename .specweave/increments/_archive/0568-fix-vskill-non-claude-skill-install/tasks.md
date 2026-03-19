---
increment: 0568-fix-vskill-non-claude-skill-install
generated: 2026-03-18
---

# Tasks: Fix vskill Non-Claude Tool Skill Installation

## US-VSK-001: Migrate Stale Skill Files to SKILL.md Naming

### T-001: Create `installer/migrate.ts` with `migrateStaleSkillFiles()`
**User Story**: US-VSK-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Status**: [x] Completed
**Test**: Given a skills directory containing stale `{name}.md` flat files → When `migrateStaleSkillFiles(skillsDir)` is called → Then each flat file is moved to `{name}/SKILL.md`, symlinks and already-correct `{name}/SKILL.md` structures are left untouched, both-exist scenario removes the flat file while preserving the existing SKILL.md, and the returned `MigrationResult` reflects accurate migrated/removed counts

### T-002: Create `installer/migrate.test.ts` with unit tests for all AC-US1-* scenarios
**User Story**: US-VSK-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Status**: [x] Completed
**Test**: Given temp directories set up for each AC scenario (flat file only, correct structure only, flat `sw/name.md`, flat+dir coexist) → When tests run via `npx vitest run` → Then all four cases pass: flat renamed to subdir/SKILL.md, correct structure unchanged, nested sw path migrated, duplicate flat removed with existing SKILL.md preserved

### T-003: Wire `migrateStaleSkillFiles()` into `vskill/src/commands/init.ts`
**User Story**: US-VSK-001 | **Satisfies ACs**: AC-US1-01, AC-US1-03
**Status**: [x] Completed
**Test**: Given a project directory with stale `{name}.md` files under a detected agent's skills dir → When `vskill init` runs → Then `migrateStaleSkillFiles()` is called for each detected agent BEFORE `syncCoreSkills()` and stale flat files are absent after init completes

---

## US-VSK-002: Enforce Frontmatter on Non-Claude Installations

### T-004: Call `ensureFrontmatter()` inside `migrateStaleSkillFiles()` when creating new SKILL.md
**User Story**: US-VSK-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] Completed
**Test**: Given a stale flat file `frontend-design.md` that has no YAML frontmatter → When `migrateStaleSkillFiles()` processes it → Then the resulting `frontend-design/SKILL.md` contains a `name:` field derived from the skill name and a `description:` field extracted from the first non-heading line or derived from the name

### T-005: Add frontmatter injection tests to `migrate.test.ts`
**User Story**: US-VSK-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] Completed
**Test**: Given migrate.test.ts scenarios with frontmatter-less stale files and files with existing valid frontmatter → When tests run → Then assertions confirm `name:` and `description:` are present in the migrated SKILL.md content and a file already containing valid frontmatter passes through unchanged

---

## US-VSK-003: Integrate vskill init into specweave init

### T-006: Create `specweave/src/cli/helpers/init/vskill-init-invoker.ts` with 3-tier fallback
**User Story**: US-VSK-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Status**: [x] Completed
**Test**: Given the 3-tier invocation logic (global `vskill init --yes` → `npx vskill@^0.5.0 init --yes` → graceful skip) → When `ensureVskillInit(projectRoot)` is called in each tier scenario → Then tier-1 uses the global binary and returns `invoked: true`, tier-2 falls back to npx with correct registry flags, tier-3 returns `{ invoked: false, skipped: true }` with a dim hint message and no thrown error

### T-007: Create `vskill-init-invoker.test.ts` with unit tests for AC-US3-01/02/03
**User Story**: US-VSK-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Status**: [x] Completed
**Test**: Given mocked `which vskill` and `spawnSync` calls → When each tier scenario is exercised (found + success, found + non-zero exit, not found) → Then AC-US3-01 returns `invoked: true`, AC-US3-02 returns `skipped: true` without throwing, AC-US3-03 logs warning and returns without blocking the caller

### T-008: Wire `ensureVskillInit()` into `specweave/src/cli/commands/init.ts`
**User Story**: US-VSK-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Status**: [x] Completed
**Test**: Given `specweave init` running in a project where vskill is globally available → When init completes plugin installation → Then `ensureVskillInit()` is invoked after plugin install, a non-zero vskill exit logs a warning but does not fail the overall init process, and absence of vskill prints a dim hint without error

### T-009: Export `ensureVskillInit` from `specweave/src/cli/helpers/init/index.ts`
**User Story**: US-VSK-003 | **Satisfies ACs**: AC-US3-01
**Status**: [x] Completed
**Test**: Given the `init/index.ts` barrel file → When `ensureVskillInit` is imported from the helpers/init barrel → Then the import resolves without error and the function is callable with a projectRoot string

---

## US-VSK-004: Core SW Skills Install as Subdirectories

### T-010: Add integration test to `core-skills/sync.test.ts` verifying `sw/{name}/SKILL.md` structure
**User Story**: US-VSK-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03
**Status**: [x] Completed
**Test**: Given `syncCoreSkills()` runs against a mock non-Claude agent with a temp skills directory that has pre-existing stale flat files (`sw/pm.md`) → When the sync completes → Then `{agentSkillsDir}/sw/architect/SKILL.md` exists (not `sw/architect.md`), agent files are written alongside SKILL.md in the same subdirectory, and stale flat files like `sw/pm.md` are absent

---

## US-VSK-005: Comprehensive Test Coverage for Non-Claude Install Paths

### T-011: Verify unit test coverage for `migrateStaleSkillFiles()` flat-file migration (AC-US5-01)
**User Story**: US-VSK-005 | **Satisfies ACs**: AC-US5-01
**Status**: [x] Completed
**Test**: Given the migrate.test.ts suite with all AC-US1-* test cases in place → When `npx vitest run --coverage` is run on `installer/migrate.ts` → Then the flat `.md` to `{name}/SKILL.md` migration path achieves >= 90% line coverage as required by the increment coverage target

### T-012: Verify unit test for `installSymlink` frontmatter injection (AC-US5-02)
**User Story**: US-VSK-005 | **Satisfies ACs**: AC-US5-02
**Status**: [x] Completed
**Test**: Given a test calling `installSymlink` or `installCopy` with skill content that has no frontmatter → When the test asserts the written SKILL.md → Then `name:` and `description:` fields are present in the file confirming `ensureFrontmatter()` was invoked during install

### T-013: Verify `syncCoreSkills` unit test confirms `sw/{name}/SKILL.md` structure (AC-US5-03)
**User Story**: US-VSK-005 | **Satisfies ACs**: AC-US5-03
**Status**: [x] Completed
**Test**: Given unit tests for `syncCoreSkills` using a mock non-Claude agent in a temp directory → When `npx vitest run` executes the sync.test.ts suite → Then assertions confirm `sw/{skill-name}/SKILL.md` exists and no flat `sw/{skill-name}.md` files are present for any synced core skill

### T-014: Add integration test for `initCommand` with pre-existing stale files (AC-US5-04)
**User Story**: US-VSK-005 | **Satisfies ACs**: AC-US5-04
**Status**: [x] Completed
**Test**: Given a temp project directory with stale flat skill files placed in an agent's skills dir before `initCommand` runs → When the integration test invokes `initCommand` → Then post-init assertions confirm all stale flat files have been removed and correct `{name}/SKILL.md` structures exist in their place

### T-015: Add edge case tests (symlinks, empty files, nested sw/ paths, both flat+dir coexist)
**User Story**: US-VSK-005 | **Satisfies ACs**: AC-US1-04, AC-US5-01, AC-US5-04
**Status**: [x] Completed
**Test**: Given edge case fixtures in migrate.test.ts (symlinked `pm.md`, 0-byte `empty.md`, `sw/ado-mapper.md`, `pm.md` alongside `pm/SKILL.md`) → When `migrateStaleSkillFiles()` runs → Then symlinks are skipped unchanged, empty files produce a frontmatter-only SKILL.md, nested sw paths are migrated one level deep, and the flat+dir coexist case leaves SKILL.md intact while removing the stale flat file
