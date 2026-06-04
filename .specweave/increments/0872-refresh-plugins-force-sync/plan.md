# Plan: 0872 refresh-plugins force-sync

## Implementation
1. **`src/utils/plugin-copier.ts`** — add `cpSync` to the node:fs import; add:
   ```ts
   export function syncNativePluginContent(
     pluginName: string, specweaveRoot: string, opts: { homeOverride?: string } = {}
   ): { synced: number; paths: string[]; fromVersion?: string; toVersion?: string }
   ```
   - source = resolve(specweaveRoot, marketplace.plugins.find(name===pluginName).source)  // ./plugins/specweave
   - records = installed_plugins.json.plugins[`${pluginName}@specweave`] (array)
   - for each record.installPath: mkdirSync(recursive) + cpSync(source, installPath, {recursive:true, force:true}) + fixHookPermissions(installPath); set record.version + lastUpdated = source plugin.json version; track from/to version.
   - write installed_plugins.json back if any record changed. Never throw (wrap, return synced:0 on error).
2. **`src/cli/commands/refresh-plugins.ts`** — after the install loop, when `useNativeCli`, for each name in `installedPluginNames` call `syncNativePluginContent(name, specweaveRoot)`; log `↻ <name>: content synced (vX → vY)` when synced>0 (respect quiet).

## TDD
- RED: unit test (tests/unit/utils/plugin-copier-sync.test.ts) with a temp HOME (homeOverride) + a fake specweaveRoot (marketplace.json + plugins/specweave/{hooks/hooks.json, .claude-plugin/plugin.json}) + a stale installPath dir (old file + an extra stale file). Assert syncNativePluginContent copies current files in, recreates a wiped dir, and bumps the version label. Fails before the function exists.
- GREEN: implement the function + wiring.
- VERIFY: build; real refresh-plugins restores a deleted cache file.

## Files
- `src/utils/plugin-copier.ts` (+ syncNativePluginContent, +cpSync import)
- `src/cli/commands/refresh-plugins.ts` (call + log)
- new `tests/unit/utils/plugin-copier-sync.test.ts`

## Ship
Republish (Anton's OK) so users get a refresh-plugins that actually syncs content.
