---
increment: 0560-consolidate-plugins
title: "Consolidate 8 Core Plugins into 1 Unified Plugin"
type: architecture
status: draft
created: 2026-03-17
---

# Architecture Plan: Plugin Consolidation

## 1. Overview

Merge 7 satellite plugins into the core `specweave` plugin through a phased file migration with import path fixups, marketplace simplification, lockfile migration, test updates, and documentation refresh.

**Approach**: Move-and-fixup (not rewrite). Each satellite plugin's content is relocated into the core plugin's directory tree with minimal structural changes. Import paths are mechanically updated. No behavior changes.

**Key architectural decision**: Files move into the core plugin using a domain-based subdirectory layout under `lib/integrations/` and `lib/features/`. Skills and commands stay flat (they already have unique names or get domain-prefixed).

## 2. Target Directory Structure

```
plugins/specweave/
├── .claude-plugin/
│   └── plugin.json                    # Updated: reflects 44 skills, 74 commands
├── PLUGIN.md                          # Updated: unified plugin description
├── agents/                            # Unchanged (sw-architect, sw-planner, sw-pm)
├── commands/
│   ├── [existing 29 core commands]
│   ├── github-cleanup-duplicates.md   # FROM specweave-github/commands/cleanup-duplicates.md
│   ├── github-clone.md                # FROM specweave-github/commands/clone.md
│   ├── github-close.md
│   ├── github-create.md
│   ├── github-pull.md
│   ├── github-push.md
│   ├── github-reconcile.md
│   ├── github-status.md
│   ├── github-sync.md
│   ├── github-update-user-story.md
│   ├── jira-cleanup-duplicates.md     # FROM specweave-jira/commands/
│   ├── jira-close.md
│   ├── jira-create.md
│   ├── jira-import-boards.md
│   ├── jira-import-projects.md
│   ├── jira-pull.md
│   ├── jira-push.md
│   ├── jira-reconcile.md
│   ├── jira-status.md
│   ├── jira-sync.md
│   ├── ado-cleanup-duplicates.md      # FROM specweave-ado/commands/
│   ├── ado-clone.md
│   ├── ado-close.md
│   ├── ado-create.md
│   ├── ado-import-areas.md
│   ├── ado-import-projects.md
│   ├── ado-pull.md
│   ├── ado-push.md
│   ├── ado-reconcile.md
│   ├── ado-status.md
│   ├── ado-sync.md
│   ├── release-align.md              # FROM specweave-release/commands/
│   ├── release-init.md
│   ├── release-npm.md
│   ├── release-platform.md
│   ├── release-rc.md
│   ├── docs-build.md                 # FROM specweave-docs/commands/
│   ├── docs-generate.md
│   ├── docs-health.md
│   ├── docs-init.md
│   ├── docs-organize.md
│   ├── docs-validate.md
│   ├── docs-view.md
│   └── diagrams-generate.md          # FROM specweave-diagrams/commands/
├── hooks/
│   ├── [existing core hooks]
│   └── v2/
│       └── integrations/              # Consolidated post-task-completion hooks
│           ├── github-post-task.sh
│           ├── jira-post-task.sh
│           ├── ado-post-task.sh
│           └── release-post-task.sh
├── knowledge-base/                    # Unchanged
├── lib/
│   ├── [existing core lib files]
│   ├── integrations/
│   │   ├── github/                    # FROM specweave-github/lib/ (all .ts/.js files)
│   │   │   ├── github-client.ts
│   │   │   ├── github-client-v2.ts
│   │   │   ├── github-ac-checkbox-sync.ts
│   │   │   ├── github-spec-sync.ts
│   │   │   └── ... (~40 lib files total)
│   │   ├── jira/                      # FROM specweave-jira/lib/
│   │   │   ├── jira-board-resolver.ts
│   │   │   ├── jira-spec-sync.ts
│   │   │   └── ... (~30 lib files total)
│   │   └── ado/                       # FROM specweave-ado/lib/
│   │       ├── ado-client.ts
│   │       ├── ado-client-v2.ts
│   │       └── ... (~30 lib files total)
│   └── features/
│       └── release/                   # FROM specweave-release/lib/
│           ├── dora-tracker.ts
│           └── dashboard-generator.ts
├── reference/
│   ├── [existing core reference files]
│   ├── github/                        # FROM specweave-github/reference/
│   ├── jira/                          # FROM specweave-jira/reference/
│   └── ado/                           # FROM specweave-ado/reference/
├── scripts/
│   ├── [existing core scripts]
│   ├── jira/                          # FROM specweave-jira/scripts/
│   └── ado/                           # FROM specweave-ado/scripts/
└── skills/
    ├── [existing 28 core skills]
    ├── github-sync/                   # FROM specweave-github/skills/
    ├── github-issue-standard/
    ├── github-multi-project/
    ├── pr-review/
    ├── jira-sync/                     # FROM specweave-jira/skills/
    ├── jira-mapper/
    ├── jira-resource-validator/
    ├── ado-sync/                      # FROM specweave-ado/skills/
    ├── ado-mapper/
    ├── ado-multi-project/
    ├── ado-resource-validator/
    ├── release-expert/                # FROM specweave-release/skills/
    ├── diagrams/                      # FROM specweave-diagrams/skills/
    ├── image/                         # FROM specweave-media/skills/
    ├── video/
    └── remotion/
```

## 3. Migration Phases

### Phase 1: File Migration (US-001)

**Order**: Simplest plugins first (no lib dependencies) to most complex.

**Step 1a — Leaf plugins (no lib, no inter-plugin deps)**:
1. `specweave-diagrams` — 1 skill, 1 command, no lib
2. `specweave-media` — 3 skills, 0 commands, no lib
3. `specweave-docs` — 0 skills, 7 commands, no lib

**Step 1b — Feature plugins (lib but no inter-plugin deps)**:
4. `specweave-release` — 1 skill, 5 commands, 2 lib files

**Step 1c — Integration plugins (lib with inter-plugin deps)**:
5. `specweave-github` — 4 skills, 10 commands, ~40 lib files (FIRST because jira/ado depend on it)
6. `specweave-jira` — 3 skills, 11 commands, ~30 lib files (imports github's AC checkbox sync)
7. `specweave-ado` — 4 skills, 11 commands, ~30 lib files (imports github's AC checkbox sync)

**For each plugin**:
1. Copy `skills/` contents → `plugins/specweave/skills/` (flat merge, directory names already unique)
2. Copy `commands/` contents → `plugins/specweave/commands/` with domain prefix (e.g., `sync.md` → `github-sync.md`)
3. Copy `lib/` contents → `plugins/specweave/lib/integrations/{domain}/` or `lib/features/{domain}/`
4. Copy `hooks/` scripts → `plugins/specweave/hooks/v2/integrations/`
5. Copy `reference/` → `plugins/specweave/reference/{domain}/`
6. Copy `scripts/` → `plugins/specweave/scripts/{domain}/`
7. Delete the satellite plugin directory

### Phase 2: Import Path Fixups (US-001 AC-06)

**Critical dependency**: MUST happen before tests can pass.

**Import categories and their transforms**:

| Current Import Pattern | New Import Pattern | Est. Count |
|---|---|---|
| `../../specweave/lib/vendor/utils/logger.js` | `../vendor/utils/logger.js` | ~30 |
| `../../specweave/lib/vendor/utils/feature-id-derivation.js` | `../vendor/utils/feature-id-derivation.js` | ~15 |
| `../../specweave/lib/vendor/sync/provider-router.js` | `../vendor/sync/provider-router.js` | ~10 |
| `../../specweave/lib/vendor/sync/status-mapper.js` | `../vendor/sync/status-mapper.js` | ~10 |
| `../../specweave/lib/vendor/sync/config.js` | `../vendor/sync/config.js` | ~10 |
| `../../specweave-github/lib/github-ac-checkbox-sync.js` (from jira/ado) | `../github/github-ac-checkbox-sync.js` | ~2 |
| `../../specweave-github/lib/github-client-v2.js` (from jira/ado) | `../github/github-client-v2.js` | ~4 |
| `../../../src/core/config/types.js` (from plugin lib) | `../../../../src/core/config/types.js` | ~20 |
| `../../../src/types/living-docs-us-file.js` | `../../../../src/types/living-docs-us-file.js` | ~10 |

**src/ imports referencing satellite plugins**:

| Current Import Pattern | New Import Pattern | Files |
|---|---|---|
| `../../plugins/specweave-github/lib/github-client-v2.js` | `../../plugins/specweave/lib/integrations/github/github-client-v2.js` | `src/sync/sync-coordinator.ts` |
| `../../plugins/specweave-ado/lib/*` | `../../plugins/specweave/lib/integrations/ado/*` | ~5 files in `src/integrations/ado/` |
| `../../plugins/specweave-jira/lib/*` | `../../plugins/specweave/lib/integrations/jira/*` | ~3 files |

**Strategy**: Use `grep -r` to find all import statements referencing satellite plugin names, then apply mechanical substitutions. Verify with `npx tsc --noEmit`.

### Phase 3: Skill Name Preservation (US-002)

**How skill resolution works**: The `PluginLoader` discovers skills by scanning `skills/` directories. Each skill's directory name becomes its skill ID. The SKILL.md frontmatter contains `description`, `argument-hint`, and trigger keywords. Claude Code matches user intent to skills via these trigger keywords.

**Why this works with no code changes**: Moving SKILL.md files with their directory names intact preserves:
- Skill directory name (used as skill ID)
- SKILL.md content (triggers, description, hooks)
- Auto-detection keywords

The user-facing prefix (e.g., `sw-github:push`) is a convention based on `{marketplace-plugin-name}:{skill-dir-name}`. After consolidation, all skills are under `sw`, so the prefix becomes `sw:{skill-dir-name}`. Since skills like `github-sync`, `jira-mapper` already have unique directory names, they're invoked as `sw:github-sync`, `sw:jira-mapper`.

**PLUGINS-INDEX.md update**: The trigger-to-plugin lookup table points all triggers to the unified `specweave` plugin. Same triggers, single target.

### Phase 4: Hook Consolidation (US-003)

**Current state**: Each integration plugin has shell scripts for post-task-completion hooks:
- `specweave-github/hooks/` — github auto-create handler, post-task-completion
- `specweave-jira/hooks/` — post-task-completion
- `specweave-ado/hooks/` — post-task-completion, post-living-docs-update
- `specweave-release/hooks/` — post-task-completion

**Target**: Consolidate into `plugins/specweave/hooks/v2/integrations/`:
- Each integration's hook script preserved with domain prefix
- Core hook runner (`run-hook.sh`) already supports routing to specific scripts
- SKILL.md frontmatter `hooks:` blocks reference `${CLAUDE_PLUGIN_ROOT}/hooks/...` — paths need updating in migrated SKILL.md files

**Command collision resolution** (AC-US3-01): Already handled by domain-prefixing in Phase 1 (e.g., `sync.md` → `github-sync.md`).

### Phase 5: Marketplace & Installer (US-004)

**marketplace.json**: Replace 8 entries with 1:
```json
{
  "name": "specweave",
  "version": "1.0.323",
  "plugins": [
    {
      "name": "sw",
      "description": "SpecWeave framework - planning, sync, diagrams, media, docs, release",
      "source": "./plugins/specweave",
      "category": "development",
      "version": "1.0.323"
    }
  ]
}
```

**plugin-installer.ts**: `installAllPlugins()` already iterates `marketplace.plugins` — with 1 entry, it automatically installs once. Update console output messages.

**refresh-plugins.ts**: `CORE_PLUGIN = 'sw'` is already the default. Minor: update messages referencing multi-plugin counts.

**cleanup-stale-plugins.ts**: Add satellite names to `REMOVED_PLUGINS`:
```typescript
const REMOVED_PLUGINS = new Set([
  'sw-tooling',      // Removed 2025-12-11
  'sw-plugin-dev',   // Removed 2026-02-02
  'sw-github',       // Consolidated into sw (0560)
  'sw-jira',         // Consolidated into sw (0560)
  'sw-ado',          // Consolidated into sw (0560)
  'sw-release',      // Consolidated into sw (0560)
  'sw-diagrams',     // Consolidated into sw (0560)
  'docs',            // Consolidated into sw (0560)
  'sw-media',        // Consolidated into sw (0560)
]);
```

**plugin-scope.ts**: Remove per-satellite scope config entries.

### Phase 6: Test Migration (US-005)

**Test files to update**:

| Test Category | Path Pattern | Est. Files | Change |
|---|---|---|---|
| GitHub integration | `tests/integration/external-tools/github/` | ~15 | Import paths |
| GitHub unit | `tests/unit/plugins/github/` | ~20 | Import paths |
| JIRA integration/unit | `tests/*/jira/` | ~15 | Import paths |
| ADO integration/unit | `tests/*/ado/` | ~18 | Import paths |
| Plugin system | `tests/unit/plugins/plugin-*.test.ts` | ~10 | Expectations |
| Plugin validation | `tests/plugin-validation/` | ~5 | Path assertions |
| Docs sync | `tests/integration/living-docs/` | ~5 | Import paths |
| E2E sync | `tests/e2e/sync/` | ~4 | Import paths |

**Strategy**: Mechanical import path substitution matching Phase 2. Verify with `npx vitest run`.

### Phase 7: Lockfile Migration (US-007)

**New function** in `plugin-copier.ts`:
```typescript
export function migrateSatelliteToUnifiedLock(homeOverride?: string): {
  migratedCount: number;
  removedEntries: string[];
} {
  const SATELLITE_NAMES = [
    'sw-github', 'sw-jira', 'sw-ado', 'sw-release',
    'sw-diagrams', 'docs', 'sw-media'
  ];
  const lock = readGlobalLockfile(homeOverride);
  if (!lock) return { migratedCount: 0, removedEntries: [] };

  const removed: string[] = [];
  for (const name of SATELLITE_NAMES) {
    if (lock.skills[name]) {
      delete lock.skills[name];
      removed.push(name);
    }
  }
  if (removed.length > 0) writeGlobalLockfile(lock, homeOverride);
  return { migratedCount: removed.length, removedEntries: removed };
}
```

**Integration points**:
- Call from `refreshPluginsCommand()` Step 0.6
- Call from `installAllPlugins()` during init
- Also clean satellite entries from project `vskill.lock` files

**Cache cleanup**: Existing `cleanupStalePlugins()` already removes cache dirs for plugins not in marketplace.json — works automatically once satellite names are removed.

### Phase 8: Documentation (US-006)

**Files to update**:
1. `plugins/PLUGINS-INDEX.md` — rewrite to single-plugin format
2. `docs-site/docs/overview/plugins-ecosystem.md` — unified architecture
3. `docs-site/docs/guides/lazy-plugin-loading.md` — updated loading explanation
4. `docs-site/docs/guides/github-integration.md` — unified plugin refs
5. `docs-site/docs/enterprise/azure-devops-migration.md` — unified plugin refs
6. `CLAUDE.md` (specweave repo) — update plugin references
7. `AGENTS.md` — update plugin references
8. Features page — 100K+ verified skills stat update

**Files to delete**: Satellite `PLUGIN.md` files and standalone docs (moved content already captured in migration).

### Phase 9: Build Scripts (US-008)

**`scripts/build/copy-plugin-js.js`**: Update to copy only `plugins/specweave/` instead of 8 dirs.
**Verification**: `npm run build` success + `dist/plugins/specweave/` contains all artifacts.

## 4. Technical Challenges and Mitigations

### Challenge 1: Inter-Plugin Import Paths (HIGH)
**Risk**: Broken imports crash at runtime.
**Mitigation**: Categorize all import patterns before migration. Use search-and-replace with verification (`grep -r`). Run `npx tsc --noEmit` after each phase. Run `npx vitest run` as final gate.

### Challenge 2: Skill Name Resolution (MEDIUM)
**Risk**: Old skill invocation names stop working after consolidation.
**Mitigation**: Verify Claude Code's skill resolution mechanism. Keep skill directory names identical. Test each skill invocation after migration.

### Challenge 3: Hook Path References in SKILL.md (MEDIUM)
**Risk**: SKILL.md `${CLAUDE_PLUGIN_ROOT}/hooks/...` references break silently.
**Mitigation**: Audit all SKILL.md hook references. Create matching path structure. Test hook execution.

### Challenge 4: Lockfile Migration on User Machines (LOW)
**Risk**: Stale lockfile entries cause duplicate installs or skip checks.
**Mitigation**: Auto-migration on init/refresh. Idempotent. Failure falls through to fresh install.

### Challenge 5: Build Artifact Size (LOW)
**Risk**: Published package size increases.
**Mitigation**: Should be neutral or slightly smaller (fewer duplicate manifests). Verify with `npm pack --dry-run`.

## 5. Testing Strategy

- **Unit**: Import resolution, lockfile migration idempotency, single-entry marketplace parsing
- **Integration**: Plugin loader discovers all 44 skills, skill resolution by name, hook dispatch routing
- **E2E**: `specweave init` installs 1 plugin, `refresh-plugins` produces clean state
- **Regression gate**: `npx vitest run` passes with 0 failures

## 6. Rollback Plan

**Pre-migration**: Git tag `pre-consolidation-0560` before starting.
**Phase-level**: Each phase is a separate commit — `git revert` individual phases.
**Full rollback**: `git reset --hard pre-consolidation-0560`.
**User-side**: `specweave refresh-plugins --force` forces clean reinstall.

## 7. Implementation Order

| Phase | US | Priority | Dependencies | Est. Files |
|-------|-----|----------|-------------|-----------|
| 1a: Move leaf plugins | US-001 | P1 | None | ~15 |
| 1b: Move feature plugins | US-001 | P1 | 1a | ~10 |
| 1c: Move integration plugins | US-001 | P1 | 1b | ~120 |
| 2: Import path fixups | US-001 | P1 | 1 | ~80 |
| 3: Skill name verification | US-002 | P1 | 2 | ~5 |
| 4: Hook consolidation | US-003 | P1 | 2 | ~15 |
| 5: Marketplace & installer | US-004 | P1 | 2 | ~10 |
| 6: Test migration | US-005 | P2 | 2 | ~80 |
| 7: Documentation | US-006 | P2 | 5 | ~15 |
| 8: Lockfile migration | US-007 | P2 | 5 | ~5 |
| 9: Build scripts | US-008 | P2 | 1 | ~3 |
| 10: Final verification | All | P1 | All | 0 |

## 8. Key Files to Modify

### Core Infrastructure
- `plugins/specweave/.claude-plugin/plugin.json` — expanded metadata
- `.claude-plugin/marketplace.json` — single plugin entry
- `src/utils/plugin-copier.ts` — lockfile migration function
- `src/utils/cleanup-stale-plugins.ts` — add satellite names to REMOVED_PLUGINS
- `src/core/types/plugin-scope.ts` — remove satellite scope entries
- `src/cli/helpers/init/plugin-installer.ts` — update console messages
- `src/cli/commands/refresh-plugins.ts` — update console messages
- `plugins/PLUGINS-INDEX.md` — single-plugin index

### Moved Files (new locations)
- `plugins/specweave/skills/` — 16 new skill directories
- `plugins/specweave/commands/` — 45 new command files
- `plugins/specweave/lib/integrations/` — ~100 lib files
- `plugins/specweave/lib/features/release/` — 2 lib files
- `plugins/specweave/hooks/v2/integrations/` — ~8 hook scripts
- `plugins/specweave/reference/{github,jira,ado}/` — reference docs
- `plugins/specweave/scripts/{jira,ado}/` — scripts

### Source Files with Import Updates
- `src/sync/sync-coordinator.ts` — github-client-v2 import
- `src/integrations/ado/*` — ado lib imports
- ~80 lib files in moved directories — relative import updates

### Deleted Directories
- `plugins/specweave-github/`
- `plugins/specweave-jira/`
- `plugins/specweave-ado/`
- `plugins/specweave-release/`
- `plugins/specweave-diagrams/`
- `plugins/specweave-media/`
- `plugins/specweave-docs/`
