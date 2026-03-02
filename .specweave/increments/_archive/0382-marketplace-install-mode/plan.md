# Implementation Plan: Claude Code Plugin Marketplace Install Mode

## Overview

Add marketplace auto-detection to the `addCommand` flow in `src/commands/add.ts`. When a user runs `vskill install owner/repo` and the target repo contains `.claude-plugin/marketplace.json`, route to a new `installMarketplaceRepo` function that presents plugin selection and uses native Claude CLI for installation.

## Architecture

### Components

- **`detectMarketplaceRepo(owner, repo, branch)`** (new, in `src/commands/add.ts`): Checks GitHub Contents API for `.claude-plugin/marketplace.json` in the repo. Returns `{ isMarketplace: boolean, manifestContent?: string }`.
- **`installMarketplaceRepo(owner, repo, manifestContent, opts)`** (new, in `src/commands/add.ts`): The main marketplace install flow -- parses plugins, presents selection UI, clones repo (temp dir), and installs via native Claude CLI.
- **Existing `getAvailablePlugins`** (reused from `src/marketplace/marketplace.ts`): Parse marketplace.json to get plugin list.
- **Existing `registerMarketplace` + `installNativePlugin`** (reused from `src/utils/claude-cli.ts`): Native Claude Code plugin install.
- **Existing `promptCheckboxList`** (reused from `src/utils/prompts.ts`): Checkbox selection UI.

### Flow Diagram

```
addCommand(source, opts)
  ├── opts.repo && opts.all → installAllRepoPlugins (existing, unchanged)
  ├── opts.repo && opts.plugin → installRepoPlugin (existing, unchanged)
  ├── opts.pluginDir && opts.plugin → installPluginDir (existing, unchanged)
  └── source is "owner/repo" (2-part, no --plugin/--repo flags)
      ├── NEW: detectMarketplaceRepo(owner, repo, branch)
      │   ├── Has marketplace.json → installMarketplaceRepo(owner, repo, manifestContent, opts)
      │   └── No marketplace.json → continue to existing discoverSkills flow
      └── existing skill discovery flow (unchanged)
```

### Key Design Decisions

1. **Detection before discovery**: Marketplace detection runs before `discoverSkills()` to avoid unnecessary API calls. A single GitHub Contents API call checks for `.claude-plugin/marketplace.json`.

2. **Shallow clone for native install**: Native `claude plugin marketplace add` requires a local path. We clone the repo to a temp directory, register the marketplace, install selected plugins, then clean up.

3. **All unchecked by default**: Unlike skill discovery (where detected items are pre-checked), marketplace plugins default to unchecked. This matches the user expectation of "browsing a marketplace" rather than "installing everything from a toolkit".

4. **Fallback chain**: If `claude` CLI is unavailable, each plugin falls back to the existing `installRepoPlugin` extraction path. This ensures the feature works even without Claude Code's native plugin system.

5. **No new files**: All code lives in `src/commands/add.ts` alongside the existing install paths. The `detectMarketplaceRepo` and `installMarketplaceRepo` functions are internal to the module. No new modules or entry points needed.

## Technology Stack

- **Language**: TypeScript (ESM, `.js` import extensions)
- **Runtime**: Node.js
- **Dependencies**: No new dependencies. Uses `node:child_process` (execSync for git clone), `node:os` (tmpdir), `node:fs` (rmSync for temp cleanup).
- **Testing**: Vitest with existing mock infrastructure from `add.test.ts`

## Implementation Phases

### Phase 1: Marketplace Detection
- Add `detectMarketplaceRepo` function
- Wire detection into `addCommand` before skill discovery
- Handle edge cases: API failures, rate limiting, private repos

### Phase 2: Marketplace Install Flow
- Add `installMarketplaceRepo` function with plugin selection UI
- Implement shallow clone + native Claude CLI install
- Add fallback to extraction-based install
- Lockfile + telemetry integration

### Phase 3: Testing
- Unit tests for `detectMarketplaceRepo` (mock GitHub API)
- Unit tests for `installMarketplaceRepo` (mock CLI + prompts)
- Integration test for full flow (marketplace detected -> plugins installed)

## Testing Strategy

- Mock `fetch` for GitHub Contents API responses (marketplace detected / not detected / API failure)
- Mock `execSync` for `git clone` and `claude` CLI calls
- Mock `promptCheckboxList` for interactive selection
- Mock filesystem for temp directory operations
- Test that existing `--plugin` and `--repo` paths are NOT affected by the change
- Test non-TTY behavior (abort with helpful error)

## Technical Challenges

### Challenge 1: Native install requires local path
**Solution**: Shallow clone (`git clone --depth 1`) to `os.tmpdir()` + cleanup after install.
**Risk**: Clone failure (private repo, no git). Mitigation: Catch error, fall back to extraction-based install via `installRepoPlugin` for each plugin.

### Challenge 2: Marketplace detection API rate limits
**Solution**: Detection is a single API call to GitHub Contents API. Already within the rate limit budget of the existing `discoverSkills` call it replaces when marketplace is detected.
**Risk**: Rate limited returns → no detection → falls through to skill discovery. This is safe -- the user just gets the old behavior.

### Challenge 3: Interaction with existing flags
**Solution**: `--plugin`/`--repo` flags are checked FIRST in `addCommand` and route to existing paths before marketplace detection runs. Detection only happens in the "bare owner/repo" case.
**Risk**: None -- existing flag behavior is unchanged by design.
