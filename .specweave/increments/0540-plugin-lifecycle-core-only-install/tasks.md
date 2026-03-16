# Tasks: Plugin lifecycle: core-only install + stale cache cleanup

## Task Notation

- `[ ]` Not started | `[x]` Completed
- `[P]` Parallelizable (no blocking deps)
- Model hint: haiku (simple edits), sonnet (default), opus (architecture decisions)

---

## US-001: Core-Only Default Install

### T-001: Add `CORE_PLUGIN` constant and core-only filter logic to `refresh-plugins.ts`
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Status**: [x] completed
**Test**: Given marketplace.json has 8 plugins and no flags are passed → When `refreshPluginsCommand({})` runs → Then only the plugin named `sw` is processed (exactly 1 plugin in loop)

**Implementation**:
- Add `const CORE_PLUGIN = 'sw';` constant after imports
- Add `plugin?: string` and `quiet?: boolean` fields to `RefreshPluginsOptions`
- Remove the `@deprecated` comment on `all` — it is now the explicit full-install opt-in
- In `refreshPluginsCommand`, after `getAvailablePlugins()`, add plugin selection logic:
  - if `options.plugin` is set: filter to that one (validation handled in T-002)
  - else if `options.all`: use all (current behavior)
  - else: `allPlugins.filter(p => p.name === CORE_PLUGIN)`
- Store selected subset in `pluginsToInstall` and iterate that instead of `allPlugins`
- Update the "Found N plugins" log to show selected vs total counts

**File**: `repositories/anton-abyzov/specweave/src/cli/commands/refresh-plugins.ts`

---

### T-002: Add `--plugin` and `--quiet` flags to Commander registration
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] completed
**Test**: Given the Commander program is registered → When `--help` is shown for `refresh-plugins` → Then `--plugin <name>` and `--quiet` options appear in help output

**Implementation**:
- Locate the Commander `.command('refresh-plugins')` registration (likely in `src/cli/index.ts` or `src/cli/commands/refresh-plugins.ts`)
- Add `.option('--plugin <name>', 'Install a specific plugin by name')`
- Add `.option('-q, --quiet', 'Suppress output (for use by hooks)')`
- Ensure `--all` option is still registered (remove any `@deprecated` text from its description)
- Wire `options.plugin` and `options.quiet` through to `refreshPluginsCommand()`

**File**: Commander registration file (check `src/cli/index.ts`)

---

### T-003: Implement `--plugin` validation and error output
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] completed
**Test**: Given marketplace.json has plugins `[sw, frontend, backend]` and `--plugin nonexistent` is passed → When `refreshPluginsCommand({ plugin: 'nonexistent' })` runs → Then process exits with code 1 and stderr includes the available plugin names

**Implementation**:
- After filtering to `options.plugin`, check if the filtered array is empty
- If empty: print error message listing available plugin names (`allPlugins.map(p => p.name).join(', ')`), set `process.exitCode = 1`, and return early
- Handle `--plugin` + `--all` precedence: when both are set, `plugin` takes precedence (filter to single plugin only)
- Strip marketplace suffix from `--plugin` value: `'sw-github@specweave'` → `'sw-github'`
- If `options.quiet` is set, suppress all `console.log` calls in `refreshPluginsCommand` (wrap existing logs behind `if (!options.quiet)`)

**File**: `repositories/anton-abyzov/specweave/src/cli/commands/refresh-plugins.ts`

---

### T-004: Verify `update.ts` pass-through — no code change needed, update JSDoc only
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04
**Status**: [x] completed
**Test**: Given `update.ts` calls `refreshPluginsCommand({ all: options.all, ... })` → When `specweave update` runs without `--all` → Then `options.all` is `undefined`, refresh selects core-only

**Implementation**:
- Read `update.ts` and confirm `refreshPluginsCommand` is called with `all: options.all`
- No logic change needed — `all` being falsy causes core-only behavior after T-001
- Update JSDoc on `UpdateOptions.all`: change `@deprecated` to active documentation: `Install all plugins, not just core (sw)`
- Update the command help string comment at the top of update.ts to reflect core-only default

**File**: `repositories/anton-abyzov/specweave/src/cli/commands/update.ts`

---

### T-005: Write Vitest unit tests for core-only + `--plugin` behavior
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] completed
**Test**: Given all test cases below → When Vitest runs → Then all pass with 0 failures

**Test file**: `repositories/anton-abyzov/specweave/tests/unit/commands/refresh-plugins.test.ts`

**Test cases**:
- **TC-001** (AC-US1-01): Given 8 plugins in marketplace.json and no options → When `refreshPluginsCommand({})` called with mocked `installPlugin` → Then `installPlugin` is called exactly once with name `'sw'`
- **TC-002** (AC-US1-02): Given 8 plugins and `{ all: true }` → When command runs → Then `installPlugin` is called 8 times
- **TC-003** (AC-US1-03): Given non-core plugins exist in `~/.claude/plugins/cache/` → When `refreshPluginsCommand({})` runs → Then those directories are untouched (no uninstall step)
- **TC-004** (AC-US2-01): Given plugin `'frontend'` exists in marketplace.json and `{ plugin: 'frontend' }` is passed → When command runs → Then `installPlugin` is called exactly once with name `'frontend'`
- **TC-005** (AC-US2-02): Given `{ plugin: 'nonexistent' }` → When command runs → Then `process.exitCode` is 1 and error output includes available plugin names
- **TC-006** (AC-US2-03): Given `{ plugin: 'frontend', all: true }` → When command runs → Then only `frontend` is installed (plugin takes precedence)
- **TC-007**: Given `{ quiet: true }` → When command runs → Then no `console.log` calls are made

---

## US-003: Multi-Marketplace Stale Plugin Cleanup

### T-006: Extend `CleanupResult` interface to include `removedCacheDirs`
**User Story**: US-003 | **Satisfies ACs**: AC-US3-04
**Status**: [x] completed
**Test**: Given `cleanupStalePlugins()` returns a result → When accessing `result.removedCacheDirs` → Then the field exists and is an array

**Implementation**:
- Add `removedCacheDirs: string[]` to `CleanupResult` interface
- Initialize `removedCacheDirs: []` in the result object at the start of `cleanupStalePlugins`

**File**: `repositories/anton-abyzov/specweave/src/utils/cleanup-stale-plugins.ts`

---

### T-007: Add dynamic marketplace discovery via `~/.claude/plugins/cache/` scan
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Status**: [x] completed
**Test**: Given `~/.claude/plugins/cache/` contains `specweave/` and `vskill/` subdirectories → When `cleanupStalePlugins()` runs → Then both marketplaces are discovered and processed independently

**Implementation**:
- After the existing settings.json cleanup, add Phase 2 discovery:
  ```
  const cacheBase = path.join(os.homedir(), '.claude', 'plugins', 'cache');
  if (!fs.existsSync(cacheBase)) return result; // AC: no cache dir = success
  const marketplaceDirs = fs.readdirSync(cacheBase, { withFileTypes: true })
    .filter(d => d.isDirectory())
    .map(d => d.name);
  ```
- For each marketplace directory, resolve its manifest at:
  `~/.claude/plugins/marketplaces/<marketplace>/.claude-plugin/marketplace.json`
- If the manifest file does not exist: skip that marketplace (log warning if verbose) — satisfies AC-US3-03
- If the manifest is malformed JSON: skip that marketplace with a warning — satisfies edge case
- Parse valid manifest and build `validPluginNames` set from `manifest.plugins[].name`
- The existing `marketplaceJsonPath` parameter still drives the specweave settings cleanup (Phase 1 unchanged)

**File**: `repositories/anton-abyzov/specweave/src/utils/cleanup-stale-plugins.ts`

---

### T-008: Implement stale settings.json cleanup for all discovered marketplaces
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02
**Status**: [x] completed
**Test**: Given settings.json has `frontend@vskill` enabled and vskill's marketplace.json does not list `frontend` → When cleanup runs → Then `frontend@vskill` is removed from settings.json

**Implementation**:
- Inside the marketplace loop from T-007, after resolving `validPluginNames`:
- Scan `settings.enabledPlugins` for entries where the `@marketplace` suffix matches the current marketplace
- If `pluginName` is not in `validPluginNames`, add to `stalePlugins`
- The existing specweave-specific `REMOVED_PLUGINS` set acts as a secondary safety net for `marketplace === 'specweave'` only
- Remove stale entries and increment `result.removedCount`

**File**: `repositories/anton-abyzov/specweave/src/utils/cleanup-stale-plugins.ts`

---

### T-009: Implement stale cache directory removal from disk
**User Story**: US-003 | **Satisfies ACs**: AC-US3-04
**Status**: [x] completed
**Test**: Given `~/.claude/plugins/cache/vskill/frontend/` exists and `frontend` is not in vskill's marketplace.json → When cleanup runs → Then that directory is removed from disk and `result.removedCacheDirs` contains its path

**Implementation**:
- Inside the marketplace loop, after settings cleanup, add cache dir Phase:
  ```
  const mktCacheDir = path.join(cacheBase, marketplaceName);
  const cachedPluginDirs = fs.readdirSync(mktCacheDir, { withFileTypes: true });
  for (const entry of cachedPluginDirs) {
    if (!entry.isDirectory() && !entry.isSymbolicLink()) continue;
    if (!validPluginNames.has(entry.name)) {
      const staleDir = path.join(mktCacheDir, entry.name);
      // Atomic rename then remove to avoid partial reads
      const tempName = staleDir + '.stale-' + Date.now();
      fs.renameSync(staleDir, tempName);
      fs.rmSync(tempName, { recursive: true, force: true });
      result.removedCacheDirs.push(staleDir);
    }
  }
  ```
- For symlinks: `entry.isSymbolicLink()` is true; `fs.renameSync` moves the symlink (not the target), then `fs.rmSync` removes it — satisfies "remove symlink not target" edge case
- Wrap in try-catch per directory; log warning on individual failure but continue

**File**: `repositories/anton-abyzov/specweave/src/utils/cleanup-stale-plugins.ts`

---

### T-010: Write Vitest unit tests for multi-marketplace cleanup
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04
**Status**: [x] completed
**Test**: Given all test cases below → When Vitest runs → Then all pass with 0 failures

**Test file**: `repositories/anton-abyzov/specweave/tests/unit/utils/cleanup-stale-plugins-multi-marketplace.test.ts`

**Test cases**:
- **TC-001** (AC-US3-01): Given cache dir has `specweave/` and `vskill/` subdirs → When cleanup runs → Then both marketplaces are iterated (verify calls to fs.readdirSync for each)
- **TC-002** (AC-US3-02): Given vskill marketplace.json exists and lists `[sw-github]` only, and settings has `frontend@vskill=true` → When cleanup runs → Then `frontend@vskill` is removed from settings.json
- **TC-003** (AC-US3-03): Given vskill marketplace.json does NOT exist at the expected path → When cleanup runs → Then vskill is skipped, result.success=true, no error thrown
- **TC-004** (AC-US3-04): Given `~/.claude/plugins/cache/vskill/frontend/` exists and is not in vskill's manifest → When cleanup runs → Then directory is removed and path appears in `result.removedCacheDirs`
- **TC-005** (edge): Given cache dir does not exist → When cleanup runs → Then result.success=true, removedCacheDirs=[]
- **TC-006** (edge): Given marketplace.json contains malformed JSON → When cleanup runs → Then that marketplace is skipped without throwing
- **TC-007** (edge): Given cache entry is a symlink → When cleanup runs → Then symlink itself is removed (target directory remains intact)

---

## US-004: On-Demand Plugin Loading Reactivation

### T-011: Restore on-demand plugin install block in `user-prompt-submit.sh`
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04
**Status**: [x] completed
**Test**: Given only `sw` is installed and LLM detect-intent returns `{"plugins":["frontend"]}` → When `user-prompt-submit.sh` is triggered with a React prompt → Then `specweave refresh-plugins --plugin frontend --quiet` is called in the background

**Implementation**:
Replace the `REMOVED (v1.0.535)` comment block (lines ~1194-1201 in hook) with:

```bash
# ==================================================================
# ON-DEMAND PLUGIN INSTALL (v1.0.540 - restored)
# ==================================================================
DETECTED_PLUGINS=$(echo "$JSON_OUTPUT" | jq -r '.plugins[]? // empty' 2>/dev/null)
if [[ -n "$DETECTED_PLUGINS" ]]; then
  CACHE_BASE="${HOME}/.claude/plugins/cache/specweave"
  SKILLS_BASE="${SW_PROJECT_ROOT:-.}/.claude/skills"
  SESSION_MARKER_DIR="${TMPDIR:-/tmp}/specweave-ondemand-$$"
  mkdir -p "$SESSION_MARKER_DIR" 2>/dev/null
  ONDEMAND_INSTALL_PID=""

  while IFS= read -r PLUGIN_NAME; do
    [[ -z "$PLUGIN_NAME" ]] && continue
    [[ "$PLUGIN_NAME" == "sw" ]] && continue

    # Idempotency: skip if already installed or already attempted this session
    if [[ -d "$CACHE_BASE/$PLUGIN_NAME" ]] || \
       [[ -d "$SKILLS_BASE/$PLUGIN_NAME" ]] || \
       [[ -f "$SESSION_MARKER_DIR/$PLUGIN_NAME" ]]; then
      continue
    fi

    # Install in background (AC-US4-02: reuse refresh-plugins, AC-US4-03: 2>/dev/null = graceful degradation)
    specweave refresh-plugins --plugin "$PLUGIN_NAME" --quiet 2>/dev/null &
    ONDEMAND_INSTALL_PID=$!
    touch "$SESSION_MARKER_DIR/$PLUGIN_NAME" 2>/dev/null

    AUTOLOAD_PLUGINS_MSG="${AUTOLOAD_PLUGINS_MSG}Installed plugin: ${PLUGIN_NAME} (on-demand)."$'\n'
  done <<< "$DETECTED_PLUGINS"

  # Wait for background install with 5s timeout
  if [[ -n "$ONDEMAND_INSTALL_PID" ]]; then
    ( sleep 5 && kill "$ONDEMAND_INSTALL_PID" 2>/dev/null ) &
    TIMEOUT_PID=$!
    wait "$ONDEMAND_INSTALL_PID" 2>/dev/null
    kill "$TIMEOUT_PID" 2>/dev/null
  fi
fi
```

**Key design points**:
- `$$` PID in marker dir path = unique per Claude Code session (AC-US4-04 idempotency)
- `specweave` CLI unavailability is already guarded at line ~1112 by existing guard; if CLI missing, `DETECTED_PLUGINS` parsing still runs but `specweave` call fails silently via `2>/dev/null` (AC-US4-03)
- Checks both `cache/specweave/<name>` (native install) and `.claude/skills/<name>` (direct-copy mode)

**File**: `repositories/anton-abyzov/specweave/plugins/specweave/hooks/user-prompt-submit.sh`

---

### T-012: Write integration test for on-demand hook behavior
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-03, AC-US4-04
**Status**: [x] completed
**Test**: Given hook test infrastructure in `tests/integration/hooks/` → When test runs → Then on-demand block installs only uninstalled plugins, skips already-installed ones, and skips `sw`

**Test file**: `repositories/anton-abyzov/specweave/tests/integration/hooks/user-prompt-submit-ondemand-install.test.ts`

**Test cases**:
- **TC-001** (AC-US4-01): Given JSON_OUTPUT has `plugins: ["frontend"]` and no `frontend` cache dir exists → When hook runs → Then `specweave refresh-plugins --plugin frontend --quiet` is invoked
- **TC-002** (AC-US4-04): Given `SESSION_MARKER_DIR/frontend` file exists (already attempted) → When hook runs again with same plugin → Then `specweave refresh-plugins` is NOT called again
- **TC-003** (AC-US4-04): Given `CACHE_BASE/frontend/` directory exists (already installed) → When hook runs → Then `specweave refresh-plugins` is NOT called
- **TC-004** (AC-US4-03): Given `specweave` command is not on PATH → When hook runs with detected plugins → Then hook exits 0 with no visible error
- **TC-005**: Given `plugins: ["sw"]` → When hook runs → Then `sw` is skipped (never re-installed)
- **TC-006**: Given `plugins: []` (empty array) → When hook runs → Then no install commands are called

**Note**: Existing test file `user-prompt-submit-autoload.test.ts` may cover some of this — check for overlap before writing to avoid duplication.

---

## Coverage Summary

| AC ID | Task(s) | Type |
|-------|---------|------|
| AC-US1-01 | T-001, T-005 | unit |
| AC-US1-02 | T-001, T-005 | unit |
| AC-US1-03 | T-001, T-005 | unit |
| AC-US1-04 | T-004 | JSDoc + passthrough verify |
| AC-US2-01 | T-002, T-003, T-005 | unit |
| AC-US2-02 | T-003, T-005 | unit |
| AC-US2-03 | T-003, T-005 | unit |
| AC-US3-01 | T-007, T-010 | unit |
| AC-US3-02 | T-008, T-010 | unit |
| AC-US3-03 | T-007, T-010 | unit |
| AC-US3-04 | T-009, T-010 | unit |
| AC-US4-01 | T-011, T-012 | integration |
| AC-US4-02 | T-011 | implementation note |
| AC-US4-03 | T-011, T-012 | integration |
| AC-US4-04 | T-011, T-012 | integration |

## Recommended Execution Order

T-001 → T-002 → T-003 → T-005 (US-001/US-002 block, sequential)
T-006 → T-007 → T-008 → T-009 → T-010 (US-003 block, sequential within block)
T-011 → T-012 (US-004 block, depends on T-002/T-003 for `--plugin` flag)
T-004 (independent, can run anytime)
