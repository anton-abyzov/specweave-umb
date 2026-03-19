---
increment: 0582-fix-duplicate-increment-creation
type: architecture
status: draft
---

# Architecture Plan: Fix Duplicate Increment Creation Bugs

## Overview

Six targeted fixes to the increment ID generation system. All changes are in `repositories/anton-abyzov/specweave/`. No new dependencies, no new modules — surgical edits to existing files.

## Architecture Decisions

### AD-1: Extract `getDirsToScan()` from `RECOGNIZED_LIFECYCLE_FOLDERS` (Bug 3)

**Problem**: 4 methods in `increment-utils.ts` hardcode `[_archive, _abandoned, _paused]`, ignoring `_backlog` which is in `RECOGNIZED_LIFECYCLE_FOLDERS`.

**Decision**: Extract a private static helper that derives scan targets from the constant.

```
RECOGNIZED_LIFECYCLE_FOLDERS = ['_archive', '_abandoned', '_paused', '_backlog']
                                          |
getDirsToScan(incrementsDir) -> [
  { path: incrementsDir, label: 'active' },
  { path: incrementsDir/_archive, label: '_archive' },
  { path: incrementsDir/_abandoned, label: '_abandoned' },
  { path: incrementsDir/_paused, label: '_paused' },
  { path: incrementsDir/_backlog, label: '_backlog' },   <-- was missing
]
```

**Callers to update** (4 methods):
1. `incrementNumberExists()` (line 174) — uses `string[]`, will use `.path`
2. `getAllIncrementNumbers()` (line 267) — uses `string[]`, will use `.path`
3. `scanAllIncrementDirectories()` (line 353) — uses `{path, label}`, direct fit
4. `findDuplicates()` (line 713) — uses `{path, label}`, direct fit

**Trade-off**: Slightly more abstraction vs DRY + guaranteed consistency. Single source of truth wins.

### AD-2: `--project-root` Option for `next-id` CLI (Bug 1)

**Problem**: `next-id` at `bin/specweave.js:376` always uses `resolveEffectiveRoot(process.cwd())`. No override available.

**Decision**: Add `--project-root <path>` option. When provided, use it directly (after validating `.specweave/config.json` exists). When absent, existing behavior is unchanged.

```
specweave next-id                              -> resolveEffectiveRoot(cwd)
specweave next-id --project-root /tmp/proj-a   -> /tmp/proj-a (validated)
```

**Validation**: If `--project-root` is provided but `<path>/.specweave/config.json` doesn't exist, exit with code 1 and error message. This prevents silent misuse.

### AD-3: Minimal config.json Before Directory Structure (Bug 2)

**Problem**: `init.ts` creates `increments/` (line 321) before `config.json` (line 402). Any code during that gap that calls `findProjectRoot()` may resolve to a sibling project.

**Decision**: Write a minimal `config.json` stub immediately after creating `.specweave/` but before `createDirectoryStructure()`. The full `createConfigFile()` at line 402 overwrites it.

```
Current init flow:
  createDirectoryStructure()  <-- creates .specweave/increments/
  ... 80 lines of setup ...
  createConfigFile()          <-- finally writes config.json

Fixed init flow:
  mkdir .specweave/
  write minimal config.json   <-- { "version": "2.0", "project": { "name": "..." } }
  createDirectoryStructure()  <-- now findProjectRoot() works during this step
  ... 80 lines of setup ...
  createConfigFile()          <-- overwrites with full config (idempotent)
```

**Why minimal, not full?** At this point we don't yet have adapter detection, provider info, or smart defaults. A minimal stub is enough for `findProjectRoot()` to anchor correctly.

**Reinit safety**: `createDirectoryStructure()` already handles existing directories (mkdirSync recursive). The stub write is also idempotent — `createConfigFile()` unconditionally overwrites.

### AD-4: Atomic ID Reservation via `--auto-id` (Bug 4)

**Problem**: TOCTOU race between `next-id` (step 1) and `create-increment --id X` (step 2). Parallel agents can claim the same ID.

**Decision**: Add `--auto-id` flag to `create-increment`. When set, the command generates + reserves the ID atomically using `mkdirSync({ recursive: false })` as a POSIX-atomic lock.

```
Two-step (existing, still supported):
  specweave next-id -> 0042
  specweave create-increment --id 0042-feature   <-- race window

Atomic (new):
  specweave create-increment --auto-id --name feature --title "Feature" ...
  -> internally: getNextIncrementNumber() -> mkdirSync(0042-feature) -> if EEXIST, retry
```

**Retry logic**: Max 10 attempts. On `EEXIST`, re-scan and try next number. Extremely unlikely to exhaust retries (would require 10 concurrent collisions).

**Changes required**:
1. `bin/specweave.js`: Add `--auto-id` and `--name` options to `create-increment`
2. `create-increment.ts`: When `autoId` is set, generate ID internally instead of requiring `--id`
3. `template-creator.ts`: Add atomic creation path in `createIncrementTemplates()`

**Backward compatibility**: `--id` still works. `--auto-id` is additive. SKILL.md updated to prefer `--auto-id`.

### AD-5: SKILL.md Adapter Portability (Bug 5)

**Problem**: SKILL.md Step 4 hardcodes Claude Code-specific tools (`TeamCreate`, `Agent()`, `SendMessage`, `EnterPlanMode`). Non-Claude adapters hallucinate these.

**Decision**: Split SKILL.md delegation into two tiers:

```
Step 4: Create Increment
+-- Default path (all adapters):
|   +-- specweave create-increment --auto-id --name "..." --title "..." --project "..."
|
+-- Enhanced path (Claude Code only -- detected by adapter):
    +-- TeamCreate + Agent() delegation for parallel PM/Architect
```

**Implementation**: Structure SKILL.md so the default path uses only CLI commands. Claude-specific features are in a clearly demarcated optional section that non-Claude adapters' `compilePlugin()` / `sanitizeFrontmatter()` will strip or ignore.

### AD-6: Name-Duplicate Warning in IncrementNumberManager (Bug 6)

**Problem**: No detection for same-name increments (different numbers, same slug). The guard hook at `increment-duplicate-guard.sh` is a no-op.

**Decision**: Add `findNameDuplicates()` to `IncrementNumberManager`. Call from `createIncrementTemplates()` before directory creation. Warning only (not blocking).

```typescript
static findNameDuplicates(
  name: string,
  projectRoot: string,
  options?: { includeArchived?: boolean }
): string[]
```

**Scope**: Per AC-US6-03, only check active + `_backlog` directories by default. Archived/abandoned names can be reused.

**Integration point**: `template-creator.ts:createIncrementTemplates()` — after `validateExplicitId()`, before `mkdirSync`. Emits `console.warn()` with the duplicate list.

## Component Diagram

```
bin/specweave.js (CLI entry)
  |-- next-id command
  |   +-- NEW: --project-root option  (AD-2)
  |
  +-- create-increment command
      +-- NEW: --auto-id, --name options  (AD-4)

src/cli/commands/
  |-- create-increment.ts
  |   +-- NEW: auto-id logic, name-duplicate warning call  (AD-4, AD-6)
  |
  +-- init.ts
      +-- FIX: write minimal config.json before createDirectoryStructure()  (AD-3)

src/core/increment/
  |-- increment-utils.ts
  |   |-- NEW: getDirsToScan() private static  (AD-1)
  |   |-- FIX: 4 methods use getDirsToScan()  (AD-1)
  |   +-- NEW: findNameDuplicates() static  (AD-6)
  |
  +-- template-creator.ts
      +-- FIX: atomic creation path + name-duplicate warning  (AD-4, AD-6)

plugins/specweave/skills/increment/SKILL.md
  +-- FIX: adapter-portable delegation  (AD-5)
```

## Implementation Order

Dependencies flow downward — each step builds on the previous:

1. **AD-1** (`getDirsToScan`) — foundational DRY fix, enables AD-6 scan scope
2. **AD-6** (`findNameDuplicates`) — depends on AD-1 for correct scan scope
3. **AD-2** (`--project-root`) — independent, simple CLI addition
4. **AD-3** (init order) — independent, surgical init.ts edit
5. **AD-4** (`--auto-id`) — depends on AD-1 being correct (uses `getNextIncrementNumber`)
6. **AD-5** (SKILL.md) — depends on AD-4 (references `--auto-id` in CLI fallback)

## Testing Strategy

| AD | Test Type | Key Scenario |
|----|-----------|--------------|
| AD-1 | Unit | `_backlog/` increment is included in scan; `getDirsToScan()` includes all RECOGNIZED_LIFECYCLE_FOLDERS |
| AD-2 | Unit + Integration | `--project-root` overrides cwd; missing config.json returns error |
| AD-3 | Integration | `init --quick` in dir with sibling project; `next-id` returns `0001` |
| AD-4 | Unit + Concurrency | Atomic retry on EEXIST; 3 parallel creates get unique IDs |
| AD-5 | Manual | Load SKILL.md in non-Claude tool; verify no Claude-specific tool refs in default path |
| AD-6 | Unit | Same-slug warning emitted; archived names not flagged; active duplicates flagged |

## Risk Mitigations

- **Init reorder** (AD-3): The minimal config.json is overwritten by `createConfigFile()` — no orphaned stubs. Reinit path tested explicitly.
- **Atomic retry exhaustion** (AD-4): 10 retries handles up to 10 concurrent agents. In practice, parallel agent count is 3-5. If exhausted, throw clear error.
- **SKILL.md regression** (AD-5): Claude Code path is preserved in conditional block. Existing Claude Code behavior unchanged.

## Files Modified

| File | Changes |
|------|---------|
| `src/core/increment/increment-utils.ts` | +`getDirsToScan()`, +`findNameDuplicates()`, refactor 4 methods |
| `bin/specweave.js` | `next-id`: +`--project-root`; `create-increment`: +`--auto-id`, +`--name` |
| `src/cli/commands/create-increment.ts` | auto-id logic, name-duplicate warning |
| `src/core/increment/template-creator.ts` | atomic creation path |
| `src/cli/commands/init.ts` | minimal config.json write before `createDirectoryStructure()` |
| `plugins/specweave/skills/increment/SKILL.md` | adapter-portable delegation |
| `tests/unit/increment-utils.test.ts` | +`_backlog` tests, +`getDirsToScan` tests, +`findNameDuplicates` tests |
