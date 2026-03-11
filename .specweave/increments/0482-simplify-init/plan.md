# Architecture Plan: Radically Simplify specweave init

## Summary

Strip the `specweave init` command down to its essential purpose: scaffold `.specweave/`, detect adapter and git provider, generate a minimal config, and show guided next steps. All external tool integration (repo hosting setup, issue tracker setup, repo cloning, multi-project folders, brownfield/greenfield classification) is removed from init and delegated to existing dedicated commands.

This is a subtraction refactoring -- no new modules, no new abstractions, no new patterns. The architecture decision is: **init does scaffolding only; everything else lives in purpose-built commands that already exist.**

## Architecture Decision

### ADR: Init as Pure Scaffolding (supersedes ADR-0008/ADR-0019 as they relate to init)

**Context**: `init.ts` grew to 1,242 lines by absorbing responsibilities that belong to other commands: `sync-setup` (external tool connections), `migrate-to-umbrella` (repo cloning, multi-project), `import` (issue import). The brownfield/greenfield distinction was added to init (ADR-0008, ADR-0018, ADR-0019) but its init-time classification adds prompts without actionable value -- brownfield analysis is better triggered per-increment via `/sw:living-docs`.

**Decision**: Init becomes a pure scaffolding command. It creates files, detects environment, and exits. No wizard flows, no external API calls, no repo cloning.

**Status**: Proposed (this increment implements it).

**Consequences**:
- Users who previously configured everything in one init run now run `specweave sync-setup` separately -- next-steps output guides them.
- `structureDeferred` and `projectMaturity` fields no longer appear in new config.json files. Existing configs with these fields still work (optional chaining).
- `resolve-structure` command gets a deprecation notice since init no longer sets `structureDeferred`.
- ADR-0008 and ADR-0019 remain valid for brownfield support in general -- only the init-time classification step is removed.

## Component Boundaries

### What init.ts KEEPS (the core scaffolding path)

```
initCommand()
  |
  +-- isNonInteractive()         # CI/quick detection (unchanged)
  +-- promptLanguageSelection()  # Language selection (unchanged)
  +-- Path resolution + guards   # Umbrella, suspicious, nested checks (unchanged)
  +-- promptSmartReinit()        # Re-init flow (unchanged)
  +-- AdapterLoader.detectTool() # Adapter detection (unchanged)
  +-- detectProvider()           # NEW import from provider-detection.ts (silent, no prompt)
  +-- createDirectoryStructure() # Directory scaffolding (unchanged)
  +-- copyTemplates()           # CLAUDE.md/AGENTS.md (unchanged)
  +-- createConfigFile()        # Config generation (SIMPLIFIED -- fewer params)
  +-- installAllPlugins()       # Claude plugin install (unchanged)
  +-- enableAgentTeamsEnvVar()  # Claude settings (unchanged)
  +-- applySmartDefaults()      # Smart defaults (unchanged)
  +-- installGitHooks()         # Git hooks (unchanged)
  +-- setupLspEnvVar()          # LSP setup (unchanged)
  +-- displaySummaryBanner()    # Summary (SIMPLIFIED interface)
  +-- showNextSteps()           # Next steps (REWRITTEN -- guided commands)
```

### What init.ts REMOVES

```
REMOVED from initCommand():
  - isGreenfieldCheck()           # No more greenfield/brownfield classification
  - projectMaturity prompt        # No more greenfield/brownfield question
  - setupRepositoryHosting()      # Replaced by silent detectProvider()
  - triggerAdoRepoCloning()       # Lives in migrate-to-umbrella
  - triggerGitHubRepoCloning()    # Lives in migrate-to-umbrella
  - triggerBitbucketRepoCloning() # Lives in migrate-to-umbrella
  - Repository config update block (lines 786-863)
  - createProjectFolders()        # Lives in migrate-to-umbrella
  - setupIssueTrackerWrapper()    # Lives in sync-setup
  - autoInstallSelectedExternalPlugin() # Lives in sync-setup
  - createMultiProjectFolders()   # Lives in migrate-to-umbrella

REMOVED functions (from init.ts):
  - createMultiProjectFolders()   # 170 lines of JIRA/ADO folder creation
  - setupIssueTrackerWrapper()    # 56 lines wrapping issue tracker setup
  - autoInstallSelectedExternalPlugin() # 53 lines of plugin auto-install
```

### Module Dependency Changes

```
BEFORE (init.ts imports):
  init.ts --> helpers/init/index.ts (setupRepositoryHosting, ProjectMaturity, RepositoryHosting)
  init.ts --> helpers/init/ado-repo-cloning.ts
  init.ts --> helpers/init/github-repo-cloning.ts
  init.ts --> helpers/init/bitbucket-repo-cloning.ts
  init.ts --> helpers/init/multi-project-folders.ts
  init.ts --> helpers/init/greenfield-detection.ts
  init.ts --> utils/env-file.ts (readEnvFile, parseEnvFile)
  init.ts --> core/types/sync-profile.ts (SyncProfile, JiraConfig)
  init.ts --> core/types/plugin-scope.ts (getPluginScope, getScopeArgs)

AFTER (init.ts imports):
  init.ts --> helpers/init/index.ts (same minus removed types/functions)
  init.ts --> helpers/init/provider-detection.ts (detectProvider) [NEW]

  REMOVED imports: ado-repo-cloning, github-repo-cloning, bitbucket-repo-cloning,
  multi-project-folders, greenfield-detection, env-file, sync-profile, plugin-scope
```

## File-by-File Change Plan

### Implementation Order

Bottom-up: modify dependencies before dependents.

```
1. directory-structure.ts  # Simplify createConfigFile() signature
2. next-steps.ts           # Rewrite to show guided commands
3. summary-banner.ts       # Remove external tool fields from interface
4. types.ts                # Remove unused types
5. index.ts                # Clean barrel exports, add detectProvider
6. init.ts                 # MAIN REWRITE -- gut 70% of the code
7. config.json.template    # Simplify reference template
8. resolve-structure.ts    # Add deprecation warning
9. init.test.ts            # Rewrite tests for new flow
```

All files are in `repositories/anton-abyzov/specweave/`.

### 1. src/cli/helpers/init/directory-structure.ts

**Change**: Remove `projectMaturity` and `structureDeferred` parameters from `createConfigFile()`. Remove `multiProject` and `issueTracker` sections from generated config.

**Signature change**:
```
Before: createConfigFile(targetDir, projectName, adapter, language, enableDocsPreview, testMode?, coverageTarget?, projectMaturity?, structureDeferred?)
After:  createConfigFile(targetDir, projectName, adapter, language, enableDocsPreview, testMode?, coverageTarget?)
```

**Config output changes**: Remove `project.maturity`, `project.structureDeferred`, `multiProject` block, `issueTracker` block from the generated config object. Keep sync defaults, hooks, auto, lsp, testing, documentation, language, translation.

**Import change**: Remove `ProjectMaturity` from the `types.ts` import.

### 2. src/cli/helpers/init/next-steps.ts

**Change**: Replace adapter-specific verbose instructions with a universal "What's next" section showing follow-up commands. Keep plugin status display for Claude. Keep i18n support.

**New output after plugin status**:
```
What's next:
  specweave sync-setup           Connect GitHub Issues, JIRA, or ADO
  specweave increment "feature"  Start your first feature
  specweave migrate-to-umbrella  Set up multi-repository workspace
```

**Remove**: Adapter-specific instruction blocks (cursor steps, generic steps). The follow-up commands are universal across all adapters.

**Keep**: Plugin status display for Claude adapter, cd step for subdirectory creation, docs/github links, i18n structure (add new keys for command descriptions).

### 3. src/cli/helpers/init/summary-banner.ts

**Interface change -- remove from `SummaryBannerOptions`**:
- `tracker` -- no longer set at init
- `repoCount` -- always 1 now (remove entirely)
- `isGreenfield` -- concept removed from init
- `hasPendingClones` -- no more cloning at init
- `externalPluginInstalled` -- moved to sync-setup
- `syncPermissions` -- moved to sync-setup
- `projectMaturity` -- concept removed from init
- `structureDeferred` -- concept removed from init

**Keep**: `projectName`, `provider`, `adapter`, `language`, `defaults`.

**Rendering changes**: Remove tracker display, sync permissions display, project maturity display, repo count display, brownfield/greenfield hint lines. Keep provider, adapter, config path, enabled defaults, quick reference.

### 4. src/cli/helpers/init/types.ts

**No removals.** Verification showed all types and constants are used by modules that are NOT being deleted:
- `ProjectMaturity` -- used by `repository-setup.ts`
- `RepositoryHosting` -- used by `repository-setup.ts`
- `REPO_FETCH_LIMITS` -- used by `github-repo-cloning.ts` and `bitbucket-repo-cloning.ts`

Init.ts stops importing `ProjectMaturity` and `RepositoryHosting` but the types remain in `types.ts` for other consumers.

### 5. src/cli/helpers/init/index.ts (barrel)

**Remove re-exports for**:
- `setupRepositoryHosting`, `RepositorySetupOptions`, `RepositorySetupResult`, `AdoProjectSelection` (from `./repository-setup.js`)
- `promptTestingConfig`, `updateConfigWithTesting`, `TestingConfigResult` (from `./testing-config.js`)
- `promptTranslationConfig`, `updateConfigWithTranslation`, `getDefaultTranslationConfig`, `TranslationConfigResult`, `TranslationScope` (from `./translation-config.js`)
- `promptAndRunExternalImport` (from `./external-import.js`)
- `promptBrownfieldAnalysis`, `updateConfigWithBrownfield`, `detectExistingDocsLocations`, `BrownfieldAnalysisConfig`, `AnalysisDepth`, `DetectedDocsLocation` (from `./brownfield-analysis.js`)
- `promptDeepInterviewConfig`, `updateConfigWithDeepInterview`, `DeepInterviewConfigResult` (from `./deep-interview-config.js`)
- `promptQualityGatesConfig`, `updateConfigWithQualityGates`, `getQualityGatePreset`, `QualityGatesConfigResult`, `QualityGatePreset`, `QualityGateSettings` (from `./quality-gates-config.js`)

**Add export**: `detectProvider`, `type ProviderInfo` from `./provider-detection.js`

**Risk mitigation**: Before removing, search codebase for any imports of these symbols from `helpers/init/index.js`. The underlying `.ts` files are NOT deleted -- only barrel re-exports are removed. Any other consumer can import directly from the source module.

### 6. src/cli/commands/init.ts (MAIN REWRITE)

**Target**: 1,242 lines --> ~300 lines.

**Remove imports**:
- `readEnvFile`, `parseEnvFile` from `../../utils/env-file.js`
- `SyncProfile`, `JiraConfig` from `../../core/types/sync-profile.js`
- `RepositoryHosting`, `ProjectMaturity` from barrel
- `setupRepositoryHosting` from barrel
- `triggerAdoRepoCloning` from `../helpers/init/ado-repo-cloning.js`
- `triggerGitHubRepoCloning` from `../helpers/init/github-repo-cloning.js`
- `triggerBitbucketRepoCloning` from `../helpers/init/bitbucket-repo-cloning.js`
- `createProjectFolders` from `../helpers/init/multi-project-folders.js`
- `isGreenfield` from `../helpers/init/greenfield-detection.js`
- `getPluginScope`, `getScopeArgs` from `../../core/types/plugin-scope.js`

**Add import**: `detectProvider` from `../helpers/init/provider-detection.js`

**Remove functions** (entire function bodies):
- `createMultiProjectFolders()` (lines 103-272)
- `setupIssueTrackerWrapper()` (lines 1122-1177)
- `autoInstallSelectedExternalPlugin()` (lines 1190-1242)

**initCommand() rewrite -- removed sections**:

| Lines | What | Replacement |
|-------|------|-------------|
| 594-622 | Greenfield/brownfield prompt | Remove entirely |
| 631-634 | `setupRepositoryHosting()` call | Silent `detectProvider()` after config creation |
| 725-741 | ADO repo cloning | Remove entirely |
| 743-766 | GitHub repo cloning | Remove entirely |
| 768-784 | Bitbucket repo cloning | Remove entirely |
| 786-863 | Repository config update block | 8-line inline `detectProvider()` block |
| 865-873 | Multi-project folders | Remove entirely |
| 875-906 | Issue tracker setup | Remove entirely |
| 909 | `createMultiProjectFolders()` call | Remove entirely |
| 959-1048 | Complex banner data building | Simplified ~15-line version |

**New provider detection block** (after `createConfigFile` call):
```typescript
const providerInfo = detectProvider(targetDir);
if (providerInfo) {
  const cfgPath = path.join(targetDir, '.specweave', 'config.json');
  const cfg = fs.readJsonSync(cfgPath);
  cfg.repository = {
    provider: providerInfo.provider,
    ...(providerInfo.owner && { organization: providerInfo.owner }),
  };
  fs.writeJsonSync(cfgPath, cfg, { spaces: 2 });
}
```

**Simplified banner call**: Only pass `projectName`, `provider`, `adapter`, `language`, `defaults`. No `tracker`, `repoCount`, `isGreenfield`, `hasPendingClones`, `externalPluginInstalled`, `syncPermissions`, `projectMaturity`, `structureDeferred`.

### 7. src/templates/config.json.template

**Change**: Reduce to hooks-only reference. The actual config is built programmatically by `createConfigFile()`.

```json
{
  "$schema": "https://spec-weave.com/schemas/config.json",
  "version": "2.0",
  "hooks": {
    "post_task_completion": { "sync_tasks_md": true, "external_tracker_sync": true },
    "post_increment_planning": { "auto_create_github_issue": true, "sync_living_docs": true },
    "post_increment_done": { "sync_living_docs": true, "sync_to_github_project": true, "close_github_issue": true }
  }
}
```

### 8. src/cli/commands/resolve-structure.ts

**Change**: Add deprecation warning at the top of `resolveStructureCommand()`. Command logic stays intact for backward compatibility.

### 9. tests/unit/cli/commands/init.test.ts

**Remove tests for**: `createMultiProjectFolders`, `setupIssueTrackerWrapper`, `autoInstallSelectedExternalPlugin`, greenfield/brownfield prompt, repository hosting setup, repo cloning (ADO/GitHub/Bitbucket).

**Remove mocks for**: `setupRepositoryHosting`, all cloning triggers, `createProjectFolders`, `isGreenfield`, `setupIssueTracker` dynamic import.

**Keep/update tests for**: `isNonInteractive()`, happy path (quick mode), re-init flow, adapter detection, path guards, config.json creation (simplified schema).

**Add new tests**: Provider auto-detection populates config correctly; no external tool prompts in any mode; next steps shows follow-up commands; config.json has no `multiProject`/`issueTracker`/`projectMaturity`/`structureDeferred` fields.

## Backward Compatibility

### Config Reading (SAFE)

All config readers use optional chaining (`config.sync?.profiles`, `config.umbrella?.enabled`, `config.issueTracker?.provider`, `config.multiProject?.enabled`). Removing fields from NEW configs does not break reading of OLD configs.

### Config Writing (ONE-WAY)

New init creates simpler configs. Old init created richer configs. No migration needed.

### resolve-structure (DEPRECATED)

Still functions for projects with `structureDeferred: true`. Prints deprecation notice.

### Helper Modules (UNTOUCHED)

The following modules are NOT deleted, only disconnected from init's import graph:
- `repository-setup.ts` -- used by `migrate-to-umbrella`
- `greenfield-detection.ts` -- used by other flows
- `brownfield-analysis.ts` -- available for `/sw:living-docs`
- All cloning helpers -- available for `migrate-to-umbrella`
- `multi-project-folders.ts` -- available for `migrate-to-umbrella`
- `testing-config.ts`, `translation-config.ts`, `quality-gates-config.ts`, `deep-interview-config.ts`, `external-import.ts` -- available for direct use

## Risk Analysis

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Barrel export removal breaks other importers | Low | High | Search all importers before removing |
| `createConfigFile` signature change breaks callers | Low | High | Only init.ts calls it -- verified |
| Summary banner type narrowing breaks callers | Low | Medium | Only init.ts calls displaySummaryBanner |
| Users expect external tool setup during init | Medium | Low | Next-steps output guides to sync-setup |
| Tests reference removed mocks/functions | Medium | Medium | Comprehensive test rewrite in step 9 |

## Verification Checklist

1. `npm run build` -- zero TypeScript errors
2. `npx vitest run tests/unit/cli/commands/init` -- init tests pass
3. `npx vitest run` -- full test suite passes (no broken barrel imports)
4. Manual: `specweave init . --quick` in test dir -- creates `.specweave/`, config.json, CLAUDE.md
5. Manual: config.json has no `sync.profiles`, `issueTracker`, `multiProject`, `maturity` fields
6. Manual: next-steps output shows `sync-setup`, `increment`, `migrate-to-umbrella`

## Technology Stack

- **Language**: TypeScript (ESM, `--moduleResolution nodenext`)
- **Testing**: Vitest with `vi.hoisted()` + `vi.mock()` for ESM mocking
- **No new dependencies** -- this is purely a subtraction refactoring

## Line Count Targets

| File | Before | After | Delta |
|------|--------|-------|-------|
| init.ts | 1,242 | ~300 | -942 |
| next-steps.ts | 161 | ~90 | -71 |
| summary-banner.ts | 178 | ~100 | -78 |
| types.ts | 223 | 223 | 0 |
| index.ts | 167 | ~100 | -67 |
| config.json.template | 93 | ~15 | -78 |
| init.test.ts | ~1,920 | ~600 | -1,320 |
| **Total** | | | **~-2,556** |
