# Implementation Plan: Studio /api/plugins 500

## Overview

Drop-in replacement for `claude plugin list`. New pure helper walks the Claude Code plugin cache + reads `enabledPlugins` from settings.json, producing the same `InstalledPlugin[]` shape the existing `parseInstalledPlugins` parser produced. Two call sites swap. Frontend untouched.

## Architecture

### New file: `src/eval-server/plugin-discovery.ts`

```ts
interface DiscoverOpts {
  cacheRoot: string;          // ~/.claude/plugins/cache
  projectDir?: string;        // for project-scope settings
}

export function discoverInstalledPlugins(opts: DiscoverOpts): InstalledPlugin[];
```

Algorithm:
1. If `cacheRoot` does not exist → return `[]`.
2. Read `enabledPlugins` from user settings (`~/.claude/settings.json`) and project settings (`<projectDir>/.claude/settings.json`) using existing `listEnabledPlugins()` from [src/settings/settings.ts:64](repositories/anton-abyzov/vskill/src/settings/settings.ts:64). Build two maps: `userEnabled: Set<string>`, `projectEnabled: Set<string>` keyed by `<name>@<marketplace>`.
3. For each `<cacheRoot>/<marketplace>/` dir (skip non-dirs, validate `isInside`):
   - For each `<plugin>/` dir inside:
     - Pick the latest version dir by mtime (skip empty parent dirs).
     - Read `<version>/.claude-plugin/plugin.json`.
     - Extract `name` (fallback: parent dir name); `version` from frontmatter or fallback to dir name; `marketplace` = parent dir name.
     - Build the lookup key `<name>@<marketplace>`.
     - Emit one row per scope where the plugin appears in `enabledPlugins`. If neither scope has it, emit one row with `enabled: false, scope: "user"` (default scope for "installed but not enabled").

### Wiring

**Edit [plugin-cli-routes.ts:81](repositories/anton-abyzov/vskill/src/eval-server/plugin-cli-routes.ts:81)**:

```ts
router.get("/api/plugins", async (_req, res) => {
  try {
    const plugins = discoverInstalledPlugins({ cacheRoot, projectDir: root });
    sendJson(res, { plugins });
  } catch (err) {
    sendError(res, 500, "unexpected", err instanceof Error ? err.message : String(err));
  }
});
```

**Edit [plugin-cli.ts:60](repositories/anton-abyzov/vskill/src/eval-server/plugin-cli.ts:60) `fetchPluginList()`**:

Change signature/body to call `discoverInstalledPlugins()`. Keep the function name + return type so all mutation routes that depend on it (`enable`, `disable`, `install`, `uninstall`) need no change. The `cwd` parameter becomes `projectDir`.

## Technology Stack

- `node:fs` — `existsSync`, `readdirSync`, `statSync`, `readFileSync`
- `node:path` — `join`, `resolve`, `sep`
- `node:os` — `homedir` (only for default cacheRoot fallback; tests inject)
- Existing `listEnabledPlugins` from `src/settings/settings.ts`
- Existing `InstalledPlugin` type from `plugin-cli.ts`

**Architecture Decisions:**

- **Pure function, dependency-injected cacheRoot/projectDir.** Tests pass tmp dirs; production passes `homedir() + .claude/plugins/cache` and the studio root. Mirrors the pattern in `plugin-orphan-cleanup.ts`.
- **Don't delete `parseInstalledPlugins` or its tests.** It's still a valid pure parser — keep it dormant in case Claude Code restores `list` later. Just stop calling it in production paths.
- **Don't move enabled-tracking into Studio's own state.** Settings.json is the source of truth; reading it twice per poll (60s) is cheap and correct.
- **Single row per plugin (latest version).** The previous CLI emitted multiple rows when the same plugin existed at multiple scopes. Match that behavior by emitting one row per (name, marketplace, scope) combination.

## Implementation Phases

### Phase 1: New helper + tests
1. Create `src/eval-server/plugin-discovery.ts` with `discoverInstalledPlugins`.
2. Vitest: `src/eval-server/__tests__/plugin-discovery.test.ts` covering all 6 ACs of US-001 + US-003 path safety.

### Phase 2: Wire call sites
3. Replace [plugin-cli-routes.ts:81-92](repositories/anton-abyzov/vskill/src/eval-server/plugin-cli-routes.ts:81) handler body.
4. Replace [plugin-cli.ts:60](repositories/anton-abyzov/vskill/src/eval-server/plugin-cli.ts:60) `fetchPluginList()` body.
5. Vitest: extend `plugin-cli-routes.test.ts` with regression test for AC-US1-07 (PATH override that fails on `claude plugin list` — endpoint must still return 200).

### Phase 3: Verification
6. Run `npm test` — full vitest suite (no regression).
7. Build: `npm run build` + `npm run build:eval-ui`.
8. Live: spin up Studio against TestLab/hi-anton via preview tools. Network tab must show 0 failed `/api/plugins` requests. Take screenshot for evidence.

## Testing Strategy

- **Unit (Vitest)**: `plugin-discovery.test.ts` — all 6 cache-walk scenarios (happy path, missing cacheRoot, missing plugin.json, multiple scopes, path-traversal rejection, no enabledPlugins entry).
- **Integration (Vitest)**: extend `plugin-cli-routes.test.ts` with the PATH-isolation regression test.
- **Live**: preview-tool screenshot of Studio network tab showing no failed `/api/plugins` calls.

## Technical Challenges

### Challenge 1: Multiple version dirs per plugin
**Solution**: Pick the most recent by mtime. Cache layout puts old versions next to new (claude doesn't GC on update). Surfacing both rows would duplicate UI entries.
**Risk**: mtime-based pick can race with claude's mid-install. **Mitigation**: lstat once, ignore if it disappears mid-walk.

### Challenge 2: Project vs user settings precedence
**Solution**: Same as old CLI — emit one row per scope where the plugin is enabled. UI already groups by name and shows scope badges.
**Risk**: Plugin enabled at user but disabled at project (project override). **Mitigation**: emit user row with `enabled:true` AND project row with `enabled:false`; UI shows both with proper scope. Mirrors observed `claude plugin list` output before removal.

### Challenge 3: settings.json key format mismatch
**Solution**: settings.json keys are `<name>@<marketplace>`; the cache walk gives us `name` + `marketplace` separately. Build the key by joining; if neither user nor project map has it → emit `enabled: false, scope: "user"` (the most common default).
