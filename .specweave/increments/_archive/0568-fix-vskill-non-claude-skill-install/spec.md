---
increment: 0568-fix-vskill-non-claude-skill-install
title: Fix vskill non-Claude tool skill installation
type: bugfix
priority: P1
status: completed
created: 2026-03-18T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Fix vskill Non-Claude Tool Skill Installation

## Problem Statement

When installing skills for non-Claude AI tools (OpenCode, Cursor, Windsurf, Aider, etc.), several bugs cause broken installations:

1. Stale skill files named `{skill-name}.md` instead of `SKILL.md` persist from older vskill versions
2. Core SW plugin skills appear as flat `.md` files (e.g., `sw/ado-mapper.md`) instead of proper subdirectories (`sw/ado-mapper/SKILL.md`)
3. Name and description frontmatter may be missing for non-Claude installations
4. `specweave init` only copies skills to `.claude/skills/` -- it never invokes `vskill init` to sync skills to detected non-Claude agents
5. Stale vskill binary may be cached, causing `specweave init` to use outdated install logic

## Goals

- All non-Claude agent skill directories use `SKILL.md` (all caps) naming exclusively
- Core SW skills install as `sw/{skill-name}/SKILL.md` subdirectories, never as flat `sw/{name}.md` files
- Frontmatter (name + description) is always present in non-Claude installations
- `specweave init` triggers `vskill init` to sync skills to all detected non-Claude agents
- Migration cleans up stale files from older installations without data loss

## User Stories

### US-VSK-001: Migrate Stale Skill Files to SKILL.md Naming
**Project**: vskill

**As a** developer using a non-Claude AI tool
**I want** stale `{skill-name}.md` files automatically renamed to `SKILL.md` inside proper subdirectories
**So that** my AI tool correctly discovers installed skills

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a skill directory containing `frontend-design.md` (no `SKILL.md`), when `vskill init` runs, then the file is moved to `frontend-design/SKILL.md` and the original flat file is removed
- [x] **AC-US1-02**: Given a skill directory already containing a correct `{name}/SKILL.md` structure, when migration runs, then no changes are made (idempotent)
- [x] **AC-US1-03**: Given a flat file `sw/ado-mapper.md` in an agent's skills directory, when migration runs, then it becomes `sw/ado-mapper/SKILL.md`
- [x] **AC-US1-04**: Given both a stale `{name}.md` file and a correct `{name}/SKILL.md` directory exist, when migration runs, then the stale flat file is removed and the existing `SKILL.md` is preserved

---

### US-VSK-002: Enforce Frontmatter on Non-Claude Installations
**Project**: vskill

**As a** developer using a non-Claude AI tool
**I want** every installed skill file to contain `name` and `description` frontmatter
**So that** my AI tool can display skill metadata correctly

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given a SKILL.md file missing `name:` frontmatter, when `installSymlink` or `installCopy` writes the file, then `name:` is injected from the skill name
- [x] **AC-US2-02**: Given a SKILL.md file missing `description:` frontmatter, when the file is written, then `description:` is extracted from the first non-heading line or derived from the skill name
- [x] **AC-US2-03**: Given the migration function encounters a stale file without frontmatter, when it migrates to `SKILL.md`, then frontmatter is added via `ensureFrontmatter()`

---

### US-VSK-003: Integrate vskill init into specweave init
**Project**: specweave

**As a** developer who runs `specweave init` in a project with non-Claude AI tools installed
**I want** `specweave init` to automatically invoke `vskill init` after installing Claude skills
**So that** skills are synced to all detected AI agents without a separate manual step

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given vskill is installed globally (resolvable via `which vskill` or `npx vskill`), when `specweave init` completes Claude skill installation, then it spawns `vskill init` in the project root
- [x] **AC-US3-02**: Given vskill is NOT installed, when `specweave init` runs, then it skips non-Claude sync gracefully with a dim hint message and does not fail
- [x] **AC-US3-03**: Given `vskill init` fails (non-zero exit), when `specweave init` runs, then it logs a warning but does not block the overall init process

---

### US-VSK-004: Core SW Skills Install as Subdirectories
**Project**: vskill

**As a** developer using a non-Claude AI tool
**I want** core SW skills to install as `sw/{skill-name}/SKILL.md` subdirectories
**So that** the directory structure matches the canonical format and agents can discover skills consistently

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given `syncCoreSkills` runs for a non-Claude agent, when it installs skill `architect`, then the file is written to `{agentSkillsDir}/sw/architect/SKILL.md` (not `sw/architect.md`)
- [x] **AC-US4-02**: Given agent files exist (e.g., `agents/frontend.md`), when a core skill is synced, then agent files are written alongside SKILL.md in the same subdirectory
- [x] **AC-US4-03**: Given stale flat files exist from a prior sync (e.g., `sw/pm.md`), when `syncCoreSkills` runs, then stale flat files are cleaned up after the new subdirectory structure is created

---

### US-VSK-005: Comprehensive Test Coverage for Non-Claude Install Paths
**Project**: vskill

**As a** maintainer of vskill
**I want** test coverage for all non-Claude agent installation and migration paths
**So that** regressions in skill naming, frontmatter, and directory structure are caught before release

**Acceptance Criteria**:
- [x] **AC-US5-01**: Given unit tests for `migrateStaleSkillFiles()`, when a flat `.md` file exists, then the test verifies it is moved to `{name}/SKILL.md`
- [x] **AC-US5-02**: Given unit tests for `installSymlink` with non-Claude agents, when content lacks frontmatter, then the test verifies frontmatter is injected
- [x] **AC-US5-03**: Given unit tests for `syncCoreSkills`, when run against a mock agent, then the test verifies `sw/{name}/SKILL.md` structure (not flat files)
- [x] **AC-US5-04**: Given integration tests for `initCommand`, when stale files exist pre-init, then the test verifies migration runs and stale files are removed

## Out of Scope

- Rewriting the Claude Code plugin installation path (`.claude/skills/` works correctly already)
- Adding new non-Claude agent definitions to the registry
- Changing the canonical `.agents/skills/` source-of-truth structure
- Global (non-project) skill installation migration

## Non-Functional Requirements

- **Backward Compatibility**: Migration must not delete any SKILL.md content -- only rename/restructure
- **Idempotency**: Running `vskill init` or migration multiple times produces identical results
- **Performance**: Migration scans only agent skill directories, not the entire project tree
- **Security**: Migration must not follow symlinks outside the project root (existing path traversal guard applies)

## Edge Cases

- Both `{name}.md` and `{name}/SKILL.md` exist: preserve SKILL.md, remove flat file
- Symlinked skill directories: migration should skip symlinks (they point to canonical source)
- Empty/corrupt `.md` files: migration should still rename, `ensureFrontmatter` handles content
- Agent skills directory does not exist yet: skip migration for that agent (no-op)
- vskill binary not in PATH but available via npx: `specweave init` should try `npx vskill init` as fallback

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| Migration deletes user-customized skill files | 0.2 | 8 | 1.6 | Only rename, never delete content; preserve existing SKILL.md over flat files |
| vskill version mismatch between specweave and vskill | 0.3 | 5 | 1.5 | Use `npx vskill@latest init` or version check before spawning |
| Race condition if user runs specweave init and vskill init concurrently | 0.1 | 4 | 0.4 | File operations are atomic (rename); acceptable risk |

## Technical Notes

- `canonical.ts` already writes `SKILL.md` correctly -- the issue is stale files from older versions
- `ensureFrontmatter()` in `frontmatter.ts` already handles name + description injection -- it just needs to be called during migration
- `syncCoreSkills()` uses `installSymlink()` which writes correct `SKILL.md` -- the flat file issue is from a prior version's sync logic
- `specweave` spawns `vskill init` as a child process -- no library coupling between the two packages
- The `COPY_FALLBACK_AGENTS` set in canonical.ts (currently only `claude-code`) handles agents with broken symlink support

## Success Metrics

- Zero stale `{name}.md` flat files remain after running `vskill init` on a project with non-Claude agents
- `specweave init` successfully syncs skills to all detected non-Claude agents in a single command
- All non-Claude skill installations contain valid `name:` and `description:` frontmatter
- Test coverage for non-Claude install paths reaches 90%+
