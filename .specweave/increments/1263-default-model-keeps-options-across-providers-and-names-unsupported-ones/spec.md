# Default model keeps options across providers and names unsupported ones

## Problem

Anton asked (November 8, 2026) for one app-wide default model, with options such as Ultra Code and Fast, that every new project and new chat starts from. It already exists: Settings › General › New threads › Model (`defaultModelSelection`, environment scope, overridable per project). New chats (`useHandleNewThread`), new projects (null override inherits) and new coordinators (`resolveCoordinatorModelSelection` falls back to the scoped default) all read it.

The gap is in the row itself. Picking another provider or model calls `createModelSelection(instanceId, model)` with no options, so effort, Fast and Ultra Code are dropped silently. Nothing says that, for example, GitHub Copilot has no Ultra Code.

## Scope

In: carrying options across a provider or model change in the default-model row (effort mapped to the nearest level, booleans kept when the new model has them), a notice naming what was dropped or adjusted, and a line naming which of Effort, Fast mode and Ultra Code the chosen model lacks. Out: the chat composer's own model switch, worker lanes and task routing.

## Acceptance Criteria

- [ ] AC-01: Switching the default model keeps every option the new model supports; effort maps to the nearest level the new model offers.
- [ ] AC-02: Options the new model lacks are named in a toast (dropped or adjusted), never dropped silently.
- [ ] AC-03: The Model row names which of Effort, Fast mode and Ultra Code the chosen model does not support (e.g. Copilot: Ultra Code).
- [ ] AC-04: A headless check (headless: true) shows the row with the unsupported-options line.

## Approach

New `packages/shared/src/modelOptionCarry.ts`: `carryModelOptions(previous, previousDescriptors, nextDescriptors)` returns kept options plus dropped and adjusted labels; `missingCommonOptions(descriptors)` names the common options a model lacks. Effort reuses `effortLevel.ts` (`resolveEffort`). Codex "Fast" is the `serviceTier` select with a `fast`/`priority` choice. `ProjectDefaultsSettings.tsx` uses both. Rejected: a new separate app-wide setting, since `defaultModelSelection` already is that setting.

## Decisions

### Asked
- D-01 slot on the shared checkout → "Branch now" (user)
### Defaulted (change any before sw-do)
- D-02 keep the existing setting rather than add a second default → reuse `defaultModelSelection`
### Open
- none

## Tasks

### T-01 Carry options across a default model change
- AC: AC-01, AC-02 | Files: [packages/shared/src/modelOptionCarry.ts, packages/shared/src/modelOptionCarry.test.ts, packages/shared/package.json, apps/web/src/components/settings/ProjectDefaultsSettings.tsx] | Test: cd repositories/anton-abyzov/specwithcode-dev/packages/shared && ../../node_modules/.bin/vp test run src/modelOptionCarry.test.ts && cd ../../apps/web && ../../node_modules/.bin/vp test run src/components/settings/ProjectDefaultsSettings.test.tsx

### T-02 Name unsupported options on the Model row
- AC: AC-03, AC-04 | Files: [apps/web/src/components/settings/ProjectDefaultsSettings.tsx, apps/web/tests/default-model/verify.mjs] | Test: cd repositories/anton-abyzov/specwithcode-dev && test -f ~/.specwithcode/m4/evidence/default-model-options-20261108/receipt.json && grep -q "the row names what Copilot lacks" ~/.specwithcode/m4/evidence/default-model-options-20261108/receipt.json
