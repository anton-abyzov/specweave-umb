# Architecture Plan: 0589 — CLI Complete Command Improvements

## Overview

Three surgical improvements to `specweave complete`: short-ID resolution, batch mode, and AC coverage validator bug fix. All changes are within the specweave CLI codebase at `repositories/anton-abyzov/specweave/`.

## Architecture Decisions

### AD-1: Extract `resolveIncrementId()` to shared utility

**Current state**: `resolveIncrementId()` lives as a private function in `src/cli/commands/evaluate-completion.ts:59-76`. It resolves short IDs (e.g., `0589`) to full directory names (e.g., `0589-cli-complete-improvements`) via prefix matching on `.specweave/increments/`.

**Decision**: Extract to `src/utils/resolve-increment-id.ts` as a standalone exported function. Both `evaluate-completion.ts` and `complete.ts` will import from this shared module.

**Rationale**:
- DRY — two commands now need this logic
- The function has no dependencies on evaluate-completion internals
- Follows existing pattern: `src/utils/increment-id-validator.ts` is already a shared utility for ID validation

**Interface**:
```typescript
// src/utils/resolve-increment-id.ts
import * as fs from 'fs';
import * as path from 'path';
import { resolveEffectiveRoot } from './find-project-root.js';

/**
 * Resolve a potentially short increment ID to the full directory name.
 * Handles both exact matches (0589-cli-complete-improvements) and
 * prefix matches (0589).
 *
 * @param incrementId - Short or full increment ID
 * @param projectRoot - Project root (defaults to resolveEffectiveRoot())
 * @returns Full increment directory name, or null if not found
 */
export function resolveIncrementId(
  incrementId: string,
  projectRoot?: string
): string | null;
```

**Migration**: `evaluate-completion.ts` will import from the new module. Its local `resolveIncrementId` and `findProjectRoot` functions are deleted — `findProjectRoot` is already available in `src/utils/find-project-root.ts`. No other callers exist (confirmed via grep).

### AD-2: Batch mode via variadic CLI argument

**Current state**: CLI registration at `bin/specweave.js:339` uses `<increment-id>` (single required argument). `completeCommand()` accepts a single `incrementId: string`.

**Decision**: Change CLI registration to `<increment-id> [more-ids...]` and add a batch loop in `completeCommand()`.

**Rationale**:
- Matches existing pattern in `archive` command (`bin/specweave.js:419`): `.command('archive [increments...]')`
- Commander.js natively supports variadic arguments — the action callback receives an array for `[more-ids...]`
- Per-ID error isolation: one failure does not abort remaining IDs

**CLI registration change** (`bin/specweave.js:339`):
```javascript
// Before:
.command('complete <increment-id>')

// After:
.command('complete <increment-id> [more-ids...]')
```

**Command handler change** (`src/cli/commands/complete.ts`):
```typescript
// Before:
export async function completeCommand(
  incrementId: string,
  options: CompleteCommandOptions
): Promise<void>

// After:
export async function completeCommand(
  incrementId: string,
  moreIds: string[],
  options: CompleteCommandOptions
): Promise<void>
```

**Batch loop design**:
1. Merge `[incrementId, ...moreIds]` into a single array
2. For each ID: resolve short-ID → call `completeIncrement()` → collect result
3. Per-ID try/catch: log error, continue to next ID
4. Exit with code 1 if ANY ID failed (matches current single-ID behavior)

**Action callback wiring** (`bin/specweave.js`):
```javascript
.action(async (incrementId, moreIds, options) => {
  // Commander passes variadic as array in second positional param
  const { completeCommand } = await import('../dist/src/cli/commands/complete.js');
  await completeCommand(incrementId, moreIds, options);
});
```

### AD-3: Fix `parseTasksWithUSLinks()` call in completion validator

**Bug found**: `completion-validator.ts:400` calls `parseTasksWithUSLinks(tasksContent)` passing the **file content string**, but `parseTasksWithUSLinks()` at `task-parser.ts:93` expects a **file path** and calls `readFileSync(tasksPath, 'utf-8')` internally. This means AC coverage validation has been silently failing for all increments — the try/catch at lines 137-140 catches the resulting `ENOENT`/`ENAMETOOLONG` error and degrades to a warning.

**Decision**: Fix the call site in `completion-validator.ts` to pass `tasksPath` (the file path) instead of `tasksContent` (the file content). Remove the now-redundant `tasksContent` read at line 394 since `parseTasksWithUSLinks` reads the file itself.

**Before** (`completion-validator.ts:393-400`):
```typescript
const specContent = await fs.readFile(specPath, 'utf-8');
const tasksContent = await fs.readFile(tasksPath, 'utf-8');

// Parse all ACs from spec.md
const allACs = this.parseAllACsWithPriority(specContent);

// Parse tasks to find AC references
const tasksByUS = parseTasksWithUSLinks(tasksContent); // BUG: passes content, not path
```

**After**:
```typescript
const specContent = await fs.readFile(specPath, 'utf-8');

// Parse all ACs from spec.md
const allACs = this.parseAllACsWithPriority(specContent);

// Parse tasks to find AC references
const tasksByUS = parseTasksWithUSLinks(tasksPath); // FIX: pass file path, not content
```

**Impact**: AC coverage validation will now actually work. This means:
- P0 ACs without implementing tasks will block closure (as intended since v0.23.0)
- Orphan tasks will generate warnings (as intended)
- Increments that previously closed despite missing task coverage may now fail validation

This is the correct behavior — the validator was designed to enforce these checks.

## File Change Map

| File | Change | Risk |
|------|--------|------|
| `src/utils/resolve-increment-id.ts` | **NEW** — extracted shared utility | Low — pure function, no side effects |
| `src/cli/commands/evaluate-completion.ts` | Delete local `resolveIncrementId` + `findProjectRoot`, import from shared utils | Low — same logic, different import path |
| `src/cli/commands/complete.ts` | Add short-ID resolution + batch loop | Medium — changes command interface |
| `bin/specweave.js:337-348` | Change `<increment-id>` to `<increment-id> [more-ids...]`, update action params | Medium — CLI interface change |
| `src/core/increment/completion-validator.ts:393-400` | Fix `parseTasksWithUSLinks(tasksContent)` → `parseTasksWithUSLinks(tasksPath)`, remove unused `tasksContent` read | Medium — enables previously-broken validation |

## Dependency Order

```
T-001 (extract resolveIncrementId)
  → T-002 (wire into complete command + batch mode)
T-003 (fix parseTasksWithUSLinks call) — independent of T-001/T-002
```

T-001 and T-003 can run in parallel. T-002 depends on T-001.

## Testing Strategy

### Unit tests (new file: `tests/unit/utils/resolve-increment-id.test.ts`)
- Exact match: `0589-cli-complete-improvements` → returns same
- Prefix match: `0589` → returns `0589-cli-complete-improvements`
- No match: `9999` → returns null
- Empty increments dir → returns null
- Multiple prefix matches: returns first (alphabetical via `readdirSync`)

### Unit tests (new file: `tests/unit/cli/complete-command.test.ts`)
- Single ID completes successfully
- Single ID with short-ID resolution
- Batch: multiple IDs all succeed
- Batch: one ID fails, others continue, exit code 1
- Batch: short-ID resolution works for all IDs
- Unknown ID returns error

### Integration test (update: `tests/integration/commands/done-command.test.ts`)
- Verify AC coverage validation detects orphaned P0 ACs (was previously silently skipped)

## Risk Assessment

1. **CLI interface change (batch mode)**: Low risk. Existing single-argument usage is fully backward compatible — `moreIds` defaults to empty array.
2. **AC coverage validator fix**: Medium risk. Increments that previously passed validation may now fail. This is correct behavior, but could surprise users mid-closure. Mitigation: the `--skip-validation` flag exists for emergency bypass.
3. **Shared utility extraction**: Low risk. Pure refactor, no behavioral change.

## Out of Scope

- Changing `parseTasksWithUSLinks()` to accept content OR path (would require signature change affecting many callers)
- Adding `--parallel` flag for batch completion (overkill for typical usage)
- Adding glob patterns for batch completion (e.g., `specweave complete 058*`)
