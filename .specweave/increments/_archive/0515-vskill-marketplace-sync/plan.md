# Architecture Plan: vskill marketplace sync command

## Overview

Add a `vskill marketplace sync` CLI command that synchronizes `plugins/*/` directories with `.claude-plugin/marketplace.json`. The command scans plugin directories, reads each `plugin.json`, and adds/updates marketplace entries. A `--dry-run` flag previews changes without writing.

## Architecture Decision: Pure Function + Thin CLI Shell

**Decision**: Separate the sync logic into a pure function (`syncMarketplace`) with zero I/O, and a thin CLI command handler that does all filesystem reads/writes.

**Why**: The existing `marketplace.ts` already follows a pure-function style -- `getAvailablePlugins(content: string)` takes raw JSON strings, not file paths. The sync function adopts the same pattern: it receives parsed data and returns a result object. This makes the core logic trivially testable without mocking `fs`.

**Rejected alternative**: A single function that reads `plugins/`, reads `marketplace.json`, and writes the result. This couples I/O to logic and requires `vi.mock("node:fs/promises")` in every test -- the pattern vskill avoids in its marketplace module.

## Component Breakdown

### 1. `src/marketplace/marketplace.ts` -- Pure sync function (extend existing)

Add to the existing module:

```
syncMarketplace(manifest: MarketplaceManifest, localPlugins: LocalPlugin[]): SyncResult
```

**New types**:

| Type | Fields | Purpose |
|------|--------|---------|
| `LocalPlugin` | `name: string`, `dirName: string`, `version?: string`, `description?: string` | Parsed plugin.json from a `plugins/*/` directory |
| `SyncPluginStatus` | `"added" \| "updated" \| "unchanged"` | Per-plugin outcome |
| `SyncPluginEntry` | `name: string`, `status: SyncPluginStatus`, `details?: string` | One row in the result |
| `SyncResult` | `entries: SyncPluginEntry[]`, `manifest: MarketplaceManifest`, `skipped: string[]` | Full sync outcome |

**Algorithm**:
1. Build a `Map<name, MarketplacePlugin>` from `manifest.plugins`
2. For each `LocalPlugin`:
   - If not in map: create entry with `source: "./plugins/<dirName>"`, mark `"added"`
   - If in map but `version` or `description` differs: patch entry, mark `"updated"`
   - If in map and identical: mark `"unchanged"`
3. Preserve existing entries not touched by sync (no orphan removal -- per spec)
4. Return new `MarketplaceManifest` with merged `plugins` array + `SyncPluginEntry[]` summary

**Edge cases handled inside pure function**:
- Duplicate plugin names across directories: first-encountered wins, second is added to `skipped` with reason
- Empty `localPlugins` array: returns original manifest unchanged, 0 entries

### 2. `src/commands/marketplace.ts` -- CLI command handler (new file)

Thin shell that:
1. Resolves project root via `findProjectRoot(opts.cwd || process.cwd())`
2. Reads `.claude-plugin/marketplace.json` -- exits 1 if missing or malformed JSON
3. Scans `plugins/*/` directories:
   - For each subdirectory, reads `.claude-plugin/plugin.json`
   - Skips non-directories (files at `plugins/` level)
   - Skips directories with missing/malformed `plugin.json` or missing `name` field -- collects as warnings
4. Calls `syncMarketplace(manifest, localPlugins)`
5. Prints warnings for skipped dirs (yellow)
6. Prints summary table using `table()` from `output.ts`:
   - Columns: status indicator (`+`/`~`/` `), plugin name
   - Status indicators: `green("+")` added, `yellow("~")` updated, `dim(" ")` unchanged
7. If not `--dry-run`: writes updated `marketplace.json` with 2-space indent + trailing newline
8. If `--dry-run`: prints `"dry run -- no changes written"` in dim

**Exit codes**: 0 on success (including "nothing to change"), 1 on missing marketplace.json or malformed JSON.

### 3. `src/index.ts` -- Commander registration (modify)

```typescript
program
  .command("marketplace [subcommand]")
  .alias("mp")
  .description("Manage marketplace.json -- sync plugins, list entries")
  .option("--dry-run", "Preview changes without writing")
  .option("--cwd <path>", "Root directory containing .claude-plugin/")
  .action(async (subcommand = "sync", opts) => {
    const { marketplaceCommand } = await import("./commands/marketplace.js");
    await marketplaceCommand(subcommand, opts);
  });
```

Pattern matches existing commands (lazy dynamic import in action handler). `subcommand` defaults to `"sync"` so `vskill mp` = `vskill marketplace sync`.

## Data Flow

```
CLI invocation
     |
     v
marketplace.ts (command)
  |-- findProjectRoot()
  |-- readFile(".claude-plugin/marketplace.json")  --> parse JSON
  |-- readdir("plugins/")
  |     |-- for each dir: readFile("plugins/<dir>/.claude-plugin/plugin.json")
  |     |-- skip on error, collect as warning
  |     v
  |   LocalPlugin[]
  |
  |-- syncMarketplace(manifest, localPlugins)  <-- PURE, no I/O
  |     |
  |     v
  |   SyncResult { entries, manifest, skipped }
  |
  |-- print warnings (skipped dirs)
  |-- print summary table
  |-- if !dryRun: writeFile(marketplace.json, JSON.stringify(manifest, null, 2) + "\n")
  v
exit 0
```

## File Inventory

| File | Action | Purpose |
|------|--------|---------|
| `src/marketplace/marketplace.ts` | Modify | Add `syncMarketplace()`, `LocalPlugin`, `SyncResult` types |
| `src/marketplace/index.ts` | Modify | Re-export new types and function |
| `src/commands/marketplace.ts` | Create | CLI command handler (FS I/O, output) |
| `src/index.ts` | Modify | Register `marketplace [subcommand]` command |
| `src/marketplace/marketplace.test.ts` | Modify | Tests for `syncMarketplace()` pure function |
| `src/commands/marketplace.test.ts` | Create | Tests for CLI command (mocked FS) |

## Testing Strategy

**TDD mode active** -- tests written before implementation.

### Unit tests (pure function -- no mocks needed)
- `syncMarketplace`: added/updated/unchanged detection
- `syncMarketplace`: duplicate name handling
- `syncMarketplace`: empty localPlugins
- `syncMarketplace`: preserves existing entries not in localPlugins

### Integration tests (CLI command -- mock `node:fs/promises`)
- Reads marketplace.json and plugin dirs correctly
- Exits 1 on missing marketplace.json
- Exits 1 on malformed marketplace.json
- Skips dirs without plugin.json (with warning)
- `--dry-run` does not call writeFile
- Summary table format matches spec (status indicator + name)

## Dependencies

- **Internal**: `findProjectRoot` (`src/utils/project-root.ts`), `table`/`green`/`yellow`/`dim`/`bold` (`src/utils/output.ts`), `MarketplaceManifest`/`MarketplacePlugin` (`src/marketplace/marketplace.ts`)
- **Node.js built-in**: `node:fs/promises` (readdir, readFile, writeFile, stat), `node:path` (join, resolve)
- **External**: None (zero new dependencies)

## Constraints

- ESM: all imports use `.js` extensions
- `--moduleResolution nodenext`
- Follows existing Commander.js lazy-import pattern
- JSON output: 2-space indentation + trailing newline (matching current marketplace.json)
- No orphan removal (explicitly out of scope per spec)
