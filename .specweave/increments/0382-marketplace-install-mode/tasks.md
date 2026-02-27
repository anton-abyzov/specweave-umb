# Tasks: Claude Code Plugin Marketplace Install Mode

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## Phase 1: Marketplace Detection

### T-001: Add detectMarketplaceRepo function
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed

**Description**: Add a `detectMarketplaceRepo(owner, repo, branch)` function to `src/commands/add.ts` that checks GitHub Contents API for `.claude-plugin/marketplace.json` in the target repo.

**Implementation Details**:
- Fetch `https://api.github.com/repos/{owner}/{repo}/contents/.claude-plugin/marketplace.json` with `User-Agent: vskill-cli`
- On 200: parse response, extract `download_url`, fetch raw content, return `{ isMarketplace: true, manifestContent }`
- On 404/error: return `{ isMarketplace: false }`
- Use the existing `getDefaultBranch` function for branch resolution

**Test Plan**:
- **File**: `src/commands/add.test.ts`
- **Tests**:
  - **TC-001**: Given a repo with `.claude-plugin/marketplace.json`, when detectMarketplaceRepo is called, then it returns `{ isMarketplace: true, manifestContent: <parsed JSON> }`
  - **TC-002**: Given a repo without marketplace.json, when detectMarketplaceRepo is called, then it returns `{ isMarketplace: false }`
  - **TC-003**: Given a GitHub API failure (network error), when detectMarketplaceRepo is called, then it returns `{ isMarketplace: false }` (graceful fallback)

**Dependencies**: None

---

### T-002: Wire marketplace detection into addCommand
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-03, AC-US1-04 | **Status**: [x] completed

**Description**: In the `addCommand` function, after the 2-part `owner/repo` check and before `discoverSkills`, insert marketplace detection. If detected, route to the new `installMarketplaceRepo` function (stubbed initially).

**Implementation Details**:
- After line ~1215 (`const [owner, repo] = parts;`) and after the `opts.skill` check
- Call `detectMarketplaceRepo(owner, repo, branch)`
- If marketplace detected, call `installMarketplaceRepo(owner, repo, result.manifestContent, opts)` and return
- If not detected, fall through to existing `discoverSkills` flow
- Ensure `--plugin` flag still routes to existing `installRepoPlugin` (checked earlier in function)

**Test Plan**:
- **File**: `src/commands/add.test.ts`
- **Tests**:
  - **TC-004**: Given `vskill install owner/repo` where repo is a marketplace, when addCommand runs, then installMarketplaceRepo is called (not discoverSkills)
  - **TC-005**: Given `vskill install owner/repo` where repo is NOT a marketplace, when addCommand runs, then discoverSkills proceeds as before
  - **TC-006**: Given `vskill install owner/repo --plugin foo`, when addCommand runs, then existing installRepoPlugin is called regardless of marketplace detection

**Dependencies**: T-001

---

## Phase 2: Marketplace Install Flow

### T-003: Add installMarketplaceRepo function with plugin selection UI
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06 | **Status**: [x] completed

**Description**: Implement the `installMarketplaceRepo` function that parses marketplace.json, shows plugin selection UI, and orchestrates installation.

**Implementation Details**:
- Parse manifest with `getAvailablePlugins(manifestContent)`
- If non-TTY and no `--yes`/`--all`: print available plugins, exit with error directing user to use `--plugin <name>` or `--all`
- If `--yes` or `--all`: select all plugins automatically
- Otherwise: show `promptCheckboxList` with all plugins unchecked by default, each item has `label: plugin.name, description: plugin.description, checked: false`
- If no plugins selected, print message and return
- For each selected plugin, call the install function (T-004)

**Test Plan**:
- **File**: `src/commands/add.test.ts`
- **Tests**:
  - **TC-007**: Given a marketplace with 3 plugins, when interactive selection shows, then all items are unchecked by default
  - **TC-008**: Given non-TTY mode without --yes, when installMarketplaceRepo runs, then it prints plugin list and exits with error
  - **TC-009**: Given --yes flag, when installMarketplaceRepo runs, then all plugins are selected
  - **TC-010**: Given user selects 0 plugins, when installMarketplaceRepo runs, then it aborts with a message

**Dependencies**: T-001

---

### T-004: Implement native plugin installation per selected plugin
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05 | **Status**: [x] completed

**Description**: For each selected plugin, clone the repo to a temp directory, register marketplace, and install via native Claude CLI. Fall back to extraction if CLI unavailable.

**Implementation Details**:
- Create temp directory: `mkdtempSync(join(os.tmpdir(), 'vskill-marketplace-'))`
- Shallow clone: `git clone --depth 1 https://github.com/{owner}/{repo}.git {tmpDir}`
- Register marketplace: `registerMarketplace(tmpDir)` (from `utils/claude-cli.ts`)
- For each plugin: `installNativePlugin(pluginName, marketplaceName)` (from `utils/claude-cli.ts`)
- Show spinner per plugin with success/failure
- If `claude` CLI not available: fall back to `installRepoPlugin(ownerRepo, pluginName, opts)` for each plugin
- Cleanup temp directory: `rmSync(tmpDir, { recursive: true, force: true })`
- Print summary with installed/failed counts

**Test Plan**:
- **File**: `src/commands/add.test.ts`
- **Tests**:
  - **TC-011**: Given claude CLI is available, when installing a plugin, then registerMarketplace and installNativePlugin are called
  - **TC-012**: Given claude CLI is NOT available, when installing a plugin, then it falls back to extraction-based installRepoPlugin
  - **TC-013**: Given 3 plugins selected and 1 fails, when install completes, then summary shows 2 installed, 1 failed
  - **TC-014**: Given successful install, then temp directory is cleaned up

**Dependencies**: T-003

---

### T-005: Lockfile and telemetry for marketplace installs
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02 | **Status**: [x] completed

**Description**: Record marketplace-installed plugins in the lockfile and report telemetry.

**Implementation Details**:
- After each successful plugin install, update lockfile with source `marketplace:{owner}/{repo}#{pluginName}`
- Set version from marketplace.json plugin version
- Report install via `reportInstall(pluginName)` (fire-and-forget)
- Use existing `ensureLockfile`/`writeLockfile` from lockfile module

**Test Plan**:
- **File**: `src/commands/add.test.ts`
- **Tests**:
  - **TC-015**: Given successful marketplace install, when lockfile is written, then source is `marketplace:{owner}/{repo}#{pluginName}`
  - **TC-016**: Given successful marketplace install, then reportInstall is called for each plugin

**Dependencies**: T-004

---

## Phase 3: Testing & Verification

### T-006: Integration tests for full marketplace flow
**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: AC-US1-01, AC-US2-01, AC-US3-05 | **Status**: [ ] not started

**Description**: End-to-end test covering the complete flow: detection -> selection -> installation -> summary.

**Test Plan**:
- **File**: `src/commands/add.test.ts`
- **Tests**:
  - **TC-017**: Given `vskill install owner/marketplace-repo` in TTY with user selecting 2 of 3 plugins, when flow completes, then exactly 2 plugins are installed and summary shows correct counts
  - **TC-018**: Given `vskill install owner/marketplace-repo --yes`, when flow completes, then all plugins are installed via native CLI
  - **TC-019**: Given `vskill install owner/regular-repo` (no marketplace.json), when flow completes, then skill discovery runs as before

**Dependencies**: T-005

---

### T-007: Run full test suite and verify no regressions
**User Story**: All | **Satisfies ACs**: All | **Status**: [ ] not started

**Description**: Run `npx vitest run` to ensure all existing tests pass and new tests pass.

**Dependencies**: T-006
