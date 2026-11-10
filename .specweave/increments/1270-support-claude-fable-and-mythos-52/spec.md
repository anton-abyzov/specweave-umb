# Support Claude Fable and Mythos 5.2

## Problem

Anthropic released Claude Fable 5.2 (`claude-fable-5-2`) on November 9, 2026. Mythos 5.2 is the same model; Anthropic offers it only to vetted organizations and publishes no public model ID for it. Fable 5.2 runs on Anton's subscription through Claude Code CLI 2.1.302: a headless `claude -p --model claude-fable-5-2` returned `ok` with a 1M context window. The CLI still logs `[claude-code:unrecognized_model]`, so it does not list the model at SDK init, and SpecWithCode does not offer 5.2 anywhere:

- The picker merges the models the CLI reports at init (`ClaudeProvider.ts`, `ClaudeNativeModels.ts`) with the bundled or remote `model-manifest.json`. Neither source contains 5.2. The lockfile pins `@anthropic-ai/claude-agent-sdk` at 0.3.276; 0.3.322, published November 9, knows the model.
- The Hardest tier and the Complex lane fall back to `tierModelFor`, which reads the literal `DEFAULT_PROVIDER_MODEL_TIERS.claudeAgent.frontier = "claude-fable-5-1"` (`packages/contracts/src/adversarialReview.ts:44`). The literal is used whenever the provider still lists 5.1, so a newer frontier model can never take over without a code change.
- The static Claude default `DEFAULT_MODEL_BY_PROVIDER` (`packages/contracts/src/model.ts:174`) and the manifest's `defaults.chat` both name 5.1.

## Scope

In:
- Fable 5.2 in the manifest, with effort low through max, ultracode, ultrathink, fast mode and a 200k/1M context window. 5.2 becomes the Claude chat default and frontier model, and 5.1 is marked legacy.
- Tier defaults follow the newest listed model of the same family, so a later Claude (or Muse) release takes over Hardest and Complex without a code edit.
- Native fallback labels for `fable` slugs on iOS and Android.
- The Settings > Providers update arrow works for Claude and Codex on macOS and Windows.

Out:
- Mythos 5.2, which has no public ID; a vetted account's CLI reports it at init and gets it automatically.
- Pricing: rates come live from LiteLLM by exact ID, including the fast multiplier, so there is no code edit.
- The SDK lockfile bump: on macOS the server runs the user's CLI, so updating Claude Code to 2.1.322 is what makes init list the model.
- A release, which goes through the "Release all platforms in 3 hours" thread.

## Acceptance Criteria

- [ ] AC-01: The bundled manifest lists `claude-fable-5-2` as the current Claude chat default, with fast mode, the 1M context option and effort low through max; `claude-fable-5-1` is legacy and the `fable` alias resolves to 5.2.
- [ ] AC-02: `tierModelFor(claude, "frontier")` returns `claude-fable-5-2` when the provider lists both 5.1 and 5.2, and still returns `claude-fable-5-1` when only 5.1 is listed. A user's own tier choice is never replaced.
- [ ] AC-04: On macOS, the Claude update arrow stages an update for a fleet release that holds only `@anthropic-ai/claude-code-darwin-arm64` (the October 9 provisioning layout), instead of showing "could not be verified for safe staging".
- [ ] AC-05: On Windows, Update Selected for Claude and Codex no longer fails with "Cannot verify that this installer is idle". The idle check lists processes through `Get-CimInstance Win32_Process` (PID, parent PID, command line), handles backslash paths, quoted `C:\Program Files\...` executables and `.exe`/`.cmd` names, and still reports a running CLI as in use with "Update anyway". This is verified on a Windows CI runner and a Windows build before release.
- [ ] AC-03: The running server's Claude provider catalog shows Claude Fable 5.2 as the default with Fast Mode, and a real turn on `claude-fable-5-2` completes.

## Approach

`model-manifest.json`: add a `fable-5-2` profile (the `fable-5` profile plus `fastMode`) and the model entry, bump `updatedAt`, move `defaults.chat` and `currentModels` to 5.2, and set 5.1 to legacy without the `fable` alias. No `minVersion`: CLI 2.1.302 already runs the ID.

`packages/shared/src/modelTiers.ts`: when the tier comes from the built-in default rather than the user, prefer the newest listed slug that has the same family stem and a trailing numeric version (`claude-fable-5-1` → `claude-fable-*`). IDs without a trailing version, such as `gpt-6-astra`, keep exact matching. The contract literals move to 5.2 as the offline fallback.

Rejected: a manifest `defaults.frontier` field. It needs a contracts field on `ServerProviderModel` and a larger PR while 1258 waits on the checkout.

Update arrow, macOS: `independentProviderMaintenance.ts` accepts a release whose owner `package.json` depends directly on the darwin-arm64 package with the matching version, in which case the version is read from that package. `stagedProviderUpdate.ts` then installs the full `@anthropic-ai/claude-code` package, as it does today. On November 9, the M4 was updated by hand with the same steps to `provider-releases/claude-2.1.322-vHpvGj`.

Update arrow, Windows: `assertProviderInstallerIdle` (`stagedProviderUpdate.ts:271`) rejects every `win32` request because it relies on `/bin/ps`, so Update has never worked on Windows since 1.0.75. Fix: a Windows lister using the same `Get-CimInstance Win32_Process` approach as `terminal/Manager.ts:863`, output as `pid ppid command` rows. `findProviderProcessesInUse` normalizes `\\` to `/` and parses a quoted argv0. If the lister fails, keep today's refusal.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: no `minVersion` on 5.2 → the model shows on CLI 2.1.302, which runs it (verified November 9, 2026).
- D-02: the SDK lockfile bump is out of this PR → keeps it small; the CLI update covers macOS.
### Open
- none

## Tasks

### T-01 Manifest, defaults and family-following tiers
- AC: AC-01, AC-02 | Files: apps/server/src/provider/model-manifest.json, packages/contracts/src/model.ts, packages/contracts/src/adversarialReview.ts, packages/shared/src/modelTiers.ts, packages/shared/src/modelTiers.test.ts, packages/shared/src/adversarialReview.test.ts, apps/web/src/components/settings/AdversarialReviewSettings.test.tsx, apps/ios/SWCKit/Sources/SWCSync/ThreadIdentity.swift, apps/android/sync/src/main/kotlin/com/specwithcode/sync/ThreadIdentity.kt, docs/studio/adversarial-review.md | Test: cd repositories/anton-abyzov/specwithcode-dev && pnpm vitest run packages/shared/src/modelTiers.test.ts packages/shared/src/adversarialReview.test.ts apps/server/src/provider

### T-03 Update arrow for binary-only fleet releases (macOS)
- AC: AC-04 | Files: apps/server/src/provider/independentProviderMaintenance.ts, apps/server/src/provider/independentProviderMaintenance.test.ts | Test: pnpm vitest run apps/server/src/provider/independentProviderMaintenance.test.ts apps/server/src/provider/providerMaintenance

### T-04 Windows installer-idle check
- AC: AC-05 | Files: apps/server/src/provider/stagedProviderUpdate.ts, apps/server/src/provider/stagedProviderUpdate.test.ts, apps/server/src/provider/providerMaintenanceRunner.test.ts | Test: pnpm vitest run apps/server/src/provider/stagedProviderUpdate.test.ts apps/server/src/provider/providerMaintenanceRunner.test.ts, plus the win32-only lister test on the Windows CI job and an installed Windows build check through the release thread

### T-02 Live check on the running server
- AC: AC-03 | Files: none | Test: headless catalog read from a dev server on the branch, plus `claude -p --model claude-fable-5-2`
