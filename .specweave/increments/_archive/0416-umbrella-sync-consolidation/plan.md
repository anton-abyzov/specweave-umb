# Architecture Plan: 0416 Umbrella Sync Consolidation

## Skill Chain Marker
architect:0416-umbrella-sync-consolidation

---

## Problem Summary

The sync pipeline (LivingDocsSync, sync-progress, ExternalIssueAutoCreator) reads only `config.sync.github` — a single global target. `childRepos[].sync` exists in config.json but is untyped and unread. StoryRouter exists but is unwired. The result: all issues land in one repo regardless of project.

---

## Architecture Decision Records

### AD-1: Resolution Strategy — Project Name First, Prefix Fallback

**Decision**: `SyncTargetResolver.resolve(projectName)` uses a two-phase lookup:

1. **Phase 1 — Name match**: `childRepos.find(r => r.name === projectName || r.id === projectName)`. Handles the common case where `**Project**: vskill` maps directly to `childRepos[].id: "vskill"`.
2. **Phase 2 — Prefix fallback**: Call existing `routeByPrefix(storyId, childRepos)` for increments that use prefixed story IDs (US-VSK-001) but have no `project:` frontmatter field.
3. **Phase 3 — Global fallback**: Return global `config.sync.{github,jira,ado}` when no match. Preserves existing behavior for uncategorized increments.

**Rationale**: Phase 1 covers the 95% case without touching StoryRouter. Phase 2 reuses the existing (unwired) router as a fallback without duplicating logic. Phase 3 ensures zero breakage for single-project setups.

**Rejected**: Per-story routing within an increment — out of scope per spec.

---

### AD-2: New Type `ChildRepoSyncConfig`

Formalizes what already exists in config.json but is currently untyped:

```typescript
// src/core/config/types.ts

export interface ChildRepoGitHubSync {
  owner: string;
  repo: string;
}

export interface ChildRepoJiraSync {
  projectKey: string;
}

export interface ChildRepoAdoSync {
  project: string;
}

export interface ChildRepoSyncConfig {
  github?: ChildRepoGitHubSync;
  jira?: ChildRepoJiraSync;
  ado?: ChildRepoAdoSync;
}

// Updated ChildRepoConfig — adds sync field
export interface ChildRepoConfig {
  id: string;
  path: string;
  name?: string;
  prefix: string;
  githubUrl?: string;
  jiraProject?: string;   // legacy — keep for backward compat
  adoProject?: string;    // legacy — keep for backward compat
  techStack?: string[];
  role?: string;
  sync?: ChildRepoSyncConfig;  // NEW
}

// Updated UmbrellaConfig — adds syncStrategy
export interface UmbrellaConfig {
  enabled: boolean;
  parentRepo?: string;
  childRepos: ChildRepoConfig[];
  storyRouting?: { enabled: boolean; defaultRepo: string };
  syncStrategy?: 'centralized' | 'distributed';  // NEW — defaults to 'centralized'
}
```

---

### AD-3: Single `SyncTargetResolver` Used by All Sync Paths

**Component**: `src/sync/sync-target-resolver.ts` (new file)

**Responsibility**: Single pure function that encapsulates the resolution chain (AD-1) and returns a typed result used by all three callers. No class, no state — trivially testable.

```typescript
export interface SyncTargetConfig {
  github?: { owner: string; repo: string };
  jira?: { projectKey: string };
  ado?: { project: string };
  source: 'child-repo-name' | 'child-repo-prefix' | 'global';
}

export function resolveSyncTarget(
  projectName: string | undefined,
  config: SpecWeaveConfig,
): SyncTargetConfig
```

**Resolution chain inside `resolveSyncTarget`**:

```
syncStrategy === 'distributed'?
  YES -> phase 1 name match   -> return childRepo.sync (source: 'child-repo-name')
      -> phase 2 prefix match -> return childRepo.sync (source: 'child-repo-prefix')
      -> phase 3 global       -> return config.sync    (source: 'global')
  NO  -> return config.sync (AC-US1-02: centralized preserved)
```

**Callers** — each reads only what it needs:

| Caller | Reads | Change |
|--------|-------|--------|
| `LivingDocsSync.syncToGitHub()` | `result.github.{owner,repo}` | Replace hardcoded `config.sync.github` |
| `sync-progress.ts` AC checkbox sync | `result.github.{owner,repo}` | Pass resolved target into `GitHubACCheckboxSync` constructor |
| `ExternalIssueAutoCreator` Jira | `result.jira.projectKey` | Add optional `overrideProjectKey` param |
| `ExternalIssueAutoCreator` ADO | `result.ado.project` | Add optional `overrideProject` param |

---

### AD-4: `--consolidate` Subcommand in `migrate-to-umbrella.ts`

Follows the existing dispatch pattern: `options.rollback` → `handleRollback()`, `options.addRepo` → `handleAddRepo()`, etc.

New: `options.consolidate` → `handleConsolidate()` delegating to a new engine module.

**New engine**: `src/core/migration/consolidation-engine.ts`

```typescript
export interface ConsolidationPlan {
  moves: Array<{ from: string; to: string; type: 'increment' | 'living-doc' }>;
  deletions: Array<{ path: string; reason: 'duplicate' }>;
}

export async function scanForOrphans(umbrellaRoot: string): Promise<ConsolidationPlan>
export async function executeConsolidation(plan: ConsolidationPlan, umbrellaRoot: string): Promise<void>
```

**Scan logic** in `scanForOrphans`:
1. Find all `repositories/*/` subdirectories containing `.specweave/`.
2. Enumerate `.specweave/increments/####-*/` in each.
3. Check umbrella root `.specweave/increments/` for same increment ID.
   - Not present → schedule `move`.
   - Present (duplicate) → schedule `deletion` of nested copy (umbrella root wins).
4. Enumerate `.specweave/docs/` entries → schedule `move` to umbrella root docs.

**Dry-run default** (AC-US2-05): `--consolidate` alone prints the plan. `--consolidate --execute` runs `executeConsolidation`. Same UX pattern as the existing migration subcommands.

---

## Component Map

```
src/sync/
  sync-target-resolver.ts        NEW  — pure resolver function (AD-3)
  story-router.ts                EXISTING — used as phase-2 fallback, no changes
  external-issue-auto-creator.ts MODIFIED — call resolver, pass overrides

src/core/living-docs/
  living-docs-sync.ts            MODIFIED — call resolver in syncToGitHub()

src/cli/commands/
  sync-progress.ts               MODIFIED — call resolver before GitHubACCheckboxSync
  migrate-to-umbrella.ts         MODIFIED — add --consolidate / --execute dispatch

src/core/migration/
  consolidation-engine.ts        NEW  — scan + execute logic (AD-4)
  types.ts                       MODIFIED — add ConsolidationPlan, MigrationOptions.consolidate

src/core/config/
  types.ts                       MODIFIED — ChildRepoSyncConfig, updated ChildRepoConfig, UmbrellaConfig (AD-2)

src/utils/
  multi-project-detector.ts      BUG FIX — displayName -> name (AC-US3-03)

src/core/project/
  project-resolution.ts          BUG FIX — getAvailableProjects() falls back to childRepos (AC-US3-04)
```

---

## Data Flow: Distributed GitHub Sync

```
LivingDocsSync.syncToGitHub(featureId, projectPath)
  |
  +-- read projectName from increment spec.md frontmatter
  |
  +-- resolveSyncTarget(projectName, config)
  |     +-- syncStrategy !== 'distributed'  -> return global (no change)
  |     +-- childRepos.find(name/id match)  -> return childRepo.sync.github
  |     +-- routeByPrefix(storyId)          -> return matched childRepo.sync.github
  |     +-- fallback                        -> return config.sync.github
  |
  +-- new GitHubClientV2({ owner, repo, token })
        +-- GitHubFeatureSync.syncFeature(...)
```

---

## Data Flow: Consolidation

```
migrate-to-umbrella --consolidate [--execute]
  |
  +-- scanForOrphans(umbrellaRoot)
  |     +-- glob repositories/*/
  |     +-- for each nested .specweave/increments/####-*/
  |     |     check umbrella for same ID
  |     |     -> ConsolidationPlan.moves[] or .deletions[]
  |     +-- for each nested .specweave/docs/**
  |           -> ConsolidationPlan.moves[]
  |
  +-- print plan (always)
  |
  +-- --execute?
        YES -> executeConsolidation(plan, umbrellaRoot)
               fs.rename() for moves, fs.rm() for deletions
        NO  -> exit (dry-run, AC-US2-05)
```

---

## Type System Fixes (US-003)

| Bug | Location | Fix |
|-----|----------|-----|
| `repo.displayName` used, field doesn't exist | `multi-project-detector.ts` line 122 | Change to `repo.name` |
| `getAvailableProjects()` ignores `childRepos` | `project-resolution.ts` line 382 | Add `else if (config.umbrella?.enabled)` branch mapping `childRepos[].name` |
| `ChildRepoConfig.sync` missing | `types.ts` | Add `sync?: ChildRepoSyncConfig` |
| `UmbrellaConfig.syncStrategy` missing | `types.ts` | Add `syncStrategy?: 'centralized' \| 'distributed'` |

---

## Technology Stack

- **Language**: TypeScript (strict mode, ESM, `.js` imports throughout)
- **Test framework**: Vitest with `vi.hoisted()` for ESM mocking
- **File ops**: Node.js `fs/promises` (no new deps)
- **No new dependencies** — resolver is pure TS, engine uses stdlib only

---

## Risk Assessment

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| `syncToGitHub()` call site doesn't have projectName in scope | Medium | Extract from spec.md frontmatter at call site; fall back to global if absent |
| `childRepo.sync` absent while `syncStrategy=distributed` | Medium | Phase 3 global fallback in resolver — no crash, graceful degradation |
| Nested repo dirty git state before consolidation | Low | Warn user if dirty working tree detected; require `--force` to override |
| `ExternalIssueAutoCreator` lacks override param | Low | Non-breaking optional param addition |

---

## Implementation Order

1. `types.ts` — add `ChildRepoSyncConfig`, update `ChildRepoConfig`, `UmbrellaConfig` (unblocks everything else)
2. `sync-target-resolver.ts` — new pure function, full unit test coverage
3. `living-docs-sync.ts` — wire resolver (US1-01, highest-value AC)
4. `sync-progress.ts` — wire resolver for AC checkbox sync (US1-03)
5. `external-issue-auto-creator.ts` — wire resolver for Jira/ADO (US1-04, US1-05)
6. Bug fixes — `multi-project-detector.ts` + `project-resolution.ts` (US3-03, US3-04)
7. `consolidation-engine.ts` — new scan/execute engine (US-002)
8. `migrate-to-umbrella.ts` — add `--consolidate` dispatch (US-002 CLI)
