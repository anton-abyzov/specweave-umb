# Ultracode toggle for Claude models

## Problem

Claude Code now turns Ultracode on as its own session setting (`ultracode`), independent of effort; its composer reads "Opus 5.5 · Medium · Ultracode". SpecWithCode modeled Ultracode as an effort level, so it could not be combined with another effort, and on agent threads the workflow policy overwrote the per-thread choice with `mode === "automatic"`, so picking Ultracode did nothing in the default On request mode.

## Scope

In: a boolean Ultracode option for Claude models that support it (xhigh-capable), shown in the composer traits menu and the settings/coordinator pickers; the chip reads "Medium · Ultracode"; the server sends `settings.ultracode` merged with the workflow mode; legacy `effort: "ultracode"` selections keep running as Extra High plus Ultracode; MCP `effort: ultracode` maps to the same. Out: live `applyFlagSettings` switching without a query restart; reading `ultracodeAvailable` from the SDK (not typed in 0.3.276); manifest JSON edits.

## Acceptance Criteria

- [ ] AC-01: For Opus 5.5 (and other models with xhigh), the traits menu offers Ultracode On/Off separate from the effort list, and the composer chip reads "Medium · Ultracode" when on.
- [ ] AC-02: The thread's toggle reaches Claude Code as `settings.ultracode` with the chosen effort unchanged; Disabled workflow mode forces it off; unset follows the mode.
- [ ] AC-03: Saved selections with effort "ultracode" read and run as Extra High with Ultracode on; models without xhigh never get the toggle.

## Approach

Server: `withClaudeUltracodeToggle` (ClaudeModelCatalog.ts) moves the manifest's `ultracode` effort choice into a boolean descriptor in code, because installed builds read the manifest from main. Native discovery adds or removes it from `supportedEffortLevels`. `compileClaudeModelSelection` reads the boolean (legacy effort maps to xhigh + on) and `compileClaudeWorkflowPolicy` takes it as input: `mode !== "disabled" && (toggle ?? (launchUltracode || mode === "automatic"))`. Text generation never sends Ultracode. Shared: `getProviderOptionDescriptors` upgrades a legacy effort only when the model offers the toggle instead of the choice, so older servers are untouched. Web: TraitsPicker shows the toggle with a description and renders "· Ultracode" beside the effort so it does not collapse with details.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Explicit toggle wins over Automatic; Disabled always wins (reversible).
- D-02 No SQL migration; legacy values normalize on read (reversible).
### Open
- none

## Tasks

### T-01 Server toggle, policy merge and legacy mapping
- AC: AC-02, AC-03 | Files: repositories/anton-abyzov/specweave-studio/apps/server/src/claudeModelOptions.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/provider/ClaudeWorkflowPolicy.ts | Test: npx vp test run src/claudeModelOptions.test.ts src/provider/ClaudeWorkflowPolicy.test.ts src/provider/ClaudeNativeModels.test.ts src/orchestration-v2/Adapters/ClaudeAdapterV2.test.ts

### T-02 Composer toggle and chip
- AC: AC-01, AC-03 | Files: repositories/anton-abyzov/specweave-studio/apps/web/src/components/chat/TraitsPicker.tsx, repositories/anton-abyzov/specweave-studio/apps/web/tests/ultracode-toggle/verify.mjs | Test: node apps/web/tests/ultracode-toggle/verify.mjs (headless)

### T-03 Verify and close 1122
- AC: AC-01, AC-02, AC-03 | Files: none | Test: specweave verify 1122-ultracode-toggle-for-claude-models
