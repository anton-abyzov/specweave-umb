# Implementation Plan: Doctor --fix flag not working for PluginsChecker and lockfile integrity

## Overview

Two targeted bug fixes in the doctor subsystem. Both changes are localized to existing checker files with no architectural impact.

## Files to Modify

### 1. `src/core/doctor/checkers/plugins-checker.ts`
- Rename `_options` to `options` in `check()` method signature
- Extract `fix` boolean from options
- Pass `fix` to each private check method
- Add fix logic to: `checkLocalPluginState`, `checkGlobalPluginCache`, `checkMarketplaceDirectory`, `checkCorePlugin`
- Import `execSync` from `child_process` for running `specweave refresh-plugins`
- Import `unlinkSync` from `fs` (already imported as `* as fs`) for deleting stale files

### 2. `src/core/doctor/checkers/installation-health-checker.ts`
- In `checkLockfileIntegrity()`, when `fix=true` and mismatches/missing skills detected, execute `specweave refresh-plugins` via `execSync`
- Wrap in try/catch: success returns `warn` with "fixed" message, failure returns `fail`

### 3. Test files (new or extended)
- Add fix-mode tests for PluginsChecker
- Add fix-mode tests for lockfile integrity (missing skills + hash mismatches)

## Architecture Decisions

- **execSync over spawn**: Fix operations are synchronous and blocking by design. The doctor command already uses execSync in its CLI handler for the same purpose.
- **stdio: 'pipe'**: Capture output rather than inheriting, so doctor report formatting isn't disrupted.
- **Idempotent fixes**: Deleting a file that doesn't exist is a no-op. Running refresh-plugins when already fresh just skips. All fixes are safe to re-run.

## Implementation Phases

### Phase 1: Fix PluginsChecker (US-001)
- Update method signatures to accept `fix` parameter
- Add fix logic for each of the 4 checks
- Add unit tests

### Phase 2: Fix lockfile integrity (US-002)
- Add execSync call when fix=true for mismatches and missing skills
- Add unit tests with mocked execSync

## Testing Strategy

- Unit tests with temp directories (existing pattern from installation-health-checker.test.ts)
- Mock `execSync` for tests that trigger `specweave refresh-plugins`
- Mock filesystem for PluginsChecker tests (already uses `os.homedir()` paths)

## Technical Challenges

### Challenge 1: PluginsChecker uses real homedir paths
**Solution**: The existing test pattern in doctor.test.ts creates temp dirs. For PluginsChecker, we need to either mock `os.homedir()` or refactor to accept injectable paths (like InstallationHealthChecker does with its constructor options).
**Risk**: Low. InstallationHealthChecker already demonstrates the injectable-path pattern.
