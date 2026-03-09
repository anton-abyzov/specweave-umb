---
increment: 0457-prevent-unwanted-agent-dotfolders
title: "Consent-First Plugin Auto-Loading"
generated_by: sw:test-aware-planner
test_mode: TDD
coverage_target: 90
by_user_story:
  US-SW-001: [T-001, T-002]
  US-SW-002: [T-003, T-004]
  US-SW-003: [T-005, T-006]
  US-SW-004: [T-007, T-008]
  US-VK-005: [T-009, T-010]
  US-SW-006: [T-011, T-012]
  US-SW-007: [T-013, T-014]
---

# Tasks: Consent-First Plugin Auto-Loading

## User Story: US-SW-001 - Default to Suggest-Only Mode

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Tasks**: 2 total, 0 completed

### T-001: Flip suggestOnly default in llm-plugin-detector.ts

**User Story**: US-SW-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Status**: [ ] pending

**Test Plan**:
- **Given** `readPluginAutoLoadConfig()` is called with no config file or a config with no `suggestOnly` field
- **When** the returned config object is inspected
- **Then** `suggestOnly` is `true`

- **Given** a config file with `suggestOnly: false`
- **When** `readPluginAutoLoadConfig()` is called
- **Then** `suggestOnly` is `false` (explicit opt-in preserved)

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/specweave/tests/unit/core/lazy-loading/llm-plugin-detector.test.ts`
   - `readPluginAutoLoadConfig_noConfig_defaultsSuggestOnlyTrue()`: no config file returns suggestOnly true
   - `readPluginAutoLoadConfig_noSuggestOnlyField_defaultsTrue()`: config without suggestOnly field defaults to true
   - `readPluginAutoLoadConfig_explicitFalse_keepsFalse()`: config with suggestOnly: false preserves it
   - **Coverage Target**: 95%

**Implementation**:
1. Open `repositories/anton-abyzov/specweave/src/core/lazy-loading/llm-plugin-detector.ts`
2. In `readPluginAutoLoadConfig()`, change the fallback default from `suggestOnly: false` to `suggestOnly: true`
3. Change the conditional from `suggestOnly: config.pluginAutoLoad.suggestOnly === true` to `suggestOnly: config.pluginAutoLoad.suggestOnly !== false` so absence of the field yields `true`
4. Run `npx vitest run tests/unit/core/lazy-loading/llm-plugin-detector.test.ts` to confirm red, then implement, then green

---

### T-002: Flip suggestOnly default in user-prompt-submit.sh

**User Story**: US-SW-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Status**: [ ] pending

**Test Plan**:
- **Given** `user-prompt-submit.sh` runs with no `suggestOnly` in config.json
- **When** `PLUGIN_SUGGEST_ONLY` is evaluated
- **Then** it equals `true`

- **Given** config.json has `"suggestOnly": false`
- **When** the hook reads the config
- **Then** `PLUGIN_SUGGEST_ONLY` is set to `false`

**Test Cases**:
1. **Manual (bash trace)**: `bash -x user-prompt-submit.sh` focused on lines ~359-397
   - Verify `PLUGIN_SUGGEST_ONLY=true` initial assignment at line ~359
   - Verify jq fallback `// true` at line ~375
   - Verify grep fallback only sets `PLUGIN_SUGGEST_ONLY=false` when `suggestOnly: false` found
   - **Coverage Target**: Manual gate (shell logic, not covered by Vitest)

**Implementation**:
1. Open `repositories/anton-abyzov/specweave/plugins/specweave/hooks/user-prompt-submit.sh`
2. Line ~359: change `PLUGIN_SUGGEST_ONLY=false` to `PLUGIN_SUGGEST_ONLY=true`
3. Line ~375: change `'.pluginAutoLoad.suggestOnly // false'` to `'.pluginAutoLoad.suggestOnly // true'`
4. Line ~376: set `PLUGIN_SUGGEST_ONLY=false` only when `SUGGEST_VALUE == "false"` (inverted — true is now default)
5. Line ~397: update grep fallback to match `suggestOnly: false` and set `PLUGIN_SUGGEST_ONLY=false` (invert logic)
6. Manually verify the three cases with bash traces

---

## User Story: US-SW-002 - Suggest-Only Recommendation Display

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Tasks**: 2 total, 0 completed

### T-003: Verify suggestion message format includes name, reason, and install command

**User Story**: US-SW-002
**Satisfies ACs**: AC-US2-01
**Status**: [ ] pending

**Test Plan**:
- **Given** a plugin is detected and `suggestOnly` is `true`
- **When** `formatHookOutput()` generates the suggestion message
- **Then** the output contains the plugin name, detection reason, and a copy-pasteable install command matching `npx vskill install --repo anton-abyzov/vskill --plugin <name> --agent claude-code`

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/specweave/tests/unit/core/lazy-loading/llm-plugin-detector.test.ts`
   - `formatHookOutput_suggestOnly_includesPluginName()`: output contains plugin name
   - `formatHookOutput_suggestOnly_includesInstallCommand()`: output contains exact install command pattern
   - `formatHookOutput_suggestOnly_includesReason()`: output contains detection reason
   - **Coverage Target**: 90%

**Implementation**:
1. Locate `formatHookOutput()` in `llm-plugin-detector.ts`
2. Confirm suggest-only branch produces output with all three required fields
3. If any field is missing, update the template string in the suggest-only branch
4. Add or update unit tests asserting all three fields are present in the output

---

### T-004: Enforce once-per-session dedup for plugin suggestions

**User Story**: US-SW-002
**Satisfies ACs**: AC-US2-02, AC-US2-03
**Status**: [ ] pending

**Test Plan**:
- **Given** a plugin suggestion was already emitted for `mobile` in this session
- **When** the hook detects `mobile` again in the same session
- **Then** no duplicate suggestion is shown

- **Given** a new session starts
- **When** the same plugin is detected
- **Then** the suggestion appears again

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/specweave/tests/unit/core/lazy-loading/llm-plugin-detector.test.ts`
   - `formatHookOutput_duplicatePlugin_suppressesSecondSuggestion()`: second call with same plugin produces no output for that plugin
   - `formatHookOutput_newSession_showsSuggestionAgain()`: session state reset allows suggestion to appear again
   - **Coverage Target**: 85%

**Implementation**:
1. Identify where session-scoped dedup is tracked (Set or temp file)
2. Confirm the dedup logic applies to the suggest-only path (not only the install path)
3. Add unit tests simulating two consecutive detections of the same plugin within one session

---

## User Story: US-SW-003 - LSP Plugin Consent Guard

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Tasks**: 2 total, 0 completed

### T-005: Add PLUGIN_SUGGEST_ONLY guard to LSP auto-install conditions

**User Story**: US-SW-003
**Satisfies ACs**: AC-US3-01, AC-US3-02
**Status**: [ ] pending

**Test Plan**:
- **Given** `PLUGIN_SUGGEST_ONLY=true`, `LSP_NEEDS_INSTALL=true`, `LSP_AUTO_INSTALL=true`
- **When** the LSP section of the hook executes
- **Then** the auto-install block is skipped and the suggest-setup path is followed

- **Given** `PLUGIN_SUGGEST_ONLY=false` and `LSP_AUTO_INSTALL=true`
- **When** the LSP section executes
- **Then** auto-install proceeds as before

**Test Cases**:
1. **Unit (TS)**: `repositories/anton-abyzov/specweave/tests/unit/core/lazy-loading/llm-plugin-detector.test.ts`
   - `lspGuard_suggestOnlyTrue_returnsRecommendation()`: LSP detection returns suggest path when suggestOnly true
   - `lspGuard_suggestOnlyFalse_returnsInstall()`: LSP detection returns install path when suggestOnly false
   - **Coverage Target**: 90%

2. **Manual (bash trace)**: Verify the guard fires correctly in the shell script at lines ~976 and ~985

**Implementation**:
1. Open `user-prompt-submit.sh`
2. Find the two LSP auto-install conditionals at lines ~976 and ~985
3. Add `&& [[ "$PLUGIN_SUGGEST_ONLY" != "true" ]]` to each condition
4. Confirm the existing suggest-setup path at line ~891 is reached when the guard fires
5. Add TS unit tests for the guarded LSP logic

---

### T-006: Verify LSP CLI fallback works without installed LSP plugin

**User Story**: US-SW-003
**Satisfies ACs**: AC-US3-03
**Status**: [ ] pending

**Test Plan**:
- **Given** `suggestOnly: true` and an LSP plugin was NOT auto-installed
- **When** the user runs `specweave lsp refs src/file.ts Symbol`
- **Then** the CLI degrades gracefully without crashing

**Test Cases**:
1. **Integration (manual)**: Run `specweave lsp refs` in a project without LSP plugin installed
   - Confirm no unhandled errors
   - Confirm a clear message or graceful fallback is returned
   - **Coverage Target**: Manual verification gate

**Implementation**:
1. No code change expected — existing CLI fallback path handles this
2. Manual smoke-test: run `specweave lsp refs` in a project without LSP plugin
3. Record output in this task's verification notes and mark complete

---

## User Story: US-SW-004 - TypeScript Types and Config Schema Update

**Linked ACs**: AC-US4-01, AC-US4-02, AC-US4-03
**Tasks**: 2 total, 0 completed

### T-007: Add suggestOnly to PluginAutoLoadConfig interface

**User Story**: US-SW-004
**Satisfies ACs**: AC-US4-01
**Status**: [ ] pending

**Test Plan**:
- **Given** the `PluginAutoLoadConfig` interface in `types.ts`
- **When** the TypeScript compiler processes it
- **Then** it includes `suggestOnly?: boolean` with JSDoc and `npx tsc --noEmit` exits 0

**Test Cases**:
1. **Type-check gate**: `npx tsc --noEmit` in `repositories/anton-abyzov/specweave/`
   - No type errors after adding the field
   - **Coverage Target**: 100% (compiler gate)

**Implementation**:
1. Open `repositories/anton-abyzov/specweave/src/core/config/types.ts`
2. Locate `PluginAutoLoadConfig` interface
3. Add: `/** When true (default), detected plugins are suggested instead of auto-installed. Set to false to restore auto-install behavior. */ suggestOnly?: boolean;`
4. Run `npx tsc --noEmit` to confirm no errors

---

### T-008: Add suggestOnly to specweave-config.schema.json

**User Story**: US-SW-004
**Satisfies ACs**: AC-US4-02, AC-US4-03
**Status**: [ ] pending

**Test Plan**:
- **Given** `specweave-config.schema.json` has `suggestOnly` under `pluginAutoLoad`
- **When** a config with `"suggestOnly": true` is validated
- **Then** validation passes

- **Given** a config with `"suggestOnly": 42` (non-boolean)
- **When** validated
- **Then** validation fails with a schema error

**Test Cases**:
1. **Unit (schema validation)**: Existing schema test harness
   - `schema_suggestOnlyBoolean_passes()`: valid boolean accepted
   - `schema_suggestOnlyNonBoolean_fails()`: non-boolean value rejected with clear error
   - **Coverage Target**: 90%

**Implementation**:
1. Open `repositories/anton-abyzov/specweave/src/core/schemas/specweave-config.schema.json`
2. Under `pluginAutoLoad` object schema, add: `"suggestOnly": { "type": "boolean", "default": true, "description": "When true (default), detected plugins are suggested instead of auto-installed." }`
3. Confirm `additionalProperties` does not block the new field
4. Run existing schema validation tests to confirm pass

---

## User Story: US-VK-005 - Clean Up Phantom Marketplace Entries

**Linked ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04
**Tasks**: 2 total, 0 completed

### T-009: Remove phantom plugins from vskill marketplace.json

**User Story**: US-VK-005
**Satisfies ACs**: AC-US5-01, AC-US5-02
**Status**: [ ] pending

**Test Plan**:
- **Given** `vskill/.claude-plugin/marketplace.json` after cleanup
- **When** the file is parsed
- **Then** it contains exactly 4 plugins: `mobile`, `skills`, `google-workspace`, `marketing`
- **Then** none of the 10 phantom names appear: `frontend`, `backend`, `testing`, `infra`, `payments`, `ml`, `kafka`, `confluent`, `security`, `blockchain`

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/` marketplace validation tests (if present)
   - `marketplace_onlyRealPlugins_listed()`: marketplace.json has exactly 4 entries
   - **Coverage Target**: 90%
2. **Manual**: `jq '[.[].name] | sort' repositories/anton-abyzov/vskill/.claude-plugin/marketplace.json` confirms 4 entries

**Implementation**:
1. Open `repositories/anton-abyzov/vskill/.claude-plugin/marketplace.json`
2. Remove entries for all 10 phantom plugins
3. Keep entries for: `mobile`, `skills`, `google-workspace`, `marketing`
4. Validate JSON is well-formed: `jq . repositories/anton-abyzov/vskill/.claude-plugin/marketplace.json`

---

### T-010: Remove phantom plugin references from specweave code and tests

**User Story**: US-VK-005
**Satisfies ACs**: AC-US5-02, AC-US5-03, AC-US5-04
**Status**: [ ] pending

**Test Plan**:
- **Given** `VSKILL_PLUGINS` in `llm-plugin-detector.ts` and `VSKILL_REPO_PLUGINS` in `user-prompt-submit.sh` are updated
- **When** each array is inspected
- **Then** only the 4 real plugins appear

- **Given** the detection prompt in `buildDetectionPrompt()`
- **When** a phantom category (e.g., `backend`) is referenced
- **Then** the prompt annotates it "[NOT YET AVAILABLE]"

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/specweave/tests/unit/core/lazy-loading/llm-plugin-detector.test.ts`
   - `vskillPlugins_onlyRealPlugins()`: VSKILL_PLUGINS contains only the 4 real plugin names
   - `vskillPlugins_noPhantoms()`: no phantom name appears in VSKILL_PLUGINS
   - `buildDetectionPrompt_phantomsMarkedUnavailable()`: prompt text contains "[NOT YET AVAILABLE]" for phantom categories
   - **Coverage Target**: 90%

2. **Unit**: `repositories/anton-abyzov/specweave/tests/plugin-validation/new-skills-validation.test.ts`
   - Update `VSKILL_PLUGINS_WITH_MANIFESTS` to the reduced set of 4 real plugins
   - All tests pass after update

**Implementation**:
1. In `llm-plugin-detector.ts`, update `VSKILL_PLUGINS` constant — remove 10 phantom + 3 unlisted (k8s, cost, docs); keep 4 real
2. In `buildDetectionPrompt()`, annotate phantom category descriptions with "[NOT YET AVAILABLE]"
3. In `user-prompt-submit.sh` line ~516, update `VSKILL_REPO_PLUGINS` to list only 4 real plugins
4. In `new-skills-validation.test.ts`, update `VSKILL_PLUGINS_WITH_MANIFESTS` to match reduced set
5. Run `npx vitest run` to confirm no regressions

---

## User Story: US-SW-006 - Update Hook Plugin Detection Logic

**Linked ACs**: AC-US6-01, AC-US6-02, AC-US6-03
**Tasks**: 2 total, 0 completed

### T-011: Verify hook uses suggest-only path as the default code branch

**User Story**: US-SW-006
**Satisfies ACs**: AC-US6-01, AC-US6-02
**Status**: [ ] pending

**Test Plan**:
- **Given** a project with no `suggestOnly` in config (default)
- **When** the hook detects a plugin via `llm-plugin-detector.ts`
- **Then** the caller reads `suggestOnly` before deciding install vs suggest
- **Then** the suggest path is chosen and no `--force --yes` flags appear in output

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/specweave/tests/unit/core/lazy-loading/llm-plugin-detector.test.ts`
   - `detectPlugins_defaultConfig_returnsSuggestOnlyTrue()`: detect() result has suggestOnly=true with no explicit config
   - `hookOutput_suggestOnlyTrue_noForceFlags()`: formatHookOutput output does not contain `--force` or `--yes`
   - **Coverage Target**: 90%

**Implementation**:
1. Confirm `llm-plugin-detector.ts` returns `suggestOnly` in its output object from `readPluginAutoLoadConfig()`
2. Trace the code path from detection to output and confirm no install flags leak into the suggest path
3. Add unit tests asserting the flag check happens before install and output contains no force flags

---

### T-012: Verify VSKILL_REPO_PLUGINS in hook matches actual plugin directories

**User Story**: US-SW-006
**Satisfies ACs**: AC-US6-03
**Status**: [ ] pending

**Test Plan**:
- **Given** `VSKILL_REPO_PLUGINS` in `user-prompt-submit.sh` after T-010 update
- **When** compared against actual directories in `repositories/anton-abyzov/vskill/plugins/`
- **Then** every entry has a corresponding directory on disk and no phantom names remain

**Test Cases**:
1. **Manual verification**: `ls repositories/anton-abyzov/vskill/plugins/` output matches updated `VSKILL_REPO_PLUGINS` list
   - **Coverage Target**: Manual gate

**Implementation**:
1. After T-010, cross-reference `VSKILL_REPO_PLUGINS` against `ls repositories/anton-abyzov/vskill/plugins/`
2. If any discrepancy remains, fix `VSKILL_REPO_PLUGINS` in `user-prompt-submit.sh`
3. This is a verification step after T-010 — mark complete once alignment is confirmed

---

## User Story: US-SW-007 - Test Suite Updates

**Linked ACs**: AC-US7-01, AC-US7-02, AC-US7-03
**Tasks**: 2 total, 0 completed

### T-013: Flip ~14 existing assertions from suggestOnly: false to suggestOnly: true

**User Story**: US-SW-007
**Satisfies ACs**: AC-US7-01, AC-US7-03
**Status**: [ ] pending

**Test Plan**:
- **Given** the updated `llm-plugin-detector.ts` defaults to `suggestOnly: true`
- **When** existing unit tests that assert `suggestOnly: false` run after T-001
- **Then** they fail (red) — the assertion flip makes them green

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/specweave/tests/unit/core/lazy-loading/llm-plugin-detector.test.ts`
   - All ~14 assertions previously expecting `suggestOnly: false` now expect `suggestOnly: true`
   - `VSKILL_PLUGINS.length` assertion updated to match reduced array count after T-010
   - Plugin containment assertions updated to remove phantom plugin names
   - Full suite: `npx vitest run` exits 0
   - **Coverage Target**: 95%

**Implementation**:
1. Run `npx vitest run tests/unit/core/lazy-loading/llm-plugin-detector.test.ts` after T-001 to identify failing tests
2. For each failing assertion: change `expect(result.suggestOnly).toBe(false)` to `expect(result.suggestOnly).toBe(true)`
3. Update array length and membership assertions after T-010
4. Run full unit suite and confirm zero regressions

---

### T-014: Add new consent-flow tests (suggestion format, dedup, opt-out, LSP guard)

**User Story**: US-SW-007
**Satisfies ACs**: AC-US7-02, AC-US7-03
**Status**: [ ] pending

**Test Plan**:
- **Given** the new consent-first behavior is implemented across T-001 through T-012
- **When** new test cases are added
- **Then** all four consent-flow scenarios are covered and `npx vitest run` exits 0

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/specweave/tests/unit/core/lazy-loading/llm-plugin-detector.test.ts`
   - `suggestion_format_includesNameReasonInstallCommand()`: suggestion output has all 3 required fields
   - `suggestion_dedup_suppressesDuplicate()`: same plugin detected twice in one session shows suggestion once
   - `suggestOnly_false_explicitOptOut_autoInstalls()`: with suggestOnly=false, output follows install path
   - `lsp_consent_suggestOnlyTrue_returnsRecommendation()`: LSP path follows suggest branch when suggestOnly=true
   - Full suite: `npx vitest run` exits 0
   - **Coverage Target**: 90%

**Implementation**:
1. Write the 4 new test cases in `llm-plugin-detector.test.ts`
2. Run each individually: confirm red before implementation, green after
3. Run `npx vitest run` — must exit 0 with no regressions
