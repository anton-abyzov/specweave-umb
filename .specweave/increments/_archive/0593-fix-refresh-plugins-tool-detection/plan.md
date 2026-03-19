# Architecture Plan: Fix refresh-plugins tool detection

## Problem Statement

`refreshPluginsCommand()` in `src/cli/commands/refresh-plugins.ts` always calls `detectClaudeCli()` to determine the installation method. It never reads `config.adapters.default` from `.specweave/config.json`. This means:

1. If a Cursor user has Claude CLI installed globally but configured `adapters.default: "cursor"`, refresh-plugins still uses Claude CLI's native plugin system instead of copying skills to `.cursor/skills/`.
2. Non-Claude adapters never get their tool-specific skills directories populated by refresh-plugins.
3. The adapter infrastructure (`AdapterLoader`, `IAdapter.compilePlugin()`, per-adapter skills directories) exists but is completely bypassed.

## Current Flow (Broken)

```
refreshPluginsCommand()
  -> detectClaudeCli()
  -> if available: installPlugin() via `claude plugin install`
  -> else: copyPluginSkillsToProject() to .claude/skills/
```

Neither path consults `config.adapters.default` or `AdapterLoader`.

## Proposed Flow (Fixed)

```
refreshPluginsCommand()
  -> resolveActiveAdapter(projectRoot)
      1. Read config.adapters.default from .specweave/config.json
      2. If value != 'claude' and value is known -> return adapter name
      3. If value == 'claude' or unset -> detectClaudeCli()
         -> if CLI available -> return 'claude-native'
         -> if CLI unavailable -> AdapterLoader.detectTool() runtime fallback
         -> if nothing detected -> return 'claude-fallback' (copy to .claude/skills/)
  -> Based on resolved adapter:
      'claude-native' -> installPlugin() via `claude plugin install` (current path)
      'claude-fallback' -> copyPluginSkillsToProject() to .claude/skills/ (current path)
      any other adapter -> copyPluginSkillsToProject() with adapter's skills dir
```

## Key Design Decisions

### D-1: Add `getSkillsDirectory()` method to IAdapter

Each adapter already hardcodes its skills directory in `compilePlugin()` (e.g., `.cursor/skills`, `.windsurf/skills`). Add a simple `getSkillsDirectory(): string` method to `IAdapter` and `AdapterBase` that returns the tool-specific skills directory path.

**Adapter skills directory mapping** (derived from codebase analysis):

| Adapter | Skills Directory |
|---------|-----------------|
| cursor | `.cursor/skills` |
| windsurf | `.windsurf/skills` |
| cline | `.cline/skills` |
| copilot | `.github/skills` |
| opencode | `.opencode/skills` |
| codex | `.codex/skills` |
| gemini | `.gemini` |
| antigravity | `.agent/skills` |
| jetbrains | `.junie/skills` |
| amazonq | `.amazonq/skills` |
| continue | `.continue/skills` |
| aider | `.aider/skills` |
| trae | `.trae/skills` |
| zed | `.zed/skills` |
| tabnine | `.tabnine/skills` |
| kimi | `.kimi/skills` |
| generic | `.agents/skills` |

### D-2: Reuse `copyPluginSkillsToProject()` with configurable target

`copyPluginSkillsToProject()` currently hardcodes `.claude/skills` as the target via `join(projectRoot, '.claude', 'skills')`. Add an optional `targetSkillsDir` parameter to `CopyPluginOptions`. When a non-Claude adapter is active, pass the adapter's skills directory instead.

This avoids duplicating the copy logic or pulling in the full Plugin type system that `compilePlugin()` requires. The source layout (marketplace plugin's `skills/` subdirectory) is the same regardless of target tool.

### D-3: New helper function `resolveActiveAdapter()`

Create a helper function within `refresh-plugins.ts` that encapsulates the resolution logic:

```typescript
interface ResolvedAdapter {
  name: string;                // e.g., 'claude', 'cursor', 'windsurf'
  method: 'native-cli' | 'file-copy';
  skillsDir: string;           // e.g., '.claude/skills', '.cursor/skills'
}

function resolveActiveAdapter(projectRoot: string): ResolvedAdapter
```

Resolution order:
1. Read `config.adapters.default` from `.specweave/config.json`
2. If adapter is explicitly set and is NOT 'claude':
   - Look up adapter via `AdapterLoader.getAdapter(name)`
   - Return `{ name, method: 'file-copy', skillsDir: adapter.getSkillsDirectory() }`
3. If adapter is 'claude' or unset:
   - Call `detectClaudeCli()`
   - If CLI available + plugin commands work: `{ name: 'claude', method: 'native-cli', skillsDir: '' }`
   - Otherwise: `{ name: 'claude', method: 'file-copy', skillsDir: '.claude/skills' }`

### D-4: No change to `installPlugin()`

`installPlugin()` (native CLI path) stays untouched. It only runs when `method === 'native-cli'`.

### D-5: Config reading approach

Read config directly via `fs.readFileSync` + `JSON.parse` rather than importing `ConfigManager`. This keeps the dependency footprint minimal (refresh-plugins currently has no config dependency) and avoids async/promise changes in the sync command path.

## Files to Modify

### Modified Files

1. **`src/cli/commands/refresh-plugins.ts`** -- Main changes:
   - Import `AdapterLoader`
   - Add `resolveActiveAdapter()` helper
   - Replace `detectClaudeCli()` call with `resolveActiveAdapter()`
   - Update mode display to show detected adapter name
   - Pass adapter's `skillsDir` to `copyPluginSkillsToProject()` when adapter != claude

2. **`src/utils/plugin-copier.ts`** -- Minor change:
   - Add optional `targetSkillsDir` field to `CopyPluginOptions`
   - Use it instead of hardcoded `join(projectRoot, '.claude', 'skills')` when provided

3. **`src/adapters/adapter-interface.ts`** -- Add `getSkillsDirectory(): string` to `IAdapter`

4. **`src/adapters/adapter-base.ts`** -- Add default `getSkillsDirectory()` returning `.claude/skills` as fallback

5. **All 17 adapter implementations** -- Add `getSkillsDirectory()` returning each adapter's skills directory path (values from D-1 table above)

### New Files

None.

### Test Files

1. **`tests/unit/refresh-plugins-adapter.test.ts`** -- Unit tests for `resolveActiveAdapter()`:
   - Config with `adapters.default: 'cursor'` returns cursor skills dir
   - Config with `adapters.default: 'claude'` + CLI available returns native-cli
   - Config with `adapters.default: 'claude'` + CLI unavailable returns file-copy to .claude/skills
   - Config missing/unset falls back to Claude CLI detection
   - Unknown adapter name falls back to detection

2. **`tests/unit/plugin-copier-target-dir.test.ts`** -- Unit test for configurable target:
   - `copyPluginSkillsToProject()` with custom `targetSkillsDir` writes to correct location

## Scope

### In Scope
- Making refresh-plugins respect `config.adapters.default`
- Adding `getSkillsDirectory()` to adapter interface
- Configurable target directory for `copyPluginSkillsToProject()`

### Out of Scope
- Changing `specweave init` (already sets `config.adapters.default`)
- Changing adapter detection logic in `AdapterLoader.detectTool()`
- Changing the `compilePlugin()` path (Plugin type compilation)
- Hook-based plugin installation

### Risks
- **Low**: Adding a method to `IAdapter` is backward-compatible since `AdapterBase` provides a default implementation
- **Low**: The `targetSkillsDir` parameter is optional with default behavior unchanged
- **Low**: Config read failure falls back to existing behavior (Claude CLI detection)

## Implementation Order

1. Add `getSkillsDirectory()` to `IAdapter` + `AdapterBase` + all 17 adapters (mechanical, parallelizable)
2. Add `targetSkillsDir` to `CopyPluginOptions` in `copyPluginSkillsToProject()`
3. Implement `resolveActiveAdapter()` in refresh-plugins.ts
4. Update `refreshPluginsCommand()` to use resolved adapter
5. Write tests
