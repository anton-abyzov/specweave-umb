# Implementation Plan: Fix marketplace temp dir registered as source

## Overview

Minimal bug fix -- one line change in `installMarketplaceRepo()` plus JSDoc update and test adjustments. No architectural changes, no new components, no API changes.

## Change Set

### 1. `src/commands/add.ts` (line ~256)

**Before**:
```typescript
marketplaceRegistered = registerMarketplace(tmpDir);
```

**After**:
```typescript
marketplaceRegistered = registerMarketplace(`${owner}/${repo}`);
```

The `owner` and `repo` variables are already function parameters of `installMarketplaceRepo()`. The temp dir clone is still needed for the extraction fallback path but is no longer used as the marketplace source.

### 2. `src/utils/claude-cli.ts` (JSDoc only)

Update the `@param marketplacePath` documentation on `registerMarketplace()` to reflect that the parameter accepts any valid Claude Code marketplace source: absolute path, URL, or GitHub `owner/repo` shorthand. Rename parameter from `marketplacePath` to `marketplaceSource` for clarity.

### 3. `src/utils/claude-cli.test.ts`

Add a test case verifying `registerMarketplace()` constructs the correct CLI command when given a GitHub `owner/repo` shorthand.

### 4. `src/commands/add.test.ts`

Update existing marketplace integration test assertions to verify `mockRegisterMarketplace` is called with `"owner/repo"` (the GitHub shorthand) instead of the mock temp dir path.

## Architecture

No architectural changes. The fix is entirely within the existing function signatures and call chain.

### Affected Call Chain

```
installMarketplaceRepo(owner, repo, manifestContent, opts)
  └─ registerMarketplace(tmpDir)        ← BUG: temp path
  └─ registerMarketplace(`${owner}/${repo}`)  ← FIX: stable GitHub source
       └─ execSync(`claude plugin marketplace add "${source}"`)
```

### Unaffected Call Chain (no changes needed)

```
installPluginDir(basePath, pluginName, opts)
  └─ tryNativeClaudeInstall(resolve(basePath), ...)
       └─ registerMarketplace(marketplacePath)  ← already a persistent local path
```

## Technology Stack

- **Language**: TypeScript (ESM)
- **Test framework**: Vitest
- **No new dependencies**

## Testing Strategy

TDD mode active. Red-green-refactor cycle:

1. **RED**: Write/update tests asserting `registerMarketplace` receives `owner/repo` (not temp path). Tests fail against current code.
2. **GREEN**: Apply the one-line fix in `add.ts`. Tests pass.
3. **REFACTOR**: Update JSDoc, rename parameter for clarity. All tests still pass.

## Technical Challenges

None. This is a straightforward one-line fix with well-scoped test updates.

## Risk Assessment

- **Risk**: `claude plugin marketplace add owner/repo` might behave differently than path-based registration in some edge case.
- **Mitigation**: The Claude CLI help explicitly states it accepts "a URL, path, or GitHub repo". The shorthand format is a documented first-class input.
