# Implementation Plan: Fix umbrella migration collision handling

## Overview

Three focused fixes to the umbrella migration system: collision classification before execution, destination safety checks during move steps, and dynamic log root switching after `.specweave/` is relocated.

## Architecture

### Components
- **`classifyExistingUmbrella()`**: Pre-execution collision classifier in `umbrella-migrator.ts`
- **`executeStep()` move case**: Safety guard checking `fs.existsSync(destination)` before any move
- **`executeMigration()` log root**: Dynamic `logRoot` variable that switches from `projectRoot` to `umbrellaPath` after `.specweave/` move step
- **`handleCollision()` CLI**: Interactive collision resolution UI in `migrate-to-umbrella.ts`

### Key Design Decisions

1. **Classify-then-act pattern**: Collision is classified before execution starts, not during move operations. This gives users actionable choices before any files are touched.
2. **Dynamic log root**: Instead of passing log target as a parameter, `logRoot` is mutated after the `.specweave/` move step. This keeps the logging simple without refactoring the step execution loop.
3. **Fail-fast on move collision**: Move steps throw immediately if destination exists rather than attempting merge/overwrite. This is safer and simpler.

## Implementation

### 1. Collision Classification (`umbrella-migrator.ts:30-62`)
- Three-state classification: `previous-migration` | `partial-migration` | `unrelated`
- Checks for `.specweave/` in target (previous), backup manifest at project root (partial), or generic directory (unrelated)

### 2. CLI Collision Handling (`migrate-to-umbrella.ts:94-235`)
- Integrates `classifyExistingUmbrella()` before execution
- Per-type prompts: wipe/rename/abort for previous, rollback/abort for partial, rename/abort for unrelated
- `--yes` mode: auto-wipe previous, abort on unrelated

### 3. Move Safety Check (`umbrella-migrator.ts:415-423`)
- `fs.existsSync(step.destination)` guard before rename/copy
- Throws descriptive error with suggestion to use collision handling

### 4. Post-Move Log Fix (`umbrella-migrator.ts:339-376`)
- `logRoot` starts as `plan.candidate.projectRoot`
- After step with `.specweave` in description completes, switches to `plan.umbrellaPath`
- All subsequent `appendMigrationLog()` calls use the updated root

## Testing Strategy

- Unit tests in `umbrella-migrator-collision.test.ts` using real filesystem (tmpdir)
- 6 test cases covering: null/previous/partial/unrelated classification, move safety, ghost log prevention
- ESM mocking via `vi.hoisted()` + `vi.mock()` for git-utils, execFileNoThrow, persistUmbrellaConfig
