# Implementation Plan: Fix init repo cloning prompt flow

## Overview

Single-file fix in `src/cli/commands/init.ts`. Three changes: add state variable, handle `clone-github` sub-choice, replace `!hasGit` guard with repositories-emptiness check.

## Changes

### Change 1: State variable (line 125)
Add `let reposClonedInMigration = false;` alongside existing `continueExisting`.

### Change 2: Handle clone-github (lines 227-242)
Add branch for `subChoice === 'clone-github'` that calls `promptRepoUrlsLoop(targetDir, language)`.
Set `reposClonedInMigration = true` for both `clone-github` and `copy-local`.
Remove stale fallthrough comment at line 242.

### Change 3: Replace !hasGit guard (lines 413-443)
- Add `!reposClonedInMigration` to outer guard
- Replace `!hasGit` with check: `repositories/` has no non-dotfile entries
- Keep all existing clone logic, error handling, and umbrellaDiscovery refresh

## Testing Strategy

TDD — tests written first in `tests/unit/cli/commands/init-repo-clone-flow.test.ts`.
Mocking pattern follows `repo-connect-loop.test.ts` (vi.hoisted + vi.mock).
