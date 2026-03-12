---
increment: 0515-vskill-marketplace-sync
title: "vskill marketplace sync command"
total_tasks: 5
completed_tasks: 5
by_user_story:
  US-001: [T-001, T-002]
  US-002: [T-001, T-002]
  US-003: [T-003, T-004]
  US-004: [T-003, T-004, T-005]
tdd_mode: strict
---

# Tasks: vskill marketplace sync command

## User Story: US-001 - Auto-add new plugins to marketplace.json

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Tasks**: 2 total, 0 completed

---

### T-001: Write failing tests for `syncMarketplace()` pure function (TDD RED)

**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed

**Test Plan**:
- **Given** a manifest with no entry for `foo` and a `LocalPlugin` for `foo` with version and description
- **When** `syncMarketplace(manifest, [fooPlugin])` is called
- **Then** the returned manifest includes `foo` with `source: "./plugins/foo"` and entries contains status `"added"`

- **Given** a manifest with `mobile` at version `2.3.0` and a `LocalPlugin` at version `2.4.0`
- **When** `syncMarketplace(manifest, [mobilePlugin])` is called
- **Then** returned manifest has `mobile` at `2.4.0` and entry status is `"updated"`

- **Given** a manifest entry whose fields exactly match the corresponding `LocalPlugin`
- **When** `syncMarketplace(manifest, [plugin])` is called
- **Then** the manifest is returned unchanged and entry status is `"unchanged"`

- **Given** an empty `localPlugins` array
- **When** `syncMarketplace(manifest, [])` is called
- **Then** `entries` is empty and the manifest is returned as-is

**Test Cases**:
1. **Unit**: `src/marketplace/marketplace.test.ts`
   - `addsNewPlugin()`: plugin absent from manifest -> entry added, source `"./plugins/<dirName>"`, status `"added"`
   - `updatesVersionDrift()`: manifest version `2.3.0`, plugin.json `2.4.0` -> status `"updated"`, manifest patched
   - `updatesDescriptionDrift()`: manifest desc `"old"`, plugin.json `"new"` -> status `"updated"`
   - `leavesUnchangedEntry()`: identical fields -> status `"unchanged"`, manifest not mutated
   - `handlesEmptyLocalPlugins()`: `localPlugins=[]` -> `entries=[]`, original manifest returned
   - `preservesExistingEntriesNotInLocalPlugins()`: entries not referenced by localPlugins stay in manifest
   - `firstEncounteredWinsOnDuplicate()`: two LocalPlugins with same name -> first added, second in `skipped`
   - **Coverage Target**: 95%

**TDD Cycle**: RED -- all tests must FAIL before implementation. Imports of `syncMarketplace` will throw.

**Implementation**:
1. Open `src/marketplace/marketplace.test.ts` in `repositories/anton-abyzov/vskill/`
2. Add imports: `syncMarketplace`, `LocalPlugin`, `SyncResult` from `./marketplace.js`
3. Write all test cases under `describe("syncMarketplace", ...)`
4. Run `npx vitest run src/marketplace/marketplace.test.ts` -- confirm all fail with import/type errors
5. Do NOT implement -- RED phase complete

---

### T-002: Implement `syncMarketplace()` and new types in `src/marketplace/marketplace.ts` (TDD GREEN)

**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed

**Test Plan**:
- **Given** the failing tests from T-001
- **When** `syncMarketplace()` and required types are exported from `marketplace.ts`
- **Then** all T-001 test cases pass with zero regressions in existing marketplace tests

**Test Cases**:
1. **Unit**: `src/marketplace/marketplace.test.ts` (all T-001 tests must now be GREEN)
   - Re-run same suite after implementation
   - **Coverage Target**: 95%

**TDD Cycle**: GREEN -- minimum code to make T-001 tests pass, no gold-plating

**Implementation**:
1. Open `src/marketplace/marketplace.ts`
2. Add types:
   - `LocalPlugin { name: string; dirName: string; version?: string; description?: string }`
   - `SyncPluginStatus = "added" | "updated" | "unchanged"`
   - `SyncPluginEntry { name: string; status: SyncPluginStatus; details?: string }`
   - `SyncResult { entries: SyncPluginEntry[]; manifest: MarketplaceManifest; skipped: string[] }`
3. Implement `syncMarketplace(manifest, localPlugins)`:
   - Build `Map<name, MarketplacePlugin>` from `manifest.plugins`
   - Track seen names set to detect duplicates (first wins, second goes to `skipped`)
   - For each `LocalPlugin`: classify added/updated/unchanged; patch manifest entry when changed
   - Preserve existing entries not touched by localPlugins (no orphan removal per spec)
   - Return `SyncResult`
4. Re-export new types from `src/marketplace/index.ts`
5. Run `npx vitest run src/marketplace/marketplace.test.ts` -- all GREEN
6. Run `npx vitest run` -- zero regressions across full suite

---

## User Story: US-003 - Dry-run preview mode

**Linked ACs**: AC-US3-01, AC-US3-02
**Tasks**: 2 total, 0 completed

---

### T-003: Write failing tests for `marketplaceCommand()` (TDD RED)

**User Story**: US-003, US-004 | **Satisfies ACs**: AC-US1-02, AC-US1-03, AC-US3-01, AC-US3-02, AC-US4-01, AC-US4-02, AC-US4-04 | **Status**: [x] completed

**Test Plan**:
- **Given** a `plugins/new-plugin/` directory and a `--dry-run` flag
- **When** `marketplaceCommand("sync", { dryRun: true })` is called
- **Then** summary table is printed but `writeFile` is never called and output includes "dry run -- no changes written"

- **Given** a `plugins/new-plugin/` directory without `--dry-run`
- **When** `marketplaceCommand("sync", {})` is called
- **Then** `writeFile` is called once with updated marketplace.json content

- **Given** a `plugins/foo/` directory with no `.claude-plugin/plugin.json`
- **When** `marketplaceCommand("sync", {})` is called
- **Then** `foo` is skipped with a warning and the command exits 0

- **Given** `.claude-plugin/marketplace.json` does not exist
- **When** `marketplaceCommand("sync", {})` is called
- **Then** an error is printed and process exits with code 1

- **Given** an unrecognized subcommand
- **When** `marketplaceCommand("badcmd", {})` is called
- **Then** an error is printed and process exits with code 1

**Test Cases**:
1. **Integration**: `src/commands/marketplace.test.ts` (new file, mock `node:fs/promises`)
   - Use `vi.hoisted()` to define mocks before imports per vskill ESM convention
   - `writesFileWhenPluginsAdded()`: new plugin dir -> `writeFile` called with JSON including new entry
   - `skipsWriteOnDryRun()`: `dryRun: true` -> `writeFile` NOT called; output includes "dry run -- no changes written"
   - `skipsDirWithoutPluginJson()`: ENOENT on plugin.json -> warning logged, exit 0, writeFile still called
   - `exits1OnMissingMarketplaceJson()`: ENOENT on marketplace.json -> exit 1
   - `exits1OnMalformedMarketplaceJson()`: invalid JSON string -> exit 1
   - `exits1OnUnknownSubcommand()`: `"unknown"` subcommand -> exit 1
   - `printsSummaryTableWithStatusIndicators()`: output contains `+` for added, `~` for updated, ` ` for unchanged
   - `printsDryRunNoChangesLine()`: dry-run output includes "no changes written"
   - **Coverage Target**: 90%

**TDD Cycle**: RED -- file does not exist; all tests must fail on import

**Implementation**:
1. Create `src/commands/marketplace.test.ts`
2. Use `vi.hoisted()` to mock `node:fs/promises` (`readFile`, `readdir`, `writeFile`, `stat`) and `../utils/project-root.js`
3. Write all test cases under `describe("marketplaceCommand", ...)`
4. Import `marketplaceCommand` from `./marketplace.js` (will fail -- expected)
5. Run `npx vitest run src/commands/marketplace.test.ts` -- confirm all fail (RED)

---

## User Story: US-004 - Informative summary output and alias

**Linked ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04
**Tasks**: 2 total, 0 completed

---

### T-004: Implement `src/commands/marketplace.ts` and register command in `src/index.ts` (TDD GREEN)

**User Story**: US-003, US-004 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04 | **Status**: [x] completed

**Test Plan**:
- **Given** the failing tests from T-003
- **When** `marketplaceCommand` is implemented and registered under alias `mp`
- **Then** all T-003 tests pass and `vskill mp sync` routes to the same handler as `vskill marketplace sync`

**Test Cases**:
1. **Integration**: `src/commands/marketplace.test.ts` (all T-003 tests must now be GREEN)
   - **Coverage Target**: 90%

**TDD Cycle**: GREEN -- minimum code to make T-003 tests pass

**Implementation**:
1. Create `src/commands/marketplace.ts`:
   - Export `MarketplaceSyncOpts { dryRun?: boolean; cwd?: string }` and `marketplaceCommand(subcommand, opts)`
   - Resolve root via `findProjectRoot(opts.cwd || process.cwd())`
   - Read `.claude-plugin/marketplace.json` with `node:fs/promises`; catch ENOENT and JSON parse errors -> print error + exit 1
   - `readdir(pluginsDir, { withFileTypes: true })` and filter to directories only (skip files silently)
   - For each dir: read `.claude-plugin/plugin.json`; on ENOENT/parse error/missing `name` -> collect warning
   - Call `syncMarketplace(manifest, localPlugins)` from `../marketplace/marketplace.js`
   - Print skipped warnings to stderr
   - Print summary table: one row per entry with `+`/`~`/` ` indicator and plugin name using `output.ts` helpers
   - If `!dryRun`: `writeFile(path, JSON.stringify(updatedManifest, null, 2) + "\n", "utf-8")`
   - If `dryRun`: print `"dry run -- no changes written"`
   - Exit 1 for unknown subcommand
   - All imports use `.js` extensions (ESM nodenext)
2. Modify `src/index.ts`:
   - Add `.command("marketplace [subcommand]").alias("mp").description("Manage marketplace.json")`
   - Options: `.option("--dry-run", "Preview without writing").option("--cwd <path>", "Project root")`
   - Action: `const { marketplaceCommand } = await import("./commands/marketplace.js"); await marketplaceCommand(subcommand ?? "sync", opts)`
3. Run `npx vitest run src/commands/marketplace.test.ts` -- all GREEN
4. Run `npx vitest run` -- full suite green, zero regressions

---

### T-005: TDD REFACTOR -- full suite, build, smoke test

**User Story**: US-001, US-002, US-003, US-004 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US2-01, AC-US2-02, AC-US2-03, AC-US3-01, AC-US3-02, AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04 | **Status**: [x] completed

**Test Plan**:
- **Given** all T-001 and T-003 tests are green
- **When** refactor, build, and smoke tests run
- **Then** all tests pass, build succeeds with no type errors, and `marketplace sync --dry-run` on the vskill repo itself produces a valid summary table and exits 0 without modifying any file

**Test Cases**:
1. **Full suite**: `npx vitest run` in `repositories/anton-abyzov/vskill/` -- zero failures
2. **Build**: `npm run build` -- exits 0, no TypeScript errors
3. **Smoke**: `node dist/index.js marketplace sync --dry-run` -- prints summary table, prints "dry run -- no changes written", exits 0
4. **Alias smoke**: `node dist/index.js mp sync --dry-run` -- identical output to above
5. **Coverage**: `npx vitest run --coverage` -- 90%+ on `src/marketplace/marketplace.ts` new code and `src/commands/marketplace.ts`

**TDD Cycle**: REFACTOR -- clean up duplication, verify ESM conventions, no behavior changes

**Implementation**:
1. Review `syncMarketplace()` for clarity -- extract plugin.json validation helper if duplicated in command handler
2. Verify all new imports use `.js` extensions
3. Check for any console output helpers duplicated from existing `output.ts` -- consolidate if found
4. Run `npx vitest run --coverage` -- confirm 90%+ on new files
5. Run `npm run build` in `repositories/anton-abyzov/vskill/`
6. Run smoke tests against the vskill repo's own `plugins/` directory
7. Confirm `.claude-plugin/marketplace.json` is NOT modified after `--dry-run`
8. Mark all tasks `[x]` and update spec.md AC checkboxes from `[ ]` to `[x]`
