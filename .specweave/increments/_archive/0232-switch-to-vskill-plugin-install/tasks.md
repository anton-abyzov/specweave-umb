# Tasks: Switch Plugin Installation to vskill

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[RED]`: TDD Red - write failing tests
- `[GREEN]`: TDD Green - implement to pass tests
- `[REFACTOR]`: TDD Refactor - clean up
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## Phase 1: vskill CLI Enhancements

### US-005: Full Claude Code Plugin Directory Support (P1)

#### T-001 [RED]: Write failing tests for vskill `add` plugin directory support
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04 | **Status**: [x] completed

**Description**: Write failing tests that define expected behavior of the extended vskill `add` command for full Claude Code plugin directories.

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill/src/commands/add.test.ts`
- **Tests**:
  - **TC-001**: `--plugin <name>` flag selects sub-plugin from multi-plugin repo
    - Given a local repo path with `plugins/specweave-frontend/`
    - When `vskill add <repo> --plugin sw-frontend`
    - Then the `sw-frontend` plugin directory is selected and installed
  - **TC-002**: Full directory structure preserved
    - Given a plugin with skills/, hooks/, commands/, agents/, .claude-plugin/
    - When installed via vskill add --plugin
    - Then all subdirectories are copied to `~/.claude/plugins/cache/specweave/sw-frontend/<version>/`
  - **TC-003**: Hook permissions fixed
    - Given a plugin with .sh files in hooks/
    - When installed via vskill add --plugin
    - Then all .sh files have executable permission (chmod +x)
  - **TC-004**: Full file scanning covers hooks
    - Given a plugin with hooks containing dangerous patterns (rm -rf, curl)
    - When scanned by Tier 1 scanner
    - Then scan findings include hook file matches (not just SKILL.md)

**Dependencies**: None
**File**: `repositories/anton-abyzov/vskill/src/commands/add.test.ts` (new)

---

#### T-002 [GREEN]: Implement vskill `add` for full plugin directories
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04 | **Status**: [x] completed

**Description**: Extend the vskill CLI `add` command to make T-001 tests pass.

**Implementation Details**:
- Add `--plugin <name>` CLI option to `add` command in commander setup
- Add `--plugin-dir` mode that copies entire plugin directory structure
- Copy to `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/`
- Preserve full structure: skills/, hooks/, commands/, agents/, .claude-plugin/
- chmod +x for all .sh files in hooks/ and scripts/
- Expand security scanning to cover all files in plugin dir (not just SKILL.md)

**Dependencies**: T-001
**File**: `repositories/anton-abyzov/vskill/src/commands/add.ts`

---

#### T-003 [RED]: Write failing tests for marketplace.json parser [P]
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US2-01 | **Status**: [x] completed

**Description**: Write failing tests for a new module that parses `.claude-plugin/marketplace.json`.

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill/src/marketplace/marketplace.test.ts`
- **Tests**:
  - **TC-005**: Parse marketplace.json returns plugin entries
    - Given a valid marketplace.json with plugins array
    - When `getAvailablePlugins(marketplacePath)` is called
    - Then returns array of plugin entries with name, source, version
  - **TC-006**: Plugin source mapping resolves paths
    - Given marketplace.json with `sw-frontend` -> `./plugins/specweave-frontend`
    - When `getPluginSource('sw-frontend', marketplacePath)` is called
    - Then returns resolved absolute path to the plugin directory
  - **TC-007**: Unknown plugin returns null
    - Given marketplace.json without `sw-nonexistent`
    - When `getPluginSource('sw-nonexistent', marketplacePath)` is called
    - Then returns null

**Dependencies**: None
**File**: `repositories/anton-abyzov/vskill/src/marketplace/marketplace.test.ts` (new)

---

#### T-004 [GREEN]: Implement marketplace.json parser [P]
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US2-01 | **Status**: [x] completed

**Description**: Implement the marketplace.json parser to make T-003 tests pass.

**Implementation Details**:
- Create `repositories/anton-abyzov/vskill/src/marketplace/marketplace.ts`
- Parse marketplace.json structure (name, plugins array with source paths)
- Map plugin names to source directories
- Export: `getAvailablePlugins()`, `getPluginSource()`, `getPluginVersion()`
- Handle both local filesystem path and cloned repo path

**Dependencies**: T-003
**File**: `repositories/anton-abyzov/vskill/src/marketplace/marketplace.ts` (new)

---

#### T-005 [RED]: Write failing tests for lockfile extensions [P]
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-04, AC-US2-05 | **Status**: [x] completed

**Description**: Write failing tests for extended lockfile schema supporting Claude Code plugin metadata.

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill/src/lockfile/lockfile.test.ts` (extend existing)
- **Tests**:
  - **TC-008**: Extended entry with marketplace field round-trips
    - Given a lockfile entry with `marketplace: "specweave"`, `pluginDir: true`, `scope: "user"`
    - When written and read back
    - Then all extended fields preserved correctly
  - **TC-009**: Backward-compatible with existing entries
    - Given a lockfile with old-format entries (no marketplace/pluginDir/scope)
    - When read
    - Then old entries still parse correctly, new fields default to undefined

**Dependencies**: None
**File**: `repositories/anton-abyzov/vskill/src/lockfile/lockfile.test.ts`

---

#### T-006 [GREEN]: Implement lockfile extensions [P]
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-04, AC-US2-05 | **Status**: [x] completed

**Description**: Extend the lockfile types and logic to make T-005 tests pass.

**Implementation Details**:
- Add optional fields to `SkillLockEntry`: `marketplace?`, `pluginDir?`, `scope?`, `installedPath?`
- Backward-compatible: existing entries without new fields still work
- Update `addSkillToLock()` to accept extended entry data

**Dependencies**: T-005
**Files**: `repositories/anton-abyzov/vskill/src/lockfile/types.ts`, `repositories/anton-abyzov/vskill/src/lockfile/lockfile.ts`

---

#### T-007 [RED]: Write failing tests for settings.json management [P]
**User Story**: US-001 | **Satisfies ACs**: AC-US1-06 | **Status**: [x] completed

**Description**: Write failing tests for a new module managing `~/.claude/settings.json` enabledPlugins.

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill/src/settings/settings.test.ts`
- **Tests**:
  - **TC-010**: Enable plugin in empty settings.json
    - Given empty or non-existent settings.json
    - When `enablePlugin('sw-frontend@specweave', { scope: 'user' })` is called
    - Then settings.json has `enabledPlugins["sw-frontend@specweave"] = true`
  - **TC-011**: Project vs user scope writes to correct location
    - Given scope 'project'
    - When `enablePlugin('sw-frontend@specweave', { scope: 'project' })` is called
    - Then writes to `.claude/settings.json` (project-local, not `~/.claude/`)
  - **TC-012**: Preserve existing settings
    - Given settings.json with existing keys (e.g., `theme: "dark"`)
    - When enabling a plugin
    - Then existing keys are preserved alongside new enabledPlugins entry

**Dependencies**: None
**File**: `repositories/anton-abyzov/vskill/src/settings/settings.test.ts` (new)

---

#### T-008 [GREEN]: Implement settings.json management [P]
**User Story**: US-001 | **Satisfies ACs**: AC-US1-06 | **Status**: [x] completed

**Description**: Implement settings.json management to make T-007 tests pass.

**Implementation Details**:
- Create `repositories/anton-abyzov/vskill/src/settings/settings.ts`
- Read `~/.claude/settings.json` (create if not exists)
- Set `enabledPlugins["<name>@<marketplace>"] = true`
- Support user scope (`~/.claude/settings.json`) vs project scope (`.claude/settings.json`)
- Export: `enablePlugin()`, `disablePlugin()`, `isPluginEnabled()`

**Dependencies**: T-007
**File**: `repositories/anton-abyzov/vskill/src/settings/settings.ts` (new)

---

#### T-009 [RED]: Write failing tests for agent registry pluginCacheDir [P]
**User Story**: US-005 | **Satisfies ACs**: AC-US5-02 | **Status**: [x] completed

**Description**: Write failing test for Claude Code agent having pluginCacheDir field.

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill/src/agents/agents-registry.test.ts` (extend)
- **Tests**:
  - **TC-013**: Claude Code agent has pluginCacheDir
    - Given the agents registry
    - When looking up 'claude-code' agent
    - Then it has `pluginCacheDir` field set to `~/.claude/plugins/cache`

**Dependencies**: None
**File**: `repositories/anton-abyzov/vskill/src/agents/agents-registry.test.ts`

---

#### T-010 [GREEN]: Implement agent registry pluginCacheDir [P]
**User Story**: US-005 | **Satisfies ACs**: AC-US5-02 | **Status**: [x] completed

**Description**: Add pluginCacheDir to Claude Code agent definition to make T-009 tests pass.

**Implementation Details**:
- Add `pluginCacheDir?: string` to agent type definition
- Set `pluginCacheDir: '~/.claude/plugins/cache'` on Claude Code agent entry
- Export helper: `getPluginCacheDir(agentSlug)` for installation logic

**Dependencies**: T-009
**File**: `repositories/anton-abyzov/vskill/src/agents/agents-registry.ts`

---

#### T-011 [REFACTOR]: Refactor Phase 1 vskill CLI code
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01 | **Status**: [x] completed

**Description**: Review and refactor Phase 1 code. Extract shared utilities, ensure consistent error handling, remove duplication. All existing tests must stay green.

**Dependencies**: T-002, T-004, T-006, T-008, T-010

---

## Phase 2: SpecWeave Integration

### US-002: Plugin Refresh via vskill (P1)

#### T-012 [RED]: Write failing tests for `refresh-plugins` command
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04 | **Status**: [x] completed

**Description**: Write failing tests for the new refresh-plugins command.

**Test Plan**:
- **File**: `repositories/anton-abyzov/specweave/src/cli/commands/__tests__/refresh-plugins.test.ts`
- **Tests**:
  - **TC-014**: Lazy mode installs only core plugin
    - Given a fresh project with no vskill.lock
    - When `specweave refresh-plugins` runs (default lazy mode)
    - Then only `sw` plugin is installed via vskill
  - **TC-015**: All mode installs all marketplace plugins
    - Given `--all` flag
    - When `specweave refresh-plugins --all` runs
    - Then all plugins from marketplace.json are installed
  - **TC-016**: Changed plugins are re-scanned
    - Given `sw-frontend` in lockfile with old hash
    - When source has different content hash
    - Then vskill re-scans and updates the plugin

**Dependencies**: T-004, T-006, T-008
**File**: `repositories/anton-abyzov/specweave/src/cli/commands/__tests__/refresh-plugins.test.ts` (new)

---

#### T-013 [GREEN]: Implement `refresh-plugins` command
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04 | **Status**: [x] completed

**Description**: Implement the refresh-plugins command to make T-012 tests pass.

**Implementation Details**:
- Modes: lazy (core only), all, minimal, force
- Invoke vskill programmatically (import from local monorepo)
- Read marketplace.json to get available plugins
- For each plugin: check lockfile → if changed, scan + install
- Register in CLI command registry

**Dependencies**: T-012
**File**: `repositories/anton-abyzov/specweave/src/cli/commands/refresh-plugins.ts` (new)

---

#### T-014 [RED]: Write failing test for `refresh-marketplace` deprecation
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [x] completed

**Description**: Write failing test for deprecation warning behavior.

**Test Plan**:
- **File**: `repositories/anton-abyzov/specweave/src/cli/commands/__tests__/refresh-marketplace.test.ts` (extend)
- **Tests**:
  - **TC-017**: Deprecation warning shown on invocation
    - Given user runs `specweave refresh-marketplace`
    - When command executes
    - Then deprecation warning is printed to stderr
    - And refresh-plugins is called with same arguments

**Dependencies**: T-013
**File**: `repositories/anton-abyzov/specweave/src/cli/commands/__tests__/refresh-marketplace.test.ts`

---

#### T-015 [GREEN]: Implement `refresh-marketplace` deprecation
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [x] completed

**Description**: Add deprecation warning and delegate to refresh-plugins. Make T-014 tests pass.

**Implementation Details**:
- Print deprecation warning: "refresh-marketplace is deprecated, use refresh-plugins instead"
- Delegate to refresh-plugins with same arguments
- Keep command registered for backward compatibility

**Dependencies**: T-014
**File**: `repositories/anton-abyzov/specweave/src/cli/commands/refresh-marketplace.ts`

---

### US-001: New User Plugin Installation (P1)

#### T-016 [RED]: Write failing tests for plugin-installer.ts vskill integration
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed

**Description**: Write failing tests for the modified plugin installer using vskill.

**Test Plan**:
- **File**: `repositories/anton-abyzov/specweave/src/cli/helpers/init/__tests__/plugin-installer.test.ts` (extend)
- **Tests**:
  - **TC-018**: Init uses vskill instead of claude plugin install
    - Given a fresh project running `specweave init`
    - When plugin installation phase runs
    - Then vskill `add` is invoked (not `claude plugin install`)
  - **TC-019**: Scan result displayed to user
    - Given vskill scan returns PASS
    - When plugin installs
    - Then scan result (PASS/CONCERNS/FAIL) is displayed

**Dependencies**: T-004, T-008
**File**: `repositories/anton-abyzov/specweave/src/cli/helpers/init/__tests__/plugin-installer.test.ts`

---

#### T-017 [GREEN]: Implement plugin-installer.ts vskill integration
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed

**Description**: Modify plugin-installer.ts to use vskill. Make T-016 tests pass.

**Implementation Details**:
- Remove `claude plugin marketplace add` calls
- Replace `claude plugin install sw@specweave` with vskill `add` invocation
- Keep same public API (`installAllPlugins()`)
- Remove `refreshMarketplace()`, `ensureOfficialMarketplace()` functions
- Add vskill path resolution (local monorepo)

**Dependencies**: T-016
**File**: `repositories/anton-abyzov/specweave/src/cli/helpers/init/plugin-installer.ts`

---

### US-003: Lazy Loading via vskill (P1)

#### T-018 [RED]: Write failing tests for lazy loading vskill integration
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04 | **Status**: [x] completed

**Description**: Write failing tests for lazy loading via vskill.

**Test Plan**:
- **File**: `repositories/anton-abyzov/specweave/src/core/lazy-loading/__tests__/llm-plugin-detector.test.ts`
- **Tests**:
  - **TC-020**: Detector uses vskill for installation
    - Given plugin detection result with `["sw-frontend"]`
    - When `installPluginViaCli()` is called
    - Then vskill add is invoked (not `claude plugin install`)
  - **TC-021**: Fast-path skip for already-installed plugins
    - Given `sw-frontend` already in vskill.lock
    - When hook detects `sw-frontend` needed
    - Then installation is skipped (no re-scan)
  - **TC-022**: Hook output compatible with additionalContext format
    - Given vskill installs a plugin
    - When hook produces output
    - Then output format matches Claude Code's additionalContext expectations

**Dependencies**: T-004, T-006
**Files**: `repositories/anton-abyzov/specweave/src/core/lazy-loading/__tests__/llm-plugin-detector.test.ts`

---

#### T-019 [GREEN]: Implement lazy loading vskill integration
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04 | **Status**: [x] completed

**Description**: Modify lazy loading to use vskill. Make T-018 tests pass.

**Implementation Details**:
- **Hook** (`plugins/specweave/hooks/user-prompt-submit.sh`): Replace `claude plugin install` with vskill add
- Add `vskill.lock` check: if plugin+version already in lockfile, skip entirely
- **LLM detector** (`llm-plugin-detector.ts`): Update `installPluginViaCli()` to call vskill
- Ensure latency stays under 5s (fast-path: lockfile check <1ms)

**Dependencies**: T-018
**Files**: `plugins/specweave/hooks/user-prompt-submit.sh`, `repositories/anton-abyzov/specweave/src/core/lazy-loading/llm-plugin-detector.ts`

---

### US-004: Migration (P2)

#### T-020 [RED]: Write failing tests for migration command
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04 | **Status**: [x] completed

**Description**: Write failing tests for the `specweave migrate-to-vskill` command.

**Test Plan**:
- **File**: `repositories/anton-abyzov/specweave/src/cli/commands/__tests__/migrate-to-vskill.test.ts`
- **Tests**:
  - **TC-023**: Lockfile creation from installed plugins
    - Given 5 plugins installed via Claude marketplace at `~/.claude/plugins/cache/specweave/`
    - When `specweave migrate-to-vskill` runs
    - Then vskill.lock contains 5 entries with correct content hashes
  - **TC-024**: Existing plugin files preserved
    - Given plugins already cached at `~/.claude/plugins/cache/specweave/`
    - When migration runs
    - Then plugin files are not moved or deleted
  - **TC-025**: Init detects marketplace installation and offers migration
    - Given marketplace-based plugins installed, no vskill.lock
    - When `specweave init` runs
    - Then migration is offered to the user

**Dependencies**: T-006, T-008
**File**: `repositories/anton-abyzov/specweave/src/cli/commands/__tests__/migrate-to-vskill.test.ts` (new)

---

#### T-021 [GREEN]: Implement migration command
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04 | **Status**: [x] completed

**Description**: Implement the migration command to make T-020 tests pass.

**Implementation Details**:
- Scan `~/.claude/plugins/cache/specweave/` for installed plugin directories
- Compute content hashes for each installed plugin directory
- Write `vskill.lock` with all entries
- Optionally remove Claude marketplace registration (with user confirmation)
- Integrate into `specweave init` (auto-detect marketplace + no vskill.lock → offer migration)

**Dependencies**: T-020
**File**: `repositories/anton-abyzov/specweave/src/cli/commands/migrate-to-vskill.ts` (new)

---

#### T-022 [GREEN]: Update remaining source files referencing `claude plugin install`
**User Story**: US-001, US-003 | **Satisfies ACs**: AC-US1-01, AC-US3-01 | **Status**: [x] completed

**Description**: Update all remaining source files that reference `claude plugin install`.

**Implementation Details**:
- `src/cli/commands/detect-intent.ts`: Update install path references
- `src/core/session/plugin-install-detector.ts`: Update detection logic
- `src/utils/cleanup-stale-plugins.ts`: Read from vskill.lock
- `src/cli/helpers/init/claude-plugin-enabler.ts`: Wire to vskill settings
- `plugins/specweave/hooks/v2/dispatchers/session-start.sh`: Update refs

**Dependencies**: T-017, T-019
**Files**: Multiple (see description)

---

#### T-023 [REFACTOR]: Refactor Phase 2 SpecWeave integration code
**User Story**: All Phase 2 | **Satisfies ACs**: All | **Status**: [x] completed

**Description**: Review and refactor Phase 2 code. Remove dead code from old marketplace system, DRY up vskill invocation patterns, ensure consistent error handling. All tests must stay green.

**Dependencies**: T-013, T-015, T-017, T-019, T-021, T-022

---

## Phase 3: Documentation & Integration Tests

#### T-024: Update CLAUDE.md and templates
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [x] completed

**Description**: Replace marketplace references with vskill/refresh-plugins in project instructions.

**Implementation Details**:
- `CLAUDE.md`: Replace `specweave refresh-marketplace` with `specweave refresh-plugins`
- `src/templates/CLAUDE.md.template`: Same updates for new projects
- Update troubleshooting section

**Dependencies**: T-013
**Files**: `CLAUDE.md`, `repositories/anton-abyzov/specweave/src/templates/CLAUDE.md.template`

---

#### T-025: Update docs-site documentation
**User Story**: US-002, US-004 | **Satisfies ACs**: AC-US2-02, AC-US4-04 | **Status**: [x] completed

**Description**: Update all user-facing documentation to reference vskill.

**Implementation Details**:
- `docs-site/docs/overview/plugins-ecosystem.md`: Installation instructions
- `docs-site/docs/guides/getting-started/installation.md`: Getting started flow
- `docs-site/docs/guides/lazy-plugin-loading.md`: Lazy loading docs
- Add migration guide section
- Update all other docs-site pages with marketplace references

**Dependencies**: T-021
**Files**: Multiple docs-site files

---

#### T-026: Update PLUGIN.md files [P]
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01 | **Status**: [x] completed

**Description**: Replace `claude plugin install` examples in all PLUGIN.md files.

**Implementation Details**:
- Search-replace across all PLUGIN.md files in `plugins/`
- Replace `claude plugin install <name>@specweave` with `vskill add` equivalent
- Verify consistent formatting

**Dependencies**: T-002
**Files**: PLUGIN.md files in `plugins/`

---

#### T-027 [RED]: Write integration tests for full pipeline
**User Story**: US-001, US-002, US-003, US-004 | **Satisfies ACs**: All | **Status**: [x] completed

**Description**: End-to-end integration tests for the full vskill plugin pipeline.

**Test Plan**:
- **File**: `repositories/anton-abyzov/specweave/tests/integration/vskill-plugin-pipeline.test.ts`
- **Tests**:
  - **TC-026**: refresh-plugins end-to-end with vskill
    - Given a configured project
    - When `refresh-plugins` runs
    - Then plugins installed via vskill, lockfile updated, settings enabled
  - **TC-027**: Init with vskill end-to-end
    - Given a new project
    - When `specweave init` runs
    - Then core plugin installed via vskill, no marketplace registration
  - **TC-028**: Migration end-to-end
    - Given marketplace-installed plugins
    - When `migrate-to-vskill` runs
    - Then lockfile created, plugins preserved, ready for vskill updates

**Dependencies**: T-013, T-017, T-019, T-021
**File**: `repositories/anton-abyzov/specweave/tests/integration/vskill-plugin-pipeline.test.ts` (new)
