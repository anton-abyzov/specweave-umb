---
increment: 0572-enforce-skill-md-naming
title: Enforce SKILL.md naming at install time for non-Claude tools
type: bugfix
priority: P1
status: completed
created: 2026-03-18T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Enforce SKILL.md Naming at Install Time

## Problem Statement

When installing skills for non-Claude AI tools (Cursor, Copilot, etc.), `copyPluginFiltered()` in `add.ts` copies `.md` files preserving their original source filename instead of renaming to `SKILL.md`. If a plugin ships `frontend-design.md` instead of `SKILL.md`, it gets installed with the wrong name and the target agent cannot discover it. Increment 0568 added reactive migration for stale files, but the root cause at install time was never fixed.

## Goals

- Fix the root cause in `copyPluginFiltered()` so `.md` files are renamed to `SKILL.md` at install time
- Add a reusable `ensureSkillMdNaming()` post-install enforcement function
- Wire enforcement into all install paths (add, update, init) for defense in depth
- Cover the fix and enforcement with unit tests

## User Stories

### US-001: Fix copyPluginFiltered rename logic
**Project**: vskill
**As a** skill author
**I want** `copyPluginFiltered()` to rename non-SKILL.md files to SKILL.md during install
**So that** skills installed for non-Claude agents always have the correct filename

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a plugin with `frontend-design.md` (no `SKILL.md`), when `copyPluginFiltered()` copies the skill directory, then the file is written as `SKILL.md` with frontmatter injected via `ensureFrontmatter()`
- [x] **AC-US1-02**: Given a plugin with an existing `SKILL.md`, when `copyPluginFiltered()` copies the skill directory, then `SKILL.md` is copied normally with frontmatter (existing behavior preserved)
- [x] **AC-US1-03**: Given a plugin with `README.md`, `CHANGELOG.md`, or `LICENSE.md` alongside other `.md` files, when `copyPluginFiltered()` processes the directory, then those documentation files are skipped from rename consideration and copied as-is
- [x] **AC-US1-04**: Given a plugin with multiple non-SKILL.md content files (e.g., `alpha.md` and `beta.md`), when `copyPluginFiltered()` processes the directory, then the first alphabetically (`alpha.md`) is renamed to `SKILL.md`

---

### US-002: Create ensureSkillMdNaming post-install guard
**Project**: vskill
**As a** vskill maintainer
**I want** a reusable `ensureSkillMdNaming(skillDir)` function in the installer module
**So that** any install path can enforce correct naming as a safety net

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given a skill directory containing `SKILL.md`, when `ensureSkillMdNaming()` runs, then it is a no-op (idempotent)
- [x] **AC-US2-02**: Given a skill directory with `frontend-design.md` but no `SKILL.md`, when `ensureSkillMdNaming()` runs, then the file is renamed to `SKILL.md` with frontmatter applied
- [x] **AC-US2-03**: Given a skill directory with multiple `.md` files and no `SKILL.md`, when `ensureSkillMdNaming()` runs, then the first alphabetically (excluding README.md, CHANGELOG.md, LICENSE.md) is renamed to `SKILL.md`
- [x] **AC-US2-04**: Given a skill directory with only `README.md` and no other `.md` files, when `ensureSkillMdNaming()` runs, then no rename occurs (no content file to promote)
- [x] **AC-US2-05**: Given `ensureSkillMdNaming()` is exported from `src/installer/migrate.ts`, when imported from other modules, then it is accessible without circular dependencies

---

### US-003: Wire enforcement into all install paths
**Project**: vskill
**As a** vskill user
**I want** SKILL.md naming enforced on add, update, and init commands
**So that** no install path can produce incorrectly named skill files

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given `vskill add` installs a plugin, when installation completes, then `ensureSkillMdNaming()` runs on every skill directory that was written
- [x] **AC-US3-02**: Given `vskill update` updates a skill, when the update completes, then `ensureSkillMdNaming()` runs on every skill directory that was updated
- [x] **AC-US3-03**: Given `vskill init` runs migration, when migration completes, then `ensureSkillMdNaming()` runs alongside `migrateStaleSkillFiles()` on each agent's skill directories

---

### US-004: Unit tests for fix and enforcement
**Project**: vskill
**As a** vskill maintainer
**I want** comprehensive tests for both the `copyPluginFiltered` fix and `ensureSkillMdNaming`
**So that** regressions are caught automatically

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given a test with a mock skill directory containing `design.md`, when `ensureSkillMdNaming()` runs, then `SKILL.md` exists with correct frontmatter and `design.md` is removed
- [x] **AC-US4-02**: Given a test with a mock skill directory already containing `SKILL.md`, when `ensureSkillMdNaming()` runs, then no files are modified (idempotent test)
- [x] **AC-US4-03**: Given a test with `README.md` and `guide.md`, when `ensureSkillMdNaming()` runs, then `guide.md` becomes `SKILL.md` and `README.md` is untouched
- [x] **AC-US4-04**: Given a test with `beta.md` and `alpha.md`, when `ensureSkillMdNaming()` runs, then `alpha.md` (first alphabetically) becomes `SKILL.md`
- [x] **AC-US4-05**: Given tests for the `copyPluginFiltered` fix, when a plugin source has `custom-name.md` instead of `SKILL.md`, then the installed output contains `SKILL.md` with frontmatter

## Out of Scope

- Changing how `SKILL.md` is handled in the canonical symlink path (`installSymlink`/`installCopy` in `canonical.ts`) -- these already write `SKILL.md` correctly
- Modifying the `migrateStaleSkillFiles()` function itself -- it handles flat-file-to-subdirectory migration, which is a different concern
- Renaming files inside `agents/` subdirectories -- those are agent definition files, not skill content

## Non-Functional Requirements

- **Idempotency**: `ensureSkillMdNaming()` must be safe to call multiple times on the same directory
- **Performance**: File rename is a single `readFileSync` + `writeFileSync` + `unlinkSync` per skill dir -- negligible overhead at install time
- **Compatibility**: Must work with existing plugin structures and not break plugins that already ship correct `SKILL.md`

## Edge Cases

- Skill directory with only documentation files (README.md, LICENSE.md): no rename, no error
- Empty skill directory (no `.md` files at all): no-op
- Skill directory where `SKILL.md` already exists alongside other `.md` files: no-op (SKILL.md takes precedence)
- File with `.MD` uppercase extension: not matched (Node.js `endsWith('.md')` is case-sensitive, consistent with existing behavior)

## Technical Notes

- `copyPluginFiltered()` is at `vskill/src/commands/add.ts` lines 648-670
- `ensureSkillMdNaming()` should be added to `vskill/src/installer/migrate.ts` alongside existing `migrateStaleSkillFiles()`
- `ensureFrontmatter()` from `vskill/src/installer/frontmatter.ts` handles frontmatter injection
- Documentation skip list: `README.md`, `CHANGELOG.md`, `LICENSE.md`
- When multiple candidates exist, sort alphabetically and pick first

## Success Metrics

- All non-Claude agent install paths produce `SKILL.md` -- verified by tests
- Zero regressions on existing `SKILL.md` handling -- verified by existing test suite passing
