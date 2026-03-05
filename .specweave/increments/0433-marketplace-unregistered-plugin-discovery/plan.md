# Implementation Plan: Marketplace Unregistered Plugin Discovery

## Overview

Add discovery of plugin directories that exist on the filesystem (under `plugins/`) but are missing from `marketplace.json`. These unregistered plugins are surfaced in the interactive picker with a visual indicator, gated behind `--force` for installation, and come with a re-submission prompt to trigger platform scanning. All changes live in the existing vskill CLI codebase -- no new commands or subcommands, no platform-side changes.

## Architecture

### Component Map

```
src/marketplace/marketplace.ts        <-- NEW: discoverUnregisteredPlugins()
src/marketplace/index.ts              <-- re-export new function + type
src/commands/add.ts
  installMarketplaceRepo()            <-- MODIFIED: discovery call, picker merge, --force gate
  installRepoPlugin()                 <-- MODIFIED: overrideSource parameter
src/api/client.ts                     <-- EXISTING: submitSkill() reused as-is
```

### Data Flow

```
installMarketplaceRepo(owner, repo, manifestContent, opts)
  |
  +--> getAvailablePlugins(manifestContent)     // existing -- returns MarketplacePlugin[]
  |
  +--> discoverUnregisteredPlugins(owner, repo, manifestContent)
  |      |
  |      +--> GET /repos/{owner}/{repo}/contents/plugins/
  |      |      filter type==="dir", diff against manifest plugin names
  |      |      returns string[] (unregistered dir names)
  |      |      on error: returns [] silently
  |      |
  |      v
  |    ["marketing", "analytics"]     // unregistered names
  |
  +--> Build combined picker items:
  |      registered:   [{label: "frontend", ...}, {label: "backend", ...}]
  |      unregistered: [{label: "marketing (new -- not in marketplace.json)", ...}]  // yellow, unchecked
  |
  +--> promptCheckboxList(combinedItems)
  |      returns indices[] into combined array
  |
  +--> Partition selected indices:
  |      registeredSelected   -> proceed to install normally
  |      unregisteredSelected -> check --force gate
  |
  +--> If unregisteredSelected.length > 0 && !opts.force:
  |      print warning per plugin
  |      promptConfirm("Submit repo for platform scanning?")
  |        yes -> submitSkill({ repoUrl }) + print tracking URL
  |        no  -> continue with registered only
  |
  +--> If unregisteredSelected.length > 0 && opts.force:
  |      install via installRepoPlugin(ownerRepo, name, opts, overrideSource)
  |      lockfile entry uses tier: "UNSCANNED"
  |
  +--> Install registered plugins via existing path (unchanged)
```

### Key Types

```typescript
// NEW -- in src/marketplace/marketplace.ts
export interface UnregisteredPlugin {
  name: string;
  source: string;  // always "plugins/{name}" by convention
}

// NEW function signature
export async function discoverUnregisteredPlugins(
  owner: string,
  repo: string,
  manifestContent: string,
): Promise<UnregisteredPlugin[]>
```

### Component Details

#### 1. `discoverUnregisteredPlugins()` -- marketplace.ts

Location: `src/marketplace/marketplace.ts`, after the existing `validateMarketplace()` function.

Responsibilities:
- Single GitHub Contents API call: `GET /repos/{owner}/{repo}/contents/plugins/`
- Filter response to `type === "dir"` entries only (AC-US1-03)
- Diff directory names against `getAvailablePlugins(manifestContent).map(p => p.name)`
- Return `UnregisteredPlugin[]` for directories not in manifest
- On any error (network, 404, rate limit): return `[]` silently (AC-US1-02)
- Uses existing `User-Agent: vskill-cli` header pattern from discovery/github-tree.ts

Why here: This module already owns all marketplace.json parsing logic. Discovery is a natural extension -- it answers "what else exists beyond the manifest?" using the same domain vocabulary.

#### 2. Picker Integration -- installMarketplaceRepo() in add.ts

Location: `src/commands/add.ts`, inside `installMarketplaceRepo()` starting at line ~162.

Changes to the function flow (by section):

**After line 170** (after `getAvailablePlugins` call):
```typescript
// Discover unregistered plugins (best-effort, never blocks)
const unregistered = await discoverUnregisteredPlugins(owner, repo, manifestContent);
```

**Header message** (line ~177):
Replace single-line header with registered/unregistered counts:
```
Marketplace: specweave -- 12 registered, 1 unregistered   // unregistered count in yellow
```

**Non-TTY branch** (line ~197):
After listing registered plugins, list unregistered with `(unregistered)` label and a note about `--force`.

**Auto-select branch** (`--yes`/`--all`, line ~206):
- Without `--force`: auto-select registered only, print skip message for unregistered
- With `--force`: auto-select all (registered + unregistered)

**Checkbox picker branch** (line ~250):
Build combined items array:
```typescript
const combinedItems = [
  ...plugins.map(p => ({ label: p.name + installedTag, description: p.description, checked: ... })),
  ...unregistered.map(u => ({
    label: u.name + yellow(" (new -- not in marketplace.json)"),
    description: undefined,
    checked: false,  // always unchecked by default (AC-US2-03)
  })),
];
```
The picker returns indices into `combinedItems`. Indices `< plugins.length` are registered; indices `>= plugins.length` map to `unregistered[i - plugins.length]`.

**Post-picker processing** (after line ~265):
```typescript
const registeredSelected = selectedIndices
  .filter(i => i < plugins.length)
  .map(i => plugins[i]);
const unregisteredSelected = selectedIndices
  .filter(i => i >= plugins.length)
  .map(i => unregistered[i - plugins.length]);
```

**Force gate** (new section after partition):
- If `unregisteredSelected.length > 0 && !opts.force`: print warning, offer re-submission, proceed with registered only
- If `unregisteredSelected.length > 0 && opts.force`: install via `installRepoPlugin()` with `overrideSource`

#### 3. `installRepoPlugin()` overrideSource -- add.ts

Location: `src/commands/add.ts`, function at line 1289.

Current signature:
```typescript
async function installRepoPlugin(ownerRepo, pluginName, opts)
```

New signature:
```typescript
async function installRepoPlugin(ownerRepo, pluginName, opts, overrideSource?: string)
```

When `overrideSource` is provided:
- Skip the marketplace.json lookup (lines 1322-1329)
- Use `overrideSource` directly as `pluginPath` (e.g., `"plugins/marketing"`)
- Set `pluginVersion` to `"0.0.0"` (no version in manifest)
- All other behavior (blocklist check, content fetching, Tier-1 scan, agent install) remains identical

This is the minimal change -- a single optional parameter that bypasses the manifest lookup when the caller already knows the path.

#### 4. Re-submission Helper -- add.ts

Location: `src/commands/add.ts`, as a local helper function near `installMarketplaceRepo()`.

```typescript
async function offerResubmission(owner: string, repo: string): Promise<void> {
  const repoUrl = `https://github.com/${owner}/${repo}`;
  const prompter = createPrompter();
  const accept = await prompter.promptConfirm(
    `Submit ${owner}/${repo} for platform scanning?`,
    true,
  );
  if (!accept) return;
  try {
    const result = await submitSkill({ repoUrl });
    console.log(green(`Submitted. Track at: ${result.trackingUrl}`));
  } catch {
    console.log(yellow(`Submission failed. Submit manually at: https://verified-skill.com/submit`));
  }
}
```

Uses existing `submitSkill()` from `src/api/client.ts` -- no new API calls needed.

#### 5. Lockfile Entries for Unregistered Plugins

When `--force` installs an unregistered plugin, the lockfile entry uses:
```typescript
lock.skills[pluginName] = {
  version: "0.0.0",
  sha,
  tier: "UNSCANNED",          // NEW tier value (field is free-form string)
  installedAt: new Date().toISOString(),
  source: `marketplace:${owner}/${repo}#${pluginName}`,
  marketplace: marketplaceName || undefined,
  pluginDir: true,
  scope: opts.global ? "user" : "project",
};
```

No schema changes needed -- `tier` is already `string` in `SkillLockEntry`.

#### 6. `--plugin <name>` Direct Targeting (AC-US3-03)

Location: The code path where `opts.plugin` is set and matched against marketplace entries (existing flow in `installMarketplaceRepo`).

When `opts.plugin` targets a name not in marketplace.json:
- Check if it matches an unregistered plugin name from discovery
- If match + no `--force`: print warning, do not install
- If match + `--force`: install via `installRepoPlugin()` with `overrideSource`
- If no match anywhere: existing error message ("Plugin X not found")

## Technology Stack

- **Language**: TypeScript (ESM, `--moduleResolution nodenext`)
- **Runtime**: Node.js 18+
- **API**: GitHub REST Contents API (single GET, no auth required for public repos)
- **Dependencies**: None new -- uses existing `fetch`, `submitSkill()`, prompter infrastructure
- **Testing**: Vitest with `vi.mock()` for fetch and `createPrompter()` stubs

## Architecture Decisions

### AD-1: Discovery in marketplace.ts, not a new module

The function queries GitHub about plugin directories and diffs against marketplace.json content. This is marketplace-domain logic -- "what plugins exist vs what's declared." Putting it alongside `getAvailablePlugins()` keeps the domain cohesive. A separate `src/discovery/unregistered.ts` would fragment the marketplace concept across two modules.

### AD-2: Combined picker with index-based partitioning

Rather than showing two separate pickers (registered, then unregistered), combine into one checkbox list. Registered items appear first, unregistered at the bottom. The caller partitions selected indices by comparing against `plugins.length`. This avoids UX friction (one interaction instead of two) and keeps the existing `promptCheckboxList` API unchanged.

### AD-3: overrideSource parameter vs. synthetic MarketplacePlugin

Two options for making `installRepoPlugin()` work with unregistered plugins:
1. Add `overrideSource?: string` parameter to skip manifest lookup
2. Synthesize a fake `MarketplacePlugin` entry and inject it into manifestContent

Option 1 is chosen because it is explicit about the bypass, does not require JSON manipulation, and the caller already knows the path. Option 2 would require modifying the manifest string (fragile) or the parsed array (leaky abstraction).

### AD-4: Best-effort discovery -- fail silent, never block

The GitHub Contents API call is unauthenticated for public repos and subject to rate limiting (60 req/hr). Discovery is a convenience feature, not a gate. If it fails:
- Return `[]` -- the existing flow proceeds as if no unregistered plugins exist
- No error messages, no spinners that hang
- `warnRateLimitOnce()` from existing code handles 403 rate limit warnings

### AD-5: Reuse --force instead of a new flag

The `--force` flag already means "bypass safety checks" throughout the CLI (blocklist, scan verdicts). Adding a `--include-unregistered` flag would create a new concept. Reusing `--force` is consistent with the existing mental model: "I know what I'm doing, proceed anyway."

## Implementation Phases

### Phase 1: Discovery Function (US-001)
- Implement `discoverUnregisteredPlugins()` in marketplace.ts
- Export from marketplace/index.ts
- Unit tests with mocked fetch

### Phase 2: Picker Integration (US-002)
- Modify `installMarketplaceRepo()` to call discovery
- Build combined picker items with visual distinction
- Update header message with counts
- Index-based partitioning of selections

### Phase 3: Force Gate + Re-submission (US-003, US-005)
- Post-picker `--force` check for unregistered selections
- `offerResubmission()` helper using existing `submitSkill()`
- `overrideSource` parameter in `installRepoPlugin()`
- Lockfile `tier: "UNSCANNED"` for force-installed plugins

### Phase 4: Non-TTY + Auto-Select (US-004)
- Non-TTY listing with `(unregistered)` labels
- `--yes`/`--all` skip unregistered, `--yes --force` includes them
- `--plugin <name>` targeting for unregistered names

## Testing Strategy

All tests in Vitest. Mocking strategy:
- `global.fetch` mocked via `vi.fn()` for GitHub Contents API responses
- `createPrompter()` mocked to return preset selections
- `submitSkill()` mocked for re-submission tests

Key test scenarios:
1. Discovery returns correct diff (registered vs filesystem)
2. Discovery returns `[]` on API error
3. Discovery ignores files, only returns directories
4. Picker shows unregistered at bottom, unchecked
5. Selecting unregistered without `--force` triggers warning + re-submission offer
6. Selecting unregistered with `--force` installs with `tier: "UNSCANNED"`
7. `--yes` skips unregistered, `--yes --force` includes them
8. Non-TTY lists unregistered with label
9. `--plugin <name>` for unregistered name without `--force` is blocked

## Technical Challenges

### Challenge 1: Index Mapping Between Combined Picker and Separate Arrays
**Solution**: Combined picker items = `[...registered, ...unregistered]`. Any selected index `i` where `i < registered.length` maps to `registered[i]`, otherwise to `unregistered[i - registered.length]`. Simple arithmetic, no lookup tables needed.

### Challenge 2: GitHub API Rate Limiting on Discovery Call
**Solution**: Single unauthenticated API call with silent failure. The existing `warnRateLimitOnce()` utility handles 403 warnings. Users with `GITHUB_TOKEN` env var get 5000 req/hr automatically (GitHub honors the token in any request with proper headers).

### Challenge 3: Ensuring Tier-1 Scan Still Runs for --force Installs
**Solution**: `installRepoPlugin()` always runs `runTier1Scan()` regardless of how it was called. The `overrideSource` parameter only changes where the plugin path comes from, not the scan pipeline. AC-US3-04 is satisfied by the existing code path.
