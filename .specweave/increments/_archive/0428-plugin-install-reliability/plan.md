# Plan: Fix vskill plugin install reliability

## Increment
`0428-plugin-install-reliability` | Type: bug | Priority: P1

## Target
`repositories/anton-abyzov/vskill/` (Node.js ESM CLI, TypeScript, Vitest)

## Problem Statement

Three reliability gaps in `vskill install`:

1. **Stale temp dir registration** -- `tryNativeClaudeInstall()` can register a temp directory path with `claude plugin marketplace add`, which becomes invalid after the temp dir is cleaned up. No guard exists to detect or prevent this.
2. **Missing single-plugin confirmation** -- When a marketplace has exactly one plugin, `installMarketplaceRepo()` auto-selects it without confirmation. Users get no chance to abort or understand what will be installed.
3. **Opaque registration failures** -- `registerMarketplace()` returns `boolean`, discarding stderr. When registration fails, the user sees a generic "Failed to register marketplace" message with no diagnostic information.

## Architecture Decisions

### AD-1: `RegisterResult` replaces `boolean` return

`registerMarketplace()` currently returns `boolean` and passes `stdio: "ignore"`. Change to:

```typescript
interface RegisterResult {
  success: boolean;
  stderr?: string;
}
```

Capture stderr via `stdio: ["pipe", "pipe", "pipe"]` on the `execSync` call. This is a breaking change -- all call sites must update atomically.

**Call sites** (3 total):
- `tryNativeClaudeInstall()` at line ~463 in `add.ts`
- `installMarketplaceRepo()` at line ~264 in `add.ts`
- `claude-cli.test.ts` -- test assertions on return type

**Risk**: Low. All call sites are in this repo. Change is atomic within a single commit.

### AD-2: Temp path guard with deregister-retry

New `isTempPath(p: string): boolean` helper in `add.ts`:

```typescript
function isTempPath(p: string): boolean {
  return p.startsWith(os.tmpdir());
}
```

Applied in `tryNativeClaudeInstall()`:
- If `marketplacePath` is a temp dir AND no `gitUrl` is available, log a warning and skip native install (fall back to extraction).
- If `marketplacePath` is a temp dir AND `gitUrl` IS available, use the git URL (current behavior, but now explicit).

New `deregisterMarketplace(source: string): boolean` in `claude-cli.ts`:
- Calls `claude plugin marketplace remove "<source>"`
- Used for retry: if registration fails, deregister stale entry, then retry once with the git URL.

New `listMarketplaces(): string[]` in `claude-cli.ts`:
- Calls `claude plugin marketplace list`
- Returns parsed list of registered marketplace sources
- Used for diagnostics and future debugging

### AD-3: Marketplace validation function

New `validateMarketplace()` in `marketplace.ts`:

```typescript
interface MarketplaceValidation {
  valid: boolean;
  error?: string;
  pluginCount: number;
  name?: string;
}

function validateMarketplace(content: string): MarketplaceValidation
```

Checks:
- JSON parses successfully
- `name` field is non-empty string
- `plugins` array is non-empty
- Each plugin has `name` and `source` fields

Exported from `marketplace/index.ts`. The existing `getAvailablePlugins()` stays unchanged -- it is a silent parser for internal consumption. `validateMarketplace()` is the diagnostic entry point for install flows.

### AD-4: No `--dry-run` flag

The existing flow already shows install summaries. The actual gap was the missing confirmation prompt for single-plugin marketplaces, which is addressed by AD-5.

### AD-5: Single-plugin confirmation prompt

In `installMarketplaceRepo()`, when `plugins.length === 1` and the plugin is NOT already installed, add a confirmation prompt before proceeding:

```
Install "frontend" from specweave marketplace? (Y/n)
```

Currently the code at line ~218 auto-selects and prints the plugin name but never asks. The fix adds `prompter.promptConfirm()` (matching the existing pattern for reinstall confirmation at line ~224).

### AD-6: Improved error messages in `installPluginDir()`

When `resolvePluginDir()` returns null (plugin not found), list all available plugins from marketplace.json in the error message.

Current output:
```
Plugin "foo" not found in marketplace.json
Checked: /path/.claude-plugin/marketplace.json
```

Improved output:
```
Plugin "foo" not found in marketplace.json
Available plugins: sw, frontend, backend
Checked: /path/.claude-plugin/marketplace.json
```

## Component Changes

### File: `src/utils/claude-cli.ts`

| Function | Change |
|---|---|
| `registerMarketplace()` | Return `RegisterResult` instead of `boolean`; capture stderr via `stdio: ["pipe", "pipe", "pipe"]` |
| NEW `deregisterMarketplace()` | Calls `claude plugin marketplace remove "<source>"`, returns boolean |
| NEW `listMarketplaces()` | Calls `claude plugin marketplace list`, parses newline-separated output into string array |

Exports added: `RegisterResult` (interface), `deregisterMarketplace`, `listMarketplaces`

### File: `src/marketplace/marketplace.ts`

| Function | Change |
|---|---|
| NEW `validateMarketplace()` | Structural validation returning `MarketplaceValidation` with diagnostic error strings |

Export added: `MarketplaceValidation` (interface), `validateMarketplace`

### File: `src/marketplace/index.ts`

Re-export `validateMarketplace` and `MarketplaceValidation` from barrel.

### File: `src/commands/add.ts`

| Function | Change |
|---|---|
| NEW `isTempPath()` | Helper: returns `true` when path starts with `os.tmpdir()` |
| `tryNativeClaudeInstall()` | Temp path guard (skip native if temp path and no git URL); handle `RegisterResult`; deregister-retry on failure |
| `installMarketplaceRepo()` | Add confirmation prompt for single-plugin case (non-installed); handle `RegisterResult` with stderr logging |
| `installPluginDir()` | List available plugins in not-found error message |

### File: `src/utils/claude-cli.test.ts`

Update `registerMarketplace` tests to assert `RegisterResult` shape. Add test suites for `deregisterMarketplace` and `listMarketplaces`.

### File: `src/marketplace/marketplace.test.ts`

Add `validateMarketplace` test suite covering valid manifest, missing name, empty plugins array, and malformed plugin entries.

## Data Flow

```
vskill install --repo owner/repo --plugin frontend
  |
  v
installMarketplaceRepo()
  |-- getAvailablePlugins(manifestContent) --> plugins[]
  |-- plugins.length === 1 && !installed? --> promptConfirm() [NEW]
  |-- isClaudeCliAvailable()? --> yes
  |-- registerMarketplace(gitUrl) --> RegisterResult [CHANGED]
  |   |-- result.success? --> continue
  |   |-- !result.success? --> log result.stderr [NEW]
  |   |                    --> deregister stale --> retry once [NEW]
  |-- installNativePlugin() per plugin
  |-- fallback to extraction on failure
```

```
installPluginDir(basePath, pluginName)
  |
  v
resolvePluginDir(basePath, pluginName)
  |-- returns null? --> list available plugins in error [IMPROVED]
  |-- returns path? --> security scan --> install
  |
tryNativeClaudeInstall(marketplacePath, ...)
  |-- isTempPath(marketplacePath) && !gitUrl? --> skip, warn [NEW]
  |-- isTempPath(marketplacePath) && gitUrl? --> use gitUrl [CLARIFIED]
  |-- registerMarketplace(source) --> RegisterResult [CHANGED]
  |   |-- !success? --> deregister stale --> retry once [NEW]
  |-- installNativePlugin()
```

## Testing Strategy

TDD mode. All changes get unit tests first (red-green-refactor).

| Test Area | File | Key Cases |
|---|---|---|
| `RegisterResult` shape | `claude-cli.test.ts` | success returns `{ success: true }`, failure returns `{ success: false, stderr: "..." }` |
| `deregisterMarketplace` | `claude-cli.test.ts` | calls correct CLI command, returns true/false |
| `listMarketplaces` | `claude-cli.test.ts` | parses newline-separated output, handles empty, handles command failure |
| `validateMarketplace` | `marketplace.test.ts` | valid manifest, missing name, empty plugins, plugin missing name/source |
| `isTempPath` | `add.test.ts` | temp dir detected, non-temp dir rejected, trailing slash edge case |
| Deregister-retry flow | `add.test.ts` | register fails -> deregister -> retry succeeds |
| Single-plugin confirm | `add.test.ts` | prompt shown when 1 plugin and not installed, skipped with `--yes` |

Coverage target: 90% (per increment config).

## Out of Scope

- Refactoring `installPluginDir()` or `installMarketplaceRepo()` beyond the targeted fixes
- Adding `--dry-run` flag (see AD-4)
- Changing `installNativePlugin()` return type (not broken, boolean is sufficient)
- Fuzzy matching / Levenshtein distance for plugin name suggestions

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| `RegisterResult` breaks a missed call site | Low | Medium | Grep for `registerMarketplace` across codebase before commit |
| `claude plugin marketplace remove` does not exist as a CLI command | Low | Low | Guard with try/catch; `deregisterMarketplace` returns false gracefully |
| `claude plugin marketplace list` output format varies across versions | Medium | Low | Parse defensively; return empty array on any failure |
| Temp path detection fails on non-standard tmpdir | Low | Low | `os.tmpdir()` is canonical; prefix match is sufficient |

## Dependency on ADRs

- **ADR-0015** (Hybrid Plugin System, superseded): Confirms native-first with extraction fallback pattern. This increment hardens the native install path without changing the overall architecture.
- No new ADRs required. All changes are implementation-level fixes within the existing architecture.

## Implementation Sequence

1. `src/utils/claude-cli.ts` -- `RegisterResult` type, update `registerMarketplace()`, add `deregisterMarketplace()` and `listMarketplaces()`
2. `src/utils/claude-cli.test.ts` -- update existing tests, add new test suites (TDD red phase)
3. `src/marketplace/marketplace.ts` -- add `validateMarketplace()`
4. `src/marketplace/marketplace.test.ts` -- add validation tests (TDD red phase)
5. `src/marketplace/index.ts` -- re-export new symbols
6. `src/commands/add.ts` -- `isTempPath()`, update `tryNativeClaudeInstall()`, update `installMarketplaceRepo()`, improve `installPluginDir()` error
7. `src/commands/add.test.ts` -- new/updated tests for add.ts changes
8. Green pass: `npx vitest run`
