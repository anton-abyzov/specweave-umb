# Implementation Plan: Consent-First Plugin Auto-Loading

## Overview

This is a surgical change to the existing plugin auto-loading pipeline. The `suggestOnly` mechanism already works end-to-end -- the problem is that it defaults to `false` (auto-install), and the LSP auto-install path ignores it entirely. The fix is three-fold:

1. Flip the `suggestOnly` default from `false` to `true` in both the shell hook and the TypeScript detector
2. Gate the LSP auto-install code path behind the same `suggestOnly` check
3. Remove phantom plugin entries from the vskill marketplace that reference non-existent directories

No new components, no new abstractions, no new data models. This is a default-flip plus a missing guard plus data cleanup.

## Architecture

### Change Map

```
specweave repo:
  src/core/lazy-loading/llm-plugin-detector.ts
    - readPluginAutoLoadConfig(): default suggestOnly false -> true
    - VSKILL_PLUGINS array: remove 8 phantom entries (keep 4 real + 3 specweave-only)
    - Detection prompt catalog: mark removed plugins as "not yet available"

  src/core/config/types.ts
    - PluginAutoLoadConfig interface: add suggestOnly?: boolean field

  src/core/schemas/specweave-config.schema.json
    - pluginAutoLoad object: add suggestOnly boolean property, default: true

  plugins/specweave/hooks/user-prompt-submit.sh
    - Line 359: PLUGIN_SUGGEST_ONLY default false -> true
    - Line 375: jq fallback default false -> true
    - Line 397: grep fallback: match suggestOnly true -> match false (invert)
    - LSP AUTO-INSTALL section (~line 976-1030): wrap with PLUGIN_SUGGEST_ONLY guard
    - VSKILL_REPO_PLUGINS line 516: remove phantom plugin names

  tests/unit/core/lazy-loading/llm-plugin-detector.test.ts
    - ~14 assertions: flip expected suggestOnly from false to true
    - New tests: LSP consent guard, suggestion dedup, suggestion display format

vskill repo:
  .claude-plugin/marketplace.json
    - Remove 8 phantom entries, keep 4 real (mobile, skills, google-workspace, marketing)
```

### Decision: Default Flip vs Migration

The spec calls for `suggestOnly: true` as the default. Two approaches considered:

**Option A: Hard default flip (SELECTED)**
- Change default in code from `false` to `true`
- All existing projects immediately get consent-first behavior
- Users who want auto-install add `"suggestOnly": false` to config

**Option B: Migration with version gate**
- Only apply new default to projects created after version X
- Existing projects keep old behavior

Option A is selected because:
- The spec explicitly states "All existing projects get the new suggestOnly: true default immediately"
- No migration needed -- the default flip IS the mechanism
- Users who deliberately want auto-install are a small minority and can opt in

### Decision: LSP Consent Guard Placement

The LSP auto-install code runs independently from the plugin auto-install code. Two guard strategies:

**Option A: Single PLUGIN_SUGGEST_ONLY check at the top of the LSP section (SELECTED)**
- At line ~976 where `LSP_NEEDS_INSTALL` and `LSP_AUTO_INSTALL` are checked, add `PLUGIN_SUGGEST_ONLY != true` as an additional condition
- When `PLUGIN_SUGGEST_ONLY == true`, fall through to the existing "suggest setup" path (line ~891) which already shows a recommendation message
- Minimal code change, reuses existing suggest path

**Option B: Duplicate the suggest-only message format inside the LSP section**
- More code, separate suggestion formatting for LSP
- Unnecessary since the existing suggest-setup path at line ~891 already handles the recommend-instead-of-install case

Option A is selected. The existing LSP code already has two branches:
1. `LSP_AUTO_INSTALL != true` -> suggest `specweave lsp setup` (line 891)
2. `LSP_AUTO_INSTALL == true` -> auto-install plugins (line 976)

The fix: when `PLUGIN_SUGGEST_ONLY == true`, force the suggest path regardless of `LSP_AUTO_INSTALL`. This means modifying the condition at line 976 from:
```bash
if [[ "$LSP_NEEDS_INSTALL" == "true" ]] && [[ "$LSP_AUTO_INSTALL" == "true" ]]; then
```
to:
```bash
if [[ "$LSP_NEEDS_INSTALL" == "true" ]] && [[ "$LSP_AUTO_INSTALL" == "true" ]] && [[ "$PLUGIN_SUGGEST_ONLY" != "true" ]]; then
```

This appears twice (lines 976 and 985). Both need the guard.

### Decision: Phantom Plugin Handling in Detection Prompt

The spec (AC-US5-03) says phantom plugin names in the LLM detection prompt should be marked as "not yet available" rather than completely removed. This prevents the LLM from suggesting them while keeping awareness.

The VSKILL_PLUGINS TypeScript array and VSKILL_REPO_PLUGINS shell variable will have phantoms removed (they control installation). But the detection prompt catalog text (inside `buildDetectionPrompt()`) will annotate phantoms:
```
frontend: React, Vue, Angular, Next.js, ...
backend: [NOT YET AVAILABLE] Java, Spring Boot, Rust, ...
```

This keeps the LLM from suggesting installation of non-existent plugins while preserving the mapping knowledge for when those plugins are created later.

### Decision: Which Plugins Are Real vs Phantom

Actual plugin directories on disk in `vskill/plugins/`:
- `mobile/`
- `skills/`
- `google-workspace/`
- `marketing/`

Phantom entries (declared in marketplace.json and code but no directory on disk):
- `frontend`, `backend`, `testing`, `infra`, `payments`, `ml`, `kafka`, `confluent`, `security`, `blockchain`

Plus three entries in VSKILL_PLUGINS that are not in marketplace.json at all:
- `k8s`, `cost`, `docs`

All 13 phantom/non-existent entries get removed from the installation arrays. The 4 real entries remain.

## Technology Stack

No new dependencies. Changes span:
- **Shell (bash)**: `user-prompt-submit.sh` hook
- **TypeScript**: `llm-plugin-detector.ts`, `types.ts`
- **JSON Schema**: `specweave-config.schema.json`
- **JSON**: `marketplace.json`
- **Test Framework**: Vitest

## Implementation Phases

### Phase 1: Type & Schema Updates (specweave)

1. Add `suggestOnly?: boolean` to `PluginAutoLoadConfig` in `types.ts` with JSDoc
2. Add `suggestOnly` boolean property to `specweave-config.schema.json` under `pluginAutoLoad`, with `default: true` and description
3. Update `additionalProperties: false` to allow the new field

### Phase 2: Default Flip (specweave)

4. In `llm-plugin-detector.ts` `readPluginAutoLoadConfig()`:
   - Change `suggestOnly: false` default to `suggestOnly: true` (line 95)
   - Change `suggestOnly: config.pluginAutoLoad.suggestOnly === true` to `suggestOnly: config.pluginAutoLoad.suggestOnly !== false` (line 114) -- this makes the default `true` unless explicitly set to `false`

5. In `user-prompt-submit.sh`:
   - Change `PLUGIN_SUGGEST_ONLY=false` to `PLUGIN_SUGGEST_ONLY=true` (line 359)
   - Change jq default: `'.pluginAutoLoad.suggestOnly // false'` to `'.pluginAutoLoad.suggestOnly // true'` (line 375)
   - Flip the jq result check: `[[ "$SUGGEST_VALUE" == "true" ]]` becomes `[[ "$SUGGEST_VALUE" == "false" ]] && PLUGIN_SUGGEST_ONLY=false` (line 376)
   - Update grep fallback: match `suggestOnly: false` to set `PLUGIN_SUGGEST_ONLY=false` (line 397, invert logic)

### Phase 3: LSP Consent Guard (specweave)

6. In `user-prompt-submit.sh`, add `PLUGIN_SUGGEST_ONLY` check to the two LSP auto-install conditions:
   - Line 976: add `&& [[ "$PLUGIN_SUGGEST_ONLY" != "true" ]]`
   - Line 985: add `&& [[ "$PLUGIN_SUGGEST_ONLY" != "true" ]]`

### Phase 4: Phantom Cleanup (specweave + vskill)

7. In `llm-plugin-detector.ts`:
   - Remove phantom entries from `VSKILL_PLUGINS` array (keep only: `mobile`, `skills`, `google-workspace`, `marketing`)
   - Note: `google-workspace` and `marketing` are not currently in the array but exist on disk -- add them if appropriate, or just keep the 4 that exist
   - Update `buildDetectionPrompt()` to mark phantom plugins as "[NOT YET AVAILABLE]" in the catalog text

8. In `user-prompt-submit.sh`:
   - Update `VSKILL_REPO_PLUGINS` (line 516) to only list real plugins

9. In `vskill/.claude-plugin/marketplace.json`:
   - Remove all phantom plugin entries, keep only: `mobile`, `skills`, `google-workspace`, `marketing`

10. In `specweave/tests/plugin-validation/new-skills-validation.test.ts`:
    - Update `VSKILL_PLUGINS_WITH_MANIFESTS` array to match the reduced set

### Phase 5: Test Updates (specweave)

11. In `llm-plugin-detector.test.ts`:
    - Flip ~14 assertions from `suggestOnly: false` to `suggestOnly: true`
    - Update `VSKILL_PLUGINS.length` assertion from `15` to match new count
    - Update plugin containment assertions to remove phantom plugins
    - Add new tests:
      - Suggestion display format includes plugin name, reason, install command
      - Once-per-session dedup (formatHookOutput with repeated plugins)
      - Explicit `suggestOnly: false` still enables auto-install
      - LSP guard: when suggestOnly is true, LSP follows suggest path

## Testing Strategy

### Unit Tests (Vitest)
- **Default behavior tests**: All assertions that check default `suggestOnly` value flip from `false` to `true`
- **Explicit opt-out**: `suggestOnly: false` in config still enables auto-install
- **VSKILL_PLUGINS**: Array length and membership tests updated for reduced set
- **formatHookOutput**: suggestOnly mode produces correct suggestion format
- **New tests**: LSP consent guard logic (mocked shell behavior in TS where applicable)

### Integration (Manual)
- Fresh project (no config): plugin detected -> suggestion shown, NOT installed
- Project with `suggestOnly: false`: plugin detected -> auto-installed
- LSP detection with default config: language detected -> suggestion shown for setup, NOT auto-installed
- LSP detection with `suggestOnly: false` and `lsp.autoInstallPlugins: true`: auto-installs as before

## Technical Challenges

### Challenge 1: Synchronized Defaults Across Shell and TypeScript
The default must be consistent between `user-prompt-submit.sh` (bash) and `llm-plugin-detector.ts` (TypeScript). Both read from `config.json` but have independent default values.

**Solution**: Both are changed in this increment. The TypeScript code uses `suggestOnly !== false` (defaults to true), and the shell uses `PLUGIN_SUGGEST_ONLY=true` as the initial value. Both only flip to `false` when config explicitly says `false`.

**Risk**: Low. Both code paths are well-tested and the change is symmetric.

### Challenge 2: Phantom Plugin References in Tests
Multiple test files reference phantom plugins by name. Removing them from the constant arrays will break containment assertions.

**Solution**: Update all test assertions that reference phantom plugins. The `new-skills-validation.test.ts` and `llm-plugin-detector.test.ts` files need plugin list updates.

**Risk**: Low. Straightforward find-and-replace with test runs to verify.

### Challenge 3: Detection Prompt Accuracy After Phantom Removal
The LLM detection prompt catalogs phantom plugins with their technology keywords. Removing them entirely could cause the LLM to stop recognizing those technologies.

**Solution**: Per AC-US5-03, mark phantoms as "[NOT YET AVAILABLE]" in the prompt text rather than removing them. The LLM will see the technology mapping but know not to suggest installation.

**Risk**: Medium. The LLM might still occasionally suggest unavailable plugins. Mitigation: the suggestion message will only list plugins that exist in the `VSKILL_PLUGINS` array, so even if the LLM returns a phantom name, it will be filtered out before display.

## Cross-Repo Coordination

Changes span two repos in the umbrella:
1. `repositories/anton-abyzov/specweave/` -- all code changes (US-SW-001 through US-SW-004, US-SW-006, US-SW-007)
2. `repositories/anton-abyzov/vskill/` -- marketplace.json cleanup only (US-VK-005)

Both repos are in the umbrella. Changes should be committed to each repo independently, then the umbrella synced.

## No Domain Skills Needed

This increment is pure infrastructure/tooling work (shell scripts, TypeScript utilities, JSON config). No frontend, backend, or other domain skills are required.
