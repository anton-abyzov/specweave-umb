# Cursor support and settings design

## Problem

Providers settings mixes account setup, model choices and runtime paths in nested groups. Provider names truncate. Cursor is absent from the model picker on M4: the live catalog reports disabled, executable unavailable and zero models. Current source already uses the official Cursor SDK; disabled snapshots label installed false, so the generic executable diagnostic needs interpretation rather than a CLI-install assumption.

## Scope

In: verified Cursor integration and licensing explanation; supported setup/discovery copy; shared settings hierarchy, readable provider names, progressive disclosure for runtime and environment variables; headless responsive light/dark evidence. Out: purchases, sign-in, credential changes, paid provider turns, upstream orchestrator adoption, independent releases or restarts.

## Acceptance Criteria

- [ ] AC-01: Cursor guidance states the actual SDK/auth/model-discovery path and accurately explains the current disabled zero-model state, with official sources and no mandatory personal Pro claim unsupported by evidence.
- [ ] AC-02: Provider navigation shows full readable names, keeping both Copilot entries distinct and adjacent; machine/account scope stays explicit.
- [ ] AC-03: Shared settings components establish a consistent SpecWithCode hierarchy across sections; advanced runtime/environment fields collapse without losing editing or search navigation.
- [ ] AC-04: Focused checks and saved headless light/dark desktop/narrow screenshots verify navigation, disclosure, editing and scope behavior; fresh review and exact-head CI are recorded.
- [ ] AC-05: Sole release owner receives the reviewed commit and acceptance recipe; installed proof is recorded separately and closure waits for required installed acceptance.

## Approach

Read current owners and provider catalog first. Work in an app-bound isolated checkout. Audit the Cursor SDK driver, provider catalog and authentication UI before any backend change. Use shared settings layout, group and dialog primitives for the overall hierarchy, then provider panel/card presentation for readable navigation and advanced disclosure. Keep behavior and semantic theme tokens. Produce a source-linked research receipt and compare before/after screenshots. Merge only after focused checks and independent review; release/install remains with the sole owner.

## Decisions

### Asked
- none

### Defaulted (change any before sw-do)
- D-01: Interpret personal Pro wording as a request to verify requirements, not permission to purchase.
- D-02: Retain existing typography and semantic theme palette; use hierarchy, spacing and disclosure to establish the app's style.
- D-03: Preserve account configuration and provider enabled state. Demonstrate setup with synthetic fixtures.

### Open
- none; app binding verified at `2e95e09ae3f681aac81930edde0c22109e2723a8` on October 24, 2026.

## Presentation contract, October 24, 2026

1031 approved presentation changes to the listed files. The final proposal at `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1031-simplify-settings-across-machines/reports/proposal.md` was reconciled on October 24, 2026: 1009 remains presentation-only; stages S1-S6 own navigation/store consolidation, and "All my machines" waits for S4. `SettingsDialog.tsx` is held for 1029 PR #642; do not edit it. No persistence, defaults, model-lane moves or backend changes. Preserve #663, #637 and other owners' files.

Use one shared `reach` prop on rows/sections: "This device", "This machine" (with its name), "All connected machines", "This project". Providers and model lanes write the selected machine. Favorites, visibility and ordering are device-local, keyed by provider instance id. Custom models belong to the selected machine.

Design: a calm inspector with a readable provider rail and one selected account editor. Retain the app's sans typography and semantic palettes: light canvas #fafafa, surface #ffffff, ink #27272a, divider #e4e4e7; dark canvas #0a0a0a, ink #f5f5f5. These are reference values, not new hard-coded CSS colors. Section titles carry stronger weight; reach sits beside inheritance, wraps on narrow screens and never substitutes for account identity. Compact controls align in the existing two-column row grid. Runtime paths and environment variables use explicit disclosure, leaving account setup visible.

Critique: avoid a new card around every field and decorative badges. Keep separators for editing groups, reserve the accent for selected providers and focus, and show full provider names rather than widening every control. Both Copilot entries remain separate and adjacent. Search jumps must open collapsed content before focus.

## Tasks

### T-01 Verify Cursor requirements and discovery presentation
- AC: AC-01 | Files: repositories/anton-abyzov/specweave-studio/apps/web/src/components/settings/providerDriverMeta.ts, repositories/anton-abyzov/specweave-studio/apps/web/src/components/settings/ProviderInstanceCard.tsx | Test: node node_modules/vite-plus/bin/vp test run apps/web/src/components/settings/ProviderInstanceCard.test.ts apps/server/src/provider/CursorProvider.test.ts apps/server/src/provider/CursorSdkCatalog.test.ts

### T-02 Unify settings hierarchy and provider presentation
- AC: AC-02, AC-03 | Files: repositories/anton-abyzov/specweave-studio/apps/web/src/components/settings/settingsLayout.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/settings/SettingsGroup.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/settings/ProviderSettingsPanel.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/settings/ProviderInstanceCard.tsx | Test: node node_modules/vite-plus/bin/vp test run apps/web/src/components/settings/settingsLayout.test.tsx apps/web/src/components/settings/ProviderSettingsPanel.environment.test.tsx

### T-03 Capture responsive evidence and deliver reviewed change
- AC: AC-04, AC-05 | Files: repositories/anton-abyzov/specweave-studio/apps/web/tests/settings-design, repositories/anton-abyzov/specweave-studio/scripts/studio-verify/settings-design.mjs | Test: PWDEBUG=0 PLAYWRIGHT_HTML_OPEN=never node scripts/studio-verify/settings-design.mjs

### T-04 Verify and close 1009
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: .specweave/increments/1009-cursor-support-and-settings-design/spec.md | Test: specweave verify 1009-cursor-support-and-settings-design


### T-05 Align presentation with final 1031 reach contract
- AC: AC-02, AC-03, AC-04 | Files: repositories/anton-abyzov/specweave-studio/apps/web/src/components/settings/settingsLayout.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/settings/ProviderSettingsPanel.tsx, repositories/anton-abyzov/specweave-studio/apps/web/tests/settings-design | Test: node node_modules/vite-plus/bin/vp test run apps/web/tests/settings-design/reach.test.tsx apps/web/src/components/settings/ProviderSettingsPanel.environment.test.tsx

Use settingsScopeEnvironmentLabel for selected-machine names. Leave unknown machine reach unlabeled. Keep SettingsScopeSentence and settingsScopeAxis unchanged; note their vocabulary mismatch for S1. Verify and close 1009 after delivery and installed gates.
