---
increment: 0482-simplify-init
title: "Radically Simplify specweave init"
total_tasks: 16
completed_tasks: 16
by_user_story:
  US-001: ["T-001", "T-002", "T-003", "T-004", "T-005"]
  US-002: ["T-006", "T-007"]
  US-003: ["T-008", "T-009", "T-010"]
  US-004: ["T-011", "T-012"]
  US-005: ["T-013", "T-014", "T-015", "T-016"]
---

# Tasks: Radically Simplify specweave init

---

## User Story: US-001 - Simplified Init Command

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06
**Tasks**: 5 total, 5 completed

---

### T-001: Simplify `createConfigFile()` in directory-structure.ts

**User Story**: US-001
**Satisfies ACs**: AC-US1-06
**Status**: [x] completed

**Test Plan**:
- **Given** `createConfigFile()` is called with targetDir, projectName, adapter, and language
- **When** the function completes
- **Then** the generated config.json contains no `multiProject`, `issueTracker`, `project.maturity`, or `project.structureDeferred` fields

**Test Cases**:
1. **Unit**: `tests/unit/cli/helpers/init/directory-structure.test.ts`
   - `testConfigHasNoCoreFluff()`: Assert config.json written to disk lacks removed fields
   - `testConfigHasCoreFields()`: Assert config has project name, adapter, hooks, auto, lsp, testing, language
   - `testFunctionSignatureDroppedParams()`: Call with old 9-arg signature fails (TS error) — call with 7-arg signature succeeds
   - **Coverage Target**: 95%

**Implementation**:
1. Open `repositories/anton-abyzov/specweave/src/cli/helpers/init/directory-structure.ts`
2. Remove `projectMaturity?: ProjectMaturity` and `structureDeferred?: boolean` parameters from `createConfigFile()` signature
3. Remove the `project.maturity` and `project.structureDeferred` spread lines from the generated config object
4. Remove the `multiProject` section block from the generated config object
5. Remove the `issueTracker` section block from the generated config object
6. Remove `ProjectMaturity` from the import of `./types.js`
7. Run `npx vitest run tests/unit/cli/helpers/init/directory-structure` to confirm existing tests pass

---

### T-002: Rewrite next-steps.ts with guided follow-up commands

**User Story**: US-001
**Satisfies ACs**: AC-US1-02
**Status**: [x] completed

**Test Plan**:
- **Given** `showNextSteps()` is called after a successful init for any adapter (Claude, Cursor, Generic)
- **When** the output is rendered
- **Then** it displays the three universal commands: `specweave sync-setup`, `specweave increment "feature"`, `specweave migrate-to-umbrella` and does NOT display adapter-specific instruction blocks

**Test Cases**:
1. **Unit**: `tests/unit/cli/helpers/init/next-steps.test.ts`
   - `testUniversalCommandsShown()`: Spy on `console.log`, assert three command strings appear for Claude adapter
   - `testUniversalCommandsShownCursor()`: Same assertion for Cursor adapter
   - `testNoAdapterSpecificBlocks()`: Assert cursor-specific or generic-specific instruction blocks are absent
   - `testPluginStatusStillShownForClaude()`: Assert Claude plugin status section still renders
   - **Coverage Target**: 90%

**Implementation**:
1. Open `repositories/anton-abyzov/specweave/src/cli/helpers/init/next-steps.ts`
2. Remove all adapter-specific instruction blocks (cursor steps, generic steps sections)
3. Replace removed blocks with a universal "What's next" section that always shows:
   - `specweave sync-setup` — Connect GitHub Issues, JIRA, or ADO
   - `specweave increment "feature"` — Start your first feature
   - `specweave migrate-to-umbrella` — Set up multi-repository workspace
4. Keep the plugin status display block for Claude adapter (unchanged)
5. Keep the cd step for subdirectory creation (unchanged)
6. Keep docs/github links at the bottom (unchanged)
7. Target line count: ~90 lines (from 161)

---

### T-003: Simplify summary-banner.ts interface

**User Story**: US-001
**Satisfies ACs**: AC-US1-06
**Status**: [x] completed

**Test Plan**:
- **Given** `displaySummaryBanner()` is called with only `projectName`, `provider`, `adapter`, `language`, and `defaults`
- **When** the banner renders
- **Then** no tracker, repoCount, greenfield, pendingClones, syncPermissions, projectMaturity, or structureDeferred fields are required or rendered

**Test Cases**:
1. **Unit**: `tests/unit/cli/helpers/init/summary-banner.test.ts`
   - `testBannerRendersWithMinimalOptions()`: Call with only kept fields — assert it renders without error
   - `testRemovedFieldsNotInOutput()`: Assert output does not mention tracker, isGreenfield, hasPendingClones
   - `testKeptFieldsInOutput()`: Assert project name, adapter, provider, language are present in output
   - **Coverage Target**: 90%

**Implementation**:
1. Open `repositories/anton-abyzov/specweave/src/cli/helpers/init/summary-banner.ts`
2. Remove from `SummaryBannerOptions` interface: `tracker`, `repoCount`, `isGreenfield`, `hasPendingClones`, `externalPluginInstalled`, `syncPermissions`, `projectMaturity`, `structureDeferred`
3. Keep in interface: `projectName`, `provider`, `adapter`, `language`, `defaults`
4. Remove corresponding rendering logic for each removed field from `formatSummaryBanner()`
5. Target line count: ~100 lines (from 178)

---

### T-004: Rewrite init.ts — main rewrite (remove 70% of code)

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Status**: [x] completed

**Test Plan**:
- **Given** `specweave init . --quick` is run in a directory
- **When** the command completes
- **Then** it creates `.specweave/`, config.json, CLAUDE.md, AGENTS.md in under 10 seconds without any prompts about external tools, hosting, or brownfield/greenfield classification

**Test Cases**:
1. **Unit**: `tests/unit/cli/commands/init.test.ts`
   - `testQuickModeNoPrompts()`: Mock all I/O — assert no prompts for external tools in `--quick` mode
   - `testInteractiveModeMaxTwoPrompts()`: Assert at most language selection and adapter confirmation prompts appear
   - `testProviderDetectedSilently()`: Mock `.git/config` — assert `detectProvider()` called, config updated without prompt
   - `testStructureCreated()`: Assert `.specweave/`, `config.json`, `CLAUDE.md`, `AGENTS.md` all created
   - **Coverage Target**: 90%

**Implementation**:
1. Open `repositories/anton-abyzov/specweave/src/cli/commands/init.ts`
2. Remove the three function bodies entirely: `createMultiProjectFolders()` (lines 103-272), `setupIssueTrackerWrapper()`, `autoInstallSelectedExternalPlugin()`
3. Remove imports: `readEnvFile`, `parseEnvFile`, `SyncProfile`, `JiraConfig`, `RepositoryHosting`, `ProjectMaturity`, `setupRepositoryHosting`, `triggerAdoRepoCloning`, `triggerGitHubRepoCloning`, `triggerBitbucketRepoCloning`, `createProjectFolders`, `isGreenfield`, `getPluginScope`, `getScopeArgs`
4. Add import: `detectProvider` from `../helpers/init/provider-detection.js`
5. Remove from `initCommand()`: greenfield/brownfield prompt block (lines 594-622), `setupRepositoryHosting()` call, all repo cloning sections (ADO 725-741, GitHub 743-766, Bitbucket 768-784), repository config update block (786-863), multi-project folder creation (865-873), issue tracker setup (875-906), `createMultiProjectFolders()` call (909), complex banner data building (959-1048)
6. Replace `createConfigFile()` call: update to simplified 7-arg signature (drop projectMaturity, structureDeferred)
7. Add inline provider detection block after `createConfigFile()` — silently read `.git/config` via `detectProvider()`, update config.json if provider found
8. Update `displaySummaryBanner()` call to pass only: `projectName`, `provider`, `adapter`, `language`, `defaults`
9. Target: ~300 lines (from 1,242)

---

### T-005: Export `detectProvider` from provider-detection.ts and barrel

**User Story**: US-001
**Satisfies ACs**: AC-US1-03
**Status**: [x] completed

**Test Plan**:
- **Given** a directory with a `.git/config` containing a GitHub remote URL
- **When** `detectProvider(targetDir)` is called
- **Then** it returns `{ provider: "github", owner: "<org>", repo: "<name>" }` without throwing

**Test Cases**:
1. **Unit**: `tests/unit/cli/helpers/init/provider-detection.test.ts`
   - `testDetectsGitHubRemote()`: Write a mock `.git/config` — assert provider is "github" with correct owner
   - `testDetectsAdoRemote()`: Write a mock `.git/config` with ADO URL — assert provider is "ado"
   - `testReturnsUndefinedWhenNoGit()`: Assert returns undefined/null when no `.git/config` exists
   - **Coverage Target**: 90%

**Implementation**:
1. Open `repositories/anton-abyzov/specweave/src/cli/helpers/init/provider-detection.ts`
2. Verify `detectProvider()` is exported — add `export` keyword if missing
3. Open `repositories/anton-abyzov/specweave/src/cli/helpers/init/index.ts`
4. Add `export { detectProvider, type ProviderInfo } from './provider-detection.js'`
5. Verify no duplicate export conflicts

---

## User Story: US-002 - Guided Next Steps

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04
**Tasks**: 2 total, 2 completed

---

### T-006: Verify guided commands appear in next-steps output

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-03, AC-US2-04
**Status**: [x] completed

**Test Plan**:
- **Given** a successful init completes
- **When** `showNextSteps()` renders the completion output
- **Then** it includes `specweave sync-setup`, `specweave increment "feature"`, `specweave migrate-to-umbrella` with descriptions, plus documentation links — and does NOT include verbose adapter-specific instruction blocks

**Test Cases**:
1. **Unit**: `tests/unit/cli/helpers/init/next-steps.test.ts`
   - `testThreeCommandsPresent()`: Spy on `console.log` output — assert all three command strings appear
   - `testDocsLinkPresent()`: Assert documentation URL still present in output
   - `testGitHubLinkPresent()`: Assert GitHub link still present in output
   - `testNoCursorSpecificBlock()`: Assert cursor-specific instruction block absent
   - **Coverage Target**: 90%

**Implementation**:
1. This task validates T-002's implementation
2. Write/update test cases in `tests/unit/cli/helpers/init/next-steps.test.ts`
3. Run `npx vitest run tests/unit/cli/helpers/init/next-steps` — assert all pass

---

### T-007: Verify summary banner shows project/adapter/provider/language

**User Story**: US-002
**Satisfies ACs**: AC-US2-02
**Status**: [x] completed

**Test Plan**:
- **Given** a successful init with a detected GitHub provider and Claude adapter
- **When** the summary banner is displayed
- **Then** it shows the project name, detected adapter (Claude Code), detected provider (github), and language

**Test Cases**:
1. **Unit**: `tests/unit/cli/helpers/init/summary-banner.test.ts`
   - `testBannerShowsProjectName()`: Assert project name appears in formatted banner
   - `testBannerShowsAdapter()`: Assert adapter name appears in banner
   - `testBannerShowsProvider()`: Assert provider appears in banner
   - `testBannerShowsLanguage()`: Assert language appears in banner
   - **Coverage Target**: 90%

**Implementation**:
1. This task validates T-003's implementation
2. Write/update test cases in `tests/unit/cli/helpers/init/summary-banner.test.ts`
3. Run `npx vitest run tests/unit/cli/helpers/init/summary-banner` — assert all pass

---

## User Story: US-003 - Simplified Config Schema

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04
**Tasks**: 3 total, 3 completed

---

### T-008: Verify config.json has no external tool fields after init

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02
**Status**: [x] completed

**Test Plan**:
- **Given** `specweave init . --quick` runs successfully
- **When** the generated config.json is inspected
- **Then** it contains no `multiProject`, `issueTracker`, `projectMaturity`, `structureDeferred`, `sync.profiles`, or provider-specific connection settings

**Test Cases**:
1. **Unit**: `tests/unit/cli/commands/init.test.ts`
   - `testConfigHasNoMultiProject()`: Run init, read written config.json, assert no `multiProject` key
   - `testConfigHasNoIssueTracker()`: Assert no `issueTracker` key
   - `testConfigHasNoMaturity()`: Assert no `project.maturity` key
   - `testConfigHasNoDeferredStructure()`: Assert no `project.structureDeferred` key
   - `testConfigHasNoSyncProfiles()`: Assert no `sync.profiles` array
   - **Coverage Target**: 90%

**Implementation**:
1. These tests validate the combination of T-001 and T-004
2. Add config schema validation test cases to `tests/unit/cli/commands/init.test.ts`
3. Run `npx vitest run tests/unit/cli/commands/init` — assert all pass

---

### T-009: Verify provider auto-detection populates config.json

**User Story**: US-003
**Satisfies ACs**: AC-US3-03
**Status**: [x] completed

**Test Plan**:
- **Given** a directory with a `.git/config` containing a GitHub remote URL `git@github.com:acme/myrepo.git`
- **When** `specweave init . --quick` runs
- **Then** config.json contains `repository.provider = "github"` and `repository.organization = "acme"`

**Test Cases**:
1. **Unit**: `tests/unit/cli/commands/init.test.ts`
   - `testGitHubProviderWrittenToConfig()`: Mock `detectProvider` to return github+acme — assert config.json has correct `repository` block
   - `testProviderBlockAbsentWhenNoGit()`: Mock `detectProvider` to return null — assert no `repository` block written
   - **Coverage Target**: 90%

**Implementation**:
1. These tests validate the inline provider detection block added in T-004
2. Add provider config validation test cases to `tests/unit/cli/commands/init.test.ts`
3. Mock `detectProvider` using `vi.hoisted()` + `vi.mock()` ESM pattern
4. Run `npx vitest run tests/unit/cli/commands/init` — assert all pass

---

### T-010: Verify backward compatibility with existing configs

**User Story**: US-003
**Satisfies ACs**: AC-US3-04
**Status**: [x] completed

**Test Plan**:
- **Given** an existing config.json that contains `sync.profiles`, `umbrella`, `issueTracker`, and `multiProject` sections
- **When** any SpecWeave command reads that config via the config loader
- **Then** it loads without error and all optional-chained fields return expected values

**Test Cases**:
1. **Unit**: Existing config loader test file
   - `testOldConfigWithSyncProfilesLoads()`: Load a fixture config with all old fields — assert no throw, optional fields accessible
   - `testOldConfigIssueTrackerLoads()`: Assert `config.issueTracker?.provider` returns correct value from old config
   - `testOldConfigMultiProjectLoads()`: Assert `config.multiProject?.enabled` returns correct value
   - **Coverage Target**: 85%

**Implementation**:
1. Create or update config loader backward-compat tests
2. Write a fixture config JSON containing all old fields (`sync.profiles`, `issueTracker`, `multiProject`, `projectMaturity`, `structureDeferred`)
3. Assert the config loader reads all fields without error via optional chaining
4. Run `npx vitest run` to confirm no regressions in config reading

---

## User Story: US-004 - Clean Summary Banner

**Linked ACs**: AC-US4-01, AC-US4-02, AC-US4-03
**Tasks**: 2 total, 2 completed

---

### T-011: Remove external tool fields from SummaryBannerOptions interface

**User Story**: US-004
**Satisfies ACs**: AC-US4-03
**Status**: [x] completed

**Test Plan**:
- **Given** the `SummaryBannerOptions` TypeScript interface in summary-banner.ts
- **When** inspected after the change
- **Then** it no longer contains `tracker`, `repoCount`, `isGreenfield`, `hasPendingClones`, `externalPluginInstalled`, `syncPermissions`, `projectMaturity`, or `structureDeferred` fields

**Test Cases**:
1. **Type-level**: TypeScript compilation verifies removed fields are absent
   - Attempting to pass `tracker: "jira"` to `displaySummaryBanner()` must produce a TS compile error
2. **Unit**: `tests/unit/cli/helpers/init/summary-banner.test.ts`
   - `testInterfaceOnlyHasKeptFields()`: Construct `SummaryBannerOptions` with only kept fields — assert no TypeScript error
   - **Coverage Target**: 90%

**Implementation**:
1. This task validates the interface changes made in T-003
2. Add a type-level test confirming the interface is narrowed
3. Run `npm run build` — assert zero TypeScript errors
4. Run `npx vitest run tests/unit/cli/helpers/init/summary-banner` — assert all pass

---

### T-012: Verify summary banner renders correctly with simplified data

**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-02
**Status**: [x] completed

**Test Plan**:
- **Given** `displaySummaryBanner({ projectName: "myapp", adapter: "Claude Code", provider: "github", language: "en", defaults: {...} })`
- **When** the banner renders
- **Then** it shows project name, adapter, provider, language, and defaults — and does not display tracker, repoCount, isGreenfield, hasPendingClones, syncPermissions, projectMaturity, or structureDeferred

**Test Cases**:
1. **Unit**: `tests/unit/cli/helpers/init/summary-banner.test.ts`
   - `testBannerOutputDoesNotMentionTracker()`: Capture console output — assert no "tracker" or "issue tracker" text
   - `testBannerOutputDoesNotMentionGreenfield()`: Assert no "greenfield" or "brownfield" text
   - `testBannerOutputDoesNotMentionPendingClones()`: Assert no "pending clones" or "repository cloning" text
   - `testBannerDefaultsSection()`: Assert testing, quality gates, LSP, git hooks defaults are displayed
   - **Coverage Target**: 90%

**Implementation**:
1. This task validates the rendering changes made in T-003
2. Update/write test cases in `tests/unit/cli/helpers/init/summary-banner.test.ts`
3. Run `npx vitest run tests/unit/cli/helpers/init/summary-banner` — assert all pass

---

## User Story: US-005 - Barrel and Type Cleanup

**Linked ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04, AC-US5-05
**Tasks**: 4 total, 4 completed

---

### T-013: Clean index.ts barrel exports

**User Story**: US-005
**Satisfies ACs**: AC-US5-02, AC-US5-03
**Status**: [x] completed

**Test Plan**:
- **Given** the `src/cli/helpers/init/index.ts` barrel file
- **When** the barrel is updated
- **Then** it no longer re-exports `setupRepositoryHosting`, `promptTestingConfig`, `promptTranslationConfig`, `promptBrownfieldAnalysis`, `promptDeepInterviewConfig`, `promptQualityGatesConfig`, `promptAndRunExternalImport` — but DOES export `detectProvider`

**Test Cases**:
1. **Type-level**: TypeScript compilation confirms removed symbols are no longer importable from the barrel
2. **Build gate**: `npm run build` passes after barrel cleanup
   - `testDetectProviderExportedFromBarrel()`: Import `detectProvider` from barrel — assert it is a function
   - **Coverage Target**: 85%

**Implementation**:
1. Search codebase first: identify all importers of removed symbols from the barrel — ensure removing them does not break other consumers (underlying `.ts` files are NOT deleted)
2. Open `repositories/anton-abyzov/specweave/src/cli/helpers/init/index.ts`
3. Remove re-exports for: `setupRepositoryHosting` and associated types, `promptTestingConfig` block, `promptTranslationConfig` block, `promptAndRunExternalImport`, `promptBrownfieldAnalysis` block, `promptDeepInterviewConfig` block, `promptQualityGatesConfig` block
4. Add `export { detectProvider, type ProviderInfo } from './provider-detection.js'`
5. Run `npm run build` — verify zero TypeScript errors

---

### T-014: Simplify config.json.template

**User Story**: US-005
**Satisfies ACs**: AC-US5-05
**Status**: [x] completed

**Test Plan**:
- **Given** the `src/templates/config.json.template` file
- **When** simplified to hooks-only content
- **Then** it is valid JSON with only `$schema`, `version`, and `hooks` fields, and the project still builds cleanly

**Test Cases**:
1. **Build gate**: `npm run build` passes after template change
2. **Unit**: Any template loading test
   - `testTemplateIsValidJson()`: Parse the simplified template — assert no JSON parse error
   - `testTemplateHasHooksOnly()`: Assert template contains `hooks` key and does not contain `multiProject`, `issueTracker`, `sync` keys
   - **Coverage Target**: 80%

**Implementation**:
1. Open `repositories/anton-abyzov/specweave/src/templates/config.json.template`
2. Replace entire content with the minimal hooks-only template (schema, version, hooks only)
3. Target: ~15 lines (from 93)
4. Run `npm run build` — assert builds cleanly

---

### T-015: Add deprecation warning to resolve-structure.ts

**User Story**: US-005
**Satisfies ACs**: AC-US5-04
**Status**: [x] completed

**Test Plan**:
- **Given** a user runs `specweave resolve-structure` on a project
- **When** the command handler executes
- **Then** a deprecation warning is printed before the command logic runs, and the command still completes normally for projects with `structureDeferred: true`

**Test Cases**:
1. **Unit**: `tests/unit/cli/commands/resolve-structure.test.ts`
   - `testDeprecationWarningPrinted()`: Spy on `console.warn` — assert deprecation message appears
   - `testCommandStillFunctions()`: Assert command still resolves structure for existing projects with `structureDeferred: true`
   - **Coverage Target**: 85%

**Implementation**:
1. Open `repositories/anton-abyzov/specweave/src/cli/commands/resolve-structure.ts`
2. Add a deprecation warning at the top of `resolveStructureCommand()` before all existing logic
3. Leave all existing command logic unchanged
4. Run `npx vitest run tests/unit/cli/commands/resolve-structure` — assert all pass

---

### T-016: Rewrite init.test.ts and run full test suite

**User Story**: US-005
**Satisfies ACs**: AC-US5-04, AC-US5-05
**Status**: [x] completed

**Test Plan**:
- **Given** the rewritten init.ts and all helper changes are complete
- **When** `npx vitest run` is executed
- **Then** zero tests fail, TypeScript compiles cleanly, and init.test.ts covers the simplified init flow with ~600 lines (from ~1,920)

**Test Cases**:
1. **Integration**: Full test suite run
   - All previously passing tests continue to pass
   - New init tests validate the simplified flow
   - No broken barrel imports detected
   - `npm run build` exits with code 0
   - **Coverage Target**: 90% for init.test.ts

**Implementation**:
1. Open `repositories/anton-abyzov/specweave/tests/unit/cli/commands/init.test.ts`
2. Remove all test blocks for: `createMultiProjectFolders`, `setupIssueTrackerWrapper`, `autoInstallSelectedExternalPlugin`, greenfield/brownfield prompt flow, repository hosting setup flow, repo cloning (ADO/GitHub/Bitbucket)
3. Remove all mocks for: `setupRepositoryHosting`, `triggerAdoRepoCloning`, `triggerGitHubRepoCloning`, `triggerBitbucketRepoCloning`, `createProjectFolders`, `isGreenfield`, `setupIssueTracker` dynamic import
4. Keep and update tests for: `isNonInteractive()`, happy path (quick mode), re-init flow, adapter detection, path guards, config.json creation (simplified schema)
5. Add new tests: provider auto-detection populates config correctly, no external tool prompts in any mode, next steps shows follow-up commands, config has no removed fields
6. Target: ~600 lines (from ~1,920)
7. Run `npm run build` — assert zero TypeScript errors
8. Run `npx vitest run` — assert zero failures across full suite
