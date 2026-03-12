---
increment: 0516-remove-native-plugin-install
---

# Architecture Plan

## Decision

Remove the `claude-cli.ts` utility module and all call sites in `add.ts`. The file-extraction path (already present) becomes the sole install method for all agents including Claude Code.

## Files Changed

| File | Action |
|---|---|
| `src/utils/claude-cli.ts` | DELETE — 6 functions, all only consumed by add.ts |
| `src/utils/claude-cli.test.ts` | DELETE — tests for deleted module |
| `src/commands/add.ts` | MODIFY — remove 6 code sections |
| `src/commands/add.test.ts` | MODIFY — remove mocks and native install test blocks |

## Sections removed from add.ts

1. Import of claude-cli functions
2. `hasClaude` variable on uninstall path
3. Native uninstall call `uninstallNativePlugin()`
4. Step 1: native install block with marketplace registration loop
5. `tryNativeClaudeInstall()` function definition
6. `claudeNativeSuccess` branch — `extractionAgents = selectedAgents` always
7. `hasClaude && marketplaceRegistered` Claude manage hint
8. `gitUrl` extraction (only used for native install)
9. Misleading `--plugin-dir` native hint

## After removal

- `cleanPluginCache()` runs unconditionally (was gated on `!claudeNativeSuccess`)
- All agents including Claude Code go through extraction path
- Lockfile still updated per-install (unchanged)
