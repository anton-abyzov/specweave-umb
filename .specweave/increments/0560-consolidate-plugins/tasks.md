# Tasks: Consolidate 8 Core Plugins into 1 Unified Plugin

## Task Notation

- `[T-###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started | `[x]`: Completed
- Model hints: haiku (simple moves), sonnet (import fixups), opus (architecture)

---

## Phase 1: File Migration — Leaf Plugins

### T-001: Move specweave-diagrams into core plugin
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-04 | **Status**: [x] Completed

**Description**: Move `specweave-diagrams` skills and commands into the core specweave plugin. This is the simplest plugin (1 skill, 1 command, no lib).

**Implementation Details**:
- Copy `plugins/specweave-diagrams/skills/diagrams/` → `plugins/specweave/skills/diagrams/`
- Copy `plugins/specweave-diagrams/commands/diagrams-generate.md` → `plugins/specweave/commands/diagrams-generate.md`
- Delete `plugins/specweave-diagrams/`

**Test Plan**:
- **File**: Manual verification
- **Tests**:
  - **TC-001**: Skill directory exists at new location
    - Given specweave-diagrams skills moved to plugins/specweave/skills/diagrams/
    - When PluginLoader scans plugins/specweave/skills/
    - Then diagrams skill is discovered with correct SKILL.md
  - **TC-002**: Command file exists at new location
    - Given diagrams-generate.md moved to plugins/specweave/commands/
    - When PluginLoader scans plugins/specweave/commands/
    - Then diagrams-generate command is discovered

**Dependencies**: None

---

### T-002: Move specweave-media into core plugin [P]
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-04 | **Status**: [x] Completed

**Description**: Move `specweave-media` skills into the core specweave plugin. 3 skills, 0 commands, no lib.

**Implementation Details**:
- Copy `plugins/specweave-media/skills/image/` → `plugins/specweave/skills/image/`
- Copy `plugins/specweave-media/skills/video/` → `plugins/specweave/skills/video/`
- Copy `plugins/specweave-media/skills/remotion/` → `plugins/specweave/skills/remotion/`
- Delete `plugins/specweave-media/`

**Test Plan**:
- **Tests**:
  - **TC-003**: All 3 media skills discoverable
    - Given image/, video/, remotion/ dirs exist under plugins/specweave/skills/
    - When PluginLoader scans
    - Then all 3 skills are found with valid SKILL.md

**Dependencies**: None

---

### T-003: Move specweave-docs into core plugin [P]
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-04 | **Status**: [x] Completed

**Description**: Move `specweave-docs` commands into the core specweave plugin. 0 skills, 7 commands, no lib.

**Implementation Details**:
- Copy `plugins/specweave-docs/commands/build.md` → `plugins/specweave/commands/docs-build.md`
- Copy `plugins/specweave-docs/commands/generate.md` → `plugins/specweave/commands/docs-generate.md`
- Copy `plugins/specweave-docs/commands/health.md` → `plugins/specweave/commands/docs-health.md`
- Copy `plugins/specweave-docs/commands/init.md` → `plugins/specweave/commands/docs-init.md`
- Copy `plugins/specweave-docs/commands/organize.md` → `plugins/specweave/commands/docs-organize.md`
- Copy `plugins/specweave-docs/commands/validate.md` → `plugins/specweave/commands/docs-validate.md`
- Copy `plugins/specweave-docs/commands/view.md` → `plugins/specweave/commands/docs-view.md`
- Delete `plugins/specweave-docs/`

**Test Plan**:
- **Tests**:
  - **TC-004**: All 7 docs commands discoverable with domain-prefixed names
    - Given docs commands moved with "docs-" prefix
    - When PluginLoader scans plugins/specweave/commands/
    - Then docs-build, docs-generate, docs-health, docs-init, docs-organize, docs-validate, docs-view are found

**Dependencies**: None

---

## Phase 2: File Migration — Feature Plugins

### T-004: Move specweave-release into core plugin
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [x] Completed

**Description**: Move `specweave-release` skills, commands, and lib into core. 1 skill, 5 commands, 2 lib files.

**Implementation Details**:
- Copy `plugins/specweave-release/skills/release-expert/` → `plugins/specweave/skills/release-expert/`
- Copy `plugins/specweave-release/commands/align.md` → `plugins/specweave/commands/release-align.md`
- Copy remaining 4 commands with "release-" prefix
- Create `plugins/specweave/lib/features/release/`
- Copy `plugins/specweave-release/lib/dora-tracker.ts` → `plugins/specweave/lib/features/release/`
- Copy `plugins/specweave-release/lib/dashboard-generator.ts` → same target
- Copy hooks if present → `plugins/specweave/hooks/v2/integrations/release-post-task.sh`
- Delete `plugins/specweave-release/`

**Test Plan**:
- **Tests**:
  - **TC-005**: Release skill and commands discoverable
    - Given release-expert skill and 5 release commands moved
    - When PluginLoader scans
    - Then all are discovered at new locations
  - **TC-006**: Release lib files accessible
    - Given dora-tracker.ts and dashboard-generator.ts in lib/features/release/
    - When imported from within the plugin
    - Then modules resolve correctly

**Dependencies**: None

---

## Phase 3: File Migration — Integration Plugins

### T-005: Move specweave-github into core plugin
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-07 | **Status**: [x] Completed

**Description**: Move `specweave-github` into core. This is the largest satellite with ~40 lib files. Must be done BEFORE jira/ado because they import from github's lib.

**Implementation Details**:
- Copy `plugins/specweave-github/skills/` (4 dirs) → `plugins/specweave/skills/`
- Copy `plugins/specweave-github/commands/` (10 files) → `plugins/specweave/commands/` with "github-" prefix
- Create `plugins/specweave/lib/integrations/github/`
- Copy all `plugins/specweave-github/lib/*.ts` and `*.js` → `plugins/specweave/lib/integrations/github/`
- Copy `plugins/specweave-github/hooks/` → `plugins/specweave/hooks/v2/integrations/`
- Copy `plugins/specweave-github/reference/` → `plugins/specweave/reference/github/`
- Delete `plugins/specweave-github/`

**Test Plan**:
- **Tests**:
  - **TC-007**: All 4 github skills discoverable at new location
    - Given github-sync, github-issue-standard, github-multi-project, pr-review moved
    - When PluginLoader scans
    - Then all 4 skills found
  - **TC-008**: All 10 github commands domain-prefixed
    - Given commands renamed with "github-" prefix
    - When PluginLoader scans commands/
    - Then github-clone, github-close, github-create, github-push, github-pull, github-reconcile, github-status, github-sync, github-cleanup-duplicates, github-update-user-story found
  - **TC-009**: GitHub lib files at new path
    - Given ~40 lib files in lib/integrations/github/
    - When files are listed
    - Then all .ts/.js files present

**Dependencies**: T-001, T-002, T-003, T-004

---

### T-006: Move specweave-jira into core plugin
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-07 | **Status**: [x] Completed

**Description**: Move `specweave-jira` into core. ~30 lib files. Imports from github's AC checkbox sync.

**Implementation Details**:
- Copy `plugins/specweave-jira/skills/` (3 dirs) → `plugins/specweave/skills/`
- Copy `plugins/specweave-jira/commands/` (11 files) → `plugins/specweave/commands/` with "jira-" prefix
- Create `plugins/specweave/lib/integrations/jira/`
- Copy all `plugins/specweave-jira/lib/*.ts` and `*.js` → `plugins/specweave/lib/integrations/jira/`
- Copy hooks → `plugins/specweave/hooks/v2/integrations/jira-post-task.sh`
- Copy reference/ → `plugins/specweave/reference/jira/`
- Copy scripts/ → `plugins/specweave/scripts/jira/`
- Delete `plugins/specweave-jira/`

**Test Plan**:
- **Tests**:
  - **TC-010**: All 3 jira skills and 11 commands discoverable
    - Given jira skills and commands moved with domain prefix
    - When PluginLoader scans
    - Then all found
  - **TC-011**: Jira lib files at new path
    - Given ~30 lib files in lib/integrations/jira/
    - When files listed
    - Then all present

**Dependencies**: T-005 (github must be moved first)

---

### T-007: Move specweave-ado into core plugin
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-07 | **Status**: [x] Completed

**Description**: Move `specweave-ado` into core. ~30 lib files. Imports from github's AC checkbox sync.

**Implementation Details**:
- Copy `plugins/specweave-ado/skills/` (4 dirs) → `plugins/specweave/skills/`
- Copy `plugins/specweave-ado/commands/` (11 files) → `plugins/specweave/commands/` with "ado-" prefix
- Create `plugins/specweave/lib/integrations/ado/`
- Copy all `plugins/specweave-ado/lib/*.ts` and `*.js` → `plugins/specweave/lib/integrations/ado/`
- Copy hooks → `plugins/specweave/hooks/v2/integrations/`
- Copy reference/ → `plugins/specweave/reference/ado/`
- Copy scripts/ → `plugins/specweave/scripts/ado/`
- Delete `plugins/specweave-ado/`

**Test Plan**:
- **Tests**:
  - **TC-012**: All 4 ado skills and 11 commands discoverable
    - Given ado skills and commands moved with domain prefix
    - When PluginLoader scans
    - Then all found

**Dependencies**: T-005 (github must be moved first)

---

## Phase 4: Import Path Fixups

### T-008: Fix import paths in moved integration lib files
**User Story**: US-001 | **Satisfies ACs**: AC-US1-06 | **Status**: [x] Completed

**Description**: Update all relative import paths in the ~100 lib files that were moved from satellite plugins to their new locations under `lib/integrations/` and `lib/features/`.

**Implementation Details**:
- **GitHub lib files** (`lib/integrations/github/`):
  - `../../specweave/lib/vendor/` → `../vendor/` (now in same plugin)
  - `../../../src/` → `../../../../src/` (one level deeper)
- **JIRA lib files** (`lib/integrations/jira/`):
  - `../../specweave/lib/vendor/` → `../vendor/`
  - `../../specweave-github/lib/` → `../github/` (now sibling dir)
  - `../../../src/` → `../../../../src/`
- **ADO lib files** (`lib/integrations/ado/`):
  - `../../specweave/lib/vendor/` → `../vendor/`
  - `../../specweave-github/lib/` → `../github/`
  - `../../../src/` → `../../../../src/`
- **Release lib files** (`lib/features/release/`):
  - `../../specweave/lib/vendor/` → `../../vendor/`

**Test Plan**:
- **File**: TypeScript compilation
- **Tests**:
  - **TC-013**: All moved lib files compile
    - Given all import paths updated
    - When `npx tsc --noEmit` runs
    - Then 0 import resolution errors in moved files

**Dependencies**: T-005, T-006, T-007

---

### T-009: Fix import paths in src/ files referencing satellite plugins
**User Story**: US-001 | **Satisfies ACs**: AC-US1-06 | **Status**: [x] Completed

**Description**: Update import paths in `src/` files that import from satellite plugin directories.

**Implementation Details**:
- `src/sync/sync-coordinator.ts`: `../../plugins/specweave-github/lib/github-client-v2.js` → `../../plugins/specweave/lib/integrations/github/github-client-v2.js`
- Scan all `src/integrations/ado/` files for `../../plugins/specweave-ado/lib/` → `../../plugins/specweave/lib/integrations/ado/`
- Scan all `src/` files for any remaining `specweave-github`, `specweave-jira`, `specweave-ado` references

**Test Plan**:
- **Tests**:
  - **TC-014**: No references to satellite plugin dirs in src/
    - Given all src/ imports updated
    - When `grep -r "specweave-github\|specweave-jira\|specweave-ado\|specweave-release\|specweave-diagrams\|specweave-media\|specweave-docs" src/ --include="*.ts"`
    - Then 0 matches

**Dependencies**: T-008

---

## Phase 5: Skill & Hook Updates

### T-010: Update SKILL.md hook path references
**User Story**: US-002, US-003 | **Satisfies ACs**: AC-US2-06, AC-US3-02 | **Status**: [x] Completed

**Description**: Update `${CLAUDE_PLUGIN_ROOT}/hooks/...` references in migrated SKILL.md files to point to the new hook locations.

**Implementation Details**:
- Scan all SKILL.md files under `plugins/specweave/skills/` for hook path references
- Update paths from satellite plugin hook structure to unified hook structure
- Verify all referenced hook scripts exist at new paths

**Test Plan**:
- **Tests**:
  - **TC-015**: All SKILL.md hook references resolve
    - Given SKILL.md hook paths updated
    - When each referenced hook script path checked
    - Then all files exist

**Dependencies**: T-005, T-006, T-007

---

### T-011: Update PLUGINS-INDEX.md
**User Story**: US-002 | **Satisfies ACs**: AC-US2-07 | **Status**: [x] Completed

**Description**: Rewrite PLUGINS-INDEX.md to reflect single unified plugin with all 44 skills.

**Implementation Details**:
- Replace 8-plugin tables with single plugin entry
- Preserve all trigger keywords
- Update totals (1 plugin, 44 skills)
- Keep progressive loading pattern description
- Update quick lookup table (all intents → `specweave (sw)`)

**Test Plan**:
- **Tests**:
  - **TC-016**: All trigger keywords preserved
    - Given PLUGINS-INDEX.md rewritten
    - When compared to old triggers list
    - Then all trigger keywords present

**Dependencies**: T-001 through T-007

---

## Phase 6: Marketplace & Installer

### T-012: Update marketplace.json to single plugin entry
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01 | **Status**: [x] Completed

**Description**: Replace 8 plugin entries in marketplace.json with 1 unified entry.

**Implementation Details**:
- Replace `plugins` array with single `sw` entry
- Update description to cover all capabilities
- Keep version and author unchanged

**Test Plan**:
- **Tests**:
  - **TC-017**: marketplace.json has exactly 1 plugin entry
    - Given marketplace.json updated
    - When parsed
    - Then plugins array has length 1 and plugins[0].name === "sw"

**Dependencies**: T-001 through T-007

---

### T-013: Add satellite names to REMOVED_PLUGINS
**User Story**: US-004 | **Satisfies ACs**: AC-US4-07, AC-US4-08 | **Status**: [x] Completed

**Description**: Update `cleanup-stale-plugins.ts` to include all 7 satellite plugin names in REMOVED_PLUGINS set.

**Implementation Details**:
- Add `sw-github`, `sw-jira`, `sw-ado`, `sw-release`, `sw-diagrams`, `docs`, `sw-media` to `REMOVED_PLUGINS`
- Update `plugin-scope.ts` to remove satellite scope entries

**Test Plan**:
- **Tests**:
  - **TC-018**: Stale satellite plugins detected and cleaned
    - Given REMOVED_PLUGINS includes all 7 satellite names
    - When cleanupStalePlugins runs against settings with satellite entries
    - Then all satellite entries removed

**Dependencies**: T-012

---

### T-014: Update plugin.json for unified plugin
**User Story**: US-001, US-004 | **Satisfies ACs**: AC-US1-05, AC-US4-01 | **Status**: [x] Completed

**Description**: Update `plugins/specweave/.claude-plugin/plugin.json` to reflect the expanded plugin scope.

**Implementation Details**:
- Update description to mention all capabilities (sync, diagrams, media, docs, release)
- Update keywords to include integration triggers
- Bump version if needed

**Test Plan**:
- **Tests**:
  - **TC-019**: plugin.json validates
    - Given plugin.json updated
    - When PluginLoader.validateManifest runs
    - Then validation passes

**Dependencies**: T-001 through T-007

---

## Phase 7: Lockfile Migration

### T-015: Implement satellite-to-unified lockfile migration
**User Story**: US-007 | **Satisfies ACs**: AC-US7-01, AC-US7-02, AC-US7-03, AC-US7-05, AC-US7-06 | **Status**: [x] Completed

**Description**: Add `migrateSatelliteToUnifiedLock()` to plugin-copier.ts and integrate it into init/refresh flows.

**Implementation Details**:
- Add function to remove satellite entries from global `plugins-lock.json`
- Add function to clean satellite entries from project `vskill.lock`
- Call from `refreshPluginsCommand()` before plugin install
- Call from `installAllPlugins()` during init
- Ensure idempotency and graceful failure

**Test Plan**:
- **File**: `tests/unit/plugins/lockfile-migration.test.ts`
- **Tests**:
  - **TC-020**: Global lockfile migration removes satellites
    - Given plugins-lock.json with 8 entries (sw + 7 satellites)
    - When migrateSatelliteToUnifiedLock runs
    - Then only sw entry remains
  - **TC-021**: Migration is idempotent
    - Given migration already ran
    - When migrateSatelliteToUnifiedLock runs again
    - Then result.migratedCount === 0
  - **TC-022**: Migration failure doesn't block install
    - Given read permission denied on lockfile
    - When migrateSatelliteToUnifiedLock runs
    - Then returns {migratedCount: 0} without throwing

**Dependencies**: T-012, T-013

---

## Phase 8: Test Migration

### T-016: Update test import paths for integration plugins
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01 | **Status**: [x] Completed

**Description**: Update all test files that reference satellite plugin paths.

**Implementation Details**:
- `tests/integration/external-tools/github/` — update imports from `plugins/specweave-github/lib/` to `plugins/specweave/lib/integrations/github/`
- `tests/unit/plugins/github/` — same import updates
- `tests/integration/external-tools/jira/` — update jira paths
- `tests/unit/plugins/jira/` — same
- `tests/integration/external-tools/ado/` — update ado paths
- `tests/unit/plugins/ado/` — same
- `tests/e2e/sync/` — update all provider paths

**Test Plan**:
- **Tests**:
  - **TC-023**: All test files compile
    - Given test import paths updated
    - When `npx tsc --noEmit`
    - Then 0 errors in test files

**Dependencies**: T-008, T-009

---

### T-017: Update test expectations for single-plugin installation
**User Story**: US-005 | **Satisfies ACs**: AC-US5-02, AC-US5-03, AC-US5-05 | **Status**: [x] Completed

**Description**: Update tests that assert multi-plugin behavior (e.g., "8 plugins installed") to expect single-plugin behavior.

**Implementation Details**:
- `tests/unit/plugins/plugin-copier.test.ts` — update expected plugin count
- `tests/unit/plugins/marketplace-parser.test.ts` — update expected entry count
- `tests/plugin-validation/` — update path assertions
- `tests/unit/plugins/installation-health-checker.test.ts` — add stale satellite detection test

**Test Plan**:
- **Tests**:
  - **TC-024**: All plugin system tests pass
    - Given test expectations updated
    - When `npx vitest run tests/unit/plugins/`
    - Then 0 failures

**Dependencies**: T-016

---

## Phase 9: Documentation

### T-018: Update docs-site pages referencing plugins
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-04, AC-US6-06 | **Status**: [x] Completed

**Description**: Update documentation pages to reflect unified plugin architecture.

**Implementation Details**:
- `docs-site/docs/overview/plugins-ecosystem.md` — unified architecture description
- `docs-site/docs/guides/lazy-plugin-loading.md` — single-plugin loading
- `docs-site/docs/guides/github-integration.md` — unified plugin refs
- `docs-site/docs/enterprise/azure-devops-migration.md` — unified plugin refs
- Features page — 100K+ verified skills stat

**Test Plan**:
- **Tests**:
  - **TC-025**: No references to satellite plugin names in docs
    - Given docs updated
    - When grep for "specweave-github", "specweave-jira", etc in docs-site/
    - Then only historical/comparison context references remain

**Dependencies**: T-012

---

### T-019: Clean up satellite plugin documentation files
**User Story**: US-006 | **Satisfies ACs**: AC-US6-05 | **Status**: [x] Completed

**Description**: Remove standalone docs from deleted satellite directories (already handled by directory deletion in Phase 1-3, but verify no orphans).

**Implementation Details**:
- Verify no orphaned PLUGIN.md files remain
- Verify no orphaned analysis docs remain
- Update CLAUDE.md and AGENTS.md if they reference satellite plugins

**Test Plan**:
- **Tests**:
  - **TC-026**: No orphaned satellite docs
    - Given satellite dirs deleted
    - When searching for satellite PLUGIN.md files
    - Then 0 found

**Dependencies**: T-001 through T-007

---

## Phase 10: Build Scripts

### T-020: Update build scripts for unified plugin
**User Story**: US-008 | **Satisfies ACs**: AC-US8-01, AC-US8-02, AC-US8-03 | **Status**: [x] Completed

**Description**: Update `scripts/build/copy-plugin-js.js` to handle the consolidated plugin structure.

**Implementation Details**:
- Update to copy only `plugins/specweave/` (not 8 separate dirs)
- Verify recursive copy handles new subdirectory depth (lib/integrations/github/, etc.)
- Run `npm run build` to verify

**Test Plan**:
- **Tests**:
  - **TC-027**: Build succeeds
    - Given build script updated
    - When `npm run build` runs
    - Then exit code 0 and dist/plugins/specweave/ contains all files
  - **TC-028**: Package size check
    - Given build complete
    - When `npm pack --dry-run` measured
    - Then size within 5% of pre-consolidation size

**Dependencies**: T-001 through T-007

---

## Phase 11: Final Verification

### T-021: Run full test suite
**User Story**: US-005 | **Satisfies ACs**: AC-US5-06 | **Status**: [x] Completed

**Description**: Run `npx vitest run` to verify 0 test failures across all test categories.

**Test Plan**:
- **Tests**:
  - **TC-029**: Full test suite passes
    - Given all migrations and fixups complete
    - When `npx vitest run`
    - Then 0 failures

**Dependencies**: T-016, T-017

---

### T-022: Verify no satellite references remain in codebase
**User Story**: All | **Satisfies ACs**: AC-US1-04, AC-US5-01 | **Status**: [x] Completed

**Description**: Grep the entire codebase for references to deleted satellite plugin directories. Only historical references in git history or changelogs are acceptable.

**Implementation Details**:
- `grep -r "specweave-github\|specweave-jira\|specweave-ado\|specweave-release\|specweave-diagrams\|specweave-media\|specweave-docs" --include="*.ts" --include="*.js" --include="*.md" --include="*.json" .`
- Exclude: node_modules, dist, .git, changelogs, ADR docs

**Test Plan**:
- **Tests**:
  - **TC-030**: Zero satellite references in active code
    - Given codebase grep
    - When excluding dist/node_modules/git/changelogs
    - Then 0 matches

**Dependencies**: All previous tasks

---

### T-023: Verify skill invocations work
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05 | **Status**: [x] Completed

**Description**: Manually verify that all 44 skills and 74 commands are discoverable by the PluginLoader after consolidation.

**Implementation Details**:
- Run PluginLoader.loadFromDirectory on `plugins/specweave/`
- Verify skills count === 44
- Verify commands count === 74
- Spot-check specific skill names from each former satellite

**Test Plan**:
- **Tests**:
  - **TC-031**: PluginLoader discovers all skills and commands
    - Given unified plugin directory
    - When PluginLoader.loadFromDirectory runs
    - Then skills.length === 44 and commands.length >= 74

**Dependencies**: T-010, T-011, T-014
