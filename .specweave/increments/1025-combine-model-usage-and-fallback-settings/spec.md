# Combine model usage and fallback settings

Linked to [1005](../1005-readable-thread-row-fallback-badge/spec.md), which owns the fallback suffix in rows and composers.

## Problem

The October 23 follow-up (five screenshots in this thread) names four faults:

- The coordinator composer shows a separate "18% left" usage chip whose "Limits by machine" popover only extends the usage the model picker already shows.
- A thread on a fallback sometimes shows no fallback at all. Cause: both the shell projection (`ProjectionStore` SQL) and the detail projection (`limitFallbackPairing`) compared only the provider instance, so a fallback to another model on the same sign-in (Codex GPT-6.1-Sol to GPT-6-Astra) was invisible.
- The fallback and Unplanned pills crowd the meta line ("Fallback for Claude Op…", "Unplanned").
- Project settings split one idea across two places: the model defaults and "Also served by" sit at the top, while the usage-limit rules (When a provider runs out, Fallback order, Other machines, Try first) sit in a separate "Usage limits" section further down.

## Scope

In:

- Fallback visibility for a fallback on the same provider.
- A glyph for fallback and one for Unplanned, each with a hover/focus explanation and an accessible name.
- Machine limits inside the coordinator's model picker.
- One "When a model runs out" card directly under the coordinator and thread model pickers in project settings.

Out:

- Routing, billing and saved preferences: no setting key, default or meaning changes.
- The global Settings page layout.
- The backend hang and provider-error work (owned by the fallback credits thread).

## Acceptance Criteria

- [x] AC-01: A thread whose limit continuation runs another model on the same provider instance shows `kind: "fallback"` in both the shell and the detail projection. The same model under a variant slug (`[1m]`) does not.
- [x] AC-02: In rows and composers the fallback is a 14px amber detour glyph with no words. Its tooltip and accessible name name the pick and the reason, and the composer trigger does not mute it.
- [x] AC-03: Unplanned rows show a 14px muted `</>` glyph instead of the text pill (informational tone, per #624). The header filter shows the same glyph. Hover and focus give "No increment / Changed code without an increment. Increments are recommended, not required.", and a screen reader hears "No increment: changed code without an increment". On touch, the thread's plan bar says "No increment".
- [x] AC-04: The coordinator composer has no separate usage chip. The model picker's footer offers "Limits by machine", which swaps the list for every machine's limits and has a Models back action and links to All limits and This project's tokens. Where no picker can show (no provider available on the host), a "Limits by machine" button opens the same panel.
- [x] AC-05: Project settings > General shows, in order: coordinator model, thread model, then one "When a model runs out" card. The card holds Also served by, When a provider runs out, Fallback order, Other machines, Try first and the remaining rules, followed by the recovery checkbox and then Worker machine. Setting keys and search row ids are unchanged; search finds "When a model runs out" and still matches "usage limits".
- [ ] AC-06: Merged to main, released, and visible in the installed desktop app.

## Approach

- `packages/shared/src/threadModelIdentity.ts`: `sameRunModel` (instance plus base slug). The `fallback_pairing_json` subquery in `ProjectionStore.ts` mirrors it with inlined `CASE instr(...,'[')` expressions.
- `ModelStateTag` renders `FallbackGlyph` (with `text-current`) without words for a fallback.
- `UnplannedThreads.tsx`: `UnplannedGlyph`, plus the chip with a `Tip` and sr-only text.
- `ProviderModelPicker` gains `secondaryView`, and `ModelPickerContent` gains a stacked footer action.
- `ProjectUsageIndicator.tsx` replaces the chip with `MachineLimitsPanel` and `MachineLimitsButton`. `CoordinatorModelPicker` passes them.
- `ProjectWorkspaceSettings`: one `SettingsSection id="project-provider-limits"` wrapping `RecommendedModelProviders` and `ProviderLimitSettings`.

Rejected alternatives:

- A nested popover inside the picker: focus and outside-click conflicts.
- Moving the usage-limit rules out of the shared `ProviderLimitSettings`: global Settings still uses it.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: The fallback and Unplanned states show a glyph alone at every width, with the words in the tooltip and accessible name. This follows the user's "replaced with a beautiful icon".
- D-02: The "has room again" line shows only when switching back is possible. While the limit holds, the picker suffix and header carry the fact.
### Open
- none

## Tasks

### T-01 Same-provider fallback visibility
- AC: AC-01 | Files: packages/shared/src/threadModelIdentity.ts, packages/shared/src/threadModelIdentity.test.ts, apps/server/src/orchestration-v2/ProjectionStore.ts, apps/server/src/orchestration-v2/ProjectionStore.modelIdentity.test.ts | Test: vp test run packages/shared/src/threadModelIdentity.test.ts apps/server/src/orchestration-v2/ProjectionStore.modelIdentity.test.ts

### T-02 Fallback and Unplanned glyphs
- AC: AC-02, AC-03 | Files: apps/web/src/components/chat/FallbackGlyph.tsx, apps/web/src/components/chat/ModelStateTag.tsx, apps/web/src/components/studio/shell/UnplannedThreads.tsx, apps/web/src/components/studio/shell/shell.css, apps/web/tests/thread-row-meta, apps/web/tests/fallback-composer | Test: node apps/web/tests/thread-row-meta/verify.mjs and node apps/web/tests/fallback-composer/verify.mjs (headless)

### T-03 Limits in the model picker
- AC: AC-04 | Files: apps/web/src/components/chat/ProviderModelPicker.tsx, apps/web/src/components/chat/ModelPickerContent.tsx, apps/web/src/components/studio/shell/ProjectUsageIndicator.tsx, apps/web/src/components/studio/shell/CoordinatorModelPicker.tsx, apps/web/src/components/studio/ProjectWorkspaceSurface.tsx | Test: vp test run src/components/studio/shell/CoordinatorModelPicker.test.tsx src/components/studio/shell/ProjectUsageIndicator.test.tsx

### T-04 One fallback card under the model defaults
- AC: AC-05 | Files: apps/web/src/components/studio/ProjectWorkspaceSettings.tsx, apps/web/src/components/studio/projectSettingsSearch.logic.ts, apps/web/src/components/settings/RecommendedModelProviders.tsx | Test: vp test run src/components/studio/ProjectWorkspaceSettings.test.tsx

### T-05 Merge, release, verify installed
- AC: AC-06 | Files: /Users/antonabyzov/.specwithcode/m4/evidence/thread-row-fallback-badge/after2 | Test: CI green, release published, installed app readback and screenshot

### T-06 Verify and close 1025
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06 | Files: .specweave/increments/1025-combine-model-usage-and-fallback-settings | Test: specweave verify and a fresh-context review
