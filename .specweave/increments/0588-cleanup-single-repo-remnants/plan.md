# Implementation Plan: Stage 2 -- Deep Cleanup of Single-Repo Remnants

## Overview

Pure refactor removing 12 specific single-repo remnants found by a 4-agent code review after Stage 1 (increment 0581). No new architecture decisions -- ADR-0244 (Always-Multi Repository Architecture) governs this work. All changes are independent and parallelizable.

**Target project**: `repositories/anton-abyzov/specweave`

## Architecture Decision

No new ADR needed. ADR-0244 Section "Stage 2" explicitly calls out this cleanup:

> Stage 2 (Future Increment): Replace all 38 `umbrella.enabled` check sites, rename `umbrella` to `workspace`, build migration utility.

This increment addresses the pre-Stage-2 cleanup (dead code, stale mocks, doc drift) rather than the umbrella rename itself.

## Change Inventory

All paths below are relative to `repositories/anton-abyzov/specweave/`.

### Group A: GitHubSetupType and issue-tracker flows (US-001)

#### A1: Remove `'single'` from `GitHubSetupType` union

**File**: `src/cli/helpers/issue-tracker/github-multi-repo.ts` (line 36)

```typescript
// BEFORE
export type GitHubSetupType = 'none' | 'single' | 'multiple' | 'monorepo' | 'auto-detect';

// AFTER
export type GitHubSetupType = 'none' | 'multiple' | 'monorepo' | 'auto-detect';
```

#### A2: Remove `configureSingleRepository()` function

**File**: `src/cli/helpers/issue-tracker/github-multi-repo.ts` (lines 282-356)

Delete the entire `configureSingleRepository()` function. It is called from:
- `configureMonorepo()` (line 508) -- replace with inline single-profile collection via `configureMultipleRepositories()` with count=1, or inline the minimal logic
- `autoDetectRepositories()` fallbacks (lines 546, 559) -- replace with `configureMultipleRepositories()`
- `autoDetectRepositories()` switch-case (line 583) -- remove the `case 'single'` branch

#### A3: Remove `'single'` from legacy prompt choices

**File**: `src/cli/helpers/issue-tracker/github-multi-repo.ts` (lines 232-261)

Remove the `'single'` option from the `select()` choices array at line 240:
```typescript
// REMOVE this choice:
{
  name: '📦 Single repository',
  value: 'single' as const
},
```

#### A4: Change fallback from `'single'` to `'multiple'`

**File**: `src/cli/helpers/issue-tracker/github-multi-repo.ts` (line 87)

```typescript
// BEFORE
return { setupType: 'single' };

// AFTER
return { setupType: 'multiple' };
```

#### A5: Remove `case 'single'` from `configureGitHubRepositories`

**File**: `src/cli/helpers/issue-tracker/github.ts` (lines 498-503)

Remove the `case 'single':` branch from the switch statement. Also remove `configureSingleRepository` from the import at line 478.

#### A6: Remove `configureSingleRepository` from import in `github.ts`

**File**: `src/cli/helpers/issue-tracker/github.ts` (line 478)

Remove `configureSingleRepository` from the destructured import.

### Group B: Save command output (US-002)

#### B1: Update mode label in save command

**File**: `src/cli/commands/save.ts` (line 125)

```typescript
// BEFORE
logger.log(`Mode: ${repos.length === 1 ? 'Single repository' : `Umbrella (${repos.length} child repos)`}\n`);

// AFTER
logger.log(`Mode: Workspace (${repos.length} ${repos.length === 1 ? 'repository' : 'repositories'})\n`);
```

### Group C: Skill and doc files (US-003)

#### C1: Remove resolve-structure block from SKILL.md

**File**: `plugins/specweave/skills/increment/SKILL.md` (approximately lines 121-143)

Delete the entire "Step 0D: Deferred Structure Resolution" block that contains:
- The `DEFERRED=$(jq ...)` check
- The "Single repo" vs "Multiple repos" question
- The `specweave resolve-structure --type single` / `--type multiple` commands

This block references a removed command and dead init options.

#### C2: Update Phase 6 in strategic-init.md

**File**: `docs-site/docs/guides/strategic-init.md` (lines 168-206)

Update Phase 6 to reflect the current 2-choice model:
- Remove `Single repository (monorepo)` as a choice
- Replace with current prompt: "Which repositories to connect?" / "Add later"
- The pattern-based selection content can remain as it is still valid for the multi-repo flow

#### C3: Update save.md docs

**File**: `docs-site/docs/commands/save.md` (around line 84-92)

Replace "Single Repo Mode" heading and `Mode: Single repository` output with "Workspace Mode" and `Mode: Workspace (1 repository)`.

### Group D: Dead code removal (US-004)

#### D1: Delete deprecated functions from prompt-consolidator.ts

**File**: `src/core/repo-structure/prompt-consolidator.ts`

Delete these functions (only tested, never imported by production code):
- `getParentRepoBenefits()` (lines 61-72) -- deprecated since v1.0.13
- `getRepoCountClarification()` (lines 81-93) -- uses parent/impl terminology that no longer applies
- `formatArchitectureChoice()` (lines 220-222) and its backing `ARCHITECTURE_LABELS` constant (lines 216-218) -- only one value remains, making it trivial

#### D2: Delete `src/core/migration/` directory

**Directory**: `src/core/migration/` (4 files, ~47KB total)

Files to delete:
- `types.ts` -- MigrationCandidate, MigrationPlan, etc.
- `umbrella-migrator.ts` -- full migration logic
- `consolidation-engine.ts` -- orphan consolidation
- `spec-project-mapper.ts` -- spec reorganization

**Verification performed**: Zero production importers outside the directory itself. Only referenced by:
- Self-referencing imports within the 4 files
- Test files under `tests/unit/core/migration/` and `tests/integration/migration/`

Note: ADR-0244 Section "Neutral" says "consolidation-engine.ts and spec-project-mapper.ts preserved (umbrella consolidation/reorganize sub-commands remain useful)". However, the `bin/specweave.js` CLI no longer registers any commands that use these modules (grep confirms zero hits for `consolidat` or `reorganize` in the CLI). The ADR statement reflects an earlier understanding; the modules are dead.

#### D3: Delete migration test files

Delete corresponding test files:
- `tests/unit/core/migration/consolidation-engine.test.ts`
- `tests/unit/core/migration/reorganize-specs.test.ts`
- `tests/unit/core/migration/spec-project-mapper.test.ts`
- `tests/unit/core/migration/umbrella-migrator.test.ts`
- `tests/unit/core/migration/umbrella-migrator-collision.test.ts`
- `tests/integration/migration/consolidation-integration.test.ts`
- `tests/integration/migration/legacy-id-preservation.test.ts`

#### D4: Update Zod schema to remove `'single'`

**File**: `src/init/research/src/config/types.ts` (line 19)

```typescript
// BEFORE
type: z.enum(['single', 'multi'])

// AFTER
type: z.enum(['multi'])
```

#### D5: Update ConfigManager default to `'multi'`

**File**: `src/init/research/src/config/ConfigManager.ts` (line 24)

```typescript
// BEFORE
project: { name: 'specweave-project', type: 'single' },

// AFTER
project: { name: 'specweave-project', type: 'multi' },
```

#### D6: Delete dead function tests from prompt-consolidator.test.ts

**File**: `tests/unit/repo-structure/prompt-consolidator.test.ts`

Remove test blocks for `getParentRepoBenefits` and `getRepoCountClarification`. Remove their imports.

### Group E: Fix stale test mocks (US-005)

#### E1: Fix init-config-validation.test.ts mocks

**File**: `tests/unit/cli/commands/init-config-validation.test.ts`

- Line 124: Change `'existing'` to `'add-later'`
- Line 334: Change `'scratch'` to `'clone-repos'`
- Line 382: Change `'multi-repo-deferred'` to `'add-later'`

Current `promptProjectSetup` returns `'clone-repos' | 'add-later'` (confirmed in `repo-connect.ts`).

#### E2: Fix init.test.ts mocks

**File**: `tests/unit/cli/commands/init.test.ts`

- Line 171: Change `'existing'` to `'add-later'`
- Line 228: Change `'existing'` to `'add-later'`

#### E3: Fix init-path-resolution.test.ts mocks

**File**: `tests/unit/cli/commands/init-path-resolution.test.ts`

- Line 188: Change `'existing'` to `'add-later'`
- Line 257: Change `'existing'` to `'add-later'`

#### E4: Fix github-multi-repo.test.ts mocks

**File**: `tests/unit/cli/helpers/issue-tracker/github-multi-repo.test.ts`

Update all `setupType: 'single'` references to `setupType: 'multiple'`:
- Lines 170, 175, 234, 948

Remove tests that specifically validate the `'single'` code path (these test deleted code).

#### E5: Fix github.test.ts mocks

**File**: `tests/unit/cli/helpers/issue-tracker/github.test.ts`

- Line 1130: Change `setupType: 'single'` to `setupType: 'multiple'`
- Line 1177: Change `{ setupType: 'single' }` to `{ setupType: 'multiple' }`

#### E6: Fix github-repo-reuse.test.ts mocks

**File**: `tests/unit/issue-tracker/github-repo-reuse.test.ts`

Update all `setupType: 'single'` occurrences (lines 156, 187, 258, 314, 380, 435, 467) to `setupType: 'multiple'`.

## Execution Order

All groups (A through E) are independent and can execute in parallel. Within each group, changes are also independent except:

- A2 depends on A1 (type must be narrowed before function deletion)
- D3 depends on D2 (delete tests after deleting source)
- D6 depends on D1 (delete tests after deleting functions)

## Testing Strategy

- **Unit tests**: Run `npx vitest run` after all changes. All existing tests must pass.
- **Type checking**: Run `npx tsc --noEmit` to verify no broken imports after deletions.
- **Grep verification**: Post-change grep to confirm zero hits for:
  - `configureSingleRepository` in `src/`
  - `getParentRepoBenefits` in `src/`
  - `getRepoCountClarification` in `src/`
  - `formatArchitectureChoice` in `src/`
  - `setupType.*'single'` in `src/`
  - `core/migration` in `src/` (excluding `sync/migration.ts` which is unrelated)

## Risk Mitigations

| Risk | Mitigation |
|------|------------|
| Migration directory has hidden runtime importer | Verified via grep: zero imports from `src/cli/` or anywhere in `src/` outside the directory itself |
| Zod narrowing breaks existing configs | Stage 1 already stopped writing `'single'`; the research config is internal and not persisted by end users |
| SKILL.md line numbers shifted | Use content matching (search for `resolve-structure` and `DEFERRED`) not line numbers |
| `configureSingleRepository` used transitively | Verified all 6 call sites are in `github-multi-repo.ts` and `github.ts` only |
| `consolidation-engine` still needed per ADR-0244 | Verified: no CLI command registers it; ADR statement was aspirational. Safe to delete. |

## Estimated Impact

- **Lines deleted**: ~1,200 (migration module ~700, functions ~100, test files ~300, prompt choices ~50)
- **Lines modified**: ~50 (test mock values, save.ts label, Zod enum, SKILL.md, docs)
- **Files deleted**: 11 source + 7 test = 18 files total
- **Files modified**: ~15 files
