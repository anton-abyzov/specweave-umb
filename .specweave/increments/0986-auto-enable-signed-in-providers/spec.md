# Auto-enable signed-in providers

## Problem

SpecWithCode checks install and sign-in only for providers that are on. Grok, OpenCode, Cursor, Pi and Antigravity start off and are never probed, so a CLI that is installed and signed in shows "Disabled". The only automatic turn-on is chat history (`restoreUsedProviders`). Proposal: /mnt/project-files/provider-auto-discovery.md (slice 1).

## Scope

In: background discovery at server startup for Grok and OpenCode; turning on the ones that are installed and signed in when the user never chose; a "Turned on automatically · Undo" notice on the provider card. Out: Rescan button, Pi, Cursor, Copilot/Gemini, wizard changes, SpecWeave init/doctor, vskill (later slices).

## Acceptance Criteria

- [ ] AC-01: On startup, Grok and OpenCode are probed only when settings.json never recorded a choice for them and chat history never used them; the probe runs `--version` plus `grok models` / `opencode auth list` with stdin closed, CI=1, BROWSER=/usr/bin/false and hard timeouts, and reads no credential file.
- [ ] AC-02: A probed provider that is installed and signed in is turned on and recorded in `providerDiscovery.autoEnabled`; an explicit false, a used provider, or a switch the user flips while the probe runs is never overridden.
- [ ] AC-03: The provider card shows "Turned on automatically because its CLI is signed in" with Undo; Undo turns it off and drops the record.

## Approach

- `packages/contracts/src/settings.ts`: `providerDiscovery.autoEnabled` (server-written, not in the patch schema).
- `apps/server/src/serverSettings.ts`: candidates decided once from the raw file on first load (later self-writes persist the default false, so they must not count as a choice); user updates drop candidates and records for drivers whose enabled flags change; `autoEnableDiscoveredProviders` re-checks under the write lock.
- `apps/server/src/provider/providerDiscovery.ts`: probes and a forked startup layer (`server.ts`).
- Web: `ProviderInstanceCard.tsx` notice + Undo; `ProviderSettingsPanel.tsx` passes `autoEnabled` for default slots.
- Risk: existing installs already persisted `enabled:false` after any settings write, so they are indistinguishable from a user's off and are not auto-enabled; slice 2's Rescan covers them.

## Decisions

### Asked
- D-01 Build slice 1 (Grok + OpenCode auto-enable) → yes (Anton, 2026-10-21)
### Defaulted (change any before sw-do)
- D-02 Existing persisted false is treated as a choice → never flipped (reversible later via Rescan)
### Open
- none

## Tasks

### T-01 Discovery probes and settings plumbing
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specweave-studio/apps/server/src/provider/providerDiscovery.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/serverSettings.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/server.ts, repositories/anton-abyzov/specweave-studio/packages/contracts/src/settings.ts | Test: cd repositories/anton-abyzov/specweave-studio/apps/server && npx vp test run src/provider/providerDiscovery.test.ts src/serverSettings.test.ts

### T-02 Card notice with Undo
- AC: AC-03 | Files: repositories/anton-abyzov/specweave-studio/apps/web/src/components/settings/ProviderInstanceCard.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/settings/ProviderSettingsPanel.tsx | Test: cd repositories/anton-abyzov/specweave-studio/apps/web && npx vp test run src/components/settings/ProviderInstanceCard.test.tsx
