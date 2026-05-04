# Implementation Plan: vskill clone hardening

## Overview

Three localized edits to the 0822 codebase to close known gaps. No new modules, no new dependencies, no public API changes. All edits live in:
- `repositories/anton-abyzov/vskill/src/commands/clone.ts`
- `repositories/anton-abyzov/vskill/src/commands/clone-prompts.ts`
- `repositories/anton-abyzov/vskill/src/index.ts` (one new flag)

Tests added:
- `repositories/anton-abyzov/vskill/src/commands/__tests__/clone.integration.test.ts` (new scenarios appended)
- `repositories/anton-abyzov/vskill/src/commands/__tests__/clone-prompts.test.ts` (new file)

## Edit 1 — Plugin-root cleanup on bulk-clone failure (FR-001 / US-001)

**File**: `src/commands/clone.ts`, function `runWholePluginClone` (around line 700-720 per code-review).

**Current behavior**: On iteration failure, loops through `completed` to remove each cloned skill dir; also removes the current iteration's `.tmp`.

**New behavior**: After the per-skill cleanup loop, if `targetKind === "new-plugin"` AND `completed.length > 0` AND a `pluginRoot` was scaffolded, also `bestEffortRm(pluginRoot)`. For `targetKind === "plugin"` (existing user-owned plugin), do NOT remove the plugin root.

**Pseudocode**:
```typescript
} catch (err) {
  // ...existing per-skill cleanup loop...
  if (targetKind === "new-plugin" && completed.length > 0 && pluginRoot) {
    bestEffortRm(pluginRoot);
  }
  throw err;
}
```

## Edit 2 — `--force` + `--target plugin` .bak staging (FR-002 / US-002)

**File**: `src/commands/clone.ts`, function `runCloneOnce`, in the `--force` branch for `targetKind === "plugin"`.

**Current behavior**: Before atomic rename, deletes the live `finalDir` via `bestEffortRm`. If the subsequent skill+manifest rename pair fails, the original is gone.

**New behavior**: Compute `bakDir = ${finalDir}.bak`. Rename `finalDir → bakDir` (instead of delete). Attempt skill rename then manifest rename. On any failure, restore: rename `bakDir → finalDir` and propagate the error. On success, `bestEffortRm(bakDir)`. If the restore-rename itself fails, log a loud warning to stderr (`"WARNING: failed to restore from .bak at <path> — manual recovery needed"`) and propagate the original error; leave `.bak` in place.

**Pseudocode**:
```typescript
if (force && targetKind === "plugin" && existsSync(finalDir)) {
  const bakDir = `${finalDir}.bak`;
  await fs.rename(finalDir, bakDir);
  try {
    await fs.rename(stagedSkillDir, finalDir);
    await fs.rename(stagedManifestPath, manifestPath);
  } catch (err) {
    try {
      await fs.rename(bakDir, finalDir);  // restore
    } catch (restoreErr) {
      console.error(`WARNING: failed to restore from .bak at ${bakDir} — manual recovery needed`);
    }
    throw err;
  }
  bestEffortRm(bakDir);
}
```

## Edit 3 — `--yes` flag + non-TTY default-deny (FR-003 / US-003)

**File 1**: `src/commands/clone-prompts.ts`, function `confirmPrompt`.

Extend signature: `confirmPrompt(question: string, opts?: { yes?: boolean; stdinIsTTY?: boolean })`.

```typescript
export async function confirmPrompt(question: string, opts: { yes?: boolean; stdinIsTTY?: boolean } = {}): Promise<boolean> {
  if (opts.yes) return true;
  const isTTY = opts.stdinIsTTY ?? process.stdin.isTTY;
  if (!isTTY) {
    console.error("refusing to prompt in non-TTY context — re-run with --yes to confirm");
    return false;
  }
  // ...existing readline confirm logic...
}
```

**File 2**: `src/index.ts`, in the `clone` Commander registration. Add `.option("-y, --yes", "Auto-confirm all prompts")`.

**File 3**: `src/commands/clone.ts`, plumb `opts.yes` from the Commander action handler to all `confirmPrompt` calls.

## Test Strategy

| Test | Layer | Coverage |
|---|---|---|
| Inject failure on iteration 2 of bulk new-plugin clone, assert pluginRoot removed | integration | AC-US1-01 |
| Inject failure on iteration 1, assert no extra cleanup | integration | AC-US1-02 |
| Bulk clone to existing plugin, fail iteration 2, assert plugin root preserved | integration | AC-US1-03 |
| `--force` + `--target plugin`, inject manifest-rename failure, assert original skill restored from .bak | integration | AC-US2-01 |
| `--force` + `--target plugin`, inject restore-rename failure, assert warning + .bak preserved | unit | AC-US2-02 |
| Re-run all 17 existing 0822 integration tests | regression | AC-US2-03 |
| `confirmPrompt({yes:true})` returns true without reading stdin | unit | AC-US3-01 |
| `confirmPrompt({stdinIsTTY:false})` returns false + error message | unit | AC-US3-02 |
| `confirmPrompt({stdinIsTTY:true})` exercises readline path | unit | AC-US3-03 |

## Domain Split

This is small enough for **one combined backend+testing agent**. Total estimated changes: ~50 LOC production + ~150 LOC tests. Well under the 15-task cap.

## Risks

| Risk | Mitigation |
|---|---|
| Breaking existing tests | Re-run all 17 0822 integration tests after each edit |
| TTY detection inconsistency across Node versions | Default to non-TTY when `process.stdin.isTTY` is `undefined`; allow opts override |
| `.bak` left on disk on restore failure | Acceptable trade-off: better to leak a `.bak` than destroy data |
