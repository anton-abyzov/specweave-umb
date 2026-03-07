---
increment: 0433-marketplace-unregistered-plugin-discovery
total_tasks: 12
completed_tasks: 12
by_user_story:
  US-001: [T-001, T-002]
  US-002: [T-003, T-004]
  US-003: [T-005, T-006, T-007]
  US-004: [T-008, T-009]
  US-005: [T-010, T-011]
  closure: [T-012]
---

# Tasks: Marketplace Unregistered Plugin Discovery

All changes are in `repositories/anton-abyzov/vskill/`.
Test files go in `repositories/anton-abyzov/vskill/tests/unit/`.

---

## User Story: US-001 - Discover Unregistered Plugin Directories

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Tasks**: 2 total, 2 completed

---

### T-001: Implement discoverUnregisteredPlugins() in marketplace.ts

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Status**: [x] completed

**Test Plan**:
- **Given** a marketplace repo where `plugins/` contains `frontend`, `backend`, `marketing` and marketplace.json lists only `frontend`, `backend`
- **When** `discoverUnregisteredPlugins("owner", "repo", manifestContent)` is called
- **Then** it returns `[{ name: "marketing", source: "plugins/marketing" }]`

- **Given** the GitHub Contents API returns a network error or 4xx
- **When** `discoverUnregisteredPlugins()` is called
- **Then** it returns `[]` without throwing

- **Given** `plugins/` contains a file `README.md` alongside directory `marketing`
- **When** discovery runs
- **Then** only `marketing` (type === "dir") is included; `README.md` is ignored

- **Given** all plugin directories are already in marketplace.json
- **When** discovery runs
- **Then** it returns `[]`

**Test Cases**:
1. **Unit**: `tests/unit/marketplace-discover.test.ts`
   - `testDiscoversDiff()`: returns unregistered dirs not in manifest
   - `testReturnsEmptyOnApiError()`: 500 response → []
   - `testReturnsEmptyOnNetworkFailure()`: fetch throws → []
   - `testIgnoresFiles()`: only type==="dir" entries count
   - `testAllRegisteredReturnsEmpty()`: manifest covers all dirs → []
   - **Coverage Target**: 95%

**Implementation**:
1. Add `UnregisteredPlugin` interface after `MarketplaceManifest` in `src/marketplace/marketplace.ts`
2. Add `discoverUnregisteredPlugins(owner, repo, manifestContent)` async function after `validateMarketplace()`
3. Fetch `https://api.github.com/repos/{owner}/{repo}/contents/plugins/` with `User-Agent: vskill-cli` header
4. On non-ok response or thrown error, return `[]`
5. Filter response JSON to entries where `type === "dir"`, extract `.name`
6. Diff against `getAvailablePlugins(manifestContent).map(p => p.name)`
7. Return `UnregisteredPlugin[]` for the difference

---

### T-002: Export discoverUnregisteredPlugins and UnregisteredPlugin from marketplace/index.ts

**User Story**: US-001
**Satisfies ACs**: AC-US1-01
**Status**: [x] completed

**Test Plan**:
- **Given** the export is added to `src/marketplace/index.ts`
- **When** a consumer imports `{ discoverUnregisteredPlugins }` from `"../marketplace/index.js"`
- **Then** the import resolves without error and the function is callable

**Test Cases**:
1. **Unit**: covered by T-001 test file (import from index path)
   - **Coverage Target**: N/A (export plumbing only)

**Implementation**:
1. Add `UnregisteredPlugin` to the `export type` line in `src/marketplace/index.ts`
2. Add `discoverUnregisteredPlugins` to the named `export` block

---

## User Story: US-002 - Display Unregistered Plugins in Picker UI

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Tasks**: 2 total, 2 completed

---

### T-003: Integrate discovery call and build combined picker items

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] completed

**Test Plan**:
- **Given** 12 registered plugins and 1 unregistered plugin `marketing`
- **When** the interactive picker is shown
- **Then** `marketing` appears at the bottom with a yellow `(new -- not in marketplace.json)` suffix and is unchecked by default

- **Given** unregistered plugins exist
- **When** the picker header is rendered
- **Then** it reads `Marketplace: <name> -- 12 registered, 1 unregistered` with the unregistered count in yellow

**Test Cases**:
1. **Unit**: `tests/unit/add-picker-integration.test.ts`
   - `testUnregisteredAppearsAtBottom()`: combined items array ends with unregistered items
   - `testUnregisteredUncheckedByDefault()`: `checked: false` for unregistered items
   - `testHeaderShowsUnregisteredCount()`: header string includes yellow count
   - `testHeaderOmitsUnregisteredWhenZero()`: no unregistered count when discovery returns []
   - **Coverage Target**: 90%

**Implementation**:
1. In `src/commands/add.ts`, inside `installMarketplaceRepo()`, after the `getAvailablePlugins()` call, add:
   `const unregistered = await discoverUnregisteredPlugins(owner, repo, manifestContent);`
2. Replace the existing header `console.log` line with a version that includes `, ${yellow(String(unregistered.length) + " unregistered")}` when `unregistered.length > 0`
3. In the checkbox picker branch, build `combinedItems`:
   - Registered items first (existing structure)
   - Unregistered items appended with `label: u.name + yellow(" (new -- not in marketplace.json)")`, `checked: false`
4. Pass `combinedItems` to `promptCheckboxList`

---

### T-004: Partition selected indices into registered vs unregistered

**User Story**: US-002
**Satisfies ACs**: AC-US2-01
**Status**: [x] completed

**Test Plan**:
- **Given** combined picker returns indices `[0, 2, 13]` where indices 0-11 are registered and 12+ are unregistered
- **When** partitioning runs
- **Then** `registeredSelected = [plugins[0], plugins[2]]` and `unregisteredSelected = [unregistered[1]]`

**Test Cases**:
1. **Unit**: `tests/unit/add-picker-integration.test.ts`
   - `testPartitionRegisteredIndices()`: indices < plugins.length map to registered array
   - `testPartitionUnregisteredIndices()`: indices >= plugins.length map to unregistered array
   - **Coverage Target**: 90%

**Implementation**:
1. After `promptCheckboxList` returns `selectedIndices`, add:
   ```typescript
   const registeredSelected = selectedIndices
     .filter(i => i < plugins.length)
     .map(i => plugins[i]);
   const unregisteredSelected = selectedIndices
     .filter(i => i >= plugins.length)
     .map(i => unregistered[i - plugins.length]);
   ```
2. Replace the existing post-picker loop (which used raw `selectedPlugins`) to use `registeredSelected` for the standard install path

---

## User Story: US-003 - Gate Unregistered Plugin Installation Behind --force

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04
**Tasks**: 3 total, 3 completed

---

### T-005: Add --force gate and offerResubmission() helper

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02
**Status**: [x] completed

**Test Plan**:
- **Given** a user selects unregistered plugin `marketing` without `--force`
- **When** confirming the selection
- **Then** a warning is printed for `marketing`, only registered plugins install, and re-submission is offered

- **Given** a user selects unregistered plugin `marketing` with `--force`
- **When** confirming the selection
- **Then** `installRepoPlugin()` is called with `overrideSource: "plugins/marketing"` and the re-submission prompt is suppressed

**Test Cases**:
1. **Unit**: `tests/unit/add-force-gate.test.ts`
   - `testNoForceWarnsAndSkipsUnregistered()`: warning printed, unregistered skipped
   - `testNoForceOffersResubmission()`: `offerResubmission()` called when unregistered selected without force
   - `testForceInstallsUnregistered()`: `installRepoPlugin` called with overrideSource
   - `testForceSkipsResubmissionPrompt()`: `offerResubmission` NOT called with --force
   - **Coverage Target**: 90%

**Implementation**:
1. Add `offerResubmission(owner, repo)` as a local function near `installMarketplaceRepo()` in `src/commands/add.ts`:
   - Prompt "Submit {owner}/{repo} for platform scanning?"
   - On accept: call `submitSkill({ repoUrl })`, print tracking URL
   - On error: print yellow fallback message with manual URL
2. After partition, add force gate:
   ```typescript
   if (unregisteredSelected.length > 0 && !opts.force) {
     for (const u of unregisteredSelected) {
       console.log(yellow(`Warning: "${u.name}" is not in marketplace.json and was skipped.`));
     }
     await offerResubmission(owner, repo);
   }
   if (unregisteredSelected.length > 0 && opts.force) {
     for (const u of unregisteredSelected) {
       await installRepoPlugin(`${owner}/${repo}`, u.name, opts, u.source);
     }
   }
   ```

---

### T-006: Add overrideSource parameter to installRepoPlugin()

**User Story**: US-003
**Satisfies ACs**: AC-US3-02, AC-US3-04
**Status**: [x] completed

**Test Plan**:
- **Given** `installRepoPlugin()` is called with `overrideSource: "plugins/marketing"`
- **When** the function runs
- **Then** it skips the marketplace.json lookup and uses `"plugins/marketing"` as `pluginPath`, version `"0.0.0"`, and still runs Tier-1 scan

- **Given** `overrideSource` is undefined
- **When** the function runs
- **Then** behavior is identical to before (no regression)

**Test Cases**:
1. **Unit**: `tests/unit/add-override-source.test.ts`
   - `testOverrideSourceSkipsManifestLookup()`: no call to `getPluginSource` when overrideSource provided
   - `testOverrideSourceSetsVersion000()`: `pluginVersion = "0.0.0"` when overrideSource provided
   - `testTier1ScanStillRuns()`: `runTier1Scan` called regardless of overrideSource
   - `testNoOverrideSourceUnchanged()`: existing behavior unchanged when overrideSource is undefined
   - **Coverage Target**: 90%

**Implementation**:
1. Change `installRepoPlugin(ownerRepo, pluginName, opts)` signature to `installRepoPlugin(ownerRepo, pluginName, opts, overrideSource?: string)`
2. At the manifest lookup section (where `getPluginSource` is called):
   ```typescript
   let pluginPath: string;
   let pluginVersion: string;
   if (overrideSource) {
     pluginPath = overrideSource;
     pluginVersion = "0.0.0";
   } else {
     pluginPath = getPluginSource(pluginName, manifestContent) ?? "";
     pluginVersion = getPluginVersion(pluginName, manifestContent) ?? "0.0.0";
   }
   ```
3. Ensure `runTier1Scan()` call is not gated on whether overrideSource was provided

---

### T-007: Handle --plugin <name> targeting unregistered plugins

**User Story**: US-003
**Satisfies ACs**: AC-US3-03
**Status**: [x] completed

**Test Plan**:
- **Given** `--plugin marketing` targets a plugin not in marketplace.json but discovered as unregistered, without `--force`
- **When** the command runs
- **Then** a warning is printed and `marketing` is not installed

- **Given** `--plugin marketing` with `--force`
- **When** the command runs
- **Then** `installRepoPlugin()` is called with `overrideSource: "plugins/marketing"`

**Test Cases**:
1. **Unit**: `tests/unit/add-force-gate.test.ts`
   - `testPluginFlagUnregisteredNoForce()`: warning + no install
   - `testPluginFlagUnregisteredWithForce()`: installs with overrideSource
   - **Coverage Target**: 90%

**Implementation**:
1. In the `opts.plugin` branch of `installMarketplaceRepo()`, after checking `hasPlugin(opts.plugin, manifestContent)`:
   - If not found in manifest, check if `unregistered.some(u => u.name === opts.plugin)`
   - If unregistered match found and `!opts.force`: print warning and return
   - If unregistered match found and `opts.force`: call `installRepoPlugin(ownerRepo, opts.plugin, opts, "plugins/" + opts.plugin)` and return
   - If no match anywhere: existing "Plugin X not found" error path

---

## User Story: US-004 - Non-TTY and Auto-Select Mode Handling

**Linked ACs**: AC-US4-01, AC-US4-02, AC-US4-03
**Tasks**: 2 total, 2 completed

---

### T-008: Non-TTY listing with (unregistered) label

**User Story**: US-004
**Satisfies ACs**: AC-US4-01
**Status**: [x] completed

**Test Plan**:
- **Given** non-TTY mode with 2 registered and 1 unregistered plugin
- **When** the plugin list is printed
- **Then** all 3 plugins are listed, unregistered one has `(unregistered)` suffix and a note: "Use --force to include unregistered plugins"

**Test Cases**:
1. **Unit**: `tests/unit/add-non-tty.test.ts`
   - `testNonTtyListsUnregisteredWithLabel()`: output includes `(unregistered)` for unregistered plugins
   - `testNonTtyPrintsForceNote()`: note about --force appears when unregistered plugins exist
   - `testNonTtyNoNoteWhenAllRegistered()`: no note when discovery returns []
   - **Coverage Target**: 85%

**Implementation**:
1. In the non-TTY branch of `installMarketplaceRepo()`, after listing registered plugins:
   ```typescript
   if (unregistered.length > 0) {
     for (const u of unregistered) {
       console.log(`  ${u.name} ${yellow("(unregistered)")}`);
     }
     console.log(yellow("  Note: use --force to include unregistered plugins"));
   }
   ```

---

### T-009: Auto-select (--yes/--all) skips unregistered; --yes --force includes them

**User Story**: US-004
**Satisfies ACs**: AC-US4-02, AC-US4-03
**Status**: [x] completed

**Test Plan**:
- **Given** `--yes` with 2 registered and 1 unregistered plugin
- **When** auto-selection runs
- **Then** only the 2 registered plugins are installed; unregistered is skipped with a message mentioning `--force`

- **Given** `--yes --force` with 1 registered and 1 unregistered plugin
- **When** auto-selection runs
- **Then** both plugins are installed (registered via normal path, unregistered via overrideSource)

**Test Cases**:
1. **Unit**: `tests/unit/add-non-tty.test.ts`
   - `testYesSkipsUnregistered()`: auto-select excludes unregistered without --force
   - `testYesPrintsSkipMessage()`: skip message mentions --force
   - `testYesForceIncludesUnregistered()`: auto-select includes unregistered with --force
   - **Coverage Target**: 90%

**Implementation**:
1. In the `--yes`/`--all` auto-select branch:
   ```typescript
   // Always auto-select all registered plugins
   const toInstall = plugins; // existing behavior
   if (unregistered.length > 0 && !opts.force) {
     console.log(yellow(`Skipping ${unregistered.length} unregistered plugin(s). Use --force to include.`));
   }
   if (unregistered.length > 0 && opts.force) {
     for (const u of unregistered) {
       await installRepoPlugin(`${owner}/${repo}`, u.name, opts, u.source);
     }
   }
   ```

---

## User Story: US-005 - Repo Re-Submission for Platform Scanning

**Linked ACs**: AC-US5-01, AC-US5-02, AC-US5-03
**Tasks**: 2 total, 2 completed

---

### T-010: offerResubmission() calls submitSkill and handles errors

**User Story**: US-005
**Satisfies ACs**: AC-US5-01, AC-US5-02
**Status**: [x] completed

**Test Plan**:
- **Given** the user accepts the re-submission prompt
- **When** `submitSkill({ repoUrl })` succeeds
- **Then** a green tracking URL is printed

- **Given** the user accepts the re-submission prompt
- **When** `submitSkill()` throws
- **Then** a yellow fallback message with manual URL is printed and install continues

- **Given** the user declines the re-submission prompt
- **When** `offerResubmission()` runs
- **Then** nothing is printed and the function returns without calling `submitSkill()`

**Test Cases**:
1. **Unit**: `tests/unit/add-resubmission.test.ts`
   - `testAcceptCallsSubmitSkill()`: submitSkill called with correct repoUrl
   - `testAcceptPrintsTrackingUrl()`: tracking URL printed on success
   - `testSubmitFailurePrintsFallback()`: fallback URL printed on error
   - `testDeclineSkipsSubmitSkill()`: submitSkill not called when user declines
   - **Coverage Target**: 90%

**Implementation**:
- `offerResubmission()` is already specified in T-005 as a local helper in `add.ts`
- This task focuses on the test coverage for the happy/error/decline paths
- Mock `submitSkill` from `src/api/client.ts` via `vi.mock()`
- Mock `createPrompter()` to control `promptConfirm` responses

---

### T-011: --force suppresses re-submission prompt

**User Story**: US-005
**Satisfies ACs**: AC-US5-03
**Status**: [x] completed

**Test Plan**:
- **Given** `--force` is used to install an unregistered plugin
- **When** the install completes
- **Then** `offerResubmission()` is not called and no re-submission prompt is shown

**Test Cases**:
1. **Unit**: `tests/unit/add-force-gate.test.ts`
   - `testForceSkipsResubmissionPrompt()`: already specified in T-005; confirm it is exercised
   - **Coverage Target**: 90%

**Implementation**:
- Verify the force gate in T-005 already handles this: `offerResubmission()` is only called in the `!opts.force` branch
- No additional code changes required; this task tracks the test verification

---

## Closure

### T-012: Run full test suite and verify all ACs pass

**User Story**: all
**Satisfies ACs**: AC-US1-01 through AC-US5-03
**Status**: [x] completed

**Test Plan**:
- **Given** all tasks T-001 through T-011 are complete
- **When** `npx vitest run` runs in `repositories/anton-abyzov/vskill/`
- **Then** all new test files pass with zero failures and overall coverage >= 90%

**Test Cases**:
1. Run: `cd repositories/anton-abyzov/vskill && npx vitest run --reporter=verbose`
2. Confirm all AC-IDs are covered (see spec.md checklist)
3. Mark AC checkboxes in spec.md as `[x]`

**Implementation**:
1. `cd repositories/anton-abyzov/vskill && npx vitest run`
2. Fix any failures before marking complete
3. Update spec.md: mark all AC-IDs `[x]`
4. Commit: `git add -p && git commit -m "feat: unregistered plugin discovery in marketplace picker"`
