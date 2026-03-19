# Implementation Plan: Rework External Tool Integration Architecture

## Overview

Replace the overlapping `umbrella` + `multiProject` + `projectMappings` config sections with a unified `workspace` section. Implement transparent migration on config read, simplify multi-project detection, update all consumers (init, sync-setup, import, dashboard, template-creator, umbrella-detector), and add a dashboard Workspace page.

## Architecture

### Component 1: WorkspaceConfig Type System

**Location**: `src/core/config/types.ts`

Replace three overlapping types with a single hierarchy:

```
BEFORE (3 overlapping sections):
  config.umbrella: UmbrellaConfig { enabled, childRepos: ChildRepoConfig[] }
  config.multiProject: MultiProjectConfig { enabled, projects }
  config.projectMappings: ProjectMappings

AFTER (1 unified section):
  config.workspace: WorkspaceConfig { repos: WorkspaceRepo[] }
```

**New types**:
```typescript
interface WorkspaceRepo {
  id: string;           // unique identifier (from ChildRepoConfig.id)
  path: string;         // relative path (from ChildRepoConfig.path)
  prefix: string;       // 3-char prefix for story routing (from ChildRepoConfig.prefix)
  remote?: string;      // git remote URL
  sync?: WorkspaceRepoSync;  // per-repo sync config (from ChildRepoConfig.sync)
}

interface WorkspaceRepoSync {
  provider: 'github' | 'jira' | 'ado';
  project?: string;     // external project identifier
  board?: string;       // board/area path
  labels?: string[];    // auto-applied labels
}

interface WorkspaceConfig {
  repos: WorkspaceRepo[];
}
```

**SpecWeaveConfig changes**: Add `workspace?: WorkspaceConfig`, deprecate (but keep for migration) `umbrella?`, `multiProject?`, `projectMappings?`.

---

### Component 2: Config Migration Layer

**Location**: New file `src/core/config/workspace-migrator.ts`

**Strategy**: Transparent migration on `ConfigManager.read()`, cleanup on `ConfigManager.write()`.

```
ConfigManager.read()
  → parse JSON
  → if (config.umbrella || config.multiProject) → migrateToWorkspace(config)
  → return config with workspace populated
  → old fields stripped from returned object

ConfigManager.write()
  → if (config.umbrella || config.multiProject) → strip old fields
  → write clean config with only workspace
```

**Migration rules**:
- `umbrella.childRepos[]` → `workspace.repos[]` (1:1 mapping)
- `multiProject.projects[]` → merge into `workspace.repos[]` by path/id
- `projectMappings` → merge into matching `workspace.repos[].sync`
- If both umbrella and multiProject define same repo → umbrella wins (it has richer data)
- Migration is idempotent — running twice produces same result

**Precedent**: `ConfigManager.read()` already strips deprecated `syncStrategy` field (lines 73-78 in config-manager.ts). This follows the same pattern.

---

### Component 3: Multi-Project Detector Rewrite

**Location**: `src/utils/multi-project-detector.ts`

**Before**: 4 separate detection strategies (umbrella config, multiProject config, sync profiles, folder scan).

**After**: 2 strategies:
1. **Primary**: `config.workspace.repos` exists and has 2+ entries → multi-project
2. **Fallback**: Folder scan under `repositories/` (for unconfigured workspaces)

The `MultiProjectDetectionResult` interface stays compatible. `umbrellaEnabled` field → deprecated, always `false`.

---

### Component 4: Sync Target Resolver Simplification

**Location**: `src/sync/sync-target-resolver.ts`

**Before**: 3-phase resolution reading from `umbrella.childRepos`.

**After**: Same 3-phase logic, but reads from `workspace.repos`:
- Phase 1: Name/ID match in `workspace.repos`
- Phase 2: Prefix fallback via story-router
- Phase 3: Global fallback

`SyncTargetConfig.source` values stay the same for backward compat.

---

### Component 5: Init Flow Changes

**Location**: `src/cli/commands/init.ts` + `src/cli/helpers/init/path-utils.ts`

- `scanUmbrellaRepos()` → rename to `scanWorkspaceRepos()`, return `WorkspaceRepo[]`
- `buildUmbrellaConfig()` → rename to `buildWorkspaceConfig()`, return `WorkspaceConfig`
- Init output writes `workspace` key instead of `umbrella` key to config.json
- No more `umbrella.enabled` flag — presence of `workspace.repos` implies enabled

---

### Component 6: Sync-Setup Wizard Rework

**Location**: `src/cli/helpers/issue-tracker/index.ts` + `sync-config-writer.ts`

- After provider credentials are validated, add step: "Map repos to external projects"
- Show list of `workspace.repos` with current sync config
- User selects repo → picks external project/board
- `writeSyncConfig()` writes to `workspace.repos[].sync` instead of propagating to `umbrella.childRepos`

---

### Component 7: Import Flow Changes

**Location**: Sync import commands (github-clone, jira-import, ado-import)

- Read workspace repos from `config.workspace.repos` instead of `config.umbrella.childRepos`
- When importing new repos, append to `workspace.repos[]`

---

### Component 8: Dashboard Workspace Page

**Location**: New `src/dashboard/client/pages/WorkspacePage.tsx` + server routes

**Server API**:
- `GET /api/workspace/repos` → list all workspace repos with sync status
- `PUT /api/workspace/repos/:id/sync` → update sync mapping for a repo
- `POST /api/workspace/repos/:id/test` → test sync connection

**Client page**:
- Table of repos: name, path, prefix, sync provider, sync status
- Click repo → edit sync mapping (provider, project, board)
- Test connection button per repo
- Follows existing dashboard patterns (React 18, Tailwind, SSE for live updates)

---

### Component 9: Template Creator Update

**Location**: `src/core/increment/template-creator.ts`

- `detectProjectFromCwd()` reads `config.workspace.repos` instead of `config.umbrella.childRepos`
- `createIncrementTemplates()` reads `config.workspace` instead of `config.umbrella`

---

### Component 10: Umbrella Detector Update

**Location**: `src/core/living-docs/umbrella-detector.ts`

- `loadFromUmbrellaConfig()` → rename to `loadFromWorkspaceConfig()`
- Read `config.workspace.repos` instead of `config.umbrella.childRepos`
- Detection strategy order: clone job config → workspace config → git directory scan

---

## Architecture Decisions

### AD-1: Unified Workspace over Dual Config (SELECTED)

**Options considered**:
1. ~~Keep both umbrella + multiProject, add adapter layer~~ — rejected: perpetuates confusion
2. **Merge into single `workspace` section** — selected: single source of truth, simpler mental model
3. ~~Remove multiProject, extend umbrella~~ — rejected: "umbrella" naming is confusing for non-umbrella repos

**Rationale**: The current system has 3 overlapping config sections (`umbrella`, `multiProject`, `projectMappings`) that often contain duplicate data. A single `workspace` section eliminates ambiguity about which section is authoritative.

### AD-2: Transparent Migration on Load

**Options considered**:
1. **Migrate on `ConfigManager.read()`** — selected: zero user action required
2. ~~CLI migration command~~ — rejected: users forget to run it
3. ~~Dual-read with preference~~ — rejected: maintains complexity

**Rationale**: Following existing precedent in ConfigManager (syncStrategy removal at lines 73-78). Users get migrated automatically; old config works until next write persists the new format.

### AD-3: Per-Repo Sync Config (Inline)

**Options considered**:
1. **Sync config inline on WorkspaceRepo** — selected: co-located, easy to reason about
2. ~~Separate sync profiles referencing repos by ID~~ — rejected: indirection adds complexity
3. ~~Keep current projectMappings alongside workspace~~ — rejected: defeats unification purpose

**Rationale**: ADR-0016 defines 3-layer sync architecture (credentials → profiles → per-increment). This change moves Layer 2 from separate `projectMappings` into `workspace.repos[].sync`, keeping the 3-layer model but eliminating the separate mapping lookup.

## Implementation Phases

### Phase 1: Foundation (Types + Migration)
- Define `WorkspaceConfig`, `WorkspaceRepo`, `WorkspaceRepoSync` types
- Implement `workspace-migrator.ts` with full migration logic
- Hook migration into `ConfigManager.read()` and cleanup into `ConfigManager.write()`
- Unit tests for all migration paths (umbrella-only, multiProject-only, both, neither)

### Phase 2: Core Consumer Updates
- Multi-project detector rewrite (2 strategies)
- Sync target resolver reads from workspace
- Story router uses `WorkspaceRepo` type
- Project manager unification
- Template creator update

### Phase 3: CLI Flow Updates
- Init flow: `scanWorkspaceRepos()` + `buildWorkspaceConfig()`
- Sync-setup wizard: repo mapping step
- Import flows: read/write workspace config

### Phase 4: Dashboard
- Server API routes for workspace management
- WorkspacePage.tsx with repo table and sync mapping UI

### Phase 5: Cleanup + Living Docs
- Remove deprecated type exports (mark as `@deprecated` first, remove in next major)
- Update umbrella-detector to workspace-detector
- Update living docs references
- ADR documenting the migration

## Testing Strategy

- **Unit tests**: Migration logic (all paths), detector rewrite, resolver changes
- **Integration tests**: Full config read/write cycle with old → new format
- **E2E**: Init flow produces workspace config, sync-setup writes to workspace
- **Coverage target**: 90% (per spec)
- **TDD mode**: RED → GREEN → REFACTOR per config.json setting

### Key Test Scenarios
1. Fresh init → workspace config created (no umbrella)
2. Existing umbrella config → transparently migrated on read
3. Existing multiProject config → migrated to workspace
4. Both umbrella + multiProject → merged correctly (umbrella wins conflicts)
5. Config write after migration → old fields stripped
6. Sync-setup → writes to workspace.repos[].sync
7. Dashboard workspace API → CRUD operations work

## Technical Challenges

### Challenge 1: Backward Compatibility During Migration
**Problem**: Plugins or external tools may read config.json directly and expect `umbrella` field.
**Solution**: Migration happens on ConfigManager.read() — the JSON file retains old format until first write. After write, old fields are gone. Document breaking change in release notes.
**Risk**: Low — all internal consumers go through ConfigManager. External consumers are undocumented/unsupported.

### Challenge 2: Merge Conflicts Between umbrella and multiProject
**Problem**: Same repo may appear in both sections with different sync configs.
**Solution**: Umbrella config wins (richer data model with prefix, sync). MultiProject data used only for repos not in umbrella. Log warning when conflict detected.
**Risk**: Low — in practice, users use one or the other, not both.

### Challenge 3: Dashboard State Consistency
**Problem**: Dashboard reads config via server API. Config migration must be consistent between CLI and dashboard server.
**Solution**: Both use ConfigManager.read() which applies migration. SSE pushes config changes to dashboard client.
**Risk**: Low — single code path for config access.
