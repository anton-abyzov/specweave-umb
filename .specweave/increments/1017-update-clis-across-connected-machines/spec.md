# 1017 Update CLIs across connected machines

## Problem
The configured Codex CLI is a pinned fleet wrapper at version 0.162.1. Providers detects a newer release but disables the update action, leaving the user without a usable path. The existing fleet action updates all eligible providers immediately and hides individual eligibility and results.

## Scope
In: verified staged Codex npm ownership, side-by-side installation and atomic wrapper activation, selected CLI and explicit connected-machine selection through the existing update RPC, actionable unsupported cases, per-machine results and session safety.
Out: app/service updates, routing/model policy, grants, credentials, forced restarts, automatic schedules, arbitrary custom-wrapper execution, durable cross-restart fleet jobs.

## Acceptance Criteria
- [ ] AC-01: A verified staged Codex wrapper exposes an update action using its owning npm toolchain; the new version installs beside the old release and only a verified executable activates. Configured paths, old releases and authentication remain intact.
- [ ] AC-02: Homebrew, native, global npm and unknown/custom installations retain their own ownership boundaries; altered wrappers and ambiguous provenance fail closed with actionable guidance.
- [ ] AC-03: The selected provider action can explicitly include eligible connected machines using the existing providers:manage RPC and show selected machines, current/target versions, skip reasons and individual outcomes. No grants are widened.
- [ ] AC-04: An unsafe in-place update does not replace files under an active provider session. Nothing kills sessions or restarts the app/service. Side-by-side Codex updates preserve existing release files.
- [ ] AC-06: After release, the installed app provider update dialog receives concrete manual acceptance; live fleet execution is reported separately and uses only existing permissions.
- [ ] AC-05: Focused tests, relevant production builds, headless UI evidence and a fresh review pass. Live fleet verification limits and authoritative latest-version receipts are recorded; release owner receives the exact ready SHA.

## Approach
Extend the internal maintenance action with a staged Codex npm update descriptor, derived only from a strictly verified wrapper and its package/toolchain. In the runner, stage with the owning npm, verify the exact target and wrapper identity again, atomically switch the wrapper, and re-probe normally. Reuse ProviderUpdatesAction for both fleet and selected-provider entry points with explicit selection and bounded execution. Retain destination authorization. Check active sessions before in-place updates. Use an isolated app worktree at /Users/antonabyzov/.specwithcode/m4/worktrees/provider-cli-fleet-update; do not edit the shared checkout.

## Decisions
### Asked
- User explicitly requests selected CLI updates and an option for eligible connected machines.
### Defaulted
- Staged wrapper support starts with Codex, the reported installation. Unsupported wrappers remain manual with a specific reason.
- Fleet runs are bounded client-side batches; persistence across app closure is deferred and disclosed.
- Busy in-place installations return retry-when-idle guidance instead of draining or stopping sessions.
### Open
- none

## Tasks

### T-01 Implement proven installer and session-safe execution
- AC: AC-01, AC-02, AC-04 | Files: apps/server/src/provider/independentProviderMaintenance.ts, apps/server/src/provider/stagedProviderUpdate.ts, apps/server/src/provider/providerMaintenance.ts, apps/server/src/provider/providerMaintenanceRunner.ts, apps/server/src/provider/independentProviderMaintenance.test.ts, apps/server/src/provider/stagedProviderUpdate.test.ts, apps/server/src/provider/providerMaintenanceRunner.test.ts, apps/server/src/provider/providerMaintenance.test.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/provider/independentProviderMaintenance.test.ts apps/server/src/provider/stagedProviderUpdate.test.ts apps/server/src/provider/providerMaintenanceRunner.test.ts apps/server/src/provider/providerMaintenance.test.ts

### T-02 Extend existing fleet action and selected CLI entry
- AC: AC-03 | Files: apps/web/src/components/ProviderUpdatesAction.tsx, apps/web/src/components/ProviderUpdatesAction.logic.ts, apps/web/src/components/ProviderUpdatesAction.test.tsx, apps/web/src/components/settings/ProviderSettingsPanel.tsx, apps/web/src/components/settings/ProviderSettingsPanel.environment.test.tsx, apps/web/tests/provider-updates/main.tsx, apps/web/tests/provider-updates/mocks.tsx, apps/web/tests/provider-updates/vite.config.ts, apps/web/tests/provider-updates/index.html, apps/web/tests/provider-updates/fixture.css | Test: node node_modules/vite-plus/bin/vp test run apps/web/src/components/ProviderUpdatesAction.test.tsx apps/web/src/components/settings/ProviderSettingsPanel.environment.test.tsx

### T-03 Verify delivery and release readiness
- AC: AC-05 | Files: README.md, CHANGELOG.md, AGENTS.md, docs/user/updating.md, /Users/antonabyzov/.specwithcode/m4/evidence/provider-cli-fleet-update-1017/report.md | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/provider/stagedProviderUpdate.test.ts apps/web/src/components/ProviderUpdatesAction.test.tsx

### T-05 Repair introduced Effect-aware typecheck failures
- AC: AC-05 | Files: apps/server/src/provider/providerMaintenanceRunner.ts, apps/server/src/provider/providerMaintenanceRunner.test.ts | Test: bash scripts/studio-verify/typecheck-gate.sh --jobs 2 --out /Users/antonabyzov/.specwithcode/m4/evidence/provider-cli-fleet-update-1017/effect-repair/typecheck

### T-04 Verify and close 1017
- AC: AC-06 | Files: /Users/antonabyzov/.specwithcode/m4/evidence/provider-cli-fleet-update-1017/installed-acceptance.md | Test: specweave verify 1017

The repository requires concrete manual acceptance for new UI. T-04 follows release owner 1015's scheduled release; source fixtures and the live local CLI update do not prove installed app UI acceptance. No competing release or restart is authorized here.
