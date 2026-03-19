# Architecture Plan: Fix vskill Non-Claude Tool Skill Installation

## Problem Summary

Five interconnected bugs in the non-Claude skill installation pipeline:

1. **Stale flat files** -- older vskill versions left `{skill-name}.md` instead of `{skill-name}/SKILL.md`
2. **Core SW skills as flat files** -- prior sync logic wrote `sw/ado-mapper.md` instead of `sw/ado-mapper/SKILL.md`
3. **Missing frontmatter** -- non-Claude installations may lack `name:` / `description:` YAML frontmatter
4. **specweave init ignores non-Claude agents** -- only writes to `.claude/skills/`, never calls `vskill init`
5. **Stale vskill binary** -- cached npx version may use outdated logic

## Architecture Decisions

### AD-1: Migration function lives in a new `installer/migrate.ts` module

**Decision**: Create `repositories/anton-abyzov/vskill/src/installer/migrate.ts` containing `migrateStaleSkillFiles()`.

**Why not in canonical.ts**: canonical.ts handles the forward path (write new files correctly). Migration is a one-time cleanup of legacy state -- different responsibility. Keeping it separate makes it testable in isolation and easy to deprecate later.

**Why not in sync.ts**: sync.ts orchestrates core skill distribution. Migration applies to ALL installed skills (core and third-party), not just core skills.

**Interface**:

```typescript
export interface MigrationResult {
  migratedCount: number;
  removedCount: number;
  errors: string[];
}

/**
 * Scan a skill directory for stale flat .md files and restructure them.
 *
 * For each `{name}.md` file found at the root level of skillsDir:
 *   1. If `{name}/SKILL.md` already exists -- delete the flat file (dedup)
 *   2. If `{name}/SKILL.md` does NOT exist -- create the subdirectory,
 *      move the content to `{name}/SKILL.md`, run ensureFrontmatter(), delete the flat file
 *
 * Skips: symlinks, directories, files not matching *.md, SKILL.md itself.
 */
export function migrateStaleSkillFiles(
  skillsDir: string,
  options?: { dryRun?: boolean }
): MigrationResult;
```

### AD-2: Migration runs INSIDE `vskill init`, not as a standalone command

**Decision**: Call `migrateStaleSkillFiles()` from `initCommand()` after agent detection, BEFORE `syncCoreSkills()`.

**Why**: Running migration before sync ensures the sync writes into a clean directory structure. Running it inside `init` means `specweave init` (which calls `vskill init`) gets migration for free.

**Execution order in initCommand**:
1. Detect agents
2. Create/update lockfile
3. Purge stale plugins
4. **NEW: Migrate stale flat files for each detected agent**
5. Sync core skills

### AD-3: specweave init calls `vskill init` using the same 3-tier fallback pattern as skill-creator-installer

**Decision**: Create `repositories/anton-abyzov/specweave/src/cli/helpers/init/vskill-init-invoker.ts` using the proven 3-tier pattern from `skill-creator-installer.ts`:

1. `vskill init --yes` (globally installed)
2. `npx --registry https://registry.npmjs.org --userconfig /dev/null --ignore-scripts --package vskill@^0.5.0 vskill init --yes`
3. Skip gracefully with hint message (no claude CLI fallback -- not applicable)

**Why reuse the pattern**: skill-creator-installer.ts solved the exact same problem (reliable vskill invocation from specweave). The 3-tier approach handles corporate .npmrc issues, missing global installs, and provides graceful degradation.

**Integration point**: Called from `specweave init` after plugin installation, regardless of whether `toolName === 'claude'`. Non-blocking (fire-and-forget with error catch).

```typescript
export interface VskillInitResult {
  invoked: boolean;
  skipped: boolean;
  error?: string;
}

export async function ensureVskillInit(projectRoot: string): Promise<VskillInitResult>;
```

### AD-4: Frontmatter enforcement already works -- no code changes needed

**Decision**: No changes to `frontmatter.ts` or `canonical.ts`.

**Why**: `ensureFrontmatter()` already injects `name:` and `description:` when missing. Both `installSymlink()` and `installCopy()` already call `ensureFrontmatter()` at line 113 and 164 of canonical.ts respectively. The migration function will also call `ensureFrontmatter()` when restructuring flat files.

The bug is not that frontmatter enforcement is missing -- it is that stale files from OLDER versions (written before this logic existed) were never retroactively fixed. The migration function (AD-1) handles this.

### AD-5: Migration scans agent directories, not canonical .agents/skills/

**Decision**: Migration iterates over each detected agent's `localSkillsDir` (e.g., `.cursor/skills/`, `.opencode/skills/`), NOT the canonical `.agents/skills/` directory.

**Why**: The canonical directory is written correctly by current code. The stale flat files live in agent-specific directories from prior installation runs.

**Scan logic**:
```
For each detected agent:
  skillsDir = join(projectRoot, agent.localSkillsDir)
  if not exists(skillsDir): skip
  for each *.md file in skillsDir (non-recursive top level):
    if file is not SKILL.md and not a directory:
      migrate(file)
  for each subdirectory in skillsDir:
    for each *.md file in subdirectory (e.g., sw/pm.md):
      if file is not SKILL.md:
        migrate(file)
```

### AD-6: Symlinks are preserved, not migrated

**Decision**: `migrateStaleSkillFiles()` skips symlinks (both files and directories) via `lstatSync()`.

**Why**: Symlinks point to the canonical `.agents/skills/` source-of-truth. They are correct by definition. Attempting to migrate a symlink could break the canonical chain.

## Component Diagram

```
specweave init                        vskill init
----------------------------------------------
|                                    |
+- installAllPlugins()               +- detectInstalledAgents()
|  +-- .claude/skills/ (Claude only) |
|                                    +- createLockfile()
+- ensureSkillCreator()              |
|  +-- 3-tier: vskill/npx/claude     +- purgeStalePlugins()
|                                    |
+- NEW: ensureVskillInit()  ---------+- NEW: migrateStaleSkillFiles()
|  +-- 3-tier: vskill/npx/skip      |  +-- Per agent: scan + restructure
|                                    |
+- done                              +- syncCoreSkills()
                                     |  +-- installSymlink() per skill
                                     |     +-- ensureFrontmatter()
                                     |     +-- SKILL.md in subdirs
                                     +- done
```

## File Changes

### New Files

| File | Purpose |
|------|---------|
| `vskill/src/installer/migrate.ts` | `migrateStaleSkillFiles()` function |
| `vskill/src/installer/migrate.test.ts` | Unit tests for migration |
| `specweave/src/cli/helpers/init/vskill-init-invoker.ts` | 3-tier vskill init caller |
| `specweave/src/cli/helpers/init/vskill-init-invoker.test.ts` | Unit tests for invoker |

### Modified Files

| File | Change |
|------|--------|
| `vskill/src/commands/init.ts` | Import and call `migrateStaleSkillFiles()` after lockfile setup, before core skills sync |
| `specweave/src/cli/commands/init.ts` | Import and call `ensureVskillInit()` after plugin installation |
| `specweave/src/cli/helpers/init/index.ts` | Export `ensureVskillInit` |

### Unchanged Files (confirmed correct)

| File | Why unchanged |
|------|---------------|
| `vskill/src/installer/canonical.ts` | Already writes `SKILL.md` in subdirectories; `ensureFrontmatter()` already called |
| `vskill/src/installer/frontmatter.ts` | Already handles name + description injection correctly |
| `vskill/src/core-skills/sync.ts` | Already uses `installSymlink()` which writes correct structure |
| `vskill/src/agents/agents-registry.ts` | No agent definitions need changing |

## Implementation Order

### Phase 1: vskill migration (US-VSK-001, US-VSK-002, US-VSK-004)

1. **T-001**: Create `installer/migrate.ts` with `migrateStaleSkillFiles()`
2. **T-002**: Create `installer/migrate.test.ts` with tests for all AC scenarios
3. **T-003**: Wire migration into `commands/init.ts` (call before syncCoreSkills)
4. **T-004**: Add integration test in `core-skills/sync.test.ts` verifying stale files are cleaned after sync

### Phase 2: specweave init integration (US-VSK-003)

5. **T-005**: Create `vskill-init-invoker.ts` with 3-tier fallback pattern
6. **T-006**: Create `vskill-init-invoker.test.ts` with unit tests
7. **T-007**: Wire `ensureVskillInit()` into `specweave init` -- call for ALL adapters

### Phase 3: Test coverage (US-VSK-005)

8. **T-008**: Verify frontmatter enforcement paths in existing `canonical.ts` tests
9. **T-009**: Add edge case tests (both flat + dir exist, empty files, symlinks, nested sw/ paths)

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Both `pm.md` and `pm/SKILL.md` exist | Remove `pm.md`, keep `pm/SKILL.md` unchanged |
| `pm.md` is a symlink | Skip (do not migrate symlinks) |
| `pm.md` is empty (0 bytes) | Create `pm/SKILL.md` with frontmatter-only content |
| `sw/` directory with flat files | Recurse one level: `sw/pm.md` becomes `sw/pm/SKILL.md` |
| Agent skills dir does not exist | Skip that agent entirely |
| Permission denied on file | Log error, continue with next file |
| `SKILL.md` at root level (not flat named) | Skip (not a stale file) |

## Testing Strategy

All tests use the existing vskill pattern: `mkdtempSync` for isolated filesystem, `makeAgent()` helper for mock agents, direct `existsSync`/`readFileSync` assertions.

No mocking of filesystem operations -- tests use real temp directories for high-fidelity validation.

| Test Suite | Location | Coverage Target |
|------------|----------|-----------------|
| migrate.test.ts | vskill/src/installer/ | All AC-US1-*, AC-US2-03, AC-US4-03 |
| sync.test.ts (additions) | vskill/src/core-skills/ | AC-US4-01, AC-US4-02, AC-US5-03 |
| vskill-init-invoker.test.ts | specweave/src/cli/helpers/init/ | AC-US3-01, AC-US3-02, AC-US3-03 |

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Migration accidentally deletes user content | Only renames/moves -- never deletes content. When flat file and SKILL.md coexist, flat file is removed (content is duplicate) |
| vskill version mismatch | `npx vskill@^0.5.0` pins minimum version; `--yes` skips prompts |
| specweave init becomes slower | `ensureVskillInit()` is fire-and-forget (non-blocking); migration scans only agent skill dirs (not whole project) |
| Migration runs on Claude's .claude/skills/ | Claude is in `COPY_FALLBACK_AGENTS` and gets direct copies from canonical.ts -- migration still works correctly but is effectively a no-op since canonical.ts already writes SKILL.md |
