# Architecture Plan: Simplify Init to Always-Multi Repository

**ADR**: [0244-always-multi-repo-architecture](../../docs/internal/architecture/adr/0244-always-multi-repo-architecture.md)
**Increment**: 0581-init-always-multi-repo
**Stage**: 1 of 2

## Overview

Remove the single vs multi-repo distinction from SpecWeave init. Every workspace uses `repositories/owner/repo` structure from day one. A single repository is just a workspace with one repo -- not a separate mode.

The change touches 4 layers: type system, init command flow, CLI command registration, and documentation. Implementation proceeds bottom-up: types first (foundation), then init rewrite (behavioral change), then command removal (dead code), then docs (communication).

## Architecture

```
BEFORE                                    AFTER
------                                    -----
init -> language -> path -> guards        init -> language -> path -> guards
     -> adapter -> provider                    -> adapter -> provider
     -> "4-way setup question"                 -> "Which repos?" (2-choice)
     -> isMultiRepo branching                  -> always create repositories/
     -> conditional multiProject.enabled       -> always umbrella.enabled=true
     -> conditional next-steps                 -> unified next-steps

Types:                                    Types:
  RepositoryHosting: 9 values               RepositoryHosting: 5 values
  RepoArchitecture: single|multi|mono       RepoArchitecture: multi|mono|parent
  SetupArchitecture: single|multi|...       SetupArchitecture: multi|mono|parent

Commands:                                 Commands:
  migrate-to-umbrella (505 lines)           DELETED (stub in bin/specweave.js)
  resolve-structure (32 lines)              DELETED (stub in bin/specweave.js)

Files:                                    Files:
  single-project-migrator.ts                DELETED
```

## Implementation Phases

### Phase 1: Config Types (Foundation, No Behavioral Change)

Clean the type system so downstream phases work against correct types. No runtime behavior changes.

#### 1a. `RepositoryHosting` Type Simplification

Remove `-single`/`-multirepo` suffixes from both locations:

**`src/cli/helpers/init/types.ts`** (lines 53-62):
```typescript
// Before: 9 values with mode suffixes
// After: 5 values, one per provider
type RepositoryHosting = 'github' | 'bitbucket' | 'ado' | 'local' | 'other';
```

**`src/cli/helpers/issue-tracker/types.ts`** (lines 194-210):
Same simplification. Keep in sync with init/types.ts.

**Consumer files** (update pattern-match sites):
- `src/cli/commands/sync-setup.ts`
- `src/cli/helpers/issue-tracker/github-multi-repo.ts`

#### 1b. `RepoArchitecture` and `SetupArchitecture` Type Changes

**`src/core/repo-structure/repo-structure-manager.ts`** (line 46):
```typescript
// Remove 'single' -- workspace always multi-capable
type RepoArchitecture = 'multi-repo' | 'monorepo' | 'parent';
```

**`src/core/repo-structure/setup-state-manager.ts`** (line 24):
```typescript
type SetupArchitecture = 'multi-repo' | 'parent' | 'monorepo';
```

#### 1c. `single-project-migrator.ts` Deletion

- DELETE: `src/core/config/single-project-migrator.ts`
- MODIFY: `src/core/config/config-manager.ts` -- remove import (lines 19-21) and call to `detectAndMigrateSingleProject`
- UPDATE: `src/core/project/project-resolution.ts` -- remove comment reference (line 213)

#### 1d. `multiProject.enabled` Deprecation

- `src/cli/commands/init.ts` (lines 444-447): Remove `isMultiRepo` conditional block that writes `multiProject.enabled`
- `MultiProjectConfig` type and `multiProject` field in `SpecWeaveConfig` REMAIN for backward compat

### Phase 2: Init Command Rewrite

Replace the 4-way prompt with simplified 2-choice repo connection. Always create `repositories/`. Always set `umbrella.enabled: true`.

#### 2a. `promptProjectSetup` Replacement

**`src/cli/helpers/init/repo-connect.ts`** (lines 75-144):

Simplify `ProjectSetupChoice`:
```typescript
// Before: 4 choices
type ProjectSetupChoice = 'existing' | 'clone-repos' | 'multi-repo-deferred' | 'scratch';

// After: 2 choices
type ProjectSetupChoice = 'clone-repos' | 'add-later';
```

Replace the 4-choice `select` prompt with a 2-choice prompt:
1. "Connect repositories" -- clone URLs, org/repo shorthand
2. "Add later via `specweave get`"

Remove `'existing'` and `'scratch'` -- subsumed by "add later" since workspace always has `repositories/`.

#### 2b. Init Flow Changes

**`src/cli/commands/init.ts`** (lines 341-467):

1. Remove `let isMultiRepo = false` declaration (line 343) and all references
2. Replace conditional `repositories/` creation with unconditional:
   ```typescript
   // Always create repositories/ (even for "add later" and CI)
   fs.mkdirSync(path.join(targetDir, 'repositories'), { recursive: true });
   ```
3. Simplify post-scaffold block: remove `hasGit` check (only check `hasRepos` and `!isCI`)
4. Make umbrella config write unconditional (lines 428-433):
   ```typescript
   const umbrellaDiscovery = scanUmbrellaRepos(targetDir);
   if (umbrellaDiscovery) {
     const umbrellaFragment = buildUmbrellaConfig(umbrellaDiscovery, finalProjectName);
     config.umbrella = umbrellaFragment.umbrella;
     config.repository = { ...config.repository, ...umbrellaFragment.repository };
   } else {
     config.umbrella = { enabled: true, projectName: finalProjectName, childRepos: [] };
   }
   ```
5. Remove `multiProject.enabled` write (lines 444-447)
6. Remove optional sync-setup chain (lines 455-467)

#### 2c. Summary Banner Update

**`src/cli/helpers/init/summary-banner.ts`** (lines 61-73):

Replace "Single repository" fallback with "Workspace (N repositories)":
```typescript
if (options.umbrellaDiscovery) {
  const d = options.umbrellaDiscovery;
  lines.push(chalk.cyan('  Structure: ') + `Workspace (${d.totalRepoCount} repositories)`);
  // ... repo list display unchanged
} else {
  lines.push(chalk.cyan('  Structure: ') + 'Workspace (0 repositories)');
}
```

#### 2d. Next Steps Update

**`src/cli/helpers/init/next-steps.ts`** (lines 213-220):

Replace conditional branching with unconditional:
```typescript
// Always show specweave get, never show migrate-to-umbrella
console.log(`   ${stepNumber + 2}. ${chalk.white('specweave get owner/repo')}        ${chalk.gray('Add a repository')}`);
console.log(`      ${chalk.white('specweave get "org/*"')}          ${chalk.gray('Add all repos from an org')}`);
```

Remove `context.isMultiRepo` and `context.isUmbrella` branching.

#### 2e. `NextStepsContext` Simplification

**`src/cli/helpers/init/types.ts`** (lines 227-233):

Remove `isMultiRepo` field. Keep `isUmbrella` and `misplacedRepos` (still useful for summary banner and warnings).

```typescript
interface NextStepsContext {
  isUmbrella?: boolean;  // Keep for summary banner
  misplacedRepos?: string[];  // Keep for warning display
}
```

### Phase 3: Command Removal + Deprecation

#### 3a. `migrate-to-umbrella.ts` Deletion

- DELETE: `src/cli/commands/migrate-to-umbrella.ts` (505 lines)
- MODIFY: `bin/specweave.js` (lines 1522-1543) -- replace with deprecation stub:
  ```javascript
  program
    .command('migrate-to-umbrella')
    .description('[Removed] Use specweave get to add repositories')
    .action(() => {
      console.log('This command has been removed. Use `specweave get` to add repositories.');
      process.exit(0);
    });
  ```

**PRESERVE**: `src/core/migration/umbrella-migrator.ts` -- used by consolidation/reorganize sub-commands which remain valid.

#### 3b. `resolve-structure.ts` Deletion

- DELETE: `src/cli/commands/resolve-structure.ts` (32 lines)
- MODIFY: `bin/specweave.js` (lines 1307-1315) -- replace with deprecation stub:
  ```javascript
  program
    .command('resolve-structure')
    .description('[Removed] Repository structure is now always workspace-based')
    .action(() => {
      console.log('This command has been removed. All workspaces now use the repositories/ structure.');
      process.exit(0);
    });
  ```

### Phase 4: Documentation Sweep

Grep-based sweep for: `single.repo`, `multi.repo`, `isMultiRepo`, `migrate-to-umbrella`, `resolve-structure`, `single vs multi`, `4-way`, `promptProjectSetup`.

#### Zone 1: Templates

| File | Change |
|------|--------|
| `templates/CLAUDE.md.template` | Remove single/multi references, update init description |
| `templates/AGENTS.md.template` | Rename "Multi-Repo Structure" -> "Repository Structure" |

#### Zone 2: Docs-site (~23 files)

Key files requiring substantive rewrites:

| File | Change |
|------|--------|
| `docs-site/docs/guides/multi-project-setup.md` | Rewrite: unified workspace model, no migration |
| `docs-site/docs/guides/command-reference-by-priority.md` | Remove `migrate-to-umbrella` entry |
| `docs-site/docs/getting-started/installation.md` | Update init flow description |
| `docs-site/docs/academy/specweave-essentials/12-init-deep-dive.md` | Rewrite setup section |
| `docs-site/docs/guides/repository-selection.md` | Remove single/multi distinction |

Remaining ~18 files: search-and-replace for outdated terminology.

#### Zone 3: In-repo docs

| File | Change |
|------|--------|
| Root `CLAUDE.md` (specweave repo) | Update "Multi-repo" section |

## Test Strategy

TDD is active per `config.json`. Tests written before implementation.

### New Tests

| Test | Target ACs |
|------|------------|
| `RepositoryHosting` has no `-single`/`-multirepo` values | AC-US4-01, AC-US4-02 |
| `RepoArchitecture` has no `'single'` value | AC-US4-03 |
| `SetupArchitecture` has no `'single'` value | AC-US4-04 |
| `promptProjectSetup` presents 2 choices, not 4 | AC-US1-01 |
| Init always creates `repositories/` | AC-US1-03 |
| Init config has no `multiProject.enabled` | AC-US6-03 |
| Summary banner shows "Workspace" not "Single repository" | AC-US1-04 |
| Next steps shows `specweave get`, no `migrate-to-umbrella` | AC-US1-05 |
| `migrate-to-umbrella` stub prints message, exits 0 | AC-US2-03 |

### Test File Updates

| Test File | Change |
|-----------|--------|
| `tests/unit/cli/commands/init-multirepo.test.ts` | Rewrite for unified flow (AC-US6-01) |
| `tests/unit/cli/helpers/init/repo-connect.test.ts` | Update for 2-choice prompt |
| `tests/unit/cli/helpers/init/summary-banner.test.ts` | Update "Single repository" assertions |
| DELETE: `tests/unit/cli/commands/migrate-to-umbrella.test.ts` | AC-US6-02 |

### Existing Test Preservation

All tests not touching removed code must continue passing. Run full `npx vitest run` after each phase.

## Dependency Order

```
Phase 1 (types) -----> Phase 2 (init rewrite) -----> Phase 4 (docs)
                  \                                /
                   --> Phase 3 (command removal) --/
```

Phase 1 must come first (types are foundation). Phases 2 and 3 depend on Phase 1 but are independent of each other. Phase 4 depends on all code changes.

## Risk Mitigations

| Risk | Mitigation |
|------|------------|
| Downstream code depends on `-single`/`-multirepo` values | Grep identified 4 consumer files; all updated in Phase 1 |
| Old configs with `multiProject.enabled` cause runtime errors | Field stays in `SpecWeaveConfig` type; tolerated at read time |
| `umbrella.enabled` always-true creates dead branches | Accepted debt for Stage 1; 38 refs in 20 files documented for Stage 2 |
| Missed doc references | Automated grep sweep before Phase 4 |
| `single-project-migrator` removal breaks config-manager | Import removed alongside file; call site removed |

## Stage 2 Roadmap (Out of Scope)

For reference -- NOT part of this increment:

1. Replace 38 `umbrella.enabled` check sites across 20 files
2. Rename `umbrella` config key to `workspace`
3. Remove `UmbrellaConfig.enabled` field (always true is pointless)
4. Build migration utility for pre-change single-repo configs
5. Remove `MultiProjectConfig` type entirely
