# Implementation Plan: Redesign specweave init project resolution

## Overview

This increment refactors the `specweave init` command's path resolution logic. The changes are confined to three files under `src/cli/` in the specweave repo. No new modules are introduced beyond a single helper function. The work is a pure refactor with one minor behavioral expansion (relaxed post-scaffold guard).

## Architecture

### Components Modified

- **`src/cli/commands/init.ts`**: Main init command -- unified path resolution, DRY umbrella config, relaxed post-scaffold guard, improved error messages
- **`src/cli/helpers/init/path-utils.ts`**: New `buildUmbrellaConfig()` helper function alongside existing umbrella scanning functions
- **`src/cli/helpers/init/index.ts`**: Updated barrel export to include new helper

### Data Model

No data model changes. The `config.json` schema remains identical. The `UmbrellaDiscoveryResult` type is consumed by the new helper but not modified.

### Function Signatures

```typescript
// New helper in path-utils.ts
export function buildUmbrellaConfig(
  discovery: UmbrellaDiscoveryResult,
  projectName: string
): {
  umbrella: { enabled: true; projectName: string; childRepos: Array<{ id: string; path: string; name: string; prefix: string }> };
  repository: { umbrellaRepo: true };
}
```

## Technology Stack

- **Language**: TypeScript (ESM, `--moduleResolution nodenext`)
- **Testing**: Vitest with ESM mocking (`vi.hoisted()` + `vi.mock()`)
- **CLI framework**: Commander.js (unchanged)

## Architecture Decisions

### AD-001: Helper in path-utils.ts (not a new file)
The `buildUmbrellaConfig()` function is ~25 lines and logically pairs with `scanUmbrellaRepos()`. Creating a separate `umbrella-config.ts` would add a new import/export chain for minimal benefit. Keeping it in `path-utils.ts` collocates related umbrella logic.

### AD-002: No behavioral change for no-args init
The current code already handles `undefined` and `'.'` identically. The refactor collapses the branch for clarity, not for behavioral change. This minimizes risk.

### AD-003: Post-scaffold guard relaxation is additive only
Showing the project setup prompt more often (when `.git` exists) never forces action -- the user can always choose "I have existing code here" to skip. The default remains "existing" so pressing Enter skips the flow.

## Implementation Phases

### Phase 1: Extract buildUmbrellaConfig helper (US-002)
Pure refactor. Extract the duplicate umbrella config logic into `buildUmbrellaConfig()` in `path-utils.ts`. Export from `index.ts`. Update both call sites in `init.ts`. Run existing tests to verify no regression.

### Phase 2: Unify path resolution (US-001)
Collapse the `!projectName || projectName === '.'` branch. Add explicit comment. The behavior is already identical, so this is a code clarity change. Add unit test asserting `initCommand(undefined)` sets `targetDir` to CWD.

### Phase 3: Improve error messages and relax guard (US-003)
Update `detectUmbrellaParent` and `detectSuspiciousPath` error blocks in `init.ts` to include `targetDir`. Change the post-scaffold condition from `!hasGit && !hasRepos` to `!hasRepos`. Add unit test for the relaxed condition.

## Testing Strategy

- **Unit tests for `buildUmbrellaConfig()`**: Verify prefix generation with 1-3 repos, prefix collision deduplication, config structure shape
- **Unit test for path resolution**: Verify that `initCommand()` with `undefined` produces the same `targetDir` as `initCommand('.')`
- **Unit test for relaxed post-scaffold**: Mock filesystem to simulate `.git` present but no `repositories/`, verify prompt is reached
- **Regression**: Full existing test suite must pass unchanged

## Technical Challenges

### Challenge 1: Testing init command with process.cwd dependency
**Solution**: The init command uses `process.cwd()` directly. Tests can mock it via `vi.spyOn(process, 'cwd')` or test the helper functions in isolation.
**Risk**: Low -- existing tests already handle this pattern.

### Challenge 2: Import chain for new export
**Solution**: Add export to `index.ts` barrel. All imports within init use the barrel, so this is a single-line change.
**Risk**: Negligible.
